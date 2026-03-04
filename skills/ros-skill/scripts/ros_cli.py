#!/usr/bin/env python3
"""ROS Skill - Standalone CLI tool for controlling ROS robots via rosbridge WebSocket.

Requires: pip install websocket-client

Global Options:
    --ip IP            Rosbridge IP address (default: 127.0.0.1)
    --port PORT        Rosbridge port number (default: 9090)
    --timeout SECONDS  Connection/request timeout (default: 5.0)

Commands:

  connect
    Test connectivity to rosbridge (ping, port check, WebSocket handshake).
    $ python ros_cli.py connect
    $ python ros_cli.py --ip 10.0.0.5 --port 9090 connect

  version
    Detect ROS version and distro running on the robot.
    $ python ros_cli.py version

  topics list
    List all active topics with their message types.
    $ python ros_cli.py topics list

  topics type <topic>
    Get the message type of a specific topic.
    $ python ros_cli.py topics type /cmd_vel
    $ python ros_cli.py topics type /turtle1/pose

  topics details <topic>
    Get topic details including type, publishers, and subscribers.
    $ python ros_cli.py topics details /cmd_vel

  topics message <message_type>
    Get the field structure of a message type.
    $ python ros_cli.py topics message geometry_msgs/Twist
    $ python ros_cli.py topics message sensor_msgs/LaserScan

  topics subscribe <topic> <msg_type> [--duration SEC] [--max-messages N]
    Subscribe to a topic. Without --duration, returns the first message and exits.
    With --duration, collects messages for the specified time.
    --duration SECONDS   Collect messages for this duration (default: single message)
    --max-messages N     Max messages to collect during duration (default: 100)
    $ python ros_cli.py topics subscribe /turtle1/pose turtlesim/Pose
    $ python ros_cli.py topics subscribe /odom nav_msgs/Odometry --duration 10 --max-messages 50
    $ python ros_cli.py topics subscribe /scan sensor_msgs/LaserScan --timeout 3
    $ python ros_cli.py topics subscribe /imu/data sensor_msgs/Imu --duration 5 --max-messages 20

  topics publish <topic> <msg_type> <json_message> [--duration SEC] [--rate HZ]
    Publish a message to a topic.
    Without --duration: sends once (single-shot).
    With --duration: publishes repeatedly at --rate Hz for the specified seconds.
    --duration SECONDS   Publish repeatedly for this duration
    --rate HZ            Publish rate (default: 10 Hz)
    $ python ros_cli.py topics publish /turtle1/cmd_vel geometry_msgs/Twist \
        '{"linear":{"x":2.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}'
    $ python ros_cli.py topics publish /cmd_vel geometry_msgs/Twist \
        '{"linear":{"x":1.0,"y":0,"z":0},"angular":{"x":0,"y":0,"z":0}}' --duration 3

  topics publish-sequence <topic> <msg_type> <json_messages> <json_durations> [--rate HZ]
    Publish a sequence of messages. Each message is repeatedly published at --rate Hz
    for its corresponding duration. This keeps velocity commands active for the full duration.
    <json_messages>   JSON array of messages to publish in order
    <json_durations>  JSON array of durations (seconds) for each message (must match length)
    --rate HZ         Publish rate (default: 10 Hz)
    $ python ros_cli.py topics publish-sequence /turtle1/cmd_vel geometry_msgs/Twist \
        '[{"linear":{"x":1.0},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":0}}]' \
        '[3.0, 0.5]'

  services list
    List all available services.
    $ python ros_cli.py services list

  services type <service>
    Get the type of a specific service.
    $ python ros_cli.py services type /rosapi/topics

  services details <service>
    Get service details including type, request fields, and response fields.
    $ python ros_cli.py services details /rosapi/topics

  services call <service> <service_type> <json_request>
    Call a service with a JSON request payload.
    $ python ros_cli.py services call /reset std_srvs/Empty '{}'
    $ python ros_cli.py services call /spawn turtlesim/Spawn \
        '{"x":3.0,"y":3.0,"theta":0.0,"name":"turtle2"}'

  nodes list
    List all active nodes.
    $ python ros_cli.py nodes list

  nodes details <node>
    Get node details including publishers, subscribers, and services.
    $ python ros_cli.py nodes details /turtlesim

  params list <node>                                          (ROS 2 only)
    List all parameters for a node.
    $ python ros_cli.py params list /turtlesim

  params get <node:param_name>                                (ROS 2 only)
    Get a parameter value. Format: /node_name:parameter_name
    $ python ros_cli.py params get /turtlesim:background_r
    $ python ros_cli.py params get /turtlesim:background_b

  params set <node:param_name> <value>                        (ROS 2 only)
    Set a parameter value. Format: /node_name:parameter_name
    $ python ros_cli.py params set /turtlesim:background_r 255
    $ python ros_cli.py params set /turtlesim:background_g 0

  actions list                                                (ROS 2 only)
    List all available action servers.
    $ python ros_cli.py actions list

  actions details <action>                                    (ROS 2 only)
    Get action details including goal, result, and feedback fields.
    $ python ros_cli.py actions details /turtle1/rotate_absolute

  actions send <action> <action_type> <json_goal>             (ROS 2 only)
    Send an action goal and wait for the result.
    $ python ros_cli.py actions send /turtle1/rotate_absolute \
        turtlesim/action/RotateAbsolute '{"theta":3.14}'

Output:
    All commands output JSON to stdout.
    Successful results contain relevant data fields.
    Errors contain an "error" field: {"error": "description"}

Examples:
    # Connect to a remote robot and explore
    python ros_cli.py --ip 10.0.0.5 connect
    python ros_cli.py --ip 10.0.0.5 topics list
    python ros_cli.py --ip 10.0.0.5 nodes list

    # Move turtlesim forward 2 sec then stop
    python ros_cli.py topics publish-sequence /turtle1/cmd_vel geometry_msgs/Twist \
      '[{"linear":{"x":2},"angular":{"z":0}},{"linear":{"x":0},"angular":{"z":0}}]' \
      '[2.0, 0.5]'

    # Read LiDAR data
    python ros_cli.py topics subscribe /scan sensor_msgs/LaserScan --timeout 3

    # Change turtlesim background to red (ROS 2)
    python ros_cli.py params set /turtlesim:background_r 255
    python ros_cli.py params set /turtlesim:background_g 0
    python ros_cli.py params set /turtlesim:background_b 0
"""

