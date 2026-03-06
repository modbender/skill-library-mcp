---
name: pywayne-vio-se3
description: SE(3) rigid body transformation library for 3D rotation and translation operations. Use when working with robot poses, camera transformations, SLAM systems, or any 3D rigid body motion tasks. Supports SE(3) matrix operations, Lie group/algebra mappings (log/Log, exp/Exp), representation conversions (quaternion, axis-angle, Euler angles), and batch processing of trajectories.
---

# SE3 Rigid Body Transformations

## Quick Start

```python
import numpy as np
from pywayne.vio.SE3 import *

# Create SE(3) transformation from rotation and translation
R = np.eye(3)
t = np.array([1, 2, 3])
T = SE3_from_Rt(R, t)

# Lie algebra operations
xi = np.array([0.1, 0.2, 0.3, 0.05, 0.1, 0.15])  # [rho, theta]
T_from_xi = SE3_Exp(xi)  # se(3) vector -> SE(3)
xi_recovered = SE3_Log(T_from_xi)  # SE(3) -> se(3) vector
```

## Core Operations

### Basic Matrix Operations

**Create/Verify SE(3) matrices:**
- `check_SE3(T)` - Validate 4x4 matrix is valid SE(3)
- `SE3_from_Rt(R, t)` - Construct from rotation matrix and translation
- `SE3_to_Rt(T)` - Extract rotation matrix and translation vector

**Combine/invert transformations:**
- `SE3_mul(T1, T2)` - Matrix multiplication (compose transforms)
- `SE3_inv(T)` - Matrix inverse
- `SE3_diff(T1, T2, from_1_to_2=True)` - Compute relative transform

### Lie Group/Lie Algebra Mappings

**Vector form (preferred):**
- `SE3_Exp(xi)` - se(3) 6D vector -> SE(3) matrix, xi = [rho, theta]
- `SE3_Log(T)` - SE(3) matrix -> se(3) 6D vector

**Matrix form (theoretical):**
- `SE3_exp(xi_hat)` - se(3) 4x4 matrix -> SE(3) matrix
- `SE3_log(T)` - SE(3) matrix -> se(3) 4x4 matrix
- `SE3_skew(xi)` - 6D vector -> 4x4 Lie algebra matrix
- `SE3_unskew(xi_hat)` - 4x4 matrix -> 6D vector

**Naming convention:** Uppercase = vector, lowercase = matrix

### Representation Conversions

**Quaternion + translation:**
- `SE3_from_quat_trans(q, t)` - q is wxyz quaternion
- `SE3_to_quat_trans(T)` - Returns (quaternion, translation)

**Axis-angle + translation:**
- `SE3_from_axis_angle_trans(axis, angle, t)`
- `SE3_to_axis_angle_trans(T)` - Returns (axis, angle, translation)

**Euler angles + translation:**
- `SE3_from_euler_trans(euler_angles, t, axes='zyx', intrinsic=True)`
- `SE3_to_euler_trans(T, axes='zyx', intrinsic=True)`

### Statistical Operations

- `SE3_mean(T_batch)` - Compute mean of multiple SE(3) matrices (Nx4x4 -> 4x4)

## Input/Output Formats

**Single transformation:**
- Input: 4x4 or 3x3/3 arrays
- Output: 4x4 or scalar vectors

**Batch operations:**
- Input: Nx4x4 or Nx3x3/Nx3 arrays
- Output: Same batched format
- All functions support both single and batch inputs

**6D vector format:** `[rho_1, rho_2, rho_3, theta_1, theta_2, theta_3]`
- First 3: translation (linear velocity)
- Last 3: rotation (angular velocity)

## Common Patterns

### Trajectory Processing

```python
# Batch process robot trajectory
poses = np.array([...])  # Nx4x4
log_poses = SE3_Log(poses)  # Nx6 Lie algebra space
mean_pose = SE3_Exp(np.mean(log_poses, axis=0))  # Intrinsic mean
```

### Relative Motion

```python
# Relative transform between two poses
T_rel = SE3_diff(T_world_keyframe1, T_world_keyframe2)
# T_rel transforms points from frame2 to frame1
```

### Camera Pose Estimation

```python
# Camera to world transformation
R_cam = np.column_stack([right, up, forward])  # Camera axes
t_cam = camera_position
T_cam2world = SE3_from_Rt(R_cam, t_cam)
T_world2cam = SE3_inv(T_cam2world)
```

## Notes

- All angles in radians
- Right-multiply convention: P' = T @ P
- Numerically stable for large angles and displacements
- Batch operations use vectorized NumPy for efficiency
- Performance reference (1000 transforms): Exp ~2.5ms, Log ~0.8ms
