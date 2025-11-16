"""
Mouse Controller Module
Controls mouse cursor movement, clicking, and dragging
"""

import pyautogui
import time
from collections import deque


class MouseController:
    def __init__(self, smoothing_factor=0.3, click_cooldown=0.3,
                 screen_margin=50, movement_threshold=2,
                 tracking_zone_min=0.15, tracking_zone_max=0.85):
        """
        Initialize mouse controller

        Args:
            smoothing_factor: Exponential smoothing (0-1, lower = more smooth)
            click_cooldown: Minimum seconds between clicks
            screen_margin: Pixels from screen edge to create dead zone
            movement_threshold: Minimum pixel movement to update cursor
            tracking_zone_min: Minimum boundary of active tracking zone (0-1)
            tracking_zone_max: Maximum boundary of active tracking zone (0-1)
        """
        self.smoothing_factor = smoothing_factor
        self.drag_smoothing_factor = 0.7  # More responsive during drag
        self.click_cooldown = click_cooldown
        self.screen_margin = screen_margin
        self.movement_threshold = movement_threshold
        self.drag_movement_threshold = 0  # No threshold during drag

        # Tracking zone boundaries (portion of camera frame to use)
        self.tracking_zone_min = tracking_zone_min
        self.tracking_zone_max = tracking_zone_max
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"Screen size: {self.screen_width}x{self.screen_height}")
        
        # Smoothed cursor position
        self.smooth_x = self.screen_width // 2
        self.smooth_y = self.screen_height // 2
        
        # Click state tracking
        self.last_click_time = 0
        self.previous_gesture = "open"
        self.is_clicking = False
        
        # Drag state tracking
        self.is_dragging = False
        self.drag_start_position = None
        self.drag_start_time = 0
        self.min_drag_time = 0.15  # Minimum time to hold before drag (seconds)
        
        # Safety settings
        pyautogui.FAILSAFE = True  # Move to corner to stop
        pyautogui.PAUSE = 0.01  # Small pause between actions
        
    def map_to_screen(self, hand_x, hand_y):
        """
        Map normalized hand coordinates (0-1) to screen coordinates
        Uses a tracking zone to allow reaching screen edges without hand leaving camera

        Args:
            hand_x: Normalized x coordinate (0-1)
            hand_y: Normalized y coordinate (0-1)

        Returns:
            tuple: (screen_x, screen_y)
        """
        # Remap hand coordinates from tracking zone to full 0-1 range
        # If hand is at tracking_zone_min, it maps to 0
        # If hand is at tracking_zone_max, it maps to 1
        zone_width = self.tracking_zone_max - self.tracking_zone_min

        # Remap x coordinate
        remapped_x = (hand_x - self.tracking_zone_min) / zone_width
        remapped_x = max(0, min(1, remapped_x))  # Clamp to 0-1

        # Remap y coordinate
        remapped_y = (hand_y - self.tracking_zone_min) / zone_width
        remapped_y = max(0, min(1, remapped_y))  # Clamp to 0-1

        # Map to screen coordinates
        screen_x = int(remapped_x * self.screen_width)
        screen_y = int(remapped_y * self.screen_height)

        # Apply margins (keep cursor away from edges)
        screen_x = max(self.screen_margin,
                      min(screen_x, self.screen_width - self.screen_margin))
        screen_y = max(self.screen_margin,
                      min(screen_y, self.screen_height - self.screen_margin))

        return screen_x, screen_y
    
    def smooth_position(self, new_x, new_y):
        """
        Apply exponential smoothing to cursor position
        
        Args:
            new_x: New x coordinate
            new_y: New y coordinate
            
        Returns:
            tuple: (smoothed_x, smoothed_y)
        """
        # Use more responsive smoothing during drag
        factor = self.drag_smoothing_factor if self.is_dragging else self.smoothing_factor
        
        # Exponential moving average
        self.smooth_x = (factor * new_x + 
                        (1 - factor) * self.smooth_x)
        self.smooth_y = (factor * new_y + 
                        (1 - factor) * self.smooth_y)
        
        return int(self.smooth_x), int(self.smooth_y)
    
    def move_cursor(self, hand_x, hand_y):
        """
        Move cursor based on hand position
        
        Args:
            hand_x: Normalized hand x position (0-1)
            hand_y: Normalized hand y position (0-1)
        """
        # Map to screen coordinates
        screen_x, screen_y = self.map_to_screen(hand_x, hand_y)
        
        # Apply smoothing
        smooth_x, smooth_y = self.smooth_position(screen_x, screen_y)
        
        # Get current cursor position
        current_x, current_y = pyautogui.position()
        
        # Use different thresholds for dragging vs normal movement
        threshold = self.drag_movement_threshold if self.is_dragging else self.movement_threshold
        
        # Only move if movement is significant (reduces jitter)
        distance = ((smooth_x - current_x)**2 + (smooth_y - current_y)**2)**0.5
        
        if distance > threshold:
            try:
                # moveTo works during drag - cursor moves while button held
                pyautogui.moveTo(smooth_x, smooth_y, _pause=False)
            except pyautogui.FailSafeException:
                print("FailSafe triggered - mouse moved to corner")
                # Clean up if failsafe triggers during drag
                if self.is_dragging:
                    pyautogui.mouseUp()
                    self.is_dragging = False
                raise
    
    def handle_click(self, gesture):
        """
        Handle click and drag based on gesture
        
        Args:
            gesture: Current gesture ("open" or "closed")
        """
        current_time = time.time()
        
        # Transition from open to closed - start drag or prepare for click
        if gesture == "closed" and self.previous_gesture == "open":
            # Check if enough time has passed since last action
            if current_time - self.last_click_time > self.click_cooldown:
                if not self.is_dragging:
                    # Start dragging - hold mouse button down
                    try:
                        pyautogui.mouseDown()
                        self.is_dragging = True
                        self.drag_start_position = pyautogui.position()
                        self.drag_start_time = current_time
                        self.is_clicking = True
                        print("Drag started!")
                    except pyautogui.FailSafeException:
                        print("FailSafe triggered during drag start")
                        raise
        
        # Transition from closed to open - end drag or register click
        elif gesture == "open" and self.previous_gesture == "closed":
            if self.is_dragging:
                try:
                    # Calculate drag distance to determine if it was a click or drag
                    current_pos = pyautogui.position()
                    drag_distance = ((current_pos[0] - self.drag_start_position[0])**2 + 
                                   (current_pos[1] - self.drag_start_position[1])**2)**0.5
                    drag_duration = current_time - self.drag_start_time
                    
                    # Release mouse button
                    pyautogui.mouseUp()
                    self.is_dragging = False
                    self.last_click_time = current_time
                    
                    # Determine if it was a click or drag
                    if drag_distance < 10 and drag_duration < self.min_drag_time:
                        print("Click!")
                    else:
                        print(f"Drag ended (moved {drag_distance:.0f}px)")
                    
                except pyautogui.FailSafeException:
                    print("FailSafe triggered during drag end")
                    if self.is_dragging:
                        pyautogui.mouseUp()
                        self.is_dragging = False
                    raise
        
        # Update clicking state
        if gesture == "open":
            self.is_clicking = False
        
        # Update previous gesture
        self.previous_gesture = gesture
    
    def update(self, hand_x, hand_y, gesture):
        """
        Update cursor position and handle clicks/drags
        
        Args:
            hand_x: Normalized hand x position (0-1)
            hand_y: Normalized hand y position (0-1)
            gesture: Current gesture ("open" or "closed")
        """
        # Move cursor (works during drag too)
        self.move_cursor(hand_x, hand_y)
        
        # Handle clicks and drags
        self.handle_click(gesture)
    
    def get_cursor_info(self):
        """
        Get current cursor information
        
        Returns:
            dict: Cursor position and state info
        """
        current_x, current_y = pyautogui.position()
        
        return {
            'x': current_x,
            'y': current_y,
            'is_clicking': self.is_clicking,
            'is_dragging': self.is_dragging,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height
        }
    
    def cleanup(self):
        """Release mouse button if still pressed"""
        if self.is_dragging:
            try:
                pyautogui.mouseUp()
                print("Cleanup: Released mouse button")
            except:
                pass
            self.is_dragging = False
            self.is_clicking = False


