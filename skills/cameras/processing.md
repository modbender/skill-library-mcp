# Video and Image Processing

## Using Vision Models

The simplest approach: capture image, send to vision model.

```python
import base64
import anthropic

# Capture snapshot (see capture.md)
snapshot_path = capture_webcam()

# Send to vision model
with open(snapshot_path, 'rb') as f:
    image_data = base64.standard_b64encode(f.read()).decode()

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
            {"type": "text", "text": "Describe what you see in this security camera image. Focus on people, vehicles, and any unusual activity."}
        ]
    }]
)
```

## Local Detection with Frigate

Frigate runs YOLO models locally for:
- Person detection
- Vehicle detection
- Animal detection
- Custom objects

**Why use Frigate instead of cloud:**
- No API costs for continuous monitoring
- Works offline
- Privacy (video stays local)
- Real-time alerts via MQTT

## OpenCV Basics

For simple local processing without ML:

```python
import cv2

# Motion detection
def detect_motion(frame1, frame2, threshold=25):
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours) > 0, contours

# Face detection (Haar cascades)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return len(faces), faces
```

## Cloud Vision APIs

### Google Cloud Vision
```python
from google.cloud import vision

def analyze_image(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as f:
        content = f.read()
    
    image = vision.Image(content=content)
    
    # Object detection
    objects = client.object_localization(image=image).localized_object_annotations
    
    # Labels
    labels = client.label_detection(image=image).label_annotations
    
    # Text (OCR)
    text = client.text_detection(image=image).text_annotations
    
    return objects, labels, text
```

### AWS Rekognition
```python
import boto3

def detect_labels(image_path):
    client = boto3.client('rekognition')
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    response = client.detect_labels(
        Image={'Bytes': image_bytes},
        MaxLabels=10
    )
    return response['Labels']
```

## Processing Patterns

### Periodic Monitoring
```python
import time

def monitor_camera(camera_url, check_interval=60):
    last_frame = None
    
    while True:
        frame = capture_snapshot(camera_url)
        
        if last_frame is not None:
            motion, _ = detect_motion(last_frame, frame)
            if motion:
                # Something changed
                description = analyze_with_vision(frame)
                alert_user(description)
        
        last_frame = frame
        time.sleep(check_interval)
```

### Event-Driven (with Frigate)
```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    event = json.loads(msg.payload)
    
    if event['type'] == 'new' and event['label'] == 'person':
        # Get snapshot
        snapshot = get_frigate_snapshot(event['id'])
        
        # Describe with vision model
        description = describe_image(snapshot)
        
        # Notify
        notify(f"Person detected: {description}")

client = mqtt.Client()
client.on_message = on_message
client.connect("frigate-host", 1883)
client.subscribe("frigate/events")
client.loop_forever()
```

## When to Use What

| Need | Solution |
|------|----------|
| Quick description | Vision model (Claude, GPT-4V) |
| Continuous monitoring | Frigate (local YOLO) |
| Simple motion | OpenCV frame diff |
| Face detection only | OpenCV Haar or dlib |
| OCR (text in image) | Google Vision or Tesseract |
| Custom objects | Train YOLO, run in Frigate |

## Privacy Considerations

- **Local first**: Frigate, OpenCV, local models
- **Minimize cloud**: Only send snapshots when needed
- **Blur faces**: If recording public areas
- **Retention limits**: Auto-delete old footage
- **Access control**: Encrypt streams, auth required
