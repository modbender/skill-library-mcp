---
name: pywayne-visualization-rerun-utils
description: Static 3D visualization utilities wrapping Rerun SDK for adding point clouds, trajectories, cameras, planes, and chessboards. Use when visualizing 3D data in Rerun, including SLAM trajectories, robot poses, camera calibration targets, and debug visualizations. All methods are static and do not require viewer instance management. For SE(3)/SO(3) matrix operations, use pywayne-vio-se3 or pywayne-vio-so3 skills.
---

# Pywayne Visualization Rerun Utils

`pywayne.visualization.rerun_utils.RerunUtils` provides static methods for adding 3D elements to a Rerun viewer.

## Quick Start

```python
import numpy as np
import rerun as rr
from pywayne.visualization.rerun_utils import RerunUtils

# Initialize Rerun (called once globally)
rr.init('my_app', spawn=True)

# Use static methods to add elements
RerunUtils.add_point_cloud(points, colors=[255, 0, 0])
RerunUtils.add_trajectory(trajectory)
RerunUtils.add_camera(pose, image='path/to/image.jpg')
```

## Point Cloud

```python
# Single color (default: red)
RerunUtils.add_point_cloud(points)

# Multi-color points
colors = np.random.randint(0, 255, (100, 3))
RerunUtils.add_point_cloud(points, colors=colors, label='colored')

# Data format: points (N, 3)
```

## Trajectory

```python
# Single-color trajectory (default: green)
RerunUtils.add_trajectory(trajectory)

# Multi-color trajectory
colors = np.array([[0, 255, 0], [255, 0, 0]], dtype=np.float32)
RerunUtils.add_trajectory(trajectory, colors=colors, label='path')

# Data format: traj_endpoints (N, 3)
```

## Camera

```python
# Camera only (no image)
RerunUtils.add_camera(pose, label='main_camera')

# Camera with image
RerunUtils.add_camera(pose, image='path/to/image.jpg', label='rgb_camera')

# Data format: camera_pose (4, 4) or (4, 7)
```

## Plane

```python
# Plane by center and normal
RerunUtils.add_plane_from_center_and_normal(center, normal, half_size=1.0)

# Plane from SE3 transformation matrix
RerunUtils.add_plane_from_Twp(Twp, half_size=1.0)
```

## Chessboard

```python
# Standard chessboard
RerunUtils.add_chessboard_from_Twp()

# Custom chessboard with colors
RerunUtils.add_chessboard_from_Twp(
    rows=9, cols=6, cell_size=0.025,
    Twp=pose_matrix,
    color1=np.array([255, 0, 0]),  # Red
    color2=np.array([0, 0, 255])   # Blue
    label='calib_board'
)
```

## Internal Helper

```python
# Get quaternion from v1 to v2 (used internally for plane rotation)
quat = RerunUtils._get_quaternion_from_v1_and_v2(v1, v2)
```

## Important Notes

- **Initialization**: Call `rr.init('name', spawn=True)` once before using methods
- **Static methods**: All methods are static class methods, no instance needed
- **Dependencies**: Requires Rerun SDK (auto-downloaded via `gettool`)
- **Data types**: All position inputs must be `float32`
- **Coordinates**: Rerun uses `ViewCoordinates.RDF` (robot-centric coordinate system)
- **SE3 poses**: Support (4, 4) or (4, 7) matrix formats
- **Color format**: RGB as numpy arrays with shape (3,)
