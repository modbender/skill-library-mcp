---
name: unitree-robot
description: "Control mobile robots (quadruped, bipedal, wheeled, aerial) via IM platforms. Supports Unitree robots and Insight9 AI stereo camera."
metadata: {
  "openclaw": {
    "emoji": "🤖",
    "requires": {
      "python": ">=3.8",
      "pip": ["numpy"]
    }
  }
}
---

# Unitree Robot Controller Skill

Control various mobile robots through instant messaging platforms.

## Supported Robots

| Code | Model | Type |
|------|-------|------|
| `unitree_go1` | Unitree GO1 | Quadruped |
| `unitree_go2` | Unitree GO2 | Quadruped |
| `unitree_g1` | Unitree G1 | Bipedal/Humanoid |
| `unitree_h1` | Unitree H1 | Bipedal/Humanoid |

## Coming Soon

| Code | Type |
|------|------|
| `wheeled_*` | Wheeled robots |
| `drone_*` | Aerial robots |
| `surface_*` | Surface vehicles |

## Supported Sensors

| Code | Sensor |
|------|--------|
| `insight9` | Looper Robotics AI Stereo Camera (RGB-D) |

## Navigation

- **TinyNav** integration for path planning and obstacle avoidance (coming soon)

## Usage

```python
from unitree_robot_skill import initialize, execute

initialize(robot="unitree_go2", im="wecom")
execute("forward 1m")
execute("turn left 45")
```
