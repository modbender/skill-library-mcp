#!/usr/bin/env python3
"""ROS 2 Skill - Standalone CLI tool for controlling ROS 2 robots directly via rclpy.

Requires: rclpy (install via ROS 2) or pip install rclpy

Commands:

  version
    Detect ROS 2 version and distro.
    $ python3 ros2_cli.py version

  estop
    Emergency stop for mobile robots. Auto-detects velocity topic and type,
    then publishes zero velocity. For mobile bases only (not arms).
    $ python3 ros2_cli.py estop

  topics list
    List all active topics with their message types.
    $ python3 ros2_cli.py topics list

  topics type <topic>
    Get the message type of a specific topic.
    $ python3 ros2_cli.py topics type /cmd_vel
    $ python3 ros2_cli.py topics type /turtle1/pose

  topics details <topic>
    Get topic details including type, publishers, and subscribers.
    $ python3 ros2_cli.py topics details /cmd_vel

  topics message <message_type>
    Get the field structure of a message type.
    $ python3 ros2_cli.py topics message geometry_msgs/Twist
    $ python3 ros2_cli.py topics message sensor_msgs/LaserScan

  topics subscribe <topic> [--duration SEC] [--max-messages N]
    Subscribe to a topic. Without --duration, returns the first message and exits.
    With --duration, collects messages for the specified time.
    --duration SECONDS   Collect messages for this duration (default: single message)
    --max-messages N     Max messages to collect during duration (default: 100)
    $ python3 ros2_cli.py topics subscribe /turtle1/pose
    $ python3 ros2_cli.py topics subscribe /odom --duration 10 --max-messages 50

  topics publish <topic> <json_message> [--duration SEC] [--rate HZ]
    Publish a message to a topic.
    Without --duration: sends once (single-shot).
    With --duration: publishes repeatedly at --rate Hz for the specified seconds.
    --duration SECONDS   Publish repeatedly for this duration
    --rate HZ            Publish rate (default: 10 Hz)
    $ python3 ros2_cli.py topics publish /turtle1/cmd_vel \
        '{"linear":{"x":2.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}'
    $ python3 ros2_cli.py topics publish /cmd_vel \
        '{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}' --duration 3

  topics publish-sequence <topic> <json_messages> <json_durations> [--rate HZ]
    Publish a sequence of messages. Each message is repeatedly published at --rate Hz
    for its corresponding duration. This keeps velocity commands active for the full duration.
    <json_messages>   JSON array of messages to publish in order
    <json_durations>  JSON array of durations (seconds) for each message (must match length)
    --rate HZ         Publish rate (default: 10 Hz)
    $ python3 ros2_cli.py topics publish-sequence /turtle1/cmd_vel \
        '[{"linear":{"x":1.0},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":0}}]' \
        '[3.0, 0.5]'

  services list
    List all available services.
    $ python3 ros2_cli.py services list

  services type <service>
    Get the type of a specific service.
    $ python3 ros2_cli.py services type /reset

  services details <service>
    Get service details including type, request fields, and response fields.
    $ python3 ros2_cli.py services details /spawn

  services call <service> <json_request>
    Call a service with a JSON request payload.
    $ python3 ros2_cli.py services call /reset '{}'
    $ python3 ros2_cli.py services call /spawn \
        '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'

  nodes list
    List all active nodes.
    $ python3 ros2_cli.py nodes list

  nodes details <node>
    Get node details including publishers, subscribers, and services.
    $ python3 ros2_cli.py nodes details /turtlesim

  params list <node>
    List all parameters for a node.
    $ python3 ros2_cli.py params list /turtlesim

  params get <node:param_name>
    Get a parameter value. Format: /node_name:parameter_name
    $ python3 ros2_cli.py params get /turtlesim:background_r
    $ python3 ros2_cli.py params get /turtlesim:background_b

  params set <node:param_name> <value>
    Set a parameter value. Format: /node_name:parameter_name
    $ python3 ros2_cli.py params set /turtlesim:background_r 255
    $ python3 ros2_cli.py params set /turtlesim:background_g 0

  actions list
    List all available action servers.
    $ python3 ros2_cli.py actions list

  actions details <action>
    Get action details including goal, result, and feedback fields.
    $ python3 ros2_cli.py actions details /turtle1/rotate_absolute

  actions send <action> <json_goal>
    Send an action goal and wait for the result.
    $ python3 ros2_cli.py actions send /turtle1/rotate_absolute '{"theta":3.14}'

Output:
    All commands output JSON to stdout.
    Successful results contain relevant data fields.
    Errors contain an "error" field: {"error": "description"}

Examples:
    # Explore the robot system
    python3 ros2_cli.py version
    python3 ros2_cli.py topics list
    python3 ros2_cli.py nodes list
    python3 ros2_cli.py services list

    # Move turtlesim forward 2 sec then stop
    python3 ros2_cli.py topics publish-sequence /turtle1/cmd_vel \
      '[{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":0}}]' \
      '[2.0, 0.5]'

    # Read LiDAR data
    python3 ros2_cli.py topics subscribe /scan --duration 3

    # Change turtlesim background to red
    python3 ros2_cli.py params set /turtlesim:background_r 255
    python3 ros2_cli.py params set /turtlesim:background_g 0
    python3 ros2_cli.py params set /turtlesim:background_b 0
"""

