---
name: ros-skill
description: "Controls ROS/ROS2 robots via rosbridge WebSocket CLI. Use when the user asks about ROS topics, services, nodes, parameters, actions, robot movement, sensor data, or any ROS/ROS2 robot interaction."
license: Apache-2.0
compatibility: "Requires python3, websocket-client pip package, and rosbridge running on the robot (default port 9090)"
user-invocable: true
metadata: {"openclaw": {"emoji": "🤖", "requires": {"bins": ["python3"], "pip": ["websocket-client"]}, "category": "robotics", "tags": ["ros", "ros2", "robotics", "rosbridge"]}, "author": "lpigeon", "version": "1.0.1"}
---

# ROS Skill

Controls and monitors ROS/ROS2 robots via rosbridge WebSocket.

**Architecture:** Agent → `ros_cli.py` → rosbridge (WebSocket :9090) → ROS/ROS2 Robot

All commands output JSON. Errors contain `{"error": "..."}`.

For full command reference with arguments, options, and output examples, see [references/COMMANDS.md](references/COMMANDS.md).

---

## Setup

### 1. Install dependency

```bash
pip install websocket-client
```

### 2. Launch rosbridge on the robot

**ROS 1:**
```bash
sudo apt install ros-${ROS_DISTRO}-rosbridge-server
roslaunch rosbridge_server rosbridge_websocket.launch
```

**ROS 2:**
```bash
sudo apt install ros-${ROS_DISTRO}-rosbridge-server
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

---

## Important: Always Connect First

Before any operation, test connectivity:

```bash
python {baseDir}/scripts/ros_cli.py connect
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> connect
```

---

## Global Options

| Flag | Default | Description |
|------|---------|-------------|
| `--ip IP` | `127.0.0.1` | Rosbridge IP address |
| `--port PORT` | `9090` | Rosbridge port number |
| `--timeout SECONDS` | `5.0` | Connection and request timeout |

---

## Command Quick Reference

| Category | Command | Description |
|----------|---------|-------------|
| Connection | `connect` | Test rosbridge connectivity (ping, port, WebSocket) |
| Connection | `version` | Detect ROS version and distro |
| Topics | `topics list` | List all active topics with types |
| Topics | `topics type <topic>` | Get message type of a topic |
| Topics | `topics details <topic>` | Get topic publishers/subscribers |
| Topics | `topics message <msg_type>` | Get message field structure |
| Topics | `topics subscribe <topic> <msg_type>` | Subscribe and receive messages |
| Topics | `topics publish <topic> <msg_type> <json>` | Publish a message to a topic |
| Topics | `topics publish-sequence <topic> <msg_type> <msgs> <durs>` | Publish message sequence |
| Services | `services list` | List all available services |
| Services | `services type <service>` | Get service type |
| Services | `services details <service>` | Get service request/response fields |
| Services | `services call <service> <type> <json>` | Call a service |
| Nodes | `nodes list` | List all active nodes |
| Nodes | `nodes details <node>` | Get node topics/services |
| Params | `params list <node>` | List node parameters (ROS 2) |
| Params | `params get <node:param>` | Get parameter value (ROS 2) |
| Params | `params set <node:param> <value>` | Set parameter value (ROS 2) |
| Actions | `actions list` | List action servers (ROS 2) |
| Actions | `actions details <action>` | Get action goal/result/feedback fields (ROS 2) |
| Actions | `actions send <action> <type> <json>` | Send action goal (ROS 2) |

---

## Key Commands

### connect

```bash
python {baseDir}/scripts/ros_cli.py connect
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> connect
```

### version

```bash
python {baseDir}/scripts/ros_cli.py version
```

### topics list / type / details / message

```bash
python {baseDir}/scripts/ros_cli.py topics list
python {baseDir}/scripts/ros_cli.py topics type /turtle1/cmd_vel
python {baseDir}/scripts/ros_cli.py topics details /turtle1/cmd_vel
python {baseDir}/scripts/ros_cli.py topics message geometry_msgs/Twist
```

### topics subscribe

Without `--duration`: returns first message. With `--duration`: collects multiple messages.

```bash
python {baseDir}/scripts/ros_cli.py topics subscribe /turtle1/pose turtlesim/Pose
python {baseDir}/scripts/ros_cli.py topics subscribe /odom nav_msgs/Odometry --duration 10 --max-messages 50
python {baseDir}/scripts/ros_cli.py topics subscribe /scan sensor_msgs/LaserScan --timeout 10
```

### topics publish

Without `--duration`: single-shot. With `--duration`: publishes repeatedly at `--rate` Hz. **Use `--duration` for velocity commands** — most robot controllers stop if they don't receive continuous `cmd_vel` messages.

```bash
# Single-shot
python {baseDir}/scripts/ros_cli.py topics publish /trigger std_msgs/Empty '{}'

# Move forward 3 seconds (velocity — use --duration)
python {baseDir}/scripts/ros_cli.py topics publish /cmd_vel geometry_msgs/Twist \
  '{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}' --duration 3

# Rotate left 2 seconds
python {baseDir}/scripts/ros_cli.py topics publish /cmd_vel geometry_msgs/Twist \
  '{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0.5}}' --duration 2

# Stop
python {baseDir}/scripts/ros_cli.py topics publish /cmd_vel geometry_msgs/Twist \
  '{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}'
