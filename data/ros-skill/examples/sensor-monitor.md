# Sensor Monitoring

Workflows for subscribing to and analyzing robot sensor data.

## 1. Discover Available Sensors

```bash
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> connect
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics list
```

Common sensor topics:
- `/scan` — LiDAR (sensor_msgs/LaserScan)
- `/imu/data` — IMU (sensor_msgs/Imu)
- `/odom` — Odometry (nav_msgs/Odometry)
- `/joint_states` — Joint positions (sensor_msgs/JointState)
- `/camera/image_raw` — Camera (sensor_msgs/Image)

## 2. Read a Single Sensor Value

```bash
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics type /scan
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics message sensor_msgs/LaserScan
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics subscribe /scan sensor_msgs/LaserScan
```

## 3. Monitor Sensor Over Time

Collect odometry data for 10 seconds:

```bash
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics subscribe /odom nav_msgs/Odometry \
  --duration 10 --max-messages 50
```

Monitor IMU:

```bash
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics subscribe /imu/data sensor_msgs/Imu \
  --duration 5 --max-messages 20
```

## 4. Joint State Monitoring

```bash
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics subscribe /joint_states sensor_msgs/JointState
```

Returns joint names, positions, velocities, and efforts.

## 5. LiDAR Obstacle Detection

```bash
python {baseDir}/scripts/ros_cli.py --ip <ROBOT_IP> topics subscribe /scan sensor_msgs/LaserScan --timeout 3
```

The response includes:
- `ranges[]` — distance measurements per angle
- `angle_min`, `angle_max` — scan range
- `range_min`, `range_max` — valid distance range
