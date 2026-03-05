# Command Reference

Full reference for all `ros_cli.py` commands with arguments, options, and output examples.

---

## connect

Test connectivity to rosbridge. Performs ping, port check, and WebSocket handshake.

```bash
python {baseDir}/scripts/ros_cli.py connect
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> connect
```

Output:
```json
{
  "ip": "127.0.0.1",
  "port": 9090,
  "ping": true,
  "port_open": true,
  "websocket": true
}
```

If connection fails:
```json
{
  "ip": "10.0.0.5",
  "port": 9090,
  "ping": true,
  "port_open": false,
  "websocket": false,
  "error": "Connection refused"
}
```

---

## version

Detect the ROS version (1 or 2) and distro name running on the robot.

```bash
python {baseDir}/scripts/ros_cli.py version
```

Output:
```json
{"version": "2", "distro": "humble"}
```

---

## topics list

List all active topics with their message types.

```bash
python {baseDir}/scripts/ros_cli.py topics list
```

Output:
```json
{
  "topics": ["/turtle1/cmd_vel", "/turtle1/pose", "/rosout"],
  "types": ["geometry_msgs/Twist", "turtlesim/Pose", "rcl_interfaces/msg/Log"],
  "count": 3
}
```

---

## topics type `<topic>`

Get the message type of a specific topic.

| Argument | Required | Description |
|----------|----------|-------------|
| `topic` | Yes | Topic name (e.g. `/cmd_vel`, `/turtle1/pose`) |

```bash
python {baseDir}/scripts/ros_cli.py topics type /turtle1/cmd_vel
```

Output:
```json
{"topic": "/turtle1/cmd_vel", "type": "geometry_msgs/Twist"}
```

---

## topics details `<topic>`

Get topic details including message type, publishers, and subscribers.

| Argument | Required | Description |
|----------|----------|-------------|
| `topic` | Yes | Topic name |

```bash
python {baseDir}/scripts/ros_cli.py topics details /turtle1/cmd_vel
```

Output:
```json
{
  "topic": "/turtle1/cmd_vel",
  "type": "geometry_msgs/Twist",
  "publishers": [],
  "subscribers": ["/turtlesim"]
}
```

---

## topics message `<message_type>`

Get the field structure of a message type.

| Argument | Required | Description |
|----------|----------|-------------|
| `message_type` | Yes | Full message type (e.g. `geometry_msgs/Twist`, `sensor_msgs/LaserScan`) |

```bash
python {baseDir}/scripts/ros_cli.py topics message geometry_msgs/Twist
```

Output:
```json
{
  "message_type": "geometry_msgs/Twist",
  "structure": {
    "geometry_msgs/Twist": {"linear": "geometry_msgs/Vector3", "angular": "geometry_msgs/Vector3"},
    "geometry_msgs/Vector3": {"x": "float64", "y": "float64", "z": "float64"}
  }
}
```

---

## topics subscribe `<topic>` `<msg_type>` [options]

Subscribe to a topic and receive messages.

| Argument | Required | Description |
|----------|----------|-------------|
| `topic` | Yes | Topic to subscribe to |
| `msg_type` | Yes | Message type of the topic |

| Option | Default | Description |
|--------|---------|-------------|
| `--duration SECONDS` | _(none)_ | Collect messages for this duration. Without this, returns first message only |
| `--max-messages N` | `100` | Maximum number of messages to collect (only with `--duration`) |

**Single message (default):**
```bash
python {baseDir}/scripts/ros_cli.py topics subscribe /turtle1/pose turtlesim/Pose
```

Output:
```json
{
  "msg": {"x": 5.544, "y": 5.544, "theta": 0.0, "linear_velocity": 0.0, "angular_velocity": 0.0}
}
```

**Collect over time:**
```bash
python {baseDir}/scripts/ros_cli.py topics subscribe /odom nav_msgs/Odometry --duration 10 --max-messages 50
```

Output:
```json
{
  "topic": "/odom",
  "collected_count": 50,
  "messages": [
    {"header": {}, "pose": {"pose": {"position": {"x": 0.1, "y": 0.0, "z": 0.0}}}},
    "..."
  ]
}
```

**With timeout for slow topics:**
```bash
python {baseDir}/scripts/ros_cli.py topics subscribe /scan sensor_msgs/LaserScan --timeout 10
```

---

## topics publish `<topic>` `<msg_type>` `<json_message>` [options]

