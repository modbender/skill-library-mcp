---
name: pywayne-visualization-pangolin-utils
description: 3D visualization toolkit wrapping Pangolin viewer for real-time display of point clouds, trajectories, cameras, planes, chessboards, and images. Use when visualizing sensor data (IMU, SLAM, tracking), robot states, or any 3D data with camera poses and trajectories. Supports dual-image display, step mode for debugging, and main camera following.
---

# Pywayne Visualization Pangolin Utils

`pywayne.visualization.pangolin_utils.PangolinViewer` provides a Python interface to Pangolin 3D visualization library.

## Quick Start

```python
from pywayne.visualization.pangolin_utils import PangolinViewer, Colors
import numpy as np

# Create viewer
viewer = PangolinViewer(800, 600)
viewer.init()

# Run visualization loop
while viewer.should_not_quit():
    # ... add/update visual elements ...
    viewer.show(delay_time_in_s=0.03)

viewer.join()  # Wait for window to close
```

## Colors

Use `Colors` class for common colors:

```python
Colors.RED      # [1.0, 0.0, 0.0]
Colors.GREEN    # [0.0, 1.0, 0.0]
Colors.BLUE     # [0.0, 0.0, 1.0]
Colors.YELLOW   # [1.0, 1.0, 0.0]
Colors.CYAN     # [0.0, 1.0, 1.0]
Colors.MAGENTA  # [1.0, 0.0, 1.0]
Colors.WHITE    # [1.0, 1.0, 1.0]
Colors.BLACK    # [0.0, 0.0, 0.0]
Colors.ORANGE   # [1.0, 0.5, 0.0]
Colors.PURPLE   # [0.5, 0.5, 0.5]
Colors.GRAY     # [0.5, 0.5, 0.5]
Colors.BROWN    # [0.6, 0.3, 0.1]
Colors.PINK     # [1.0, 0.75, 0.8]
```

## Core Control

```python
viewer.run()          # Start main loop (blocking)
viewer.close()         # Close viewer
viewer.join()         # Wait for process to end
viewer.reset()         # Reset viewer state
viewer.init()          # Initialize view (set initial camera)
viewer.show(0.03)      # Render frame with delay (s)
viewer.should_not_quit()  # Check if viewer should continue
viewer.clear_all_visual_elements()  # Clear all elements
```

## Point Cloud

```python
# Clear all points
viewer.clear_all_points()

# Add single-color points (default: red)
viewer.add_points(points, point_size=4.0)

# Add points with custom colors
viewer.add_points_with_colors(points, colors, point_size=4.0)

# Add points with named color
viewer.add_points_with_color_name(points, color_name="red", point_size=4.0)

# Data format: points (N, 3), colors (N, 3)
```

## Trajectory

```python
# Clear all trajectories
viewer.clear_all_trajectories()

# Add trajectory with quaternions (positions + orientations)
viewer.add_trajectory_quat(
    positions,           # (N, 3)
    orientations,        # (N, 4) or (N, 7) depending on quat_format
    color=Colors.GREEN,
    quat_format="wxyz",   # "wxyz" or "xyzw"
    line_width=2.0,
    show_cameras=True,    # Show camera models along trajectory
    camera_size=0.05
)

# Add trajectory with SE3 poses
viewer.add_trajectory_se3(
    poses_se3,           # (N, 4) or (N, 7)
    color=Colors.GREEN,
    line_width=2.0,
    show_cameras=False
)
```

## Camera

```python
# Clear all cameras
viewer.clear_all_cameras()

# Set main camera (view follows this camera)
viewer.set_main_camera(camera_id)

# Add camera with quaternion
cam_id = viewer.add_camera_quat(
    position,           # (3,)
    orientation,         # (4,) or (7) depending on quat_format
    color=Colors.YELLOW,
    quat_format="wxyz",
    scale=0.1,
    line_width=1.0
)

# Add camera with SE3 pose
cam_id = viewer.add_camera_se3(
    pose_se3,            # (4,) or (7)
    color=Colors.YELLOW,
    scale=0.1,
    line_width=1.0
)
```

## Plane

```python
# Clear all planes
viewer.clear_all_planes()

# Add plane by vertices
viewer.add_plane(
    vertices,        # (>=3, 3)
    color=Colors.GRAY,
    alpha=0.5,       # Transparency 0-1
    label="plane"
)

# Add plane by normal + center
viewer.add_plane_normal_center(
    normal,          # (3,) - direction of plane normal
    center,          # (3,) - center point
    size,            # half-size (distance from center to edge)
    color=Colors.GRAY,
    alpha=0.5,
    label="plane"
)

# Add plane from SE3 transformation
viewer.add_plane_from_Twp(
    Twp,             # (4, 4) - world pose matrix
    size=1.0,
    color=Colors.GREEN,
    alpha=0.5,
    label="plane"
)
```

## Chessboard

Useful for camera calibration and spatial reference:

```python
# Add chessboard on XY plane
viewer.add_chessboard(rows=8, cols=8, cell_size=0.1)

# Add chessboard on custom plane with normal
viewer.add_chessboard(
    rows=9, cols=6, cell_size=0.025,
    origin=np.array([0, 0, 0]),
    normal=np.array([1, 0, 0]),  # YZ plane
    color1=Colors.RED,
    color2=Colors.YELLOW,
    alpha=0.8
)

# Add chessboard from SE3 transformation
viewer.add_chessboard_from_Twp(
    rows=9, cols=6, cell_size=0.025,
    Twp=pose_matrix,
    color1=Colors.BLACK,
    color2=Colors.WHITE,
    alpha=0.8,
    label="calib"
)
```

## Line

```python
viewer.clear_all_lines()

viewer.add_line(
    start_point,      # (3,)
    end_point,        # (3,)
    color=Colors.WHITE,
    line_width=1.0
)
```

## Image Display

```python
# Set image resolution
viewer.set_img_resolution(width, height)

# Add left image
viewer.add_image_1(img_array)           # Use numpy array
viewer.add_image_1(image_path="path.jpg")  # Use file path

# Add right image
viewer.add_image_2(img_array)
viewer.add_image_2(image_path="path.jpg")
```

## Step Mode (Debugging)

```python
viewer.is_step_mode_active()   # Check if step mode is active
viewer.wait_for_step()         # Wait for step trigger
```

## Important Notes

- **Dependencies**: Requires Pangolin library (auto-downloaded via `gettool`)
- **Data types**: All position/point inputs must be `float32`
- **Quaternion formats**: Support `wxyz` and `xyzw` formats
- **SE3 poses**: Support (4, 4) or (4, 7) matrix formats
- **Automatic cleaning**: `clear_all_visual_elements()` clears points, trajectories, cameras, planes, lines
- **Camera following**: Use `set_main_camera()` with camera ID from `add_camera_*()` return