import argparse
import json
import os
import sys
import time
import threading

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.action import ActionClient
    from rclpy.qos import qos_profile_system_default
except ImportError:
    print(json.dumps({"error": "rclpy not installed. Run: pip install rclpy (or source ROS 2)"}))
    sys.exit(1)

from rcl_interfaces.msg import Parameter, ParameterValue
from rcl_interfaces.srv import GetParameters, SetParameters, ListParameters
from rosidl_runtime_py import import_message


def get_msg_type(type_str):
    if not type_str:
        return None
    
    formats = []
    
    if '/msg/' in type_str:
        pkg, msg_name = type_str.split('/msg/', 1)
        msg_name = msg_name.strip()
        formats = [
            f"{pkg}.msg.{msg_name}",
        ]
    elif '/' in type_str:
        pkg, msg_name = type_str.rsplit('/', 1)
        formats = [
            f"{pkg}.msg.{msg_name}",
        ]
    else:
        formats = [type_str]
    
    for fmt in formats:
        try:
            return import_message(fmt)
        except Exception:
            continue
    
    for fmt in formats:
        try:
            parts = fmt.split('.')
            module = __import__(parts[0])
            for part in parts[1:]:
                module = getattr(module, part)
            return module
        except Exception:
            continue
    
    return None


def get_msg_error(msg_type):
    """Generate helpful error message when message type cannot be loaded."""
    ros_distro = os.environ.get('ROS_DISTRO', '')
    suggestions = []
    base_type = msg_type.split('/')[-1] if '/' in msg_type else msg_type
    common_types = {
        'twist': 'geometry_msgs/msg/Twist',
        'twiststamped': 'geometry_msgs/msg/TwistStamped',
        'pose': 'turtlesim/msg/Pose',
        'odom': 'nav_msgs/msg/Odometry',
        'laserscan': 'sensor_msgs/msg/LaserScan',
        'image': 'sensor_msgs/msg/Image',
        'battery': 'sensor_msgs/msg/BatteryState',
        'jointstate': 'sensor_msgs/msg/JointState',
        'imu': 'sensor_msgs/msg/Imu',
    }
    if base_type.lower() in common_types:
        suggestions.append(common_types[base_type.lower()])
    
    hint = "ROS 2 message types use /msg/ format (e.g., geometry_msgs/msg/Twist)"
    if ros_distro:
        hint += f". Ensure ROS 2 workspace is built: cd ~/ros2_ws && colcon build && source install/setup.bash"
    else:
        hint += ". Ensure ROS 2 environment is sourced: source /opt/ros/<distro>/setup.bash"
    
    return {
        "error": f"Unknown message type: {msg_type}",
        "hint": hint,
        "suggestions": suggestions if suggestions else None,
        "ros_distro": ros_distro if ros_distro else None,
        "troubleshooting": [
            "1. Source ROS 2: source /opt/ros/<distro>/setup.bash",
            "2. If using custom messages, build workspace: cd ~/ros2_ws && colcon build",
            "3. Verify: python3 -c 'from geometry_msgs.msg import Twist; print(Twist)'"
        ]
    }


def msg_to_dict(msg):
    result = {}
    for field in msg.get_fields_and_field_types():
        value = getattr(msg, field, None)
        if value is None:
            continue
        if hasattr(value, 'get_fields_and_field_types'):
            result[field] = msg_to_dict(value)
        elif isinstance(value, (list, tuple)):
            result[field] = [msg_to_dict(v) if hasattr(v, 'get_fields_and_field_types') else v for v in value]
        else:
            result[field] = value
    return result


def dict_to_msg(msg_type, data):
    msg = msg_type()
    for key, value in data.items():
        if hasattr(msg, key):
            if isinstance(value, dict):
                setattr(msg, key, dict_to_msg(getattr(msg, key).__class__, value))
            else:
                setattr(msg, key, value)
    return msg


