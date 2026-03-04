# ROS — Robot Operating System

## ROS1 vs ROS2 Compatibility Matrix

| Feature | ROS1 (Noetic) | ROS2 (Humble/Iron) |
|---------|---------------|---------------------|
| Python API | `rospy` | `rclpy` |
| C++ API | `roscpp` | `rclcpp` |
| Build | `catkin_make` | `colcon build` |
| Workspace source | `source devel/setup.bash` | `source install/setup.bash` |
| Launch | XML only | Python (preferred) or XML |
| Param server | Global | Per-node, namespaced |
| Discovery | rosmaster | DDS (no master) |

**NEVER mix these.** `import rospy` in ROS2 = `ModuleNotFoundError`.

## Package Creation

### ROS2 (Python)
```bash
cd ~/ros2_ws/src
ros2 pkg create my_robot --build-type ament_python \
    --dependencies rclpy std_msgs geometry_msgs
```

### ROS2 (C++)
```bash
ros2 pkg create my_robot --build-type ament_cmake \
    --dependencies rclcpp std_msgs geometry_msgs
```

## Build Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Package not found" | Didn't source workspace | `source install/setup.bash` |
| "Cannot find -lrclcpp" | Missing dependency | Add to package.xml AND CMakeLists.txt |
| "Multiple definitions" | Header included twice | Add include guards or #pragma once |
| "Unknown CMake command" | Wrong build type | ament_cmake vs ament_python mismatch |

## QoS Profiles — Critical for Message Delivery

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

# Sensor data — OK to drop old messages
sensor_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=10
)

# Commands — must not drop
cmd_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    depth=1
)

# Late-joiner needs last message (e.g., map)
latched_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    depth=1
)
```

**QoS mismatch = silent failure.** Publisher BEST_EFFORT + Subscriber RELIABLE = no messages, no error.

## Launch File (Python, ROS2)

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim', default_value='true'),
        
        Node(
            package='my_robot',
            executable='controller',
            name='controller_node',
            parameters=[{
                'use_sim': LaunchConfiguration('use_sim'),
                'max_speed': 1.5
            }],
            remappings=[
                ('/cmd_vel', '/robot/cmd_vel'),
                ('/odom', '/robot/odom')
            ]
        ),
    ])
```

## TF2 Static Transform

```bash
# ROS2 Humble syntax
ros2 run tf2_ros static_transform_publisher \
    --x 0 --y 0 --z 0.1 --roll 0 --pitch 0 --yaw 0 \
    --frame-id base_link --child-frame-id laser_frame

# Older ROS2 syntax (Foxy)
ros2 run tf2_ros static_transform_publisher \
    0 0 0.1 0 0 0 base_link laser_frame
```

**Syntax changed between versions.** Check your distro's documentation.

## Gazebo Version Matrix

| ROS Distro | Default Gazebo | Plugin System |
|------------|----------------|---------------|
| Noetic | Gazebo 11 (Classic) | libgazebo_ros_* |
| Foxy | Gazebo 11 (Classic) | libgazebo_ros_* |
| Humble | Gazebo Fortress | gz-sim plugins |
| Iron | Gazebo Harmonic | gz-sim plugins |

**Classic plugins don't work in Fortress/Harmonic.** Migration required.

## Common Debugging Commands

```bash
# List running nodes
ros2 node list

# Show node info (topics, services, params)
ros2 node info /controller_node

# Echo topic messages
ros2 topic echo /cmd_vel

# Check topic QoS (why messages not arriving?)
ros2 topic info /scan --verbose

# List parameters
ros2 param list /controller_node

# Check TF tree
ros2 run tf2_tools view_frames
```
