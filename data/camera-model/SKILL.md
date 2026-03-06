---
name: pywayne-cv-camera-model
description: Camera model wrapper for camera_models C++ library via pybind11. Use when working with pywayne.cv.camera_model module to load camera models from YAML configuration files, access camera properties (model type, image size, parameters), perform projection operations (lift_projective, space_to_plane), and export camera parameters as dictionaries.
---

# Pywayne Camera Model

This module wraps the `camera_models` C++ library via pybind11, providing a Python interface for camera operations.

## Quick Start

```python
from pywayne.cv.camera_model import CameraModel
from pywayne.cv.tools import write_cv_yaml
import numpy as np

# Create camera model
camera = CameraModel()

# Load from YAML file
camera.load_from_yaml('camera_config.yaml')

# Access properties
print(f"Model: {camera.model_type}")
print(f"Size: {camera.image_width}x{camera.image_height}")
```

## Loading from YAML

```python
from pathlib import Path

# Sample YAML configuration
yaml_data = {
    "model_type": "PINHOLE",
    "camera_name": "my_camera",
    "image_width": 1280,
    "image_height": 720,
    "distortion_parameters": {"k1": 0.0, "k2": 0.0},
    "projection_parameters": {"fx": 600.0, "fy": 600.0, "cx": 640.0, "cy": 360.0}
}

# Write YAML file
write_cv_yaml('camera_config.yaml', yaml_data)

# Load model
camera.load_from_yaml('camera_config.yaml')
```

## Supported Camera Models

| Model Type | Description |
|------------|-------------|
| `PINHOLE` | Standard pinhole camera with radial distortion |
| `PINHOLE_FULL` | Full pinhole model with all distortion parameters |
| `CATA` | Catadioptric camera model |
| `EQUIDISTANT` | Equidistant camera model |
| `OCAM` | Unified camera model |

## Projection Operations

### lift_projective()

Lifts a 2D image point to a 3D projective ray:

```python
# Input can be tuple, list, or numpy array
ray_3d = camera.lift_projective([u, v])  # Returns np.ndarray (x, y, z)
```

### space_to_plane()

Projects a 3D point onto the 2D image plane:

```python
# Input can be tuple, list, or numpy array
uv = camera.space_to_plane([x, y, z])  # Returns np.ndarray (u, v)
```

## Properties

| Property | Description |
|---------|-------------|
| `model_type` | Camera model type (enum) |
| `camera_name` | Name of the loaded camera |
| `image_width` | Image width in pixels |
| `image_height` | Image height in pixels |

## Parameters Dictionary

Export all camera parameters as a dictionary:

```python
params = camera.get_parameters_as_dict()
print(params)
```

Includes model-specific parameters:
- **Pinhole**: `k1`, `k2`, `p1`, `p2`, `fx`, `fy`, `cx`, `cy`
- **Pinhole Full**: `k1-k6`, `p1-p2`, `fx`, `fy`, `cx`, `cy`
- **CATA**: `xi`, `k1-k2`, `p1-p2`, `gamma1-2`, `u0`, `v0`
- **Equidistant**: `k2-k5`, `mu`, `mv`, `u0`, `v0`
- **OCAM**: `C`, `D`, `E`, `center_x`, `center_y`, `poly`, `inv_poly`

## Requirements

- `camera_models` - C++ library (auto-downloaded via gettool if missing)
- `numpy` - Array operations
- `pywayne.cv.tools.write_cv_yaml` - For writing YAML files

## Notes

- Library is automatically checked and downloaded via `gettool` if not found
- Supports both tuple/list and numpy array inputs for projection methods
- Output from projection methods is always `np.ndarray` with `dtype=np.float64`
