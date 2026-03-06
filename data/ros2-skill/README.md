# ROS 2 Skill

![Static Badge](https://img.shields.io/badge/ROS%202-Supported-green)
![Static Badge](https://img.shields.io/badge/License-Apache%202.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![ClawHub](https://img.shields.io/badge/ClawHub-ros2--skill-orange)](https://clawhub.ai/adityakamath/ros2-skill)

[Agent Skill](https://agentskills.io) for ROS 2 robot control via rclpy.

```text
Agent (LLM) → ros2_cli.py → rclpy → ROS 2
```

## Overview

An AI agent skill that lets agents control ROS 2 robots through natural language. The agent reads `SKILL.md`, understands available commands, and executes `ros2_cli.py` to interact with ROS 2 systems directly via rclpy.

## Quick Start (CLI)

Use `ros2_cli.py` directly from the command line.

```bash
# Source ROS 2 environment
source /opt/ros/${ROS_DISTRO}/setup.bash

# Install dependencies
pip install rclpy rosidl-runtime-py

# Run commands
python3 scripts/ros2_cli.py version
python3 scripts/ros2_cli.py topics list
python3 scripts/ros2_cli.py nodes list

# Move robot forward for 3 seconds
python3 scripts/ros2_cli.py topics publish /cmd_vel \
  '{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}' --duration 3

# Read sensor data
python3 scripts/ros2_cli.py topics subscribe /scan --duration 3
```

## Quick Start (AI Agent)

**ros2-skill** works with any AI agent that supports [Agent Skills](https://agentskills.io). For easy setup, we recommend [OpenClaw](https://github.com/openclaw/openclaw) — install **ros2-skill** from [ClawHub](https://clawhub.ai/adityakamath/ros2-skill) and talk to your robot:

- "What topics are available?"
- "Move the robot forward 1 meter"

See the [OpenClaw tutorial](examples/openclaw.md) for full setup and usage.

## Supported Commands

| Category | Commands |
| -------- | -------- |
| Connection | `version` |
| Topics | `list`, `type`, `details`, `message`, `subscribe`, `publish`, `publish-sequence` |
| Services | `list`, `type`, `details`, `call` |
| Nodes | `list`, `details` |
| Parameters | `list`, `get`, `set` |
| Actions | `list`, `details`, `send` |

All commands output JSON. See `SKILL.md` for quick reference and `references/COMMANDS.md` for full details with output examples.

## How It Works

1. The agent platform loads `SKILL.md` into the agent's system prompt
2. `{baseDir}` in commands is replaced with the actual skill installation path
3. User asks something like "move the robot forward"
4. Agent executes: `python3 {baseDir}/scripts/ros2_cli.py topics publish /cmd_vel ...`
5. `ros2_cli.py` uses rclpy to communicate with ROS 2 and returns JSON
6. Agent parses the JSON and responds in natural language

## File Structure

```
ros2-skill/
├── SKILL.md              # Skill document (loaded into agent's system prompt)
├── scripts/
│   └── ros2_cli.py       # Standalone CLI tool (all ROS 2 operations)
├── references/
│   └── COMMANDS.md      # Full command reference with output examples
├── examples/
│   ├── turtlesim.md     # Turtlesim tutorial
│   ├── sensor-monitor.md # Sensor monitoring workflows
│   └── openclaw.md      # OpenClaw integration tutorial
└── tests/
    └── test_ros_cli.py  # Unit tests (tests ros2_cli.py)
```

## Requirements

- Python 3.10+
- ROS 2 environment sourced
- `rclpy` and `rosidl-runtime-py` packages

## Testing

```bash
# Source ROS 2 environment
source /opt/ros/${ROS_DISTRO}/setup.bash

# Run tests
python3 -m pytest tests/ -v
```

Note: Some tests require a ROS 2 environment to run fully.

---

## About

This is a fork of the original [ros-skill](https://github.com/lpigeon/ros-skill) repository. The original supports both ROS 1 and ROS 2 using rosbridge WebSocket for communication, making it suitable for controlling remote robots over a network.

This version (`ros2-skill`) is designed to run directly on a ROS 2 robot and uses `rclpy` for direct local communication with ROS 2, without requiring rosbridge.
