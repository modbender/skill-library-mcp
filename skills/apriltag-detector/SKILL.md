---
name: pywayne-cv-apriltag-detector
description: AprilTag corner detection for camera calibration and pose estimation. Use when working with pywayne.cv.apriltag_detector module to detect AprilTag fiducial markers in images, with automatic library installation via gettool, drawing detection results with corners and IDs, and support for both file paths and numpy arrays.
---

# Pywayne AprilTag Detector

This module detects AprilTag fiducial markers for camera calibration and pose estimation.

## Quick Start

```python
from pywayne.cv.apriltag_detector import ApriltagCornerDetector

# Create detector
detector = ApriltagCornerDetector()

# Detect from file path
detections = detector.detect('test.png', show_result=True)

# Detect from numpy array
import cv2
image = cv2.imread('test.png')
detections = detector.detect(image)
```

## Detection Methods

### detect()

Detect AprilTags in an image:

```python
detections = detector.detect(
    image,           # File path, Path object, or numpy array
    show_result=False  # Show visualization window
)
```

Returns list of detection results with:
- `id`: Tag ID
- `hamming_distance`: Detection confidence
- `center`: Tag center coordinates (x, y)
- `corners`: 4 corner coordinates

### detect_and_draw()

Detect AprilTags and draw results on original image:

```python
result_image = detector.detect_and_draw(image)
cv2.imshow('Detection Result', result_image)
cv2.waitKey(0)
```

Visualization includes:
- Green polygon outlines
- Red corner circles
- Red ID labels at tag centers

## Requirements

- `cv2` (OpenCV) - Image processing
- `numpy` - Array operations
- `gettool` - Downloads apriltag_detection library automatically

## Library Installation

The detector automatically checks for and installs the `apriltag_detection` library using `gettool` if not found.

## Detection Result Format

Each detection contains:

| Field | Description |
|--------|-------------|
| `id` | Tag identifier |
| `hamming_distance` | Hamming distance (lower = more confident) |
| `center` | Tag center as (x, y) tuple |
| `corners` | 4 corner coordinates as [(x1, y1), (x2, y2), (x3, y3), (x4, y4)] |

## Notes

- Supports both grayscale and BGR images
- Automatic grayscale conversion for detection
- Visualization sizes scale with image dimensions
- Uses AprilTag 36h11 tag family
