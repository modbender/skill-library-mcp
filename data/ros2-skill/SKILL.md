---
name: ros2-skill
description: "Controls ROS 2 robots directly via rclpy CLI. Use when the user asks about ROS 2 topics, services, nodes, parameters, actions, robot movement, sensor data, or any ROS 2 robot interaction."
license: Apache-2.0
compatibility: "Requires python3, rclpy, and ROS 2 environment sourced"
user-invocable: true
metadata: {"openclaw": {"emoji": "🤖", "requires": {"bins": ["python3", "ros2"], "pip": ["rclpy", "rosidl-runtime-py"]}, "category": "robotics", "tags": ["ros2", "robotics", "rclpy"]}, "author": ["adityakamath", "lpigeon"], "version": "3.0.0"}
---

# ROS 2 Skill

Controls and monitors ROS 2 robots directly via rclpy.

**Architecture:** Agent → `ros2_cli.py` → rclpy → ROS 2

All commands output JSON. Errors contain `{"error": "..."}`.

For full command reference with arguments, options, and output examples, see [references/COMMANDS.md](references/COMMANDS.md).

---

## Setup

### 1. Source ROS 2 environment

```bash
source /opt/ros/${ROS_DISTRO}/setup.bash
```

### 2. Install dependencies

```bash
pip install rclpy rosidl-runtime-py
```

### 3. Run on ROS 2 robot

The CLI must run on a machine with ROS 2 installed and sourced.

---

## Important: Check ROS 2 First

Before any operation, verify ROS 2 is available:

```bash
python3 {baseDir}/scripts/ros2_cli.py version
```

---

## Command Quick Reference

| Category | Command | Description |
|----------|---------|-------------|
| Connection | `version` | Detect ROS 2 distro |
| Safety | `estop` | Emergency stop for mobile robots |
| Topics | `topics list` | List all active topics with types |
| Topics | `topics type <topic>` | Get message type of a topic |
| Topics | `topics details <topic>` | Get topic publishers/subscribers |
| Topics | `topics message <msg_type>` | Get message field structure |
| Topics | `topics subscribe <topic>` | Subscribe and receive messages |
| Topics | `topics publish <topic> <json>` | Publish a message to a topic |
| Topics | `topics publish-sequence <topic> <msgs> <durs>` | Publish message sequence |
| Services | `services list` | List all available services |
| Services | `services type <service>` | Get service type |
| Services | `services details <service>` | Get service request/response fields |
| Services | `services call <service> <json>` | Call a service |
| Nodes | `nodes list` | List all active nodes |
| Nodes | `nodes details <node>` | Get node topics/services |
| Params | `params list <node>` | List node parameters |
| Params | `params get <node:param>` | Get parameter value |
| Params | `params set <node:param> <value>` | Set parameter value |
| Actions | `actions list` | List action servers |
| Actions | `actions details <action>` | Get action goal/result/feedback fields |
| Actions | `actions send <action> <json>` | Send action goal |

---

## Key Commands

### version

```bash
python3 {baseDir}/scripts/ros2_cli.py version
```

### topics list / type / details / message

```bash
python3 {baseDir}/scripts/ros2_cli.py topics list
python3 {baseDir}/scripts/ros2_cli.py topics type /turtle1/cmd_vel
python3 {baseDir}/scripts/ros2_cli.py topics details /turtle1/cmd_vel
python3 {baseDir}/scripts/ros2_cli.py topics message geometry_msgs/Twist
```

### topics subscribe

Without `--duration`: returns first message. With `--duration`: collects multiple messages.

```bash
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /turtle1/pose
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /odom --duration 10 --max-messages 50
```

### topics publish

Without `--duration`: single-shot. With `--duration`: publishes repeatedly at `--rate` Hz. **Use `--duration` for velocity commands** — most robot controllers stop if they don't receive continuous `cmd_vel` messages.

```bash
# Single-shot
python3 {baseDir}/scripts/ros2_cli.py topics publish /trigger '{"data": ""}'

# Move forward 3 seconds (velocity — use --duration)
python3 {baseDir}/scripts/ros2_cli.py topics publish /cmd_vel \
  '{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}' --duration 3

# Stop
python3 {baseDir}/scripts/ros2_cli.py topics publish /cmd_vel \
  '{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}'
```

Options: `--duration SECONDS`, `--rate HZ` (default 10)

### topics publish-sequence

Publish a sequence of messages, each repeated at `--rate` Hz for its corresponding duration. Arrays must have the same length.

```bash
# Forward 3s then stop
python3 {baseDir}/scripts/ros2_cli.py topics publish-sequence /cmd_vel \
  '[{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}},{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}]' \
  '[3.0, 0.5]'

# Draw a square (turtlesim)
python3 {baseDir}/scripts/ros2_cli.py topics publish-sequence /turtle1/cmd_vel \
  '[{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":0},"angular":{"z":0}}]' \
  '[1,1,1,1,1,1,1,1,0.5]'
```

