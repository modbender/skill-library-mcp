---
name: pywayne-vio-tools
description: VIO (Visual Inertial Odometry) data processing utilities for SE(3) pose conversion and 3D visualization. Use when working with SE(3) matrices and need pose representation conversion (tx,ty,tz,qw,qx,qy,qz), 3D visualization of pose trajectories with orientation arrows, or Visual Inertial Odometry data transformation and analysis
---

# Pywayne VIO Tools

## Overview

Provides utilities for VIO data processing: convert between SE(3) transformation matrices and pose representations, and visualize pose trajectories in 3D with orientation indicators.

## Quick Start

```python
from pywayne.vio.tools import SE3_to_pose, pose_to_SE3, visualize_pose
import numpy as np

# Convert SE(3) to pose
SE3 = np.eye(4)  # Single 4x4 SE(3) matrix
pose = SE3_to_pose(SE3)  # Returns [tx, ty, tz, qw, qx, qy, qz]

# Batch conversion
SE3_array = np.random.randn(10, 4, 4)  # 10 SE(3) matrices
poses = SE3_to_pose(SE3_array)

# Convert back to SE(3)
SE3_recon = pose_to_SE3(pose)

# Visualize poses
visualize_pose(poses)  # 3D plot with position markers and orientation arrows
```

## Core Functions

### SE3_to_pose

Convert SE(3) transformation matrices to pose representation.

**Input:** `SE3_mat` - Single 4x4 SE(3) matrix or array of N SE(3) matrices shape (N, 4, 4)

**Output:** `pose` - Array shape (7,) or (N, 7) containing [tx, ty, tz, qw, qx, qy, qz]

**Dependencies:** `qmt.quatFromRotMat()` for quaternion extraction

### pose_to_SE3

Convert pose representation back to SE(3) transformation matrices.

**Input:** `pose_mat` - Single pose shape (7,) or array of N poses shape (N, 7) with [tx, ty, tz, qw, qx, qy, qz]

**Output:** `SE3_mat` - Array of SE(3) matrices shape (4, 4) or (N, 4, 4)

**Dependencies:** `qmt.quatToRotMat()`, `ahrs.Quaternion`

### visualize_pose

3D visualization of SE(3) poses with position markers and orientation arrows.

**Parameters:**
- `poses`: Array of poses [tx, ty, tz, qw, qx, qy, qz]
- `arrow_length_ratio`: Scale factor for orientation arrows (default: 0.1)

**Visualization:**
- Black dots: Position (translation)
- Red arrow: X-axis orientation
- Green arrow: Y-axis orientation
- Blue arrow: Z-axis orientation

**Dependencies:** `matplotlib.pyplot`, `qmt.quatToRotMat()`

## Data Formats

### SE(3) Matrix
```
[[R00 R01 R02 tx]
 [R10 R11 R12 ty]
 [R20 R21 R22 tz]
 [  0   0   0  1]]
```

### Pose Representation
```
[tx, ty, tz, qw, qx, qy, qz]
```
Translation: tx, ty, tz (meters)
Quaternion: qw, qx, qy, qz (Hamilton convention)

## Dependencies

Required packages:
- `numpy` - Array operations
- `qmt` - Quaternion utilities
- `ahrs` - Quaternion class
- `matplotlib` - 3D visualization

Install with:
```bash
pip install numpy qmt ahrs matplotlib
```
