# Webcam and USB Camera Capture

## Listing Available Cameras

### macOS
```bash
ffmpeg -f avfoundation -list_devices true -i ""
# Output: [0] FaceTime HD Camera, [1] Capture Card, etc.
```

### Linux
```bash
v4l2-ctl --list-devices
ls /dev/video*
```

### Windows
```bash
ffmpeg -f dshow -list_devices true -i dummy
```

## Capturing Snapshots

### macOS
```bash
# Device index 0 (usually built-in webcam)
ffmpeg -f avfoundation -framerate 30 -i "0" -frames:v 1 snapshot.jpg
```

### Linux
```bash
ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 snapshot.jpg
```

### With OpenCV (Python)
```python
import cv2

cap = cv2.VideoCapture(0)  # Device index
ret, frame = cap.read()
cv2.imwrite('snapshot.jpg', frame)
cap.release()
```

## Recording Clips

```bash
# Record 10 seconds from webcam
ffmpeg -f avfoundation -framerate 30 -i "0" -t 10 -c:v libx264 clip.mp4
```

## Using Phone as Camera

### iPhone → Mac
1. Connect via USB or same WiFi
2. Use Continuity Camera (macOS Ventura+)
3. Appears as standard video device

### Android → Any
1. Install DroidCam or IP Webcam
2. Connect via USB (DroidCam) or get RTSP URL (IP Webcam)
3. `ffmpeg -i "http://phone-ip:8080/video" -frames:v 1 snap.jpg`

### IP Webcam (Android)
```bash
# After starting IP Webcam app
curl "http://192.168.1.50:8080/shot.jpg" -o snapshot.jpg
ffmpeg -i "http://192.168.1.50:8080/video" -t 5 clip.mp4
```

## Capture Cards

HDMI capture cards (Elgato, generic USB) appear as webcams:
```bash
# Find device
ffmpeg -f avfoundation -list_devices true -i ""
# Capture
ffmpeg -f avfoundation -i "2" -frames:v 1 capture.jpg
```

## Agent Integration Pattern

```python
import subprocess
import tempfile

def capture_webcam(device_index=0):
    """Capture snapshot from webcam"""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        output = f.name
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'avfoundation',  # or v4l2 on Linux
        '-framerate', '30',
        '-i', str(device_index),
        '-frames:v', '1',
        '-q:v', '2',
        output
    ]
    subprocess.run(cmd, capture_output=True)
    return output

def list_cameras():
    """List available cameras"""
    result = subprocess.run(
        ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', ''],
        capture_output=True, text=True
    )
    return result.stderr  # ffmpeg outputs to stderr
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Permission denied | macOS: System Preferences → Privacy → Camera |
| Device busy | Close other apps using camera |
| Black frames | Add `-framerate 30` or use device's native rate |
| Wrong camera | List devices first, use correct index |
| Low quality | Add `-q:v 2` or increase `-b:v` for video |
