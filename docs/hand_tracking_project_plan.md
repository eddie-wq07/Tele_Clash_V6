# Hand Tracking Mouse Control - 18 Hour Sprint Plan

## Project Overview
Build a hand-tracking system that controls the mouse cursor using laptop camera:
- Open hand = hover/move cursor
- Closed fist = click

## Tech Stack
- **Python 3.8+**
- **OpenCV** (`cv2`) - Camera capture and image processing
- **MediaPipe** (Google) - Hand landmark detection
- **PyAutoGUI** - Mouse control
- **NumPy** - Mathematical operations

## System Architecture

```
Camera Feed → MediaPipe Hand Detection → Gesture Recognition → Mouse Control
     ↓              ↓                          ↓                    ↓
  OpenCV      21 hand landmarks         Open/Closed logic      PyAutoGUI
```

## Core Components

### 1. Camera Handler (`camera_handler.py`)
- Initialize webcam
- Capture frames
- Adjust resolution for performance

### 2. Hand Detector (`hand_detector.py`)
- MediaPipe integration
- Hand landmark extraction
- Coordinate normalization

### 3. Gesture Recognizer (`gesture_recognizer.py`)
- Detect open vs closed hand
- Calculate finger distances
- Smooth gesture transitions

### 4. Mouse Controller (`mouse_controller.py`)
- Map hand position to screen coordinates
- Smooth cursor movement
- Handle click events
- Add click debouncing

### 5. Main Application (`main.py`)
- Integration of all components
- UI overlay (optional)
- Configuration settings

## Team Structure (4 People)

### Person 1: Camera & Hand Detection (4-5 hours)
**Tasks:**
- Set up OpenCV camera capture
- Integrate MediaPipe hands
- Extract hand landmarks
- Test detection accuracy

**Deliverables:**
- `camera_handler.py`
- `hand_detector.py`
- Basic visualization of landmarks

### Person 2: Gesture Recognition (5-6 hours)
**Tasks:**
- Calculate finger tip distances
- Implement open/closed hand logic
- Add smoothing algorithms
- Handle edge cases (hand exits frame)

**Deliverables:**
- `gesture_recognizer.py`
- Gesture state machine
- Unit tests for gestures

### Person 3: Mouse Control (4-5 hours)
**Tasks:**
- Implement PyAutoGUI mouse movement
- Screen coordinate mapping
- Cursor smoothing (exponential moving average)
- Click detection and debouncing
- Safety bounds (prevent out-of-screen)

**Deliverables:**
- `mouse_controller.py`
- Configuration for sensitivity
- Click state management

### Person 4: Integration & Polish (6-8 hours)
**Tasks:**
- Create main application loop
- Integrate all components
- Add UI overlay (FPS, gesture status)
- Performance optimization
- Error handling
- Documentation
- Testing and debugging

**Deliverables:**
- `main.py`
- `config.py`
- `README.md`
- `requirements.txt`

## Timeline (18 Hours)

### Hours 0-2: Setup & Planning
- **All team members:**
  - Environment setup
  - Install dependencies
  - Review architecture
  - Define interfaces between modules

### Hours 2-6: Parallel Development
- **Person 1:** Camera + MediaPipe integration
- **Person 2:** Start gesture recognition logic
- **Person 3:** Mouse control foundation
- **Person 4:** Project structure, config system

### Hours 6-10: Core Development
- **Person 1:** Hand detection refinement, pass to Person 4
- **Person 2:** Complete gesture recognition
- **Person 3:** Mouse smoothing and click logic
- **Person 4:** Begin integration

### Hours 10-14: Integration Phase
- **Persons 1-3:** Support integration, fix bugs
- **Person 4:** Main application loop, connect all modules
- **All:** First end-to-end test

### Hours 14-16: Testing & Refinement
- **All team members:**
  - Test in different lighting
  - Adjust sensitivity
  - Fix bugs
  - Optimize performance

### Hours 16-18: Polish & Documentation
- **Person 1 & 2:** Documentation, README
- **Person 3 & 4:** Final testing, demo preparation
- **All:** Code cleanup, comments

## Key Technical Details

### Hand Landmark Detection
MediaPipe provides 21 landmarks per hand:
- Wrist (0)
- Thumb (1-4)
- Index (5-8)
- Middle (9-12)
- Ring (13-16)
- Pinky (17-20)

### Open vs Closed Hand Detection
**Method 1: Finger Distance**
```python
# Measure distance between fingertips and palm center
# Open hand: distances are large
# Closed fist: distances are small
threshold = 0.1  # Normalized distance
```

**Method 2: Finger Curl**
```python
# Compare fingertip Y-coordinate to knuckle Y-coordinate
# If all fingertips below knuckles → closed
# If most fingertips above knuckles → open
```

### Coordinate Mapping
```python
# Hand coordinates (0-1) → Screen coordinates
screen_x = hand_x * screen_width
screen_y = hand_y * screen_height

# Add smoothing
smoothed_x = alpha * new_x + (1-alpha) * old_x
alpha = 0.3  # Smoothing factor
```

## Critical Success Factors

1. **Clear Interfaces**: Define function signatures early
2. **Version Control**: Use Git with clear branch strategy
3. **Frequent Integration**: Integrate every 2-3 hours
4. **Fallback Plans**: Have simpler gesture detection if complex fails
5. **Performance**: Target 30 FPS minimum

## Risk Mitigation

### Risk 1: MediaPipe Accuracy
- **Mitigation**: Adjust lighting, camera position
- **Fallback**: Use simpler color-based hand detection

### Risk 2: Integration Issues
- **Mitigation**: Define interfaces in hours 0-2
- **Fallback**: Person 4 starts integration early (hour 4)

### Risk 3: Performance Issues
- **Mitigation**: Lower camera resolution (640x480)
- **Fallback**: Reduce frame rate, optimize processing

### Risk 4: Click Detection Unreliable
- **Mitigation**: Add time-based filtering (hold for 200ms)
- **Fallback**: Use keyboard key as alternative click

## Installation & Setup

### Required Libraries
```bash
pip install opencv-python mediapipe pyautogui numpy
```

### Development Environment
- Python 3.8+
- Webcam with decent lighting
- Screen resolution: 1920x1080 recommended
- IDE: VSCode recommended

## Testing Strategy

### Unit Tests (Each Component)
- Test hand detection with sample images
- Test gesture logic with mock coordinates
- Test mouse controller with boundaries

### Integration Tests
- End-to-end gesture → click workflow
- Performance under different conditions
- Multi-hand scenarios (should ignore)

### User Acceptance
- Can control cursor smoothly
- Can click reliably
- No false positives/negatives
- Works in normal room lighting

## Success Metrics

- **FPS**: Minimum 25 FPS
- **Latency**: <100ms from gesture to action
- **Accuracy**: >95% gesture recognition
- **Usability**: Can click a button after 30 seconds practice

## Communication Strategy

### Standups (Every 3 hours)
- What did you complete?
- What are you working on?
- Any blockers?

### Shared Resources
- Google Doc for notes
- Discord/Slack for communication
- GitHub for code (or shared folder)
- Shared test video for development

## Bonus Features (If Time Permits)
1. Pinch gesture for right-click
2. Two-hand gestures for scrolling
3. Gesture calibration UI
4. Settings panel
5. Multi-hand support
6. Gesture history visualization

## Final Deliverables

1. Working Python application
2. Requirements.txt
3. README with setup instructions
4. Demo video (2-3 minutes)
5. Architecture diagram
6. Known issues documentation

---

## Quick Start Code Snippets

### Basic MediaPipe Setup
```python
import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
```

### Basic Camera Loop
```python
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Process frame
    cv2.imshow('Hand Tracking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
```

### Basic PyAutoGUI
```python
import pyautogui
pyautogui.FAILSAFE = True  # Move to corner to stop
pyautogui.moveTo(x, y, duration=0.1)
pyautogui.click()
```

Good luck with your sprint! 🚀