Options: `--rate HZ` (default 10)

### services list / type / details

```bash
python3 {baseDir}/scripts/ros2_cli.py services list
python3 {baseDir}/scripts/ros2_cli.py services type /spawn
python3 {baseDir}/scripts/ros2_cli.py services details /spawn
```

### services call

```bash
python3 {baseDir}/scripts/ros2_cli.py services call /reset '{}'
python3 {baseDir}/scripts/ros2_cli.py services call /spawn \
  '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'
```

### nodes list / details

```bash
python3 {baseDir}/scripts/ros2_cli.py nodes list
python3 {baseDir}/scripts/ros2_cli.py nodes details /turtlesim
```

### params list / get / set

Uses `node:param_name` format.

```bash
python3 {baseDir}/scripts/ros2_cli.py params list /turtlesim
python3 {baseDir}/scripts/ros2_cli.py params get /turtlesim:background_r
python3 {baseDir}/scripts/ros2_cli.py params set /turtlesim:background_r 255
```

### actions list / details / send

```bash
python3 {baseDir}/scripts/ros2_cli.py actions list
python3 {baseDir}/scripts/ros2_cli.py actions details /turtle1/rotate_absolute
python3 {baseDir}/scripts/ros2_cli.py actions send /turtle1/rotate_absolute \
  '{"theta":3.14}'
```

---

## Workflow Examples

### 1. Explore a Robot System

```bash
python3 {baseDir}/scripts/ros2_cli.py version
python3 {baseDir}/scripts/ros2_cli.py topics list
python3 {baseDir}/scripts/ros2_cli.py nodes list
python3 {baseDir}/scripts/ros2_cli.py services list
python3 {baseDir}/scripts/ros2_cli.py topics type /cmd_vel
python3 {baseDir}/scripts/ros2_cli.py topics message geometry_msgs/Twist
python3 {baseDir}/scripts/ros2_cli.py actions list
python3 {baseDir}/scripts/ros2_cli.py params list /robot_node
```

### 2. Move a Robot

Always check the message structure first, then publish movement, and always stop after.

```bash
python3 {baseDir}/scripts/ros2_cli.py topics message geometry_msgs/Twist
python3 {baseDir}/scripts/ros2_cli.py topics publish-sequence /cmd_vel \
  '[{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}},{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}]' \
  '[2.0, 0.5]'
```

### 3. Read Sensor Data

```bash
python3 {baseDir}/scripts/ros2_cli.py topics type /scan
python3 {baseDir}/scripts/ros2_cli.py topics message sensor_msgs/LaserScan
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /scan --duration 3
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /odom --duration 10 --max-messages 50
```

### 4. Use Services

```bash
python3 {baseDir}/scripts/ros2_cli.py services list
python3 {baseDir}/scripts/ros2_cli.py services details /spawn
python3 {baseDir}/scripts/ros2_cli.py services call /spawn \
  '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'
```

### 5. Actions

```bash
python3 {baseDir}/scripts/ros2_cli.py actions list
python3 {baseDir}/scripts/ros2_cli.py actions details /turtle1/rotate_absolute
python3 {baseDir}/scripts/ros2_cli.py actions send /turtle1/rotate_absolute \
  '{"theta":1.57}'
```

### 6. Change Parameters

```bash
python3 {baseDir}/scripts/ros2_cli.py params list /turtlesim
python3 {baseDir}/scripts/ros2_cli.py params get /turtlesim:background_r
python3 {baseDir}/scripts/ros2_cli.py params set /turtlesim:background_r 255
python3 {baseDir}/scripts/ros2_cli.py params set /turtlesim:background_g 0
python3 {baseDir}/scripts/ros2_cli.py params set /turtlesim:background_b 0
```

---

## Safety Notes

**Destructive commands** (can move the robot or change state):
- `topics publish` / `topics publish-sequence` — sends movement or control commands
- `services call` — can reset, spawn, kill, or change robot state
- `params set` — modifies runtime parameters
- `actions send` — triggers robot actions (rotation, navigation, etc.)

**Always stop the robot after movement.** The last message in any `publish-sequence` should be all zeros:
```json
{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}
```

**Always check JSON output for errors before proceeding.**

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| rclpy not installed | Missing Python packages | Run: `pip install rclpy rosidl-runtime-py` |
| ROS 2 not sourced | Environment not set up | Run: `source /opt/ros/${ROS_DISTRO}/setup.bash` |
| No topics found | ROS nodes not running | Ensure nodes are launched and workspace is sourced |
| Service not found | Service not available | Use `services list` to see available services |
| Parameter commands fail | Node doesn't have parameters | Some nodes don't expose parameters |
| Action commands fail | Action server not available | Use `actions list` to see available actions |
| Invalid JSON error | Malformed message | Validate JSON before passing (watch for single vs double quotes) |
| Subscribe timeout | No publisher on topic | Check `topics details` to verify publishers exist |
| publish-sequence length error | Array mismatch | `messages` and `durations` arrays must have the same length |
