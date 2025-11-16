"""
Camera Handler Module
Manages webcam initialization and frame capture
"""

import cv2
import numpy as np


class CameraHandler:
    def __init__(self, camera_index=0, width=640, height=480):
        """
        Initialize camera handler
        
        Args:
            camera_index: Camera device index (0 for default)
            width: Frame width
            height: Frame height
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        
    def start(self):
        """Start camera capture"""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            raise Exception(f"Could not open camera {self.camera_index}")
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Set FPS (if supported)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print(f"Camera started: {self.width}x{self.height}")
        
    def read_frame(self):
        """
        Read a frame from camera
        
        Returns:
            tuple: (success, frame) - success is bool, frame is numpy array
        """
        if self.cap is None:
            raise Exception("Camera not started. Call start() first.")
        
        ret, frame = self.cap.read()
        
        if ret:
            # Flip horizontally for mirror effect (more intuitive)
            frame = cv2.flip(frame, 1)
        
        return ret, frame
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            print("Camera released")
    
    def is_opened(self):
        """Check if camera is opened"""
        return self.cap is not None and self.cap.isOpened()


if __name__ == "__main__":
    # Test camera handler
    camera = CameraHandler()
    camera.start()
    
    print("Press 'q' to quit")
    
    while camera.is_opened():
        ret, frame = camera.read_frame()
        
        if not ret:
            print("Failed to read frame")
            break
        
        cv2.imshow("Camera Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()