def output(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


class ROS2CLI(Node):
    def __init__(self, node_name='ros2_cli'):
        super().__init__(node_name)

    def get_topic_names(self):
        return self.get_topic_names_and_types()

    def get_service_names(self):
        return self.get_service_names_and_types()


def get_msg_fields(msg_type_str):
    try:
        msg_class = get_msg_type(msg_type_str)
        if msg_class is None:
            return {}
        msg = msg_class()
        return msg_to_dict(msg)
    except Exception as e:
        return {}


def parse_node_param(name):
    if ':' in name:
        parts = name.split(':', 1)
        return parts[0], parts[1]
    return name, None


def cmd_version(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        version = rclpy.utilities.get_domain_id()
        distro = os.environ.get('ROS_DISTRO', 'unknown')
        result = {"version": "2", "distro": distro, "domain_id": version}
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


VELOCITY_TOPICS = ["/cmd_vel", "/cmd_vel_nav", "/cmd_vel_raw", "/mobile_base/commands/velocity"]
VELOCITY_TYPES = ["geometry_msgs/Twist", "geometry_msgs/TwistStamped"]


def find_velocity_topic(node):
    """Find the velocity command topic and its type."""
    topics = node.get_topic_names()
    for topic_name, types in topics:
        if topic_name in VELOCITY_TOPICS:
            for msg_type in types:
                if msg_type in VELOCITY_TYPES:
                    return topic_name, msg_type
    for topic_name, types in topics:
        if "cmd_vel" in topic_name.lower():
            return topic_name, types[0] if types else None
    return None, None


def cmd_estop(args):
    """Emergency stop for mobile robots - auto-detect and publish zero velocity.

    This command is designed for mobile base robots (differential drive, omnidirectional, etc.)
    that use velocity commands for movement. It will NOT work for robotic arms or manipulators.

    The command:
    1. Searches for common velocity topics (/cmd_vel, /cmd_vel_nav, etc.)
    2. Auto-detects message type (Twist or TwistStamped)
    3. Publishes zero velocity to stop all movement
    4. Only works for mobile robots with velocity-based control

    Not applicable for: robot arms, grippers, or position-controlled robots.
    """
    rclpy.init()
    node = ROS2CLI("estop")

    topic, msg_type = find_velocity_topic(node)

    if not topic:
        rclpy.shutdown()
        return output({
            "error": "Could not find velocity command topic",
            "hint": "This command is for mobile robots only (not arms). Ensure the robot has a /cmd_vel topic."
        })

    msg_class = get_msg_type(msg_type)
    if not msg_class:
        for t in VELOCITY_TYPES:
            msg_class = get_msg_type(t)
            if msg_class:
                msg_type = t
                break

    if not msg_class:
        rclpy.shutdown()
        return output({"error": f"Could not load message type: {msg_type}"})

    pub = node.create_publisher(msg_class, topic, 10)
    msg = msg_class()

    if hasattr(msg, "twist"):
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.twist.linear.x = 0.0
        msg.twist.linear.y = 0.0
        msg.twist.linear.z = 0.0
        msg.twist.angular.x = 0.0
        msg.twist.angular.y = 0.0
        msg.twist.angular.z = 0.0
    else:
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0

    pub.publish(msg)
    time.sleep(0.1)
    rclpy.shutdown()
    output({
        "success": True,
        "topic": topic,
        "type": msg_type,
        "message": "Emergency stop activated (mobile robot stopped)"
    })


def cmd_topics_list(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        topics = node.get_topic_names()
        topic_list = []
        type_list = []
        for name, types in topics:
            topic_list.append(name)
            type_list.append(types[0] if types else "")
        result = {"topics": topic_list, "types": type_list, "count": len(topic_list)}
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_topics_type(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        topics = node.get_topic_names()
        result = {"topic": args.topic, "type": ""}
        for name, types in topics:
            if name == args.topic:
                result["type"] = types[0] if types else ""
                break
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_topics_details(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        publishers = node.get_publisher_names_and_types_by_node(args.node)
        subscribers = node.get_subscriber_names_and_types_by_node(args.node)
        topic_types = node.get_topic_names_and_types()
        
        result = {"topic": args.topic, "type": "", "publishers": [], "subscribers": []}
        
        for name, types in topic_types:
            if name == args.topic:
                result["type"] = types[0] if types else ""
                break
        
        for node_name, topics in publishers:
            for t in topics:
                if t[0] == args.topic:
                    result["publishers"].append(node_name)
        
        for node_name, topics in subscribers:
            for t in topics:
                if t[0] == args.topic:
                    result["subscribers"].append(node_name)
        
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_topics_message(args):
    try:
        fields = get_msg_fields(args.message_type)
        output({"message_type": args.message_type, "structure": fields})
    except Exception as e:
        output({"error": str(e)})


class TopicSubscriber(Node):
    def __init__(self, topic, msg_type):
        super().__init__('subscriber')
        self.msg_type = msg_type
        self.messages = []
        self.lock = threading.Lock()
        
        msg_class = get_msg_type(msg_type)
        if msg_class:
            self.sub = self.create_subscription(
                msg_class, topic, self.callback, qos_profile_system_default
            )
    
    def callback(self, msg):
        with self.lock:
            self.messages.append(msg_to_dict(msg))


def cmd_topics_subscribe(args):
    try:
        rclpy.init()
        node = ROS2CLI("temp")
        
        msg_type = args.msg_type
        if not msg_type:
            topics = node.get_topic_names()
            for name, types in topics:
                if name == args.topic:
                    msg_type = types[0] if types else None
                    break
            if not msg_type:
                rclpy.shutdown()
                return output({"error": f"Could not detect message type for topic: {args.topic}"})
        
        subscriber = TopicSubscriber(args.topic, msg_type)
        
        if args.duration:
            executor = rclpy.executors.SingleThreadedExecutor()
            executor.add_node(subscriber)
            end_time = time.time() + args.duration
            while time.time() < end_time and len(subscriber.messages) < (args.max_messages or 100):
                executor.wait_once(timeout_sec=0.1)
            
            with subscriber.lock:
                messages = subscriber.messages[:args.max_messages] if args.max_messages else subscriber.messages
            
            rclpy.shutdown()
            output({
                "topic": args.topic,
                "collected_count": len(messages),
                "messages": messages
            })
        else:
            executor = rclpy.executors.SingleThreadedExecutor()
            executor.add_node(subscriber)
            timeout_sec = args.timeout if hasattr(args, 'timeout') else 5.0
            end_time = time.time() + timeout_sec
            
            while time.time() < end_time:
                executor.wait_once(timeout_sec=0.1)
                with subscriber.lock:
                    if subscriber.messages:
                        msg = subscriber.messages[0]
                        rclpy.shutdown()
                        output({"msg": msg})
                        return
            
            rclpy.shutdown()
            output({"error": "Timeout waiting for message"})
    except Exception as e:
        output({"error": str(e)})


class TopicPublisher(Node):
    def __init__(self, topic, msg_type):
        super().__init__('publisher')
        self.topic = topic
        self.msg_type = msg_type
        
        msg_class = get_msg_type(msg_type)
        if msg_class:
            self.pub = self.create_publisher(msg_class, topic, qos_profile_system_default)


def cmd_topics_publish(args):
    try:
        msg_data = json.loads(args.msg)
    except json.JSONDecodeError as e:
        return output({"error": f"Invalid JSON message: {e}"})
    
    try:
        rclpy.init()
        
        msg_type = args.msg_type
        topic = args.topic
        
        if not msg_type:
            node = ROS2CLI("temp")
            topics = node.get_topic_names()
            for name, types in topics:
                if name == topic:
                    msg_type = types[0] if types else None
                    break
            if not msg_type:
                rclpy.shutdown()
                return output({"error": f"Could not detect message type for topic: {topic}"})
        
        msg_class = get_msg_type(msg_type)
        if not msg_class:
            rclpy.shutdown()
            return output(get_msg_error(msg_type))
        
        publisher = TopicPublisher(topic, msg_type)
        
        if publisher.pub is None:
            rclpy.shutdown()
            return output({"error": f"Failed to create publisher for {msg_type}"})
        
        msg = dict_to_msg(msg_class, msg_data)
        
        rate = getattr(args, "rate", None) or 10.0
        duration = getattr(args, "duration", None)
        interval = 1.0 / rate
        
        if duration and duration > 0:
            published = 0
            end_time = time.time() + duration
            while time.time() < end_time:
                publisher.pub.publish(msg)
                published += 1
                remaining = end_time - time.time()
                if remaining > 0:
                    time.sleep(min(interval, remaining))
            rclpy.shutdown()
            output({"success": True, "topic": topic, "msg_type": msg_type,
                    "duration": duration, "rate": rate, "published_count": published})
        else:
            publisher.pub.publish(msg)
            time.sleep(0.1)
            rclpy.shutdown()
            output({"success": True, "topic": topic, "msg_type": msg_type})
    except Exception as e:
        output({"error": str(e)})


def cmd_topics_publish_sequence(args):
    try:
        messages = json.loads(args.messages)
        durations = json.loads(args.durations)
    except json.JSONDecodeError as e:
        return output({"error": f"Invalid JSON: {e}"})
    if len(messages) != len(durations):
        return output({"error": "messages and durations must have same length"})

    try:
        rclpy.init()
        
        msg_type = args.msg_type
        topic = args.topic
        
        if not msg_type:
            node = ROS2CLI("temp")
            topics = node.get_topic_names()
            for name, types in topics:
                if name == topic:
                    msg_type = types[0] if types else None
                    break
            if not msg_type:
                rclpy.shutdown()
                return output({"error": f"Could not detect message type for topic: {topic}"})
        
        msg_class = get_msg_type(msg_type)
        if not msg_class:
            rclpy.shutdown()
            return output(get_msg_error(msg_type))
        
        publisher = TopicPublisher(topic, msg_type)
        
        if publisher.pub is None:
            rclpy.shutdown()
            return output({"error": f"Failed to create publisher for {msg_type}"})
        
        rate = getattr(args, "rate", None) or 10.0
        interval = 1.0 / rate
        
        total_published = 0
        for msg_data, dur in zip(messages, durations):
            msg = dict_to_msg(msg_class, msg_data)
            if dur > 0:
                end_time = time.time() + dur
                while time.time() < end_time:
                    publisher.pub.publish(msg)
                    total_published += 1
                    remaining = end_time - time.time()
                    if remaining > 0:
                        time.sleep(min(interval, remaining))
            else:
                publisher.pub.publish(msg)
                total_published += 1
        
        rclpy.shutdown()
        output({"success": True, "published_count": total_published, "topic": topic,
                "rate": rate})
    except Exception as e:
        output({"error": str(e)})


def cmd_services_list(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        services = node.get_service_names()
        service_list = []
        type_list = []
        for name, types in services:
            service_list.append(name)
            type_list.append(types[0] if types else "")
        result = {"services": service_list, "types": type_list, "count": len(service_list)}
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_services_type(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        services = node.get_service_names()
        result = {"service": args.service, "type": ""}
        for name, types in services:
            if name == args.service:
                result["type"] = types[0] if types else ""
                break
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_services_details(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        services = node.get_service_names()
        
        result = {"service": args.service, "type": "", "request": {}, "response": {}}
        
        for name, types in services:
            if name == args.service:
                result["type"] = types[0] if types else ""
                break
        
        if result["type"]:
            service_type = result["type"]
            if '/' in service_type:
                pkg, name = service_type.rsplit('/', 1)
                req_type = f"{pkg}/srv/{name}Request"
                resp_type = f"{pkg}/srv/{name}Response"
                try:
                    req_fields = get_msg_fields(req_type)
                    result["request"] = req_fields
                except Exception:
                    pass
                try:
                    resp_fields = get_msg_fields(resp_type)
                    result["response"] = resp_fields
                except Exception:
                    pass
        
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_services_call(args):
    try:
        request_data = json.loads(args.request)
    except json.JSONDecodeError as e:
        return output({"error": f"Invalid JSON request: {e}"})
    
    try:
        rclpy.init()
        node = ROS2CLI()
        
        services = node.get_service_names()
        service_type = None
        for name, types in services:
            if name == args.service:
                service_type = types[0] if types else ""
                break
        
        if not service_type:
            rclpy.shutdown()
            return output({"error": f"Service not found: {args.service}"})
        
        if '/' in service_type:
            pkg, name = service_type.rsplit('/', 1)
            srv_type = f"{pkg}.srv.{name}"
            try:
                srv_class = import_message(srv_type)
            except Exception as e:
                rclpy.shutdown()
                return output({"error": f"Cannot load service type: {e}"})
            
            client = node.create_client(srv_class, args.service)
            
            if not client.wait_for_service(timeout_sec=5.0):
                rclpy.shutdown()
                return output({"error": f"Service not available: {args.service}"})
            
            request = dict_to_msg(srv_class.Request, request_data)
            future = client.call_async(request)
            
            timeout = args.timeout if hasattr(args, 'timeout') else 5.0
            end_time = time.time() + timeout
            
            while time.time() < end_time and not future.done():
                rclpy.spin_once(node, timeout_sec=0.1)
            
            if future.done():
                result_msg = future.result()
                result_dict = msg_to_dict(result_msg)
                rclpy.shutdown()
                output({"service": args.service, "success": True, "result": result_dict})
            else:
                rclpy.shutdown()
                output({"service": args.service, "success": False, "error": "Service call timeout"})
        else:
            rclpy.shutdown()
            output({"error": "Invalid service type"})
    except Exception as e:
        output({"error": str(e)})


def cmd_nodes_list(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        names = [n for n, _ in node.get_node_names_and_types()]
        result = {"nodes": names, "count": len(names)}
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_nodes_details(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        
        publishers = node.get_publisher_names_and_types_by_node(args.node)
        subscribers = node.get_subscriber_names_and_types_by_node(args.node)
        services = node.get_service_names_and_types_by_node(args.node)
        
        result = {
            "node": args.node,
            "publishers": [t[0] for node_name, topics in publishers for t in topics],
            "subscribers": [t[0] for node_name, topics in subscribers for t in topics],
            "services": [s[0] for node_name, srvs in services for s in srvs]
        }
        
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_params_list(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        
        node_name, param_name = parse_node_param(args.node)
        if not node_name.startswith('/'):
            node_name = '/' + node_name
        
        service_name = f"{node_name}/list_parameters"
        
        client = node.create_client(ListParameters, service_name)
        
        if not client.wait_for_service(timeout_sec=5.0):
            rclpy.shutdown()
            return output({"error": f"Parameter service not available for {node_name}"})
        
        request = ListParameters.Request()
        future = client.call_async(request)
        
        end_time = time.time() + 5.0
        while time.time() < end_time and not future.done():
            rclpy.spin_once(node, timeout_sec=0.1)
        
        if future.done():
            result = future.result()
            names = result.result.names if result.result else []
            formatted = [f"{node_name}:{n}" for n in names]
            rclpy.shutdown()
            output({"node": node_name, "parameters": formatted, "count": len(formatted)})
        else:
            rclpy.shutdown()
            output({"error": "Timeout listing parameters"})
    except Exception as e:
        output({"error": str(e)})


def cmd_params_get(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        
        full_name = args.name
        if ':' in full_name:
            node_name, param_name = full_name.split(':', 1)
        else:
            node_name = full_name
            param_name = None
        
        if not node_name.startswith('/'):
            node_name = '/' + node_name
        
        service_name = f"{node_name}/get_parameters"
        
        client = node.create_client(GetParameters, service_name)
        
        if not client.wait_for_service(timeout_sec=5.0):
            rclpy.shutdown()
            return output({"error": f"Parameter service not available for {node_name}"})
        
        request = GetParameters.Request()
        request.names = [param_name] if param_name else []
        
        future = client.call_async(request)
        
        end_time = time.time() + 5.0
        while time.time() < end_time and not future.done():
            rclpy.spin_once(node, timeout_sec=0.1)
        
        if future.done():
            result = future.result()
            values = result.values if result.values else []
            value_str = ""
            if values:
                v = values[0]
                if v.type == 1:
                    value_str = str(v.bool_value)
                elif v.type == 2:
                    value_str = str(v.integer_value)
                elif v.type == 3:
                    value_str = str(v.double_value)
                elif v.type == 4:
                    value_str = v.string_value
                elif v.type in [5, 6, 7, 8, 9]:
                    value_str = str(v)
            rclpy.shutdown()
            output({"name": args.name, "value": value_str, "exists": bool(value_str)})
        else:
            rclpy.shutdown()
            output({"error": "Timeout getting parameter"})
    except Exception as e:
        output({"error": str(e)})


def cmd_params_set(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        
        full_name = args.name
        if ':' in full_name:
            node_name, param_name = full_name.split(':', 1)
        else:
            node_name = full_name
            param_name = None
        
        if not node_name.startswith('/'):
            node_name = '/' + node_name
        
        service_name = f"{node_name}/set_parameters"
        
        client = node.create_client(SetParameters, service_name)
        
        if not client.wait_for_service(timeout_sec=5.0):
            rclpy.shutdown()
            return output({"error": f"Parameter service not available for {node_name}"})
        
        request = SetParameters.Request()
        
        param = Parameter()
        param.name = param_name
        
        pv = ParameterValue()
        try:
            if '.' in args.value:
                pv.type = 3
                pv.double_value = float(args.value)
            else:
                try:
                    pv.type = 2
                    pv.integer_value = int(args.value)
                except Exception:
                    pv.type = 4
                    pv.string_value = args.value
        except Exception:
            pv.type = 4
            pv.string_value = args.value
        
        param.value = pv
        request.parameters = [param]
        
        future = client.call_async(request)
        
        end_time = time.time() + 5.0
        while time.time() < end_time and not future.done():
            rclpy.spin_once(node, timeout_sec=0.1)
        
        rclpy.shutdown()
        if future.done():
            output({"name": args.name, "value": args.value, "success": True})
        else:
            output({"error": "Timeout setting parameter"})
    except Exception as e:
        output({"error": str(e)})


def cmd_actions_list(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        
        topics = node.get_topic_names_and_types()
        actions = []
        seen = set()
        
        for name, types in topics:
            for t in types:
                if '/action/' in t:
                    action_name = name.rsplit('/goal', 1)[0].rsplit('/cancel', 1)[0].rsplit('/feedback', 1)[0].rsplit('/result', 1)[0]
                    if action_name not in seen:
                        seen.add(action_name)
                        actions.append(action_name)
        
        rclpy.shutdown()
        output({"actions": actions, "count": len(actions)})
    except Exception as e:
        output({"error": str(e)})


def cmd_actions_details(args):
    try:
        rclpy.init()
        node = ROS2CLI()
        
        topics = node.get_topic_names_and_types()
        
        result = {"action": args.action, "action_type": "", "goal": {}, "result": {}, "feedback": {}}
        
        action_type = ""
        for name, types in topics:
            if name == args.action + "/goal":
                for t in types:
                    if '/action/' in t:
                        action_type = t.replace('/Goal', '').replace('/goal', '')
                        break
                if action_type:
                    break
            elif name == args.action:
                for t in types:
                    if '/action/' in t:
                        action_type = t.replace('/Goal', '').replace('/goal', '')
                        break
                if action_type:
                    break
        
        result["action_type"] = action_type
        
        if action_type:
            goal_type = action_type + "/Goal"
            result_type = action_type + "/Result"
            feedback_type = action_type + "/Feedback"
            
            try:
                result["goal"] = get_msg_fields(goal_type)
            except Exception:
                pass
            try:
                result["result"] = get_msg_fields(result_type)
            except Exception:
                pass
            try:
                result["feedback"] = get_msg_fields(feedback_type)
            except Exception:
                pass
        
        rclpy.shutdown()
        output(result)
    except Exception as e:
        output({"error": str(e)})


def cmd_actions_send(args):
    try:
        goal_data = json.loads(args.goal)
    except json.JSONDecodeError as e:
        return output({"error": f"Invalid JSON goal: {e}"})
    
    try:
        rclpy.init()
        node = ROS2CLI()
        
        topics = node.get_topic_names_and_types()
        
        action_type = None
        for name, types in topics:
            if name == args.action + "/goal":
                for t in types:
                    if '/action/' in t:
                        action_type = t.replace('/Goal', '').replace('/goal', '')
                        break
                if action_type:
                    break
        
        if not action_type:
            rclpy.shutdown()
            return output({"error": f"Action server not found: {args.action}"})
        
        try:
            action_class = import_message(f"{action_type}/action/{action_type.split('/')[-1]}")
        except Exception as e:
            rclpy.shutdown()
            return output({"error": f"Cannot load action type: {e}"})
        
        client = ActionClient(node, action_class, args.action)
        
        if not client.wait_for_server(timeout_sec=5.0):
            rclpy.shutdown()
            return output({"error": f"Action server not available: {args.action}"})
        
        goal_msg = dict_to_msg(action_class.Goal, goal_data)
        
        goal_id = f"goal_{int(time.time() * 1000)}"
        
        future = client.send_goal_async(goal_msg)
        
        timeout = args.timeout if hasattr(args, 'timeout') else 5.0
        end_time = time.time() + timeout
        
        while time.time() < end_time and not future.done():
            rclpy.spin_once(node, timeout_sec=0.1)
        
        if not future.done():
            rclpy.shutdown()
            output({"action": args.action, "success": False, "error": "Timeout waiting for goal acceptance"})
            return
        
        goal_handle = future.result()
        
        if not goal_handle.accepted:
            rclpy.shutdown()
            output({"action": args.action, "success": False, "error": "Goal rejected"})
            return
        
        result_future = goal_handle.get_result_async()
        
        end_time = time.time() + timeout
        while time.time() < end_time and not result_future.done():
            rclpy.spin_once(node, timeout_sec=0.1)
        
        if result_future.done():
            result_msg = result_future.result().result
            result_dict = msg_to_dict(result_msg)
            rclpy.shutdown()
            output({"action": args.action, "success": True,
                    "goal_id": goal_id, "result": result_dict})
        else:
            rclpy.shutdown()
            output({"action": args.action, "success": False, "error": f"Timeout after {timeout}s"})
    except Exception as e:
        output({"error": str(e)})


def build_parser():
    parser = argparse.ArgumentParser(description="ROS 2 Skill CLI - Control ROS 2 robots directly via rclpy")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("version", help="Detect ROS 2 version")

    estop = sub.add_parser("estop", help="Emergency stop for mobile robots (publishes zero velocity)")
    estop.add_argument("--topic", dest="topic", default=None, help="Custom velocity topic (default: auto-detect)")

    topics = sub.add_parser("topics", help="Topic operations")
    tsub = topics.add_subparsers(dest="subcommand")
    tsub.add_parser("list", help="List all topics")
    p = tsub.add_parser("type", help="Get topic message type")
    p.add_argument("topic")
    p = tsub.add_parser("details", help="Get topic details")
    p.add_argument("topic")
    p = tsub.add_parser("message", help="Get message structure")
    p.add_argument("message_type")
    p = tsub.add_parser("subscribe", help="Subscribe to a topic")
    p.add_argument("topic", nargs="?")
    p.add_argument("--msg-type", dest="msg_type", default=None, help="Message type (auto-detected if not provided)")
    p.add_argument("--duration", type=float, default=None, help="Subscribe for duration (seconds)")
    p.add_argument("--max-messages", type=int, default=100, help="Max messages to collect")
    p = tsub.add_parser("publish", help="Publish a message")
    p.add_argument("topic", nargs="?")
    p.add_argument("msg", nargs="?", help="JSON message")
    p.add_argument("--msg-type", dest="msg_type", default=None, help="Message type (auto-detected if not provided)")
    p.add_argument("--duration", type=float, default=None, help="Publish repeatedly for duration (seconds)")
    p.add_argument("--rate", type=float, default=10.0, help="Publish rate in Hz (default: 10)")
    p = tsub.add_parser("publish-sequence", help="Publish message sequence with delays")
    p.add_argument("topic", nargs="?")
    p.add_argument("messages", nargs="?", help="JSON array of messages")
    p.add_argument("durations", nargs="?", help="JSON array of durations in seconds (message is repeated during each)")
    p.add_argument("--msg-type", dest="msg_type", default=None, help="Message type (auto-detected if not provided)")
    p.add_argument("--rate", type=float, default=10.0, help="Publish rate in Hz (default: 10)")

    services = sub.add_parser("services", help="Service operations")
    ssub = services.add_subparsers(dest="subcommand")
    ssub.add_parser("list", help="List all services")
    p = ssub.add_parser("type", help="Get service type")
    p.add_argument("service")
    p = ssub.add_parser("details", help="Get service details")
    p.add_argument("service")
    p = ssub.add_parser("call", help="Call a service")
    p.add_argument("service")
    p.add_argument("request", help="JSON request")

    nodes = sub.add_parser("nodes", help="Node operations")
    nsub = nodes.add_subparsers(dest="subcommand")
    nsub.add_parser("list", help="List all nodes")
    p = nsub.add_parser("details", help="Get node details")
    p.add_argument("node")

    params = sub.add_parser("params", help="Parameter operations")
    psub = params.add_subparsers(dest="subcommand")
    p = psub.add_parser("list", help="List parameters for a node")
    p.add_argument("node")
    p = psub.add_parser("get", help="Get parameter value")
    p.add_argument("name")
    p = psub.add_parser("set", help="Set parameter value")
    p.add_argument("name")
    p.add_argument("value")

    actions = sub.add_parser("actions", help="Action operations")
    asub = actions.add_subparsers(dest="subcommand")
    asub.add_parser("list", help="List all actions")
    p = asub.add_parser("details", help="Get action details")
    p.add_argument("action")
    p = asub.add_parser("send", help="Send action goal")
    p.add_argument("action")
    p.add_argument("goal", help="JSON goal")

    return parser


DISPATCH = {
    ("version", None): cmd_version,
    ("estop", None): cmd_estop,
    ("topics", "list"): cmd_topics_list,
    ("topics", "type"): cmd_topics_type,
    ("topics", "details"): cmd_topics_details,
    ("topics", "message"): cmd_topics_message,
    ("topics", "subscribe"): cmd_topics_subscribe,
    ("topics", "publish"): cmd_topics_publish,
    ("topics", "publish-sequence"): cmd_topics_publish_sequence,
    ("services", "list"): cmd_services_list,
    ("services", "type"): cmd_services_type,
    ("services", "details"): cmd_services_details,
    ("services", "call"): cmd_services_call,
    ("nodes", "list"): cmd_nodes_list,
    ("nodes", "details"): cmd_nodes_details,
    ("params", "list"): cmd_params_list,
    ("params", "get"): cmd_params_get,
    ("params", "set"): cmd_params_set,
    ("actions", "list"): cmd_actions_list,
    ("actions", "details"): cmd_actions_details,
    ("actions", "send"): cmd_actions_send,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    key = (args.command, getattr(args, "subcommand", None))
    handler = DISPATCH.get(key)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
