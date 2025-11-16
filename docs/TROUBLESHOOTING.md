# TROUBLESHOOTING GUIDE

## Quick Diagnostics

Run this first:
```bash
python test_system.py
```

This will identify most common issues.

---

## Installation Issues

### "No module named 'cv2'"
**Problem**: OpenCV not installed  
**Solution**:
```bash
pip install opencv-python
```

### "No module named 'mediapipe'"
**Problem**: MediaPipe not installed  
**Solution**:
```bash
pip install mediapipe
```

### "ImportError: DLL load failed" (Windows)
**Problem**: Missing Visual C++ redistributables  
**Solution**:
- Download and install Microsoft Visual C++ Redistributable
- Or try: `pip install opencv-python-headless`

### pip install fails with permissions error
**Problem**: Need admin rights or use virtual environment  
**Solution**:
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Camera Issues

### "Camera could not be opened"
**Possible Causes**:
1. Camera is being used by another app
2. Wrong camera index
3. No camera permissions

**Solutions**:
1. Close other apps using camera (Zoom, Teams, etc.)
2. Try different camera indices in `config.py`:
   ```python
   CAMERA_INDEX = 1  # Try 0, 1, 2...
   ```
3. Check camera permissions:
   - **Windows**: Settings → Privacy → Camera
   - **macOS**: System Preferences → Security & Privacy → Camera
   - **Linux**: Check if user is in 'video' group

### Camera works but video is frozen
**Solution**:
- Restart the application
- Unplug and replug USB camera
- Reboot computer

### Camera video is upside down or mirrored wrong
**Solution**: Edit `camera_handler.py`, change flip parameters:
```python
frame = cv2.flip(frame, 1)  # 1 = horizontal, 0 = vertical, -1 = both
```

---

## Hand Detection Issues

### "Hand: NOT DETECTED" even when hand is visible

**Lighting Problems**:
- Ensure bright, even lighting
- Avoid backlighting (light source behind you)
- Use natural light or bright room lights

**Background Issues**:
- Use plain, contrasting background
- Avoid busy patterns
- Keep background static

**Hand Position**:
- Position hand 1-2 feet from camera
- Keep entire hand in frame
- Face palm toward camera

**Settings Adjustment**:
Edit `config.py`:
```python
MIN_DETECTION_CONFIDENCE = 0.5  # Lower = more sensitive (default 0.7)
MIN_TRACKING_CONFIDENCE = 0.3   # Lower = more sensitive (default 0.5)
```

### Hand detected but landmarks are jittery
**Solution**: Increase tracking confidence in `config.py`:
```python
MIN_TRACKING_CONFIDENCE = 0.7  # Higher = more stable
```

---

## Gesture Recognition Issues

### Gestures not being recognized correctly

**Open hand not detected**:
- Spread fingers wide
- Extend fingers fully
- Adjust threshold:
  ```python
  CLOSED_HAND_THRESHOLD = 0.10  # Increase from 0.08
  ```

**Closed fist not detected**:
- Make a tight fist
- Curl all fingers
- Adjust threshold:
  ```python
  CLOSED_HAND_THRESHOLD = 0.06  # Decrease from 0.08
  ```

### Gestures keep switching rapidly
**Solution**: Increase smoothing in `config.py`:
```python
GESTURE_SMOOTHING_FRAMES = 7  # Increase from 5
```

---

## Mouse Control Issues

### Cursor is jittery/shaky

**Solution 1**: Increase smoothing
```python
CURSOR_SMOOTHING_FACTOR = 0.2  # Decrease from 0.3 (smaller = smoother)
```

**Solution 2**: Increase movement threshold
```python
MOVEMENT_THRESHOLD = 5  # Increase from 2
```

**Solution 3**: Use SmoothConfig preset
```python
ACTIVE_CONFIG = SmoothConfig
```

### Cursor moves too slowly

**Solution 1**: Reduce smoothing
```python
CURSOR_SMOOTHING_FACTOR = 0.5  # Increase from 0.3
```

**Solution 2**: Use ResponsiveConfig preset
```python
ACTIVE_CONFIG = ResponsiveConfig
```

### Cursor doesn't reach screen edges

**Solution**: Reduce screen margin in `config.py`:
```python
SCREEN_MARGIN = 20  # Decrease from 50
```

### Cursor moves in wrong direction

**Solution**: Check camera flip settings in `camera_handler.py`:
```python
# Should be flip(frame, 1) for mirror effect
frame = cv2.flip(frame, 1)
```

---

## Click Issues

### Clicks not registering

**Make sure you're making a clear fist**:
- Close all fingers tightly
- Hold for 0.5 seconds

**Adjust click cooldown**:
```python
CLICK_COOLDOWN = 0.2  # Reduce from 0.3
```

**Lower closed threshold**:
```python
CLOSED_HAND_THRESHOLD = 0.06  # Decrease from 0.08
```

### Too many accidental clicks

**Increase click cooldown**:
```python
CLICK_COOLDOWN = 0.5  # Increase from 0.3
```

