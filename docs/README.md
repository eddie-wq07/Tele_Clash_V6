# Hand Tracking Mouse Control System

Control your mouse cursor using hand gestures captured by your laptop camera!

- **Open hand** = Move cursor (hover)
- **Closed fist** = Click

## 🎯 Project Overview

This project uses computer vision and machine learning to detect hand gestures and control the mouse cursor in real-time. Built with Python, OpenCV, and MediaPipe.

### Features

✅ Real-time hand tracking  
✅ Gesture recognition (open/closed hand)  
✅ Smooth cursor movement  
✅ Click detection with debouncing  
✅ Configurable sensitivity  
✅ FPS monitoring  
✅ Emergency failsafe (move to corner)  

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam
- Operating System: Windows, macOS, or Linux

### Installation

1. **Clone or download this project**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

This will install:
- opencv-python (camera and image processing)
- mediapipe (hand landmark detection)
- pyautogui (mouse control)
- numpy (mathematical operations)

### Running the Application

```bash
python main.py
```

The application will:
1. Initialize the camera and hand detector
2. Show a 3-second countdown
3. Start tracking your hand movements

### Controls

- **Open hand** → Move the cursor
- **Closed fist** → Click
- **Press 'Q'** → Quit the application
- **Move mouse to screen corner** → Emergency stop

## 📁 Project Structure

```
.
├── main.py                  # Main application entry point
├── camera_handler.py        # Camera capture management
├── hand_detector.py         # MediaPipe hand detection
├── gesture_recognizer.py    # Gesture classification
├── mouse_controller.py      # Mouse movement and clicking
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
└── hand_tracking_project_plan.md  # Detailed project plan
```

## 🎛️ Configuration

Edit `config.py` to customize the behavior:

### Common Settings

```python
# Camera resolution (lower = faster, higher = more accurate)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Cursor smoothing (0.1 = very smooth, 0.5 = responsive)
CURSOR_SMOOTHING_FACTOR = 0.3

# Click cooldown in seconds
CLICK_COOLDOWN = 0.3

# Gesture smoothing frames (higher = more stable)
GESTURE_SMOOTHING_FRAMES = 5
```

### Preset Configurations

The project includes preset configurations:

- **Default** - Balanced performance and accuracy
- **HighPerformanceConfig** - Optimized for speed
- **HighAccuracyConfig** - Optimized for precision
- **ResponsiveConfig** - Minimal latency
- **SmoothConfig** - Maximum smoothness

To use a preset, edit `config.py`:
```python
ACTIVE_CONFIG = HighPerformanceConfig  # Change this line
```

## 🛠️ Development Guide

### Module Descriptions

#### camera_handler.py
Manages webcam initialization and frame capture. Handles:
- Camera device selection
- Resolution configuration
- Frame mirroring for intuitive control

#### hand_detector.py
Uses MediaPipe to detect hand landmarks. Provides:
- 21 landmark points per hand
- Hand tracking across frames
- Palm center calculation
- Fingertip position extraction

#### gesture_recognizer.py
Classifies hand gestures. Features:
- Open/closed hand detection
- Finger extension analysis
- Temporal smoothing
- Distance-based validation

#### mouse_controller.py
Controls the mouse cursor. Implements:
- Screen coordinate mapping
- Exponential smoothing
- Click debouncing
- Safety margins
- FailSafe protection

### Testing Individual Modules

Each module can be tested independently:

```bash
# Test camera
python camera_handler.py

# Test hand detection
python hand_detector.py

# Test gesture recognition
python gesture_recognizer.py

# Test mouse control
python mouse_controller.py
```

## 🐛 Troubleshooting

### Camera Not Found
- Check camera permissions
- Try different CAMERA_INDEX values (0, 1, 2...)
- Ensure no other application is using the camera

### Hand Not Detected
- Ensure good lighting
- Position hand clearly in view
- Adjust MIN_DETECTION_CONFIDENCE in config.py
- Try a plain background

### Cursor Movement Jittery
- Increase CURSOR_SMOOTHING_FACTOR (make it smaller, e.g., 0.2)
- Increase GESTURE_SMOOTHING_FRAMES
- Lower camera resolution

### Cursor Movement Too Slow/Laggy
- Decrease CURSOR_SMOOTHING_FACTOR (make it larger, e.g., 0.5)
- Use HighPerformanceConfig preset
- Lower camera resolution

### Clicks Not Registering
- Adjust CLOSED_HAND_THRESHOLD in config.py
- Make a tighter fist
- Increase GESTURE_SMOOTHING_FRAMES

### Too Many Accidental Clicks
- Increase CLICK_COOLDOWN
- Increase GESTURE_SMOOTHING_FRAMES
- Adjust CLOSED_HAND_THRESHOLD

### Low FPS
- Use HighPerformanceConfig preset
- Lower camera resolution
- Close other applications
- Reduce GESTURE_SMOOTHING_FRAMES

## 🎯 Performance Tips

1. **Lighting**: Good lighting significantly improves hand detection
2. **Background**: Plain backgrounds work best
3. **Hand Position**: Keep hand at medium distance from camera
4. **Resolution**: Start with 640x480, adjust as needed
5. **CPU Usage**: Lower resolution and FPS if needed

## 📊 System Requirements

### Minimum
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Camera: 480p webcam
- Python 3.8+

### Recommended
- CPU: Quad-core 2.5 GHz or higher
- RAM: 8 GB
- Camera: 720p webcam
- Python 3.9+

## 🔒 Safety Features

- **FailSafe**: Move mouse to screen corner to stop
- **Screen Margins**: Cursor can't go to extreme edges
- **Click Cooldown**: Prevents rapid accidental clicks
- **Gesture Smoothing**: Reduces false positives

## 🏗️ 18-Hour Development Plan

This project was designed to be completed in 18 hours with a team of 4:

- **Person 1**: Camera & Hand Detection (4-5 hours)
- **Person 2**: Gesture Recognition (5-6 hours)
- **Person 3**: Mouse Control (4-5 hours)
- **Person 4**: Integration & Polish (6-8 hours)

See `hand_tracking_project_plan.md` for the detailed timeline and task breakdown.

## 🤝 Team Collaboration Tips

1. **Define interfaces early** - Agree on function signatures in first 2 hours
2. **Use version control** - Git with feature branches
3. **Integrate frequently** - Every 2-3 hours
4. **Communication** - Stand-ups every 3 hours
5. **Testing** - Test modules independently before integration

## 📝 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

- **MediaPipe** by Google for hand landmark detection
- **OpenCV** for computer vision tools
- **PyAutoGUI** for mouse control

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the project plan document
3. Test individual modules to isolate problems
4. Adjust configuration settings

## 🎓 Learning Resources

- [MediaPipe Hands Documentation](https://google.github.io/mediapipe/solutions/hands.html)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [PyAutoGUI Documentation](https://pyautogui.readthedocs.io/)

## 🚀 Future Enhancements

Possible improvements if you have more time:
- Pinch gesture for right-click
- Two-hand gestures for scrolling
- Gesture calibration UI
- Multi-hand support
- Gesture macros
- Voice commands integration
- Machine learning for custom gestures

---

**Built with ❤️ using Python, OpenCV, and MediaPipe**
