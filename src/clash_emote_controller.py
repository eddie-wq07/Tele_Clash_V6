"""
Clash Emote Controller
Detects hand gestures and triggers keyboard shortcuts for Clash Royale emotes.
Includes training mode for custom gesture recognition.
"""

import cv2
import numpy as np
import pyautogui
import time
import json
import os
from collections import deque
import pickle

# Import from existing modules
from camera_handler import CameraHandler
from hand_detector import HandDetector
from mouse_controller import MouseController
from config import ACTIVE_CONFIG as Config


class GestureClassifier:
    """Simple KNN classifier for gesture recognition based on hand landmarks"""

    def __init__(self, model_path="gesture_model.pkl"):
        self.model_path = model_path
        self.training_data = {"features": [], "labels": []}
        self.load_model()

    def extract_features(self, hands_data):
        """Extract features from hand landmarks for classification"""
        if len(hands_data) < 2:
            return None

        features = []

        for hand in hands_data[:2]:
            landmarks = hand['landmarks']
            if len(landmarks) < 21:
                return None

            # Extract key features:
            # 1. Hand center position (normalized)
            wrist = landmarks[0]
            middle_base = landmarks[9]
            center_x = (wrist['x'] + middle_base['x']) / 2
            center_y = (wrist['y'] + middle_base['y']) / 2
            features.extend([center_x, center_y])

            # 2. Finger extension states (4 fingers, excluding thumb complexity)
            for tip_idx, pip_idx in [(8, 6), (12, 10), (16, 14), (20, 18)]:
                tip_y = landmarks[tip_idx]['y']
                pip_y = landmarks[pip_idx]['y']
                extended = 1.0 if tip_y < pip_y else 0.0
                features.append(extended)

            # 3. Hand height (y position)
            features.append(center_y)

            # 4. Fingertip spread (distance between index and pinky)
            index_tip = landmarks[8]
            pinky_tip = landmarks[20]
            spread = np.sqrt((index_tip['x'] - pinky_tip['x'])**2 +
                           (index_tip['y'] - pinky_tip['y'])**2)
            features.append(spread)

        return np.array(features)

    def add_training_sample(self, hands_data, label):
        """Add a training sample"""
        features = self.extract_features(hands_data)
        if features is not None:
            self.training_data["features"].append(features.tolist())
            self.training_data["labels"].append(label)
            return True
        return False

    def predict(self, hands_data):
        """Predict gesture using KNN"""
        if not self.training_data["features"]:
            return None, 0.0

        features = self.extract_features(hands_data)
        if features is None:
            return None, 0.0

        # Simple KNN with k=5
        train_features = np.array(self.training_data["features"])
        train_labels = np.array(self.training_data["labels"])

        # Calculate distances
        distances = np.sqrt(np.sum((train_features - features)**2, axis=1))

        # Get k nearest neighbors
        k = min(5, len(distances))
        nearest_indices = np.argsort(distances)[:k]
        nearest_labels = train_labels[nearest_indices]
        nearest_distances = distances[nearest_indices]

        # Vote for most common label
        unique_labels, counts = np.unique(nearest_labels, return_counts=True)
        best_label = unique_labels[np.argmax(counts)]
        confidence = np.max(counts) / k

        # Also check if average distance is reasonable
        avg_distance = np.mean(nearest_distances)
        if avg_distance > 0.5:  # Too different from training data
            confidence *= 0.5

        return best_label, confidence

    def save_model(self):
        """Save training data to file"""
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.training_data, f)
        print(f"Model saved with {len(self.training_data['labels'])} samples")

    def load_model(self):
        """Load training data from file"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.training_data = pickle.load(f)
            print(f"Loaded model with {len(self.training_data['labels'])} samples")
        else:
            print("No existing model found, starting fresh")

    def get_sample_counts(self):
        """Get count of samples per label"""
        if not self.training_data["labels"]:
            return {}
        labels = np.array(self.training_data["labels"])
        unique, counts = np.unique(labels, return_counts=True)
        return dict(zip(unique, counts))

    def clear_training_data(self):
        """Clear all training data"""
        self.training_data = {"features": [], "labels": []}
        if os.path.exists(self.model_path):
            os.remove(self.model_path)
        print("Training data cleared")


class ClashEmoteApp:
    def __init__(self):
        print("="*60)
        print("CLASH EMOTE CONTROLLER")
        print("="*60)

        # Initialize camera
        self.camera = CameraHandler(
            camera_index=Config.CAMERA_INDEX,
            width=Config.CAMERA_WIDTH,
            height=Config.CAMERA_HEIGHT
        )

        # Hand detector (2 hands for emotes)
        self.detector = HandDetector(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0,
            min_hand_size=getattr(Config, 'MIN_HAND_SIZE', 0.15),
            max_hand_depth=getattr(Config, 'MAX_HAND_DEPTH', 0.1)
        )

        # Mouse controller
        self.controller = MouseController(
            smoothing_factor=Config.CURSOR_SMOOTHING_FACTOR,
            click_cooldown=Config.CLICK_COOLDOWN,
            screen_margin=Config.SCREEN_MARGIN,
            movement_threshold=Config.MOVEMENT_THRESHOLD,
            tracking_zone_min=Config.TRACKING_ZONE_MIN,
            tracking_zone_max=Config.TRACKING_ZONE_MAX
        )

        # Gesture classifier
        self.classifier = GestureClassifier()

        # State tracking
        self.emote_mode = False
        self.emote_cooldown = 2.0  # Seconds between emote triggers
        self.last_emote_time = 0
        self.emote_detection_history = deque(maxlen=10)

        # Two-hand detection cooldown
        self.last_two_hand_check_time = 0
        self.two_hand_check_interval = 0.5  # Check every 0.5 seconds

        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()

        # Training mode
        self.training_mode = False
        self.training_label = None
        self.samples_collected = 0

        # PyAutoGUI settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01

        print("Initialization complete!")

    def calculate_fps(self):
        self.frame_count += 1
        elapsed = time.time() - self.fps_start_time
        if elapsed > 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = time.time()

    def is_hand_closed(self, landmarks):
        """Check if hand is closed (fist)"""
        closed_count = 0
        for tip_idx, pip_idx in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            if landmarks[tip_idx]['y'] > landmarks[pip_idx]['y'] - 0.02:
                closed_count += 1
        return closed_count >= 3

    def detect_emote_rule_based(self, hands_data):
        """Rule-based emote detection (fallback if no training data)"""
        if len(hands_data) < 2:
            return None

        hand1 = hands_data[0]['landmarks']
        hand2 = hands_data[1]['landmarks']

        # Get hand centers
        h1_center_y = (hand1[0]['y'] + hand1[9]['y']) / 2
        h2_center_y = (hand2[0]['y'] + hand2[9]['y']) / 2
        h1_center_x = (hand1[0]['x'] + hand1[9]['x']) / 2
        h2_center_x = (hand2[0]['x'] + hand2[9]['x']) / 2

        h1_closed = self.is_hand_closed(hand1)
        h2_closed = self.is_hand_closed(hand2)

        # GOBLIN CRYING: Both fists high up (near eyes)
        if h1_closed and h2_closed:
            if h1_center_y < 0.45 and h2_center_y < 0.45:
                return "GOBLIN"

        # WIZARD 67: Both hands open, spread apart
        if not h1_closed and not h2_closed:
            horizontal_spread = abs(h1_center_x - h2_center_x)
            if horizontal_spread > 0.3:
                return "WIZARD"

        # PRINCESS YAWNING: One hand near center/mouth area
        for hand in [hand1, hand2]:
            center_x = (hand[0]['x'] + hand[9]['x']) / 2
            center_y = (hand[0]['y'] + hand[9]['y']) / 2
            if 0.3 < center_x < 0.7 and 0.25 < center_y < 0.5:
                if not self.is_hand_closed(hand):
                    return "PRINCESS"

        return None

    def process_emote(self, hands_data):
        """Process emote detection and trigger keys"""
        current_time = time.time()

        # 2-second cooldown between emotes
        if current_time - self.last_emote_time < self.emote_cooldown:
            return None

        # Try ML prediction first, fall back to rules
        emote = None
        confidence = 0.0

        if self.classifier.training_data["features"]:
            emote, confidence = self.classifier.predict(hands_data)
            if confidence < 0.6:
                emote = None

        # Fallback to rule-based detection
        if emote is None:
            emote = self.detect_emote_rule_based(hands_data)
            if emote:
                confidence = 0.7

        # If still nothing, just return
        if emote is None:
            # Optional: keep history just for debugging/overlay
            self.emote_detection_history.append(None)
            return None

        # Optional: track history but don't delay triggering
        self.emote_detection_history.append(emote)

        # Trigger immediately (no 5-frame waiting)
        self.trigger_emote(emote)
        self.last_emote_time = current_time
        return emote


    def trigger_emote(self, emote):
        """Press the corresponding key for the emote"""
        key_map = {
            "GOBLIN": "g",
            "WIZARD": "w",
            "PRINCESS": "p"
        }

        if emote in key_map:
            key = key_map[emote]
            pyautogui.press("e")
            time.sleep(0.1)  # Small delay to ensure 'e' is registered
            print(f"Pressing 'e' for emote menu")
            print(f"🎮 {emote} emote triggered! Pressing '{key}'")
            pyautogui.press(key)

    def draw_ui(self, frame, num_hands, current_emote=None):
        """Draw UI overlay"""
        h, w = frame.shape[:2]

        # Overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        y = 25

        # FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Mode
        mode_text = "EMOTE MODE" if self.emote_mode else "MOUSE MODE"
        mode_color = (0, 165, 255) if self.emote_mode else (0, 255, 0)
        cv2.putText(frame, mode_text, (150, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)

        y += 30
        cv2.putText(frame, f"Hands: {num_hands}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if current_emote:
            cv2.putText(frame, f"Emote: {current_emote}", (150, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Training mode indicator
        if self.training_mode:
            y += 30
            cv2.putText(frame, f"TRAINING: {self.training_label} ({self.samples_collected} samples)",
                       (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Sample counts
        y += 30
        counts = self.classifier.get_sample_counts()
        count_text = " | ".join([f"{k}:{v}" for k, v in counts.items()])
        cv2.putText(frame, f"Training data: {count_text}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Instructions
        cv2.putText(frame, "Q=Quit | T=Train mode | S=Save model | C=Clear data",
                   (10, h-40), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame, "Training: 1=Goblin | 2=Wizard | 3=Princess | SPACE=Capture",
                   (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    def run(self):
        """Main loop"""
        self.camera.start()

        print("\n" + "="*60)
        print("CONTROLS:")
        print("  2 hands detected → Press 'E' (emote mode)")
        print("  Goblin Crying → Press 'G'")
        print("  Wizard 67 → Press 'W'")
        print("  Princess Yawning → Press 'P'")
        print("\nTRAINING MODE:")
        print("  Press T to toggle training mode")
        print("  Press 1/2/3 to select emote to train")
        print("  Press SPACE to capture sample")
        print("  Press S to save model")
        print("  Press C to clear all training data")
        print("="*60 + "\n")

        time.sleep(2)

        try:
            while True:
                ret, frame = self.camera.read_frame()
                if not ret:
                    break

                # Detect hands
                frame, hands_data = self.detector.find_hands(frame, draw=True)
                num_hands = len(hands_data)

                triggered_emote = None

                # Check for mode switch (only check every 0.5 seconds)
                current_time = time.time()

                # EMOTE MODE ACTIVATION LOGIC
                if not self.emote_mode:
                    # Only begin checking if there are 2 hands
                    if num_hands >= 2:
                        # If this is the first frame noticing 2 hands, start the timer
                        if self.last_two_hand_check_time == 0:
                            self.last_two_hand_check_time = current_time

                        # If 0.5 seconds have passed, and still 2 hands → switch to emote mode
                        elif current_time - self.last_two_hand_check_time >= self.two_hand_check_interval:
                            if num_hands >= 2:
                                self.emote_mode = True
                                self.controller.cleanup()

                            # Reset the timer either way
                            self.last_two_hand_check_time = 0
                    else:
                        # If fewer than 2 hands, reset the timer
                        self.last_two_hand_check_time = 0

                if self.emote_mode:
                    if num_hands >= 2:
                        if not self.training_mode:
                            triggered_emote = self.process_emote(hands_data)
                            if triggered_emote:
                                # Return to mouse mode after emote
                                self.emote_mode = False
                                print("Returning to MOUSE MODE")
                    else:
                        # Lost second hand, return to mouse mode
                        self.emote_mode = False
                        print("Returning to MOUSE MODE")

                elif num_hands == 1:
                    # Mouse control mode
                    landmarks = hands_data[0]['landmarks']
                    wrist = landmarks[0]

                    # Simple open/closed detection for click
                    is_closed = self.is_hand_closed(landmarks)
                    gesture = "closed" if is_closed else "open"

                    try:
                        self.controller.update(wrist['x'], wrist['y'], gesture)
                    except pyautogui.FailSafeException:
                        print("FailSafe triggered!")
                        break

                self.calculate_fps()
                self.draw_ui(frame, num_hands, triggered_emote)

                cv2.imshow("Clash Emote Controller", frame)

                # Handle key presses
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q') or key == ord('Q'):
                    break

                elif key == ord('t') or key == ord('T'):
                    self.training_mode = not self.training_mode
                    print(f"Training mode: {'ON' if self.training_mode else 'OFF'}")

                elif key == ord('s') or key == ord('S'):
                    self.classifier.save_model()

                elif key == ord('c') or key == ord('C'):
                    self.classifier.clear_training_data()

                elif key == ord('1'):
                    self.training_label = "GOBLIN"
                    self.samples_collected = 0
                    print("Training GOBLIN CRYING gesture")

                elif key == ord('2'):
                    self.training_label = "WIZARD"
                    self.samples_collected = 0
                    print("Training WIZARD 67 gesture")

                elif key == ord('3'):
                    self.training_label = "PRINCESS"
                    self.samples_collected = 0
                    print("Training PRINCESS YAWNING gesture")

                elif key == ord(' ') and self.training_mode and self.training_label:
                    # Capture training sample
                    if num_hands >= 2:
                        if self.classifier.add_training_sample(hands_data, self.training_label):
                            self.samples_collected += 1
                            print(f"Captured sample {self.samples_collected} for {self.training_label}")
                        else:
                            print("Failed to capture sample")
                    else:
                        print("Need 2 hands visible to capture sample")

        except KeyboardInterrupt:
            print("\nInterrupted")

        finally:
            self.controller.cleanup()
            self.detector.release()
            self.camera.release()
            cv2.destroyAllWindows()
            print("Cleanup complete")


if __name__ == "__main__":
    app = ClashEmoteApp()
    app.run()