if __name__ == "__main__":
    # Test mouse controller with drag feature
    import cv2
    from camera_handler import CameraHandler
    from hand_detector import HandDetector
    from gesture_recognizer import GestureRecognizer
    
    camera = CameraHandler()
    camera.start()
    
    detector = HandDetector()
    recognizer = GestureRecognizer()
    controller = MouseController()
    
    print("Hand Mouse Control Test with Drag")
    print("Open hand = move cursor")
    print("Close fist and hold = drag")
    print("Close and release quickly = click")
    print("Press 'q' to quit")
    print("Move mouse to screen corner to emergency stop")
    
    try:
        while camera.is_opened():
            ret, frame = camera.read_frame()
            
            if not ret:
                break
            
            # Detect hands
            frame, hands_data = detector.find_hands(frame, draw=True)
            
            if hands_data:
                # Get first hand
                landmarks = hands_data[0]['landmarks']
                
                # Get index finger tip position (use as cursor control point)
                index_tip = landmarks[8]  # Index finger tip
                hand_x = index_tip['x']
                hand_y = index_tip['y']
                
                # Recognize gesture
                gesture = recognizer.get_smoothed_gesture(landmarks)
                
                # Update mouse
                try:
                    controller.update(hand_x, hand_y, gesture)
                except pyautogui.FailSafeException:
                    print("Emergency stop activated!")
                    break
                
                # Display info
                cursor_info = controller.get_cursor_info()
                
                # Color based on state
                if cursor_info['is_dragging']:
                    color = (255, 0, 255)  # Magenta for dragging
                    status = "DRAGGING"
                elif gesture == "closed":
                    color = (0, 0, 255)  # Red for closed
                    status = "CLOSED"
                else:
                    color = (0, 255, 0)  # Green for open
                    status = "HOVER"
                
                cv2.putText(frame, f"Gesture: {status}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                cv2.putText(frame, f"Cursor: ({cursor_info['x']}, {cursor_info['y']})",
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if cursor_info['is_dragging']:
                    cv2.putText(frame, "DRAG ACTIVE", (10, 110),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            
            cv2.imshow("Mouse Control Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        controller.cleanup()
        detector.release()
        camera.release()
        cv2.destroyAllWindows()