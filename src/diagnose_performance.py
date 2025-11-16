"""
Performance Diagnostic Script
Identifies exactly where the bottleneck is
"""

import cv2
import mediapipe as mp
import time
import numpy as np

def test_camera_only():
    """Test raw camera FPS"""
    print("\n" + "="*50)
    print("TEST 1: Camera Only (no processing)")
    print("="*50)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    start = time.time()
    frame_count = 0
    
    while time.time() - start < 3:
        ret, frame = cap.read()
        if ret:
            frame_count += 1
    
    fps = frame_count / 3
    print(f"Camera FPS: {fps:.1f}")
    cap.release()
    return fps


def test_camera_with_display():
    """Test camera + display FPS"""
    print("\n" + "="*50)
    print("TEST 2: Camera + Display (no ML)")
    print("="*50)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    start = time.time()
    frame_count = 0
    
    while time.time() - start < 3:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            cv2.imshow("Test", frame)
            cv2.waitKey(1)
            frame_count += 1
    
    fps = frame_count / 3
    print(f"Camera + Display FPS: {fps:.1f}")
    cap.release()
    cv2.destroyAllWindows()
    return fps


def test_mediapipe_lite():
    """Test MediaPipe with Lite model"""
    print("\n" + "="*50)
    print("TEST 3: MediaPipe Lite Model (model_complexity=0)")
    print("="*50)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,  # Lite
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    start = time.time()
    frame_count = 0
    detection_times = []
    
    while time.time() - start < 5:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            t1 = time.time()
            results = hands.process(rgb)
            t2 = time.time()
            detection_times.append(t2 - t1)
            
            cv2.imshow("Test", frame)
            cv2.waitKey(1)
            frame_count += 1
    
    fps = frame_count / 5
    avg_detection = np.mean(detection_times) * 1000
    print(f"MediaPipe Lite FPS: {fps:.1f}")
    print(f"Avg detection time: {avg_detection:.1f}ms")
    
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    return fps, avg_detection


def test_mediapipe_full():
    """Test MediaPipe with Full model"""
    print("\n" + "="*50)
    print("TEST 4: MediaPipe Full Model (model_complexity=1)")
    print("="*50)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,  # Full
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    start = time.time()
    frame_count = 0
    detection_times = []
    
    while time.time() - start < 5:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            t1 = time.time()
            results = hands.process(rgb)
            t2 = time.time()
            detection_times.append(t2 - t1)
            
            cv2.imshow("Test", frame)
            cv2.waitKey(1)
            frame_count += 1
    
    fps = frame_count / 5
    avg_detection = np.mean(detection_times) * 1000
    print(f"MediaPipe Full FPS: {fps:.1f}")
    print(f"Avg detection time: {avg_detection:.1f}ms")
    
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    return fps, avg_detection


def test_lower_resolution():
    """Test with lower resolution"""
    print("\n" + "="*50)
    print("TEST 5: Lower Resolution (320x240) + Lite Model")
    print("="*50)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    start = time.time()
    frame_count = 0
    detection_times = []
    
    while time.time() - start < 5:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            t1 = time.time()
            results = hands.process(rgb)
            t2 = time.time()
            detection_times.append(t2 - t1)
            
            cv2.imshow("Test", frame)
            cv2.waitKey(1)
            frame_count += 1
    
    fps = frame_count / 5
    avg_detection = np.mean(detection_times) * 1000
    print(f"Low Res + Lite FPS: {fps:.1f}")
    print(f"Avg detection time: {avg_detection:.1f}ms")
    
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    return fps, avg_detection


def test_frame_skipping():
    """Test with frame skipping"""
    print("\n" + "="*50)
    print("TEST 6: Frame Skipping (process every 3rd frame)")
    print("="*50)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    start = time.time()
    frame_count = 0
    skip_count = 3
    
    while time.time() - start < 5:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            
            # Only process every Nth frame
            if frame_count % skip_count == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)
            
            cv2.imshow("Test", frame)
            cv2.waitKey(1)
            frame_count += 1
    
    fps = frame_count / 5
    print(f"Frame Skipping (every 3rd) FPS: {fps:.1f}")
    
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    return fps


def main():
    print("="*50)
    print("PERFORMANCE DIAGNOSTIC")
    print("="*50)
    print("This will run 6 tests to identify the bottleneck")
    print("Each test runs for 3-5 seconds")
    input("Press Enter to start...")
    
    results = {}
    
    # Test 1
    results['camera_only'] = test_camera_only()
    time.sleep(1)
    
    # Test 2
    results['camera_display'] = test_camera_with_display()
    time.sleep(1)
    
    # Test 3
    fps, ms = test_mediapipe_lite()
    results['mp_lite_fps'] = fps
    results['mp_lite_ms'] = ms
    time.sleep(1)
    
    # Test 4
    fps, ms = test_mediapipe_full()
    results['mp_full_fps'] = fps
    results['mp_full_ms'] = ms
    time.sleep(1)
    
    # Test 5
    fps, ms = test_lower_resolution()
    results['low_res_fps'] = fps
    results['low_res_ms'] = ms
    time.sleep(1)
    
    # Test 6
    results['frame_skip'] = test_frame_skipping()
    
    # Summary
    print("\n" + "="*50)
    print("DIAGNOSTIC SUMMARY")
    print("="*50)
    print(f"Camera Only:           {results['camera_only']:.1f} FPS")
    print(f"Camera + Display:      {results['camera_display']:.1f} FPS")
    print(f"MediaPipe Lite:        {results['mp_lite_fps']:.1f} FPS ({results['mp_lite_ms']:.1f}ms/detection)")
    print(f"MediaPipe Full:        {results['mp_full_fps']:.1f} FPS ({results['mp_full_ms']:.1f}ms/detection)")
    print(f"Low Res (320x240):     {results['low_res_fps']:.1f} FPS ({results['low_res_ms']:.1f}ms/detection)")
    print(f"Frame Skip (3rd):      {results['frame_skip']:.1f} FPS")
    
    print("\n" + "="*50)
    print("RECOMMENDATIONS")
    print("="*50)
    
    if results['mp_lite_ms'] > 50:
        print("⚠️  MediaPipe is VERY slow on your system")
        print("   This is likely due to M4 Mac ARM architecture")
        print("\nTry these solutions:")
        print("1. Use frame skipping (PROCESS_EVERY_N_FRAMES = 3 or 4)")
        print("2. Lower resolution to 320x240")
        print("3. Consider using OpenCV-only detection (no ML)")
        
        if results['low_res_fps'] > results['mp_lite_fps'] * 1.5:
            print("\n✓ BEST OPTION: Use lower resolution (320x240)")
        if results['frame_skip'] > 20:
            print("✓ GOOD OPTION: Use aggressive frame skipping")
    else:
        print("MediaPipe performance is reasonable")
        print("Bottleneck may be elsewhere")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    main()