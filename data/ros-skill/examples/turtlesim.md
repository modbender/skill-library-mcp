# Turtlesim Tutorial

End-to-end workflow for controlling turtlesim with `ros_cli.py`.

## Prerequisites

```bash
# Install dependency
pip install websocket-client

# Launch turtlesim (ROS 2)
ros2 run turtlesim turtlesim_node
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

## Step 1: Connect and explore

```bash
python {baseDir}/scripts/ros_cli.py connect
python {baseDir}/scripts/ros_cli.py version
python {baseDir}/scripts/ros_cli.py topics list
python {baseDir}/scripts/ros_cli.py nodes list
python {baseDir}/scripts/ros_cli.py services list
```

## Step 2: Understand message types

```bash
python {baseDir}/scripts/ros_cli.py topics type /turtle1/cmd_vel
python {baseDir}/scripts/ros_cli.py topics message geometry_msgs/Twist
```

## Step 3: Read turtle position

```bash
python {baseDir}/scripts/ros_cli.py topics subscribe /turtle1/pose turtlesim/Pose
```

## Step 4: Move the turtle

Move forward for 2 seconds (use `--duration` to keep the velocity command active):

```bash
python {baseDir}/scripts/ros_cli.py topics publish /turtle1/cmd_vel geometry_msgs/Twist \
  '{"linear":{"x":2.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}' --duration 2
```

## Step 5: Draw a square

```bash
python {baseDir}/scripts/ros_cli.py topics publish-sequence /turtle1/cmd_vel geometry_msgs/Twist \
  '[{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":0},"angular":{"z":0}}]' \
  '[1,1,1,1,1,1,1,1,0.5]'
```

## Step 6: Use services

```bash
# Reset turtle position
python {baseDir}/scripts/ros_cli.py services call /reset std_srvs/Empty '{}'

# Spawn a new turtle
python {baseDir}/scripts/ros_cli.py services call /spawn turtlesim/Spawn \
  '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'
```

## Step 7: Change background color (ROS 2)

```bash
python {baseDir}/scripts/ros_cli.py params set /turtlesim:background_r 255
python {baseDir}/scripts/ros_cli.py params set /turtlesim:background_g 0
python {baseDir}/scripts/ros_cli.py params set /turtlesim:background_b 0
```

## Step 8: Use actions (ROS 2)

```bash
python {baseDir}/scripts/ros_cli.py actions list
python {baseDir}/scripts/ros_cli.py actions details /turtle1/rotate_absolute
python {baseDir}/scripts/ros_cli.py actions send /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute '{"theta":3.14}'
```
