"""
Configuration File
Centralized settings for the hand tracking mouse control system
"""


class Config:
    # Camera Settings
    CAMERA_INDEX = 0  # Default camera (usually 0)
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Hand Detection Settings
    MAX_NUM_HANDS = 1
    MIN_DETECTION_CONFIDENCE = 0.5  # Lowered for faster processing
    MIN_TRACKING_CONFIDENCE = 0.5
    MODEL_COMPLEXITY = 0  # 0 = Lite (fastest), 1 = Full (slower but more accurate)
    MIN_HAND_SIZE = 0.15  # Minimum hand size as fraction of frame (filters out small/distant hands)
    MAX_HAND_DEPTH = 0.1  # Maximum depth/distance from camera (smaller = closer, filters far hands)
    
    # Frame Processing Settings
    PROCESS_EVERY_N_FRAMES = 1  # Process every frame (1 = no skipping)
    
    # Gesture Recognition Settings
    GESTURE_SMOOTHING_FRAMES = 5  # Number of frames for smoothing
    CLOSED_HAND_THRESHOLD = 0.08  # Distance threshold for closed hand
    
    # Mouse Control Settings
    CURSOR_SMOOTHING_FACTOR = 0.3  # 0-1, lower = smoother but slower
    CLICK_COOLDOWN = 0.3  # Seconds between clicks
    SCREEN_MARGIN = 0  # Pixels from edge (0 = can reach actual edges)
    MOVEMENT_THRESHOLD = 2  # Minimum pixels to move (reduces jitter)
    TRACKING_ZONE_MIN = 0.10  # Start of active tracking zone (0-1)
    TRACKING_ZONE_MAX = 0.90  # End of active tracking zone (0-1)
    
    # UI Settings
    SHOW_CAMERA_FEED = True
    DRAW_HAND_LANDMARKS = True
    SHOW_FPS = True
    SHOW_GESTURE_STATUS = True
    SHOW_CURSOR_POSITION = True
    SHOW_TRACKING_ZONE = True  # Show tracking zone boundaries on camera feed
    
    # Performance Settings
    MAX_FPS = 60  # Cap FPS (60 = effectively no cap)
    
    # Control Point Settings
    CURSOR_CONTROL_LANDMARK = 8  # Index finger tip
    
    # Color Settings (BGR format)
    COLOR_OPEN_HAND = (0, 255, 0)  # Green
    COLOR_CLOSED_HAND = (0, 0, 255)  # Red
    COLOR_TEXT = (255, 255, 255)  # White
    COLOR_FPS_GOOD = (0, 255, 0)  # Green (>25 FPS)
    COLOR_FPS_MEDIUM = (0, 255, 255)  # Yellow (15-25 FPS)
    COLOR_FPS_BAD = (0, 0, 255)  # Red (<15 FPS)


# Preset configurations for different use cases

class HighPerformanceConfig(Config):
    """Optimized for performance - lower quality but faster"""
    CAMERA_WIDTH = 480
    CAMERA_HEIGHT = 360
    GESTURE_SMOOTHING_FRAMES = 3
    MIN_DETECTION_CONFIDENCE = 0.5
    MIN_TRACKING_CONFIDENCE = 0.4
    MODEL_COMPLEXITY = 0  # Lite model
    PROCESS_EVERY_N_FRAMES = 2  # Skip frames


class HighAccuracyConfig(Config):
    """Optimized for accuracy - higher quality but slower"""
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    GESTURE_SMOOTHING_FRAMES = 7
    MIN_DETECTION_CONFIDENCE = 0.8
    MIN_TRACKING_CONFIDENCE = 0.7
    CURSOR_SMOOTHING_FACTOR = 0.2
    MODEL_COMPLEXITY = 1  # Full model
    PROCESS_EVERY_N_FRAMES = 1


class ResponsiveConfig(Config):
    """Optimized for responsiveness - less smoothing"""
    CURSOR_SMOOTHING_FACTOR = 0.5
    GESTURE_SMOOTHING_FRAMES = 3
    CLICK_COOLDOWN = 0.2
    MODEL_COMPLEXITY = 0
    PROCESS_EVERY_N_FRAMES = 1


class SmoothConfig(Config):
    """Optimized for smooth cursor movement"""
    CURSOR_SMOOTHING_FACTOR = 0.2
    GESTURE_SMOOTHING_FRAMES = 7
    MOVEMENT_THRESHOLD = 1
    MODEL_COMPLEXITY = 0
    PROCESS_EVERY_N_FRAMES = 1


# Select which configuration to use
ACTIVE_CONFIG = Config  # Default configuration
# ACTIVE_CONFIG = HighPerformanceConfig
# ACTIVE_CONFIG = HighAccuracyConfig
# ACTIVE_CONFIG = ResponsiveConfig
# ACTIVE_CONFIG = SmoothConfig