import argparse
import json
import socket
import subprocess
import sys
import time
import platform

try:
    import websocket
except ImportError:
    print(json.dumps({"error": "websocket-client not installed. Run: pip install websocket-client"}))
    sys.exit(1)


# ---------------------------------------------------------------------------
# WebSocket helpers
# ---------------------------------------------------------------------------

def ws_connect(ip, port, timeout=5.0):
    """Create a WebSocket connection to rosbridge."""
    try:
        url = f"ws://{ip}:{port}"
        ws = websocket.create_connection(url, timeout=timeout)
        return ws, None
    except Exception as e:
        return None, str(e)


def ws_request(ws, message, timeout=5.0):
    """Send a request and wait for a response."""
    try:
        ws.send(json.dumps(message))
        ws.settimeout(timeout)
        raw = ws.recv()
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


def ws_subscribe_once(ws, topic, msg_type, timeout=5.0):
    """Subscribe to a topic and return the first message."""
    sub_msg = {"op": "subscribe", "topic": topic, "type": msg_type}
    try:
        ws.send(json.dumps(sub_msg))
        end_time = time.time() + timeout
        while time.time() < end_time:
            ws.settimeout(max(0.5, end_time - time.time()))
            try:
                raw = ws.recv()
                data = json.loads(raw)
                if data.get("op") == "status" and data.get("level") == "error":
                    return {"error": data.get("msg", "Unknown error")}
                if data.get("op") == "publish" and data.get("topic") == topic:
                    ws.send(json.dumps({"op": "unsubscribe", "topic": topic}))
                    return {"msg": data.get("msg", {})}
            except websocket.WebSocketTimeoutException:
                continue
        ws.send(json.dumps({"op": "unsubscribe", "topic": topic}))
        return {"error": "Timeout waiting for message"}
    except Exception as e:
        return {"error": str(e)}


