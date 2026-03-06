---
name: pywayne-vio-so3
description: SO(3) rotation matrix utilities including Lie group/ Lie algebra operations, rotation representation conversions, skew-symmetric matrix operations, and rotation averaging. Use when working with 3D rotations, robot kinematics, computer vision, SLAM, or any task requiring SO(3) matrix validation and manipulation, quaternion/ axis-angle/ Euler angle conversions, Lie algebra Log/Exp mapping, skew-symmetric matrix operations, or rotation matrix averaging
---

# Pywayne VIO SO3

## Overview

Complete SO(3) rotation matrix toolkit for 3D rotations with Lie group/ Lie algebra operations, rotation representation conversions, skew-symmetric matrix operations, and rotation averaging.

## Quick Start

```python
from pywayne.vio.SO3 import SO3_skew, SO3_Exp, SO3_Log, SO3_to_quat
import numpy as np

# Skew-symmetric matrix
vec = np.array([1, 2, 3])
skew = SO3_skew(vec)  # Returns 3x3 skew-symmetric matrix

# Log/Exp mapping
R = np.eye(3)
rotvec = SO3_Log(R)  # Rotation vector (Lie algebra)
R_recon = SO3_Exp(rotvec)  # Back to rotation matrix

# Quaternion conversion
quat = SO3_to_quat(R)  # Returns [w, x, y, z]
```

## Core Functions

### Basic Operations

#### check_SO3(R)
Check if matrix is a valid SO(3) rotation matrix.
- Validates shape (3, 3)
- Checks R.T @ R = I (orthogonality)

#### SO3_mul(R1, R2)
Multiply two rotation matrices: `R1 @ R2`.

#### SO3_diff(R1, R2, from_1_to_2=True)
Compute relative rotation between two matrices.
- `from_1_to_2=True`: Returns `R1.T @ R2`
- `from_1_to_2=False`: Returns `R2.T @ R1`

#### SO3_inv(R)
Compute inverse of rotation matrix (transpose).
- Supports single (3, 3) or batch (N, 3, 3) inputs

### Skew-Symmetric Matrices

#### SO3_skew(vec)
Convert 3D vector to skew-symmetric matrix.
```
vec = [x, y, z] -> [[ 0, -z,  y],
                    [ z,  0, -x],
                    [-y,  x,  0]]
```
- Supports single vector (3,) or batch (N, 3)

#### SO3_unskew(skew)
Extract vector from skew-symmetric matrix.
- Single matrix (3, 3) -> vector (3,)
- Batch (N, 3, 3) -> vectors (N, 3)

### Rotation Representation Conversions

#### Quaternion
- `SO3_from_quat(q)` - Quaternion [w, x, y, z] to rotation matrix
- `SO3_to_quat(R)` - Rotation matrix to quaternion [w, x, y, z]
- Uses Hamilton convention (wxyz)

#### Axis-Angle
- `SO3_from_axis_angle(axis, angle)` - Axis-angle to rotation matrix
- `SO3_to_axis_angle(R)` - Returns (axis, angle) tuple

#### Euler Angles
- `SO3_from_euler(euler_angles, axes='zyx', intrinsic=True)` - Euler to matrix
- `SO3_to_euler(R, axes='zyx', intrinsic=True)` - Matrix to Euler
- Supports all rotation sequences

### Lie Group/ Lie Algebra Mapping

#### SO3_Log(R)
SO(3) to so(3) log map, returns rotation vector (3D).
- Input: (3, 3) or (N, 3, 3)
- Output: (3,) or (N, 3)

#### SO3_log(R)
SO(3) to so(3) log map, returns skew-symmetric matrix (3x3).
- Equivalent to `SO3_skew(SO3_Log(R))`

#### SO3_Exp(rotvec)
so(3) to SO(3) exp map from rotation vector.
- Handles zero vectors gracefully
- Input: (3,) or (N, 3)
- Output: (3, 3) or (N, 3, 3)

#### SO3_exp(omega_hat)
so(3) to SO(3) exp map from skew-symmetric matrix.
- Equivalent to `SO3_Exp(SO3_unskew(omega_hat))`

### Averaging

#### SO3_mean(R)
Compute mean rotation matrix from multiple rotations.
- Uses scipy Rotation.mean()
- Input: (N, 3, 3)
- Output: (3, 3)

## Data Formats

### Single vs Batch
- Single matrix: shape (3, 3)
- Batch: shape (N, 3, 3)

Most functions handle both automatically.

### SO(3) Matrix Properties
```
R @ R.T = I  (orthogonal)
det(R) = 1   (special)
```

### Lie Algebra Vector
Rotation vector where direction is axis, magnitude is angle.

## Dependencies

Required packages:
- `numpy` - Array operations
- `qmt` - Quaternion utilities
- `scipy` - Rotation averaging

Install with:
```bash
pip install numpy qmt scipy
```

## Example Usage

```python
# Create rotation from axis-angle
axis = np.array([0, 0, 1])  # Z-axis
angle = np.pi / 4  # 45 degrees
R = SO3_from_axis_angle(axis, angle)

# Verify it's valid
print(check_SO3(R))  # True

# Get Lie algebra representation
rotvec = SO3_Log(R)
print(f"Rotation vector: {rotvec}")

# Convert back
R_recon = SO3_Exp(rotvec)
print(f"Reconstruction error: {np.linalg.norm(R - R_recon):.2e}")

# Batch averaging
R_batch = np.array([R, SO3_inv(R), SO3_mul(R, R)])
R_mean = SO3_mean(R_batch)
```
