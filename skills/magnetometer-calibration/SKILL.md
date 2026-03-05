---
name: pywayne-calibration-magnetometer-calibration
description: Sensor calibration toolkit with magnetometer calibration using close-form method. Use when calibrating IMU sensors (accelerometer, gyroscope, magnetometer) to compute soft-iron matrix and hard-iron offset for magnetometer correction. Requires sensor fusion with VQF for orientation estimation.
---

# Pywayne Calibration

`pywayne.calibration.MagnetometerCalibrator` provides magnetometer calibration using sensor data (accelerometer, gyroscope, magnetometer).

## Quick Start

```python
from pywayne.calibration import MagnetometerCalibrator
import numpy as np

# Sensor data: ts (N,), acc (N,3), gyro (N,3), mag (N,3)
calibrator = MagnetometerCalibrator(method='close_form')
Sm, h = calibrator.process(ts, acc, gyro, mag)

# Sm: Soft-iron matrix (3x3)
# h: Hard-iron offset vector (3,)
```

## Input Data Format

Sensor data must be numpy arrays with matching sample counts:

```python
ts   # (N,)     - Timestamps (seconds)
acc  # (N, 3)   - Accelerometer [ax, ay, az]
gyro # (N, 3)   - Gyroscope [gx, gy, gz]
mag  # (N, 3)   - Magnetometer [mx, my, mz]
```

**Data requirements:**
- Sensor data should cover various orientations for effective calibration
- Minimum data points required (exact number depends on calibration stability)
- Arrays must be C-contiguous (auto-converted internally)

## Calibration Parameters

`process()` returns:

| Parameter | Shape | Description |
|-----------|--------|-------------|
| `Sm` | (3, 3) | Soft-iron matrix |
| `h` | (3,) | Hard-iron offset vector |

## Usage in Application

Apply calibration to raw magnetometer readings:

```python
# Calibrated reading
m_calibrated = Sm @ (m_raw - h)
```

## Temporal Calibration

Temporal calibration module exists but is reserved for future expansion. Currently no functionality is implemented.

## Important Notes

- **Dependencies**: Requires `vqf` (VQF quaternion filter) and `qmt` (quaternion math) modules
- **Method**: Currently only supports `close_form` method
- **Orientation**: Uses VQF for sensor fusion and orientation estimation during calibration
- **Output**: Prints calibration parameters during processing
