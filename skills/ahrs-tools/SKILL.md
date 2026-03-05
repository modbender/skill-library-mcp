---
name: pywayne-ahrs-tools
description: AHRS quaternion decomposition and roll/pitch compensation utilities. Use when working with pywayne.ahrs.tools module for quaternion to Euler angle decomposition, or compensating orientation to zero pitch and roll using roll-pitch compensation method.
---

# Pywayne AHRS Tools

This module provides quaternion-based AHRS (Attitude and Heading Reference System) utilities.

## Quick Start

```python
from pywayne.ahrs.tools import quaternion_decompose, quaternion_roll_pitch_compensate
import numpy as np

# Quaternion decomposition
q = np.array([0.70710678, 0, 0, 0.707962])  # w, x, y, z
angle_all, angle_heading, angle_inclination = quaternion_decompose(q)

# Roll/pitch compensation
q_comp = quaternion_roll_pitch_compensate(q)
```

## Quaternion Decomposition

```python
from pywayne.ahrs.tools import quaternion_decompose
import numpy as np

# Input quaternion (w, x, y, z)
q = np.array([w, x, y, z])

# Decompose into angles
angle_all, angle_heading, angle_inclination = quaternion_decompose(q)

# angle_all: Rotation angles around all axes (vertical + horizontal)
# angle_heading: Angle around vertical axis (inclination)
# angle_inclination: Angle around horizontal axis (bank)
```

## Roll/Pitch Compensation

```python
from pywayne.ahrs.tools import quaternion_roll_pitch_compensate
import numpy as np

# Input quaternion (w, x, y, z)
q = np.array([0.989893, -0.099295, 0.024504, -0.098242])

# Compensate pitch and roll to zero
q_comp = quaternion_roll_pitch_compensate(q)
```

## Requirements

- `numpy` - Array operations
- `qmt` - OpenCV's quaternion module for conversions

## Notes

- Decomposition returns both angles (in radians) and heading/inclination
- `angle_all` is computed using 2*arccos/abs(quaternion_z)
- `angle_heading` uses `arctan2(np.abs(quaternion_xy))`
- `angle_inclination` uses `2*arcsin(np.abs(quaternion_xy))`
- Roll/pitch compensation sets pitch and roll of q_comp to zero by using inverse rotation
