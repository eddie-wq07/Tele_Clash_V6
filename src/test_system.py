"""
Quick Test Script
Verifies that all dependencies are installed correctly
"""

import sys


def test_imports():
    """Test if all required libraries can be imported"""
    print("Testing imports...")
    print("-" * 50)
    
    errors = []
    
    # Test OpenCV
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        errors.append("opencv-python")
    
    # Test MediaPipe
    try:
        import mediapipe as mp
        print(f"✓ MediaPipe version: {mp.__version__}")
    except ImportError as e:
        print(f"✗ MediaPipe import failed: {e}")
        errors.append("mediapipe")
    
    # Test PyAutoGUI
    try:
        import pyautogui
        print(f"✓ PyAutoGUI version: {pyautogui.__version__}")
    except ImportError as e:
        print(f"✗ PyAutoGUI import failed: {e}")
        errors.append("pyautogui")
    
    # Test NumPy
    try:
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        errors.append("numpy")
    
    print("-" * 50)
    
    if errors:
        print(f"\n❌ Missing dependencies: {', '.join(errors)}")
        print("\nInstall with: pip install " + " ".join(errors))
        return False
    else:
        print("\n✅ All dependencies installed successfully!")
        return True


def test_camera():
    """Test if camera is accessible"""
    print("\nTesting camera access...")
    print("-" * 50)
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Camera could not be opened")
            print("  - Check camera permissions")
            print("  - Try a different camera index")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            h, w, c = frame.shape
            print(f"✓ Camera working! Resolution: {w}x{h}")
            return True
        else:
            print("✗ Camera opened but couldn't read frame")
            return False
    
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False


def test_screen():
    """Test screen size detection"""
    print("\nTesting screen detection...")
    print("-" * 50)
    
    try:
        import pyautogui
        width, height = pyautogui.size()
        print(f"✓ Screen size: {width}x{height}")
        return True
    except Exception as e:
        print(f"✗ Screen detection failed: {e}")
        return False


def test_modules():
    """Test if project modules can be imported"""
    print("\nTesting project modules...")
    print("-" * 50)
    
    modules = [
        'camera_handler',
        'hand_detector',
        'gesture_recognizer',
        'mouse_controller',
        'config'
    ]
    
    errors = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}.py")
        except ImportError as e:
            print(f"✗ {module}.py - {e}")
            errors.append(module)
    
    print("-" * 50)
    
    if errors:
        print(f"\n❌ Failed to import: {', '.join(errors)}")
        print("Make sure all .py files are in the same directory")
        return False
    else:
        print("\n✅ All project modules imported successfully!")
        return True


def main():
    """Run all tests"""
    print("="*50)
    print("HAND TRACKING MOUSE CONTROL - SYSTEM TEST")
    print("="*50)
    print()
    
    results = []
    
    # Test imports
    results.append(("Dependencies", test_imports()))
    
    # Test camera
    results.append(("Camera", test_camera()))
    
    # Test screen
    results.append(("Screen", test_screen()))
    
    # Test modules
    results.append(("Project Modules", test_modules()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to run the application.")
        print("\nRun the application with: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check camera permissions")
        print("3. Ensure all .py files are in the same directory")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
