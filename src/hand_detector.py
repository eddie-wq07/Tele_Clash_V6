"""
Hand Detector Module
Uses MediaPipe to detect hand landmarks
"""

import cv2
import mediapipe as mp
import numpy as np


class HandDetector:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, 
                 min_tracking_confidence=0.5, model_complexity=0):
        """
        Initialize MediaPipe hand detector
        
        Args:
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
            model_complexity: 0 for Lite model (faster), 1 for Full model (more accurate)
        """
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,  # Video mode for tracking (faster)
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,  # 0 = Lite, 1 = Full
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Landmark indices
        self.WRIST = 0
        self.THUMB_TIP = 4
        self.INDEX_TIP = 8
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        self.PINKY_TIP = 20
        
        # Cache for frame dimensions
        self._frame_shape = None
        
    def find_hands(self, frame, draw=True):
        """
        Find hands in frame
        
        Args:
            frame: BGR image from camera
            draw: Whether to draw landmarks on frame
            
        Returns:
            tuple: (processed_frame, hands_data)
                hands_data is list of dicts with 'landmarks' and 'handedness'
        """
        # Cache frame shape for efficiency
        if self._frame_shape is None or self._frame_shape != frame.shape:
            self._frame_shape = frame.shape
            self._h, self._w, self._c = frame.shape
        
        # Convert BGR to RGB for MediaPipe
        # Use cv2.cvtColor which is optimized
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Set writeable to False for performance (MediaPipe recommendation)
        rgb_frame.flags.writeable = False
        
        # Process frame
        results = self.hands.process(rgb_frame)
        
        # Set writeable back to True
        rgb_frame.flags.writeable = True
        
        hands_data = []
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw landmarks if requested
                if draw:
                    self.mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                
                # Extract landmark coordinates
                landmarks = []
                
                for lm in hand_landmarks.landmark:
                    # Convert normalized coordinates to pixel coordinates
                    cx, cy = int(lm.x * self._w), int(lm.y * self._h)
                    landmarks.append({
                        'x': lm.x,  # Normalized (0-1)
                        'y': lm.y,  # Normalized (0-1)
                        'z': lm.z,  # Depth
                        'pixel_x': cx,
                        'pixel_y': cy
                    })
                
                # Get handedness (left or right)
                handedness = "Unknown"
                if results.multi_handedness:
                    handedness = results.multi_handedness[hand_idx].classification[0].label
                
                hands_data.append({
                    'landmarks': landmarks,
                    'handedness': handedness
                })
        
        return frame, hands_data
    
    def get_finger_tip_positions(self, landmarks):
        """
        Get positions of all finger tips
        
        Args:
            landmarks: List of landmark dicts
            
        Returns:
            dict: Finger tip positions
        """
        if len(landmarks) < 21:
            return None
        
        return {
            'thumb': landmarks[self.THUMB_TIP],
            'index': landmarks[self.INDEX_TIP],
            'middle': landmarks[self.MIDDLE_TIP],
            'ring': landmarks[self.RING_TIP],
            'pinky': landmarks[self.PINKY_TIP]
        }
    
    def get_palm_center(self, landmarks):
        """
        Calculate palm center from wrist and middle finger base
        
        Args:
            landmarks: List of landmark dicts
            
        Returns:
            dict: Palm center coordinates
        """
        if len(landmarks) < 21:
            return None
        
        wrist = landmarks[self.WRIST]
        middle_base = landmarks[9]  # Middle finger MCP joint
        
        return {
            'x': (wrist['x'] + middle_base['x']) / 2,
            'y': (wrist['y'] + middle_base['y']) / 2,
            'pixel_x': (wrist['pixel_x'] + middle_base['pixel_x']) // 2,
            'pixel_y': (wrist['pixel_y'] + middle_base['pixel_y']) // 2
        }
    
    def release(self):
        """Release MediaPipe resources"""
        self.hands.close()


if __name__ == "__main__":
    # Test hand detector
    from camera_handler import CameraHandler
    
    camera = CameraHandler()
    camera.start()
    
    detector = HandDetector(model_complexity=0)  # Use lite model for testing
    
    print("Show your hand to the camera. Press 'q' to quit.")
    
    while camera.is_opened():
        ret, frame = camera.read_frame()
        
        if not ret:
            break
        
        # Detect hands
        frame, hands_data = detector.find_hands(frame, draw=True)
        
        # Display hand count
        cv2.putText(frame, f"Hands: {len(hands_data)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Hand Detection Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    detector.release()
    camera.release()
    cv2.destroyAllWindows()