Publish a message to a topic. Without `--duration`, sends once. With `--duration`, publishes repeatedly at `--rate` Hz — required for velocity commands since most robot controllers stop if they don't receive continuous commands.

| Argument | Required | Description |
|----------|----------|-------------|
| `topic` | Yes | Topic to publish to |
| `msg_type` | Yes | Message type |
| `json_message` | Yes | JSON string of the message payload |

| Option | Default | Description |
|--------|---------|-------------|
| `--duration SECONDS` | _(none)_ | Publish repeatedly for this duration |
| `--rate HZ` | `10` | Publish rate in Hz (used with `--duration`) |

**Single-shot (trigger, one-time command):**
```bash
python {baseDir}/scripts/ros_cli.py topics publish /turtle1/cmd_vel geometry_msgs/Twist \
  '{"linear":{"x":2.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}'
```

**Move forward for 3 seconds (recommended for velocity):**
```bash
python {baseDir}/scripts/ros_cli.py topics publish /cmd_vel geometry_msgs/Twist \
  '{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}' --duration 3
```

Output:
```json
{"success": true, "topic": "/cmd_vel", "msg_type": "geometry_msgs/Twist", "duration": 3.0, "rate": 10.0, "published_count": 30}
```

**Rotate left for 2 seconds:**
```bash
python {baseDir}/scripts/ros_cli.py topics publish /cmd_vel geometry_msgs/Twist \
  '{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0.5}}' --duration 2
```

**Stop (single-shot is fine for stop):**
```bash
python {baseDir}/scripts/ros_cli.py topics publish /cmd_vel geometry_msgs/Twist \
  '{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}'
```

---

## topics publish-sequence `<topic>` `<msg_type>` `<json_messages>` `<json_durations>` [options]

Publish a sequence of messages. Each message is published repeatedly at `--rate` Hz for its corresponding duration. The arrays must have the same length.

| Argument | Required | Description |
|----------|----------|-------------|
| `topic` | Yes | Topic to publish to |
| `msg_type` | Yes | Message type |
| `json_messages` | Yes | JSON array of messages to publish in order |
| `json_durations` | Yes | JSON array of durations (seconds) for each message |

| Option | Default | Description |
|--------|---------|-------------|
| `--rate HZ` | `10` | Publish rate in Hz |

**Move forward 3 seconds then stop:**
```bash
python {baseDir}/scripts/ros_cli.py topics publish-sequence /cmd_vel geometry_msgs/Twist \
  '[{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}},{"linear":{"x":0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}]' \
  '[3.0, 0.5]'
```

Output:
```json
{"success": true, "published_count": 35, "topic": "/cmd_vel", "rate": 10.0}
```

**Draw a square (turtlesim):**
```bash
python {baseDir}/scripts/ros_cli.py topics publish-sequence /turtle1/cmd_vel geometry_msgs/Twist \
  '[{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":0},"angular":{"z":0}}]' \
  '[1,1,1,1,1,1,1,1,0.5]'
```

---

## services list

List all available services.

```bash
python {baseDir}/scripts/ros_cli.py services list
```

Output:
```json
{
  "services": ["/clear", "/kill", "/reset", "/spawn", "/turtle1/set_pen", "/turtle1/teleport_absolute"],
  "count": 6
}
```

---

## services type `<service>`

Get the type of a specific service.

| Argument | Required | Description |
|----------|----------|-------------|
| `service` | Yes | Service name (e.g. `/spawn`, `/reset`) |

```bash
python {baseDir}/scripts/ros_cli.py services type /spawn
```

Output:
```json
{"service": "/spawn", "type": "turtlesim/Spawn"}
```

---

## services details `<service>`

Get service details including type, request fields, and response fields.

| Argument | Required | Description |
|----------|----------|-------------|
| `service` | Yes | Service name |

```bash
python {baseDir}/scripts/ros_cli.py services details /spawn
```

Output:
```json
{
  "service": "/spawn",
  "type": "turtlesim/Spawn",
  "request": {"x": "float32", "y": "float32", "theta": "float32", "name": "string"},
  "response": {"name": "string"}
}
```

---

## services call `<service>` `<service_type>` `<json_request>`

Call a service with a JSON request payload.

| Argument | Required | Description |
|----------|----------|-------------|
| `service` | Yes | Service name |
| `service_type` | Yes | Service type |
| `json_request` | Yes | JSON string of the request arguments |

