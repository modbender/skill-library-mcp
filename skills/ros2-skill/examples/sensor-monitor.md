# Sensor Monitoring

Workflows for subscribing to and analyzing robot sensor data.

## Prerequisites

```bash
# Source ROS 2 environment
source /opt/ros/${ROS_DISTRO}/setup.bash

# Install dependencies
pip install rclpy rosidl-runtime-py
```

## 1. Discover Available Sensors

```bash
python3 {baseDir}/scripts/ros2_cli.py topics list
```

Common sensor topics:
- `/scan` — LiDAR (sensor_msgs/LaserScan)
- `/imu/data` — IMU (sensor_msgs/Imu)
- `/odom` — Odometry (nav_msgs/Odometry)
- `/joint_states` — Joint positions (sensor_msgs/JointState)
- `/camera/image_raw` — Camera (sensor_msgs/Image)

## 2. Read a Single Sensor Value

```bash
python3 {baseDir}/scripts/ros2_cli.py topics type /scan
python3 {baseDir}/scripts/ros2_cli.py topics message sensor_msgs/LaserScan
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /scan
```

## 3. Monitor Sensor Over Time

Collect odometry data for 10 seconds:

```bash
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /odom --duration 10 --max-messages 50
```

Monitor IMU:

```bash
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /imu/data --duration 5 --max-messages 20
```

## 4. Joint State Monitoring

```bash
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /joint_states
```

Returns joint names, positions, velocities, and efforts.

## 5. LiDAR Obstacle Detection

```bash
python3 {baseDir}/scripts/ros2_cli.py topics subscribe /scan --duration 3
```

The response includes:
- `ranges[]` — distance measurements per angle
- `angle_min`, `angle_max` — scan range
- `range_min`, `range_max` — valid distance range
