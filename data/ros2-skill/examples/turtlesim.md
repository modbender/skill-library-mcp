# Turtlesim Tutorial

End-to-end workflow for controlling turtlesim with `ros2_cli.py`.

## Prerequisites

```bash
# Source ROS 2 environment
source /opt/ros/${ROS_DISTRO}/setup.bash

# Install dependencies
pip install rclpy rosidl-runtime-py

# Launch turtlesim (ROS 2)
ros2 run turtlesim turtlesim_node
```

## Step 1: Check version and explore

```bash
python3 {baseDir}/scripts/ros2_cli.py version
python3 {baseDir}/scripts/ros2_cli.py topics list
python3 {baseDir}/scripts/ros2_cli.py nodes list
python3 {baseDir}/scripts/ros2_cli.py services list
```

## Step 2: Understand message types

```bash
python3 {baseDir}/scripts/ros2_cli.py topics type /turtle1/cmd_vel
python3 {baseDir}/scripts/ros2_cli.py topics message geometry_msgs/Twist
```

## Step 3: Read turtle position

```bash
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /turtle1/pose
```

## Step 4: Move the turtle

Move forward for 2 seconds (use `--duration` to keep the velocity command active):

```bash
python3 {baseDir}/scripts/ros2_cli.py topics publish /turtle1/cmd_vel \
  '{"linear":{"x":2.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}' --duration 2
```

## Step 5: Draw a square

```bash
python3 {baseDir}/scripts/ros2_cli.py topics publish-sequence /turtle1/cmd_vel \
  '[{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":1.5708}},{"linear":{"x":0},"angular":{"z":0}}]' \
  '[1,1,1,1,1,1,1,1,0.5]'
```

## Step 6: Use services

```bash
# Reset turtle position
python3 {baseDir}/scripts/ros2_cli.py services call /reset '{}'

# Spawn a new turtle
python3 {baseDir}/scripts/ros2_cli.py services call /spawn \
  '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'
```

## Step 7: Change background color

```bash
python3 {baseDir}/scripts/ros2_cli.py params set /turtlesim:background_r 255
python3 {baseDir}/scripts/ros2_cli.py params set /turtlesim:background_g 0
python3 {baseDir}/scripts/ros2_cli.py params set /turtlesim:background_b 0
```

## Step 8: Use actions

```bash
python3 {baseDir}/scripts/ros2_cli.py actions list
python3 {baseDir}/scripts/ros2_cli.py actions details /turtle1/rotate_absolute
python3 {baseDir}/scripts/ros2_cli.py actions send /turtle1/rotate_absolute \
  '{"theta":3.14}'
```