```

Options: `--duration SECONDS`, `--rate HZ` (default 10)

### topics publish-sequence

Publish a sequence of messages, each repeated at `--rate` Hz for its corresponding duration. Arrays must have the same length.

```bash
# Forward 3s then stop
python {baseDir}/scripts/ros_cli.py topics publish-sequence /cmd_vel geometry_msgs/Twist \
  '[{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}},{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}]' \
  '[3.0, 0.5]'

# Draw a square (turtlesim)
python {baseDir}/scripts/ros_cli.py topics publish-sequence /turtle1/cmd_vel geometry_msgs/Twist \
  '[{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":0},"angular":{"z":0}}]' \
  '[1,1,1,1,1,1,1,1,0.5]'
```

Options: `--rate HZ` (default 10)

### services list / type / details

```bash
python {baseDir}/scripts/ros_cli.py services list
python {baseDir}/scripts/ros_cli.py services type /spawn
python {baseDir}/scripts/ros_cli.py services details /spawn
```

### services call

```bash
python {baseDir}/scripts/ros_cli.py services call /reset std_srvs/Empty '{}'
python {baseDir}/scripts/ros_cli.py services call /spawn turtlesim/Spawn \
  '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'
python {baseDir}/scripts/ros_cli.py services call /turtle1/set_pen turtlesim/srv/SetPen \
  '{"r":255,"g":0,"b":0,"width":3,"off":0}'
```

### nodes list / details

```bash
python {baseDir}/scripts/ros_cli.py nodes list
python {baseDir}/scripts/ros_cli.py nodes details /turtlesim
```

### params list / get / set (ROS 2 only)

Uses `node:param_name` format from `params list` output.

```bash
python {baseDir}/scripts/ros_cli.py params list /turtlesim
python {baseDir}/scripts/ros_cli.py params get /turtlesim:background_r
python {baseDir}/scripts/ros_cli.py params set /turtlesim:background_r 255
```

### actions list / details / send (ROS 2 only)

```bash
python {baseDir}/scripts/ros_cli.py actions list
python {baseDir}/scripts/ros_cli.py actions details /turtle1/rotate_absolute
python {baseDir}/scripts/ros_cli.py actions send /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute '{"theta":3.14}'
```

---

## Workflow Examples

### 1. Explore a Robot System

```bash
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> connect
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> version
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics list
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> nodes list
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> services list
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics type /cmd_vel
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics message geometry_msgs/Twist
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> actions list
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> params list /robot_node
```

### 2. Move a Robot

Always check the message structure first, then publish movement, and always stop after.

```bash
python {baseDir}/scripts/ros_cli.py topics message geometry_msgs/Twist
python {baseDir}/scripts/ros_cli.py topics publish-sequence /cmd_vel geometry_msgs/Twist \
  '[{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}},{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}]' \
  '[2.0, 0.5]'
```

### 3. Read Sensor Data

```bash
python {baseDir}/scripts/ros_cli.py topics type /scan
python {baseDir}/scripts/ros_cli.py topics message sensor_msgs/LaserScan
python {baseDir}/scripts/ros_cli.py topics subscribe /scan sensor_msgs/LaserScan --timeout 3
python {baseDir}/scripts/ros_cli.py topics subscribe /odom nav_msgs/Odometry --duration 10 --max-messages 50
```

### 4. Use Services

```bash
python {baseDir}/scripts/ros_cli.py services list
python {baseDir}/scripts/ros_cli.py services details /spawn
python {baseDir}/scripts/ros_cli.py services call /spawn turtlesim/Spawn \
  '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'
```

### 5. ROS 2 Actions

```bash
python {baseDir}/scripts/ros_cli.py actions list
python {baseDir}/scripts/ros_cli.py actions details /turtle1/rotate_absolute
python {baseDir}/scripts/ros_cli.py actions send /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute '{"theta":1.57}'
```

### 6. Change Parameters (ROS 2)

```bash
python {baseDir}/scripts/ros_cli.py params list /turtlesim
python {baseDir}/scripts/ros_cli.py params get /turtlesim:background_r
python {baseDir}/scripts/ros_cli.py params set /turtlesim:background_r 255
python {baseDir}/scripts/ros_cli.py params set /turtlesim:background_g 0
python {baseDir}/scripts/ros_cli.py params set /turtlesim:background_b 0
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
| Connection refused | rosbridge not running | Start rosbridge: `ros2 launch rosbridge_server rosbridge_websocket_launch.xml` |
| Timeout errors | Slow network or large data | Increase timeout: `--timeout 10` or `--timeout 30` |
| No topics found | ROS nodes not running | Ensure nodes are launched and workspace is sourced |
| Empty topic list | rosapi not available | Verify rosbridge includes rosapi (default in standard install) |
| Parameter commands fail | Using ROS 1 | `params` commands only work with ROS 2 |
| Action commands fail | Using ROS 1 | `actions` commands only work with ROS 2 |
| Invalid JSON error | Malformed message | Validate JSON before passing (watch for single vs double quotes) |
| Subscribe timeout | No publisher on topic | Check `topics details` to verify publishers exist |
| publish-sequence length error | Array mismatch | `messages` and `durations` arrays must have the same length |
