---
name: pywayne-cv-geometric-hull-calculator
description: Geometric hull calculator for 2D point sets supporting convex hull, concave hull (concave-hull, alphashape), and minimum bounding rectangle. Use when working with pywayne.cv.geometric_hull_calculator module to compute geometric hulls, visualize results with OpenCV or matplotlib, and generate random test point sets.
---

# Pywayne Geometric Hull Calculator

This module computes geometric hulls (convex and concave) for 2D point sets.

## Quick Start

```python
from pywayne.cv.geometric_hull_calculator import GeometricHullCalculator
import numpy as np

# Create calculator with random points
points = GeometricHullCalculator.generate_random_points(num_points=50)
calculator = GeometricHullCalculator(points, algorithm='concave-hull')

# Get results
print(f"MBR: {calculator.get_mbr()}")
print(f"Convex Hull: {calculator.get_convex_hull()}")
print(f"Concave Hull: {calculator.get_concave_hull()}")

# Visualize with matplotlib
calculator.visualize_matplotlib()
```

## Initialization

```python
# algorithm options: 'concave-hull' or 'alphashape'
# use_filtered_pts: Enable point filtering based on radius
calculator = GeometricHullCalculator(
    points=your_points,
    algorithm='alphashape',
    use_filtered_pts=True
)
```

## Supported Algorithms

| Algorithm | Description |
|-----------|-------------|
| `concave-hull` | Concave hull using concave_hull library |
| `alphashape` | Concave hull using alphashape library |

## Hull Types

| Type | Method | Description |
|------|---------|-------------|
| Convex Hull | `get_convex_hull()` | Outer hull containing all points |
| Concave Hull | `get_concave_hull()` | Inner concave boundary |

## Properties

| Property | Description |
|---------|-------------|
| `points` | Input 2D points (N×2 numpy array) |
| `algorithm` | Algorithm used for concave hull |
| `use_filtered_pts` | Whether filtered points were used |
| `box` | Minimum Bounding Rectangle corners |
| `center` | Center point of input points |
| `filter_radius` | Radius used for point filtering |
| `concave_hull_result` | Concave hull points or polygons |

## Visualization

### OpenCV Visualization

```python
calculator.visualize_opencv()
```

Displays: All input points, MBR, center, filter circle (if enabled), concave hull (green), convex hull (red).

### Matplotlib Visualization

```python
calculator.visualize_matplotlib()
```

Displays: All input points (red), MBR (blue), center, filter radius circle (if enabled), concave hull (orange), convex hull (purple).

## Requirements

- `numpy` - Array operations
- `cv2` (OpenCV) - For OpenCV visualization and MBR computation
- `matplotlib` - For matplotlib visualization
- `scipy` - For convex hull computation
- `concave_hull` - Concave hull algorithm
- `alphashape` - Alphashape algorithm
- `shapely` - Polygon operations for area calculation

## Notes

- Point filtering uses radius = 30% of shorter MBR edge length
- MBR computed using OpenCV's minAreaRect
- Convex hull uses scipy's ConvexHull
- Supports both single Polygon and MultiPolygon from alphashape results