def ws_subscribe_duration(ws, topic, msg_type, duration=5.0, max_messages=100):
    """Subscribe to a topic for a duration and collect messages."""
    sub_msg = {"op": "subscribe", "topic": topic, "type": msg_type}
    try:
        ws.send(json.dumps(sub_msg))
        messages = []
        end_time = time.time() + duration
        while time.time() < end_time and len(messages) < max_messages:
            ws.settimeout(max(0.5, end_time - time.time()))
            try:
                raw = ws.recv()
                data = json.loads(raw)
                if data.get("op") == "publish" and data.get("topic") == topic:
                    messages.append(data.get("msg", {}))
            except websocket.WebSocketTimeoutException:
                continue
        ws.send(json.dumps({"op": "unsubscribe", "topic": topic}))
        return {"topic": topic, "collected_count": len(messages), "messages": messages}
    except Exception as e:
        return {"error": str(e)}


def ping_ip(ip, timeout=2.0):
    """Ping an IP address."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    try:
        result = subprocess.run(
            ["ping", param, "1", timeout_param, str(int(timeout)), ip],
            capture_output=True, text=True, timeout=timeout + 2
        )
        return result.returncode == 0
    except Exception:
        return False


def check_port(ip, port, timeout=2.0):
    """Check if a port is open."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def output(data):
    """Print JSON output to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_connect(args):
    ip, port = args.ip, args.port
    ping_ok = ping_ip(ip)
    port_ok = check_port(ip, port)
    ws, err = ws_connect(ip, port, timeout=args.timeout)
    result = {
        "ip": ip,
        "port": port,
        "ping": ping_ok,
        "port_open": port_ok,
        "websocket": err is None,
    }
    if err:
        result["error"] = err
    if ws:
        ws.close()
    output(result)


def cmd_topics_list(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/topics",
        "type": "rosapi/Topics", "args": {}, "id": "topics"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        v = resp["values"]
        output({"topics": v.get("topics", []), "types": v.get("types", []),
                "count": len(v.get("topics", []))})
    else:
        output(resp)


def cmd_topics_type(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/topic_type",
        "type": "rosapi/TopicType", "args": {"topic": args.topic}, "id": "tt"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        output({"topic": args.topic, "type": resp["values"].get("type", "")})
    else:
        output(resp)


def cmd_topics_details(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    result = {"topic": args.topic, "type": "unknown", "publishers": [], "subscribers": []}
    # type
    r = ws_request(ws, {"op": "call_service", "service": "/rosapi/topic_type",
        "type": "rosapi/TopicType", "args": {"topic": args.topic}, "id": "t1"}, args.timeout)
    if "values" in r:
        result["type"] = r["values"].get("type", "unknown")
    # publishers
    r = ws_request(ws, {"op": "call_service", "service": "/rosapi/publishers",
        "type": "rosapi/Publishers", "args": {"topic": args.topic}, "id": "t2"}, args.timeout)
    if "values" in r:
        result["publishers"] = r["values"].get("publishers", [])
    # subscribers
    r = ws_request(ws, {"op": "call_service", "service": "/rosapi/subscribers",
        "type": "rosapi/Subscribers", "args": {"topic": args.topic}, "id": "t3"}, args.timeout)
    if "values" in r:
        result["subscribers"] = r["values"].get("subscribers", [])
    ws.close()
    output(result)


def cmd_topics_message(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/message_details",
        "type": "rosapi/MessageDetails", "args": {"type": args.message_type}, "id": "md"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        typedefs = resp["values"].get("typedefs", [])
        structure = {}
        for td in typedefs:
            fields = dict(zip(td.get("fieldnames", []), td.get("fieldtypes", [])))
            structure[td.get("type", args.message_type)] = fields
        output({"message_type": args.message_type, "structure": structure})
    else:
        output(resp)


def cmd_topics_subscribe(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    if args.duration:
        result = ws_subscribe_duration(ws, args.topic, args.msg_type,
                                       duration=args.duration, max_messages=args.max_messages or 100)
    else:
        result = ws_subscribe_once(ws, args.topic, args.msg_type, timeout=args.timeout)
    ws.close()
    output(result)


def cmd_topics_publish(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    try:
        msg = json.loads(args.msg)
    except json.JSONDecodeError as e:
        return output({"error": f"Invalid JSON message: {e}"})

    rate = getattr(args, "rate", None) or 10.0
    duration = getattr(args, "duration", None)
    interval = 1.0 / rate

    ws.send(json.dumps({"op": "advertise", "topic": args.topic, "type": args.msg_type}))
    time.sleep(0.1)

    if duration and duration > 0:
        # Repeatedly publish at the given rate for the duration
        published = 0
        end_time = time.time() + duration
        while time.time() < end_time:
            ws.send(json.dumps({"op": "publish", "topic": args.topic, "msg": msg}))
            published += 1
            remaining = end_time - time.time()
            if remaining > 0:
                time.sleep(min(interval, remaining))
        ws.send(json.dumps({"op": "unadvertise", "topic": args.topic}))
        ws.close()
        output({"success": True, "topic": args.topic, "msg_type": args.msg_type,
                "duration": duration, "rate": rate, "published_count": published})
    else:
        # Single-shot publish
        ws.send(json.dumps({"op": "publish", "topic": args.topic, "msg": msg}))
        time.sleep(0.1)
        ws.send(json.dumps({"op": "unadvertise", "topic": args.topic}))
        ws.close()
        output({"success": True, "topic": args.topic, "msg_type": args.msg_type})


def cmd_topics_publish_sequence(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    try:
        messages = json.loads(args.messages)
        durations = json.loads(args.durations)
    except json.JSONDecodeError as e:
        return output({"error": f"Invalid JSON: {e}"})
    if len(messages) != len(durations):
        return output({"error": "messages and durations must have same length"})

    rate = getattr(args, "rate", None) or 10.0
    interval = 1.0 / rate

    ws.send(json.dumps({"op": "advertise", "topic": args.topic, "type": args.msg_type}))
    time.sleep(0.1)
    total_published = 0
    for msg, dur in zip(messages, durations):
        if dur > 0:
            # Repeatedly publish at the given rate for the duration
            end_time = time.time() + dur
            while time.time() < end_time:
                ws.send(json.dumps({"op": "publish", "topic": args.topic, "msg": msg}))
                total_published += 1
                remaining = end_time - time.time()
                if remaining > 0:
                    time.sleep(min(interval, remaining))
        else:
            # duration 0: single-shot
            ws.send(json.dumps({"op": "publish", "topic": args.topic, "msg": msg}))
            total_published += 1
    ws.send(json.dumps({"op": "unadvertise", "topic": args.topic}))
    ws.close()
    output({"success": True, "published_count": total_published, "topic": args.topic,
            "rate": rate})


def cmd_services_list(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/services",
        "type": "rosapi_msgs/srv/Services", "args": {}, "id": "svc"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        services = resp["values"].get("services", [])
        output({"services": services, "count": len(services)})
    else:
        output(resp)


def cmd_services_type(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/service_type",
        "type": "rosapi_msgs/srv/ServiceType", "args": {"service": args.service}, "id": "st"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        output({"service": args.service, "type": resp["values"].get("type", "")})
    else:
        output(resp)


def cmd_services_details(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    result = {"service": args.service, "type": "", "request": {}, "response": {}}

    r = ws_request(ws, {"op": "call_service", "service": "/rosapi/service_type",
        "type": "rosapi_msgs/srv/ServiceType", "args": {"service": args.service}, "id": "sd1"}, args.timeout)
    if "values" in r:
        result["type"] = r["values"].get("type", "")

    if result["type"]:
        r = ws_request(ws, {"op": "call_service", "service": "/rosapi/service_request_details",
            "type": "rosapi_msgs/srv/ServiceRequestDetails",
            "args": {"type": result["type"]}, "id": "sd2"}, args.timeout)
        if "values" in r:
            for td in r["values"].get("typedefs", []):
                result["request"] = dict(zip(td.get("fieldnames", []), td.get("fieldtypes", [])))

        r = ws_request(ws, {"op": "call_service", "service": "/rosapi/service_response_details",
            "type": "rosapi_msgs/srv/ServiceResponseDetails",
            "args": {"type": result["type"]}, "id": "sd3"}, args.timeout)
        if "values" in r:
            for td in r["values"].get("typedefs", []):
                result["response"] = dict(zip(td.get("fieldnames", []), td.get("fieldtypes", [])))
    ws.close()
    output(result)


def cmd_services_call(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    try:
        request = json.loads(args.request)
    except json.JSONDecodeError as e:
        return output({"error": f"Invalid JSON request: {e}"})
    resp = ws_request(ws, {
        "op": "call_service", "service": args.service, "type": args.service_type,
        "args": request, "id": "call"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        output({"service": args.service, "success": resp.get("result", True),
                "result": resp["values"]})
    else:
        output(resp)


def cmd_nodes_list(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/nodes",
        "type": "rosapi/Nodes", "args": {}, "id": "nodes"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        nodes = resp["values"].get("nodes", [])
        output({"nodes": nodes, "count": len(nodes)})
    else:
        output(resp)


def cmd_nodes_details(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/node_details",
        "type": "rosapi/NodeDetails", "args": {"node": args.node}, "id": "nd"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        v = resp["values"]
        output({"node": args.node, "publishers": v.get("publishing", []),
                "subscribers": v.get("subscribing", []), "services": v.get("services", [])})
    else:
        output(resp)


def cmd_params_list(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    node = args.node if args.node.startswith("/") else f"/{args.node}"
    resp = ws_request(ws, {
        "op": "call_service", "service": f"{node}/list_parameters",
        "type": "rcl_interfaces/srv/ListParameters", "args": {}, "id": "pl"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        result_obj = resp["values"].get("result", {})
        names = result_obj.get("names", []) if isinstance(result_obj, dict) else []
        formatted = [f"{node}:{n}" for n in names]
        output({"node": node, "parameters": formatted, "count": len(formatted)})
    else:
        output(resp)


def cmd_params_get(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/get_param",
        "type": "rosapi_msgs/srv/GetParam", "args": {"name": args.name}, "id": "pg"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        value = resp["values"].get("value", "")
        output({"name": args.name, "value": value, "exists": bool(value and value.strip('"'))})
    else:
        output(resp)


def cmd_params_set(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/set_param",
        "type": "rosapi_msgs/srv/SetParam",
        "args": {"name": args.name, "value": args.value}, "id": "ps"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        output({"name": args.name, "value": args.value, "success": True})
    else:
        output(resp)


def cmd_actions_list(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/action_servers",
        "type": "rosapi/ActionServers", "args": {}, "id": "al"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        actions = resp["values"].get("action_servers", [])
        output({"actions": actions, "count": len(actions)})
    else:
        output(resp)


def cmd_actions_details(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    result = {"action": args.action, "action_type": "unknown", "goal": {}, "result": {}, "feedback": {}}

    # Find action type from interfaces
    r = ws_request(ws, {"op": "call_service", "service": "/rosapi/interfaces",
        "type": "rosapi/Interfaces", "args": {}, "id": "ai"}, args.timeout)
    if "values" in r:
        action_name_part = args.action.split("/")[-1]
        for iface in r["values"].get("interfaces", []):
            if "/action/" in iface and action_name_part.lower() in iface.lower():
                result["action_type"] = iface
                break

    atype = result["action_type"]
    if atype != "unknown":
        for part, svc, svc_type in [
            ("goal", "/rosapi/action_goal_details", "rosapi_msgs/srv/ActionGoalDetails"),
            ("result", "/rosapi/action_result_details", "rosapi_msgs/srv/ActionResultDetails"),
            ("feedback", "/rosapi/action_feedback_details", "rosapi_msgs/srv/ActionFeedbackDetails"),
        ]:
            r = ws_request(ws, {"op": "call_service", "service": svc,
                "type": svc_type, "args": {"type": atype}, "id": f"ad_{part}"}, args.timeout)
            if "values" in r:
                for td in r["values"].get("typedefs", []):
                    result[part] = dict(zip(td.get("fieldnames", []), td.get("fieldtypes", [])))
    ws.close()
    output(result)


def cmd_actions_send(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    try:
        goal = json.loads(args.goal)
    except json.JSONDecodeError as e:
        return output({"error": f"Invalid JSON goal: {e}"})

    goal_id = f"goal_{int(time.time() * 1000)}"
    ws.send(json.dumps({
        "op": "send_action_goal", "id": goal_id, "action": args.action,
        "action_type": args.action_type, "args": goal, "feedback": True
    }))

    end_time = time.time() + args.timeout
    while time.time() < end_time:
        ws.settimeout(max(0.5, end_time - time.time()))
        try:
            raw = ws.recv()
            data = json.loads(raw)
            if data.get("op") == "action_result":
                ws.close()
                return output({"action": args.action, "success": True,
                    "goal_id": goal_id, "result": data.get("values", {})})
        except websocket.WebSocketTimeoutException:
            continue
        except Exception:
            break

    ws.close()
    output({"action": args.action, "goal_id": goal_id, "success": False,
            "error": f"Timeout after {args.timeout}s"})


def cmd_version(args):
    ws, err = ws_connect(args.ip, args.port, args.timeout)
    if err:
        return output({"error": err})
    # Try ROS 2
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/get_ros_version",
        "args": {}, "id": "ver"
    }, args.timeout)
    if "values" in resp and "version" in resp["values"]:
        ws.close()
        return output({"version": resp["values"]["version"], "distro": resp["values"].get("distro", "")})
    # Fallback ROS 1
    resp = ws_request(ws, {
        "op": "call_service", "service": "/rosapi/get_param",
        "args": {"name": "/rosdistro"}, "id": "ver1"
    }, args.timeout)
    ws.close()
    if "values" in resp:
        distro = resp["values"].get("value", "").strip('"').strip()
        output({"version": "1", "distro": distro})
    else:
        output({"error": "Could not detect ROS version"})


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(description="ROS Skill CLI - Control ROS robots via rosbridge")
    parser.add_argument("--ip", default="127.0.0.1", help="Rosbridge IP (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9090, help="Rosbridge port (default: 9090)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout in seconds (default: 5)")
    sub = parser.add_subparsers(dest="command")

    # connect
    sub.add_parser("connect", help="Test connection to rosbridge")

    # version
    sub.add_parser("version", help="Detect ROS version")

    # topics
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
    p.add_argument("topic")
    p.add_argument("msg_type")
    p.add_argument("--duration", type=float, default=None, help="Subscribe for duration (seconds)")
    p.add_argument("--max-messages", type=int, default=100, help="Max messages to collect")
    p = tsub.add_parser("publish", help="Publish a message")
    p.add_argument("topic")
    p.add_argument("msg_type")
    p.add_argument("msg", help="JSON message")
    p.add_argument("--duration", type=float, default=None, help="Publish repeatedly for duration (seconds)")
    p.add_argument("--rate", type=float, default=10.0, help="Publish rate in Hz (default: 10)")
    p = tsub.add_parser("publish-sequence", help="Publish message sequence with delays")
    p.add_argument("topic")
    p.add_argument("msg_type")
    p.add_argument("messages", help="JSON array of messages")
    p.add_argument("durations", help="JSON array of durations in seconds (message is repeated during each)")
    p.add_argument("--rate", type=float, default=10.0, help="Publish rate in Hz (default: 10)")

    # services
    services = sub.add_parser("services", help="Service operations")
    ssub = services.add_subparsers(dest="subcommand")
    ssub.add_parser("list", help="List all services")
    p = ssub.add_parser("type", help="Get service type")
    p.add_argument("service")
    p = ssub.add_parser("details", help="Get service details")
    p.add_argument("service")
    p = ssub.add_parser("call", help="Call a service")
    p.add_argument("service")
    p.add_argument("service_type")
    p.add_argument("request", help="JSON request")

    # nodes
    nodes = sub.add_parser("nodes", help="Node operations")
    nsub = nodes.add_subparsers(dest="subcommand")
    nsub.add_parser("list", help="List all nodes")
    p = nsub.add_parser("details", help="Get node details")
    p.add_argument("node")

    # params (ROS 2 only)
    params = sub.add_parser("params", help="Parameter operations (ROS 2 only)")
    psub = params.add_subparsers(dest="subcommand")
    p = psub.add_parser("list", help="List parameters for a node")
    p.add_argument("node")
    p = psub.add_parser("get", help="Get parameter value")
    p.add_argument("name")
    p = psub.add_parser("set", help="Set parameter value")
    p.add_argument("name")
    p.add_argument("value")

    # actions (ROS 2 only)
    actions = sub.add_parser("actions", help="Action operations (ROS 2 only)")
    asub = actions.add_subparsers(dest="subcommand")
    asub.add_parser("list", help="List all actions")
    p = asub.add_parser("details", help="Get action details")
    p.add_argument("action")
    p = asub.add_parser("send", help="Send action goal")
    p.add_argument("action")
    p.add_argument("action_type")
    p.add_argument("goal", help="JSON goal")

    return parser


# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------

DISPATCH = {
    ("connect", None): cmd_connect,
    ("version", None): cmd_version,
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
