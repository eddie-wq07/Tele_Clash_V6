"""
Main Application
Hand Tracking Mouse Control System
"""

import cv2
import time
import numpy as np
from camera_handler import CameraHandler
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from mouse_controller import MouseController
from config import ACTIVE_CONFIG as Config


class HandMouseApp:
    def __init__(self):
        """Initialize the hand mouse control application"""
        print("="*50)
        print("Hand Tracking Mouse Control System")
        print("="*50)
        
        # Initialize components
        print("Initializing camera...")
        self.camera = CameraHandler(
            camera_index=Config.CAMERA_INDEX,
            width=Config.CAMERA_WIDTH,
            height=Config.CAMERA_HEIGHT
        )
        
        print("Initializing hand detector...")
        self.detector = HandDetector(
            max_num_hands=Config.MAX_NUM_HANDS,
            min_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE,
            model_complexity=getattr(Config, 'MODEL_COMPLEXITY', 0)
        )
        
        print("Initializing gesture recognizer...")
        self.recognizer = GestureRecognizer(
            smoothing_frames=Config.GESTURE_SMOOTHING_FRAMES,
            closed_threshold=Config.CLOSED_HAND_THRESHOLD
        )
        
        print("Initializing mouse controller...")
        self.controller = MouseController(
            smoothing_factor=Config.CURSOR_SMOOTHING_FACTOR,
            click_cooldown=Config.CLICK_COOLDOWN,
            screen_margin=Config.SCREEN_MARGIN,
            movement_threshold=Config.MOVEMENT_THRESHOLD,
            tracking_zone_min=Config.TRACKING_ZONE_MIN,
            tracking_zone_max=Config.TRACKING_ZONE_MAX
        )
        
        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()
        
        # Frame skipping for performance
        self.process_every_n_frames = getattr(Config, 'PROCESS_EVERY_N_FRAMES', 1)
        self.frame_counter = 0
        
        # Cache last detection results for frame skipping
        self.last_hands_data = []
        self.last_gesture = "open"
        self.last_hand_x = 0.5
        self.last_hand_y = 0.5
        
        # Running state
        self.running = False
        
        print(f"Frame skipping: Process every {self.process_every_n_frames} frame(s)")
        print("Initialization complete!")
        print("="*50)
        
    def calculate_fps(self):
        """Calculate and update FPS"""
        self.frame_count += 1
        
        # Update FPS every second
        elapsed = time.time() - self.fps_start_time
        if elapsed > 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = time.time()
    
    def draw_ui(self, frame, gesture, hand_detected):
        """
        Draw UI overlay on frame

        Args:
            frame: Camera frame
            gesture: Current gesture ("open", "closed", or None)
            hand_detected: Whether a hand was detected
        """
        h, w, _ = frame.shape

        # Draw tracking zone boundaries
        if Config.SHOW_TRACKING_ZONE:
            zone_x1 = int(w * Config.TRACKING_ZONE_MIN)
            zone_y1 = int(h * Config.TRACKING_ZONE_MIN)
            zone_x2 = int(w * Config.TRACKING_ZONE_MAX)
            zone_y2 = int(h * Config.TRACKING_ZONE_MAX)

            # Draw tracking zone rectangle
            cv2.rectangle(frame, (zone_x1, zone_y1), (zone_x2, zone_y2),
                         (0, 255, 255), 2)  # Yellow border

            # Add corner markers for better visibility
            marker_size = 20
            color = (0, 255, 255)
            thickness = 3
            # Top-left corner
            cv2.line(frame, (zone_x1, zone_y1), (zone_x1 + marker_size, zone_y1), color, thickness)
            cv2.line(frame, (zone_x1, zone_y1), (zone_x1, zone_y1 + marker_size), color, thickness)
            # Top-right corner
            cv2.line(frame, (zone_x2, zone_y1), (zone_x2 - marker_size, zone_y1), color, thickness)
            cv2.line(frame, (zone_x2, zone_y1), (zone_x2, zone_y1 + marker_size), color, thickness)
            # Bottom-left corner
            cv2.line(frame, (zone_x1, zone_y2), (zone_x1 + marker_size, zone_y2), color, thickness)
            cv2.line(frame, (zone_x1, zone_y2), (zone_x1, zone_y2 - marker_size), color, thickness)
            # Bottom-right corner
            cv2.line(frame, (zone_x2, zone_y2), (zone_x2 - marker_size, zone_y2), color, thickness)
            cv2.line(frame, (zone_x2, zone_y2), (zone_x2, zone_y2 - marker_size), color, thickness)

        # Semi-transparent overlay for better text visibility
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        y_offset = 30

        # FPS
        if Config.SHOW_FPS:
            fps_color = Config.COLOR_FPS_GOOD
            if self.fps < 15:
                fps_color = Config.COLOR_FPS_BAD
            elif self.fps < 25:
                fps_color = Config.COLOR_FPS_MEDIUM

            cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, fps_color, 2)
            y_offset += 35

        # Hand detection status
        if hand_detected:
            cv2.putText(frame, "Hand: DETECTED", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Hand: NOT DETECTED", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y_offset += 35

        # Get cursor info for drag status
        cursor_info = self.controller.get_cursor_info()

        # Gesture status
        if Config.SHOW_GESTURE_STATUS and gesture:
            if cursor_info['is_dragging']:
                gesture_text = "DRAGGING"
                color = (255, 0, 255)  # Magenta for dragging
            elif gesture == "open":
                gesture_text = "HOVER"
                color = Config.COLOR_OPEN_HAND
            else:
                gesture_text = "CLOSED"
                color = Config.COLOR_CLOSED_HAND

            cv2.putText(frame, f"Gesture: {gesture_text}", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 35

        # Cursor position
        if Config.SHOW_CURSOR_POSITION:
            cv2.putText(frame,
                       f"Cursor: ({cursor_info['x']}, {cursor_info['y']})",
                       (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, Config.COLOR_TEXT, 2)

        # Instructions (bottom of screen)
        instructions = [
            "Controls: Open Hand = Move | Close & Hold = Drag | Quick Close = Click",
            "Press 'Q' to quit | Move mouse to corner for emergency stop"
        ]

        y_pos = h - 60
        for instruction in instructions:
            cv2.putText(frame, instruction, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, Config.COLOR_TEXT, 1)
            y_pos += 25
    
    def process_frame(self):
        """
        Process a single frame
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Read frame
        ret, frame = self.camera.read_frame()
        if not ret:
            print("Failed to read frame")
            return False
        
        # Increment frame counter
        self.frame_counter += 1
        
        # Decide whether to process hand detection this frame
        should_process = (self.frame_counter % self.process_every_n_frames == 0)
        
        gesture = self.last_gesture
        hand_detected = len(self.last_hands_data) > 0
        hand_x = self.last_hand_x
        hand_y = self.last_hand_y

        if should_process:
            # Detect hands (expensive operation)
            frame, hands_data = self.detector.find_hands(
                frame, 
                draw=Config.DRAW_HAND_LANDMARKS
            )
            
            # Cache results
            self.last_hands_data = hands_data
            hand_detected = len(hands_data) > 0

            if hand_detected:
                # Get first hand
                landmarks = hands_data[0]['landmarks']

                # Calculate palm center (average of palm base landmarks)
                palm_landmarks = [0]
                hand_x = sum(landmarks[i]['x'] for i in palm_landmarks) / len(palm_landmarks)
                hand_y = sum(landmarks[i]['y'] for i in palm_landmarks) / len(palm_landmarks)
                
                # Cache position
                self.last_hand_x = hand_x
                self.last_hand_y = hand_y

                # Recognize gesture
                gesture = self.recognizer.get_smoothed_gesture(landmarks)
                self.last_gesture = gesture
        else:
            # Use cached data but still draw landmarks if we have them
            if Config.DRAW_HAND_LANDMARKS and hand_detected:
                # We skip drawing on non-processed frames for performance
                pass

        # Update mouse control using cached or new data
        if hand_detected:
            try:
                self.controller.update(hand_x, hand_y, gesture)
            except Exception as e:
                print(f"Mouse control error: {e}")
                return False

        # Calculate FPS
        self.calculate_fps()

        # Draw UI
        if Config.SHOW_CAMERA_FEED:
            self.draw_ui(frame, gesture, hand_detected)
            cv2.imshow("Hand Mouse Control", frame)
        
        return True
    
    def run(self):
        """Run the main application loop"""
        try:
            # Start camera
            self.camera.start()
            self.running = True
            
            print("\n" + "="*50)
            print("APPLICATION RUNNING")
            print("="*50)
            print("\nControls:")
            print("  • Open hand = Move cursor")
            print("  • Close fist and hold = Drag")
            print("  • Close and release quickly = Click")
            print("  • Press 'Q' = Quit")
            print("  • Move mouse to corner = Emergency stop")
            print("\nStarting in 3 seconds...")
            print("="*50 + "\n")
            
            # Give user time to prepare
            time.sleep(3)
            
            # Main loop
            while self.running:
                # Process frame
                if not self.process_frame():
                    break
                
                # Check for quit command
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\nQuit command received")
                    break
                
                # Optional: Cap FPS to reduce CPU usage
                # Removed sleep to maximize FPS - the processing itself is the bottleneck
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        self.running = False
        
        # Clean up mouse controller (release any held buttons)
        if hasattr(self, 'controller'):
            self.controller.cleanup()
        
        if hasattr(self, 'detector'):
            self.detector.release()
        
        if hasattr(self, 'camera'):
            self.camera.release()
        
        cv2.destroyAllWindows()
        
        print("Cleanup complete. Goodbye!")


def main():

    """Main entry point"""
    print("\n" + "="*60)
    print("CLASH ROYALE CONTROLLER - BLUESTACKS EDITION")
    print("="*60)
    print("\nSetup Instructions:")
    print("  1. Open BlueStacks Android Emulator")
    print("  2. Download and launch Clash Royale in BlueStacks")
    print("  3. Configure BlueStacks key mapping:")
    print("     - 'G' key = Emote 1 aka Crying emote")
    print("     - 'W' key = Emote 2 aka 6-7 emote")
    print("\nHow to Play:")
    print("  • Open hand = Move cursor")
    print("  • Close fist & hold = Drag troops onto battlefield")
    print("  • Quick close = Click/Select")
    print("  • Two fists near eye-level = Emote 1 (G key)")
    print("  • Six-seven gesture = Emote 6-7 (W key)")
    print("\nPhysical Setup:")
    print("  ✓ Camera has good lighting")
    print("  ✓ Plain background behind you")
    print("  ✓ Sit 1-2 feet from camera")
    print("\nReady to start?")
    print("="*60)
    
    input("Press ENTER to begin...")
    
    app = HandMouseApp()
    app.run()


if __name__ == "__main__":
    main()