**Increase closed threshold**:
```python
CLOSED_HAND_THRESHOLD = 0.10  # Increase from 0.08
```

**Increase gesture smoothing**:
```python
GESTURE_SMOOTHING_FRAMES = 7  # Increase from 5
```

### Double-clicking when single click intended

**Solution**: Increase click cooldown
```python
CLICK_COOLDOWN = 0.5  # Increase from 0.3
```

---

## Performance Issues

### Low FPS (below 20)

**Solution 1**: Lower camera resolution in `config.py`:
```python
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 360
```

**Solution 2**: Use HighPerformanceConfig:
```python
ACTIVE_CONFIG = HighPerformanceConfig
```

**Solution 3**: Close other applications

**Solution 4**: Check CPU usage:
- Close background apps
- Disable antivirus temporarily
- Update graphics drivers

### High latency (delay between gesture and action)

**Reduce smoothing**:
```python
GESTURE_SMOOTHING_FRAMES = 3  # Decrease from 5
CURSOR_SMOOTHING_FACTOR = 0.5  # Increase from 0.3
```

**Use ResponsiveConfig**:
```python
ACTIVE_CONFIG = ResponsiveConfig
```

### Application freezes or crashes

**Check system resources**:
```bash
# Monitor CPU and memory
# Windows: Task Manager
# macOS: Activity Monitor
# Linux: top or htop
```

**Reduce camera resolution**:
```python
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 360
```

**Add error handling**: Check console for error messages

---

## Display Issues

### No camera window appears

**Check config**:
```python
SHOW_CAMERA_FEED = True  # Make sure this is True
```

**Try explicit display**:
```bash
# Linux: Check DISPLAY variable
echo $DISPLAY

# macOS: Check XQuartz if using SSH
```

### UI elements not visible

**Text too small**: Edit `main.py`, increase font sizes:
```python
cv2.FONT_HERSHEY_SIMPLEX, 1.0  # Increase from 0.7
```

**Colors hard to see**: Edit color values in `config.py`

---

## Platform-Specific Issues

### Windows

**"Access Denied" on camera**:
- Settings → Privacy → Camera → Allow apps to access camera

**PyAutoGUI not working**:
- Run as administrator
- Check Windows Defender settings

### macOS

**Camera permission denied**:
- System Preferences → Security & Privacy → Camera
- Add Terminal/IDE to allowed apps

**Screen recording permission**:
- System Preferences → Security & Privacy → Screen Recording
- Required for PyAutoGUI

### Linux

**Camera permission denied**:
```bash
sudo usermod -a -G video $USER
# Log out and back in
```

**PyAutoGUI X11 error**:
```bash
sudo apt-get install python3-tk python3-dev
```

---

## Integration Issues

### Modules can't find each other

**Solution**: Make sure all .py files are in same directory
```bash
ls *.py
# Should show: main.py, camera_handler.py, hand_detector.py, etc.
```

### "Circular import" error

**Solution**: Don't run modules that import each other
- Run only `main.py` for full application
- Individual module tests are for development only

---

## Error Message Reference

### "FailSafe triggered"
**Meaning**: Mouse moved to screen corner  
**Solution**: This is intentional - emergency stop  
**To disable**: Set `pyautogui.FAILSAFE = False` in mouse_controller.py (not recommended)

### "Failed to read frame"
**Meaning**: Camera disconnected or error  
**Solution**: Check camera connection, restart application

### "No hand landmarks found"
**Meaning**: Hand not detected in frame  
**Solution**: Position hand clearly in view

---

## Getting More Help

1. **Check console output**: Look for error messages
2. **Run test script**: `python test_system.py`
3. **Test individual modules**: Run each .py file separately
4. **Check documentation**: Read README.md
5. **Review project plan**: See hand_tracking_project_plan.md

---

## Debugging Checklist

When something doesn't work:

- [ ] Run `python test_system.py`
- [ ] Check camera is working (run `python camera_handler.py`)
- [ ] Verify good lighting
- [ ] Check hand position (not too close/far)
- [ ] Review console error messages
- [ ] Try default config settings
- [ ] Restart application
- [ ] Reboot computer

---

## Performance Optimization Guide

For best performance, apply these settings in order:

1. **Lower resolution first**:
   ```python
   CAMERA_WIDTH = 480
   CAMERA_HEIGHT = 360
   ```

2. **Then reduce smoothing**:
   ```python
   GESTURE_SMOOTHING_FRAMES = 3
   ```

3. **Increase minimum confidence**:
   ```python
   MIN_DETECTION_CONFIDENCE = 0.8
   ```

4. **Disable UI elements if needed**:
   ```python
   SHOW_CAMERA_FEED = False  # Run headless
   ```

---

## Contact & Support

If issues persist:
1. Document the exact error message
2. Note your Python version: `python --version`
3. Note your OS and version
4. List installed package versions: `pip list`
5. Describe steps to reproduce
6. Check if issue occurs with default config

---

**Most Common Fix**: Restart everything!
1. Close application
2. Close camera
3. Restart application
4. If that doesn't work, reboot computer

Good luck! 🍀