**Reset turtlesim:**
```bash
python {baseDir}/scripts/ros_cli.py services call /reset std_srvs/Empty '{}'
```

**Spawn a new turtle:**
```bash
python {baseDir}/scripts/ros_cli.py services call /spawn turtlesim/Spawn \
  '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'
```

Output:
```json
{"service": "/spawn", "success": true, "result": {"name": "turtle2"}}
```

**Set pen color:**
```bash
python {baseDir}/scripts/ros_cli.py services call /turtle1/set_pen turtlesim/srv/SetPen \
  '{"r":255,"g":0,"b":0,"width":3,"off":0}'
```

---

## nodes list

List all active ROS nodes.

```bash
python {baseDir}/scripts/ros_cli.py nodes list
```

Output:
```json
{
  "nodes": ["/turtlesim", "/rosbridge_websocket"],
  "count": 2
}
```

---

## nodes details `<node>`

Get node details including topics and services.

| Argument | Required | Description |
|----------|----------|-------------|
| `node` | Yes | Node name (e.g. `/turtlesim`) |

```bash
python {baseDir}/scripts/ros_cli.py nodes details /turtlesim
```

Output:
```json
{
  "node": "/turtlesim",
  "publishers": ["/turtle1/color_sensor", "/turtle1/pose", "/rosout"],
  "subscribers": ["/turtle1/cmd_vel"],
  "services": ["/clear", "/kill", "/reset", "/spawn", "/turtle1/set_pen", "/turtle1/teleport_absolute"]
}
```

---

## params list `<node>` (ROS 2 only)

List all parameters for a specific node.

| Argument | Required | Description |
|----------|----------|-------------|
| `node` | Yes | Node name (e.g. `/turtlesim`) |

```bash
python {baseDir}/scripts/ros_cli.py params list /turtlesim
```

Output:
```json
{
  "node": "/turtlesim",
  "parameters": ["/turtlesim:background_r", "/turtlesim:background_g", "/turtlesim:background_b", "/turtlesim:use_sim_time"],
  "count": 4
}
```

---

## params get `<node:param_name>` (ROS 2 only)

Get a parameter value.

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Parameter in `/node:param` format |

```bash
python {baseDir}/scripts/ros_cli.py params get /turtlesim:background_r
```

Output:
```json
{"name": "/turtlesim:background_r", "value": "69", "exists": true}
```

---

## params set `<node:param_name>` `<value>` (ROS 2 only)

Set a parameter value.

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Parameter in `/node:param` format |
| `value` | Yes | New value to set |

```bash
python {baseDir}/scripts/ros_cli.py params set /turtlesim:background_r 255
```

Output:
```json
{"name": "/turtlesim:background_r", "value": "255", "success": true}
```

---

## actions list (ROS 2 only)

List all available action servers.

```bash
python {baseDir}/scripts/ros_cli.py actions list
```

Output:
```json
{
  "actions": ["/turtle1/rotate_absolute"],
  "count": 1
}
```

---

## actions details `<action>` (ROS 2 only)

Get action details including goal, result, and feedback field structures.

| Argument | Required | Description |
|----------|----------|-------------|
| `action` | Yes | Action server name |

```bash
python {baseDir}/scripts/ros_cli.py actions details /turtle1/rotate_absolute
```

Output:
```json
{
  "action": "/turtle1/rotate_absolute",
  "action_type": "turtlesim/action/RotateAbsolute",
  "goal": {"theta": "float32"},
  "result": {"delta": "float32"},
  "feedback": {"remaining": "float32"}
}
```

---

## actions send `<action>` `<action_type>` `<json_goal>` (ROS 2 only)

Send an action goal and wait for the result.

| Argument | Required | Description |
|----------|----------|-------------|
| `action` | Yes | Action server name |
| `action_type` | Yes | Action type |
| `json_goal` | Yes | JSON string of the goal arguments |

```bash
python {baseDir}/scripts/ros_cli.py actions send /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute '{"theta":3.14}'
```

Output:
```json
{
  "action": "/turtle1/rotate_absolute",
  "success": true,
  "goal_id": "goal_1709312000000",
  "result": {"delta": -1.584}
}
```

If timeout:
```json
{
  "action": "/turtle1/rotate_absolute",
  "goal_id": "goal_1709312000000",
  "success": false,
  "error": "Timeout after 5.0s"
}
```
