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
    MIN_DETECTION_CONFIDENCE = 0.5  # Balanced for performance
    MIN_TRACKING_CONFIDENCE = 0.5
    MODEL_COMPLEXITY = 0  # 0 = Lite (fastest), 1 = Full (slower but more accurate)
    MIN_HAND_SIZE = 0.15  # Minimum hand size as fraction of frame (filters out small/distant hands)
    MAX_HAND_DEPTH = 0.1  # Maximum depth/distance from camera (smaller = closer, filters far hands)

    # Frame Processing Settings
    PROCESS_EVERY_N_FRAMES = 2  # Process every 2nd frame for better FPS

    # Gesture Recognition Settings
    GESTURE_SMOOTHING_FRAMES = 3  # Reduced for faster response and better FPS
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
    """Optimized for maximum FPS - significantly faster"""
    CAMERA_WIDTH = 480
    CAMERA_HEIGHT = 360
    GESTURE_SMOOTHING_FRAMES = 2  # Minimal smoothing
    MIN_DETECTION_CONFIDENCE = 0.4  # Lower threshold for faster detection
    MIN_TRACKING_CONFIDENCE = 0.3
    MODEL_COMPLEXITY = 0  # Lite model
    PROCESS_EVERY_N_FRAMES = 3  # Process every 3rd frame
    DRAW_HAND_LANDMARKS = False  # Skip drawing for max speed
    SHOW_TRACKING_ZONE = False
    MIN_HAND_SIZE = 0.12  # Allow slightly smaller hands


class UltraPerformanceConfig(Config):
    """Optimized for absolute maximum FPS - lowest latency"""
    CAMERA_WIDTH = 320
    CAMERA_HEIGHT = 240
    GESTURE_SMOOTHING_FRAMES = 1  # No smoothing
    MIN_DETECTION_CONFIDENCE = 0.3
    MIN_TRACKING_CONFIDENCE = 0.3
    MODEL_COMPLEXITY = 0
    PROCESS_EVERY_N_FRAMES = 4  # Process every 4th frame
    DRAW_HAND_LANDMARKS = False
    SHOW_TRACKING_ZONE = False
    SHOW_CURSOR_POSITION = False
    MIN_HAND_SIZE = 0.10


class HighAccuracyConfig(Config):
    """Optimized for accuracy - higher quality but slower"""
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    GESTURE_SMOOTHING_FRAMES = 5
    MIN_DETECTION_CONFIDENCE = 0.7
    MIN_TRACKING_CONFIDENCE = 0.6
    CURSOR_SMOOTHING_FACTOR = 0.2
    MODEL_COMPLEXITY = 0  # Keep lite for reasonable FPS
    PROCESS_EVERY_N_FRAMES = 1
    MIN_HAND_SIZE = 0.18  # Require larger hands for accuracy


class BalancedConfig(Config):
    """Balanced performance and accuracy (recommended)"""
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    GESTURE_SMOOTHING_FRAMES = 3
    MIN_DETECTION_CONFIDENCE = 0.5
    MIN_TRACKING_CONFIDENCE = 0.5
    MODEL_COMPLEXITY = 0
    PROCESS_EVERY_N_FRAMES = 2
    CURSOR_SMOOTHING_FACTOR = 0.3


# Select which configuration to use
# Uncomment ONE of the following lines to activate a preset:

ACTIVE_CONFIG = Config  # Default: Balanced performance (30-60 FPS)
# ACTIVE_CONFIG = BalancedConfig  # Recommended: Best balance (40-70 FPS)
# ACTIVE_CONFIG = HighPerformanceConfig  # Fast: Lower res, skip frames (60-90 FPS)
# ACTIVE_CONFIG = UltraPerformanceConfig  # Maximum FPS: Minimal features (80-120 FPS)
# ACTIVE_CONFIG = HighAccuracyConfig  # Accurate: High res, more processing (20-40 FPS)

# Performance Tips:
# - Lower camera resolution = higher FPS
# - Higher PROCESS_EVERY_N_FRAMES = higher FPS but less responsive
# - Disable DRAW_HAND_LANDMARKS for +10-15 FPS
# - Lower GESTURE_SMOOTHING_FRAMES = faster response but more jitter