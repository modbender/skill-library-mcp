#!/usr/bin/env python3
"""Unit tests for ros_cli.py.

Tests cover argument parsing, dispatch table, JSON handling,
utility functions, and command handlers (with mocked WebSocket).
"""

import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import ros_cli


# ---------------------------------------------------------------------------
# Argument parser tests
# ---------------------------------------------------------------------------

class TestBuildParser(unittest.TestCase):
    def setUp(self):
        self.parser = ros_cli.build_parser()

    def test_default_global_options(self):
        args = self.parser.parse_args(["connect"])
        self.assertEqual(args.ip, "127.0.0.1")
        self.assertEqual(args.port, 9090)
        self.assertEqual(args.timeout, 5.0)

    def test_custom_global_options(self):
        args = self.parser.parse_args(["--ip", "10.0.0.5", "--port", "9091", "--timeout", "10", "connect"])
        self.assertEqual(args.ip, "10.0.0.5")
        self.assertEqual(args.port, 9091)
        self.assertEqual(args.timeout, 10.0)

    def test_connect_command(self):
        args = self.parser.parse_args(["connect"])
        self.assertEqual(args.command, "connect")

    def test_version_command(self):
        args = self.parser.parse_args(["version"])
        self.assertEqual(args.command, "version")

    def test_topics_list(self):
        args = self.parser.parse_args(["topics", "list"])
        self.assertEqual(args.command, "topics")
        self.assertEqual(args.subcommand, "list")

    def test_topics_type(self):
        args = self.parser.parse_args(["topics", "type", "/cmd_vel"])
        self.assertEqual(args.subcommand, "type")
        self.assertEqual(args.topic, "/cmd_vel")

    def test_topics_subscribe_defaults(self):
        args = self.parser.parse_args(["topics", "subscribe", "/scan", "sensor_msgs/LaserScan"])
        self.assertEqual(args.topic, "/scan")
        self.assertEqual(args.msg_type, "sensor_msgs/LaserScan")
        self.assertIsNone(args.duration)
        self.assertEqual(args.max_messages, 100)

    def test_topics_subscribe_with_duration(self):
        args = self.parser.parse_args([
            "topics", "subscribe", "/odom", "nav_msgs/Odometry",
            "--duration", "10", "--max-messages", "50"
        ])
        self.assertEqual(args.duration, 10.0)
        self.assertEqual(args.max_messages, 50)

    def test_topics_publish(self):
        msg = '{"linear":{"x":1.0}}'
        args = self.parser.parse_args(["topics", "publish", "/cmd_vel", "geometry_msgs/Twist", msg])
        self.assertEqual(args.topic, "/cmd_vel")
        self.assertEqual(args.msg_type, "geometry_msgs/Twist")
        self.assertEqual(args.msg, msg)
        self.assertIsNone(args.duration)
        self.assertEqual(args.rate, 10.0)

    def test_topics_publish_with_duration_and_rate(self):
        args = self.parser.parse_args([
            "topics", "publish", "/cmd_vel", "geometry_msgs/Twist", '{}',
            "--duration", "3", "--rate", "20"
        ])
        self.assertEqual(args.duration, 3.0)
        self.assertEqual(args.rate, 20.0)

    def test_topics_publish_sequence(self):
        msgs = '[{"linear":{"x":1}},{"linear":{"x":0}}]'
        durs = '[2.0, 0.5]'
        args = self.parser.parse_args([
            "topics", "publish-sequence", "/cmd_vel", "geometry_msgs/Twist", msgs, durs
        ])
        self.assertEqual(args.subcommand, "publish-sequence")
        self.assertEqual(args.messages, msgs)
        self.assertEqual(args.durations, durs)

    def test_services_call(self):
        args = self.parser.parse_args([
            "services", "call", "/spawn", "turtlesim/Spawn",
            '{"x":3.0,"y":3.0}'
        ])
        self.assertEqual(args.command, "services")
        self.assertEqual(args.subcommand, "call")
        self.assertEqual(args.service, "/spawn")
        self.assertEqual(args.service_type, "turtlesim/Spawn")

    def test_nodes_details(self):
        args = self.parser.parse_args(["nodes", "details", "/turtlesim"])
        self.assertEqual(args.subcommand, "details")
        self.assertEqual(args.node, "/turtlesim")

    def test_params_list(self):
        args = self.parser.parse_args(["params", "list", "/turtlesim"])
        self.assertEqual(args.command, "params")
        self.assertEqual(args.node, "/turtlesim")

    def test_params_get(self):
        args = self.parser.parse_args(["params", "get", "/turtlesim:background_r"])
        self.assertEqual(args.name, "/turtlesim:background_r")

    def test_params_set(self):
        args = self.parser.parse_args(["params", "set", "/turtlesim:background_r", "255"])
        self.assertEqual(args.name, "/turtlesim:background_r")
        self.assertEqual(args.value, "255")

    def test_actions_send(self):
        args = self.parser.parse_args([
            "actions", "send", "/turtle1/rotate_absolute",
            "turtlesim/action/RotateAbsolute", '{"theta":3.14}'
        ])
        self.assertEqual(args.action, "/turtle1/rotate_absolute")
        self.assertEqual(args.action_type, "turtlesim/action/RotateAbsolute")
        self.assertEqual(args.goal, '{"theta":3.14}')


# ---------------------------------------------------------------------------
# Dispatch table tests
# ---------------------------------------------------------------------------

class TestDispatchTable(unittest.TestCase):
    def test_all_keys_have_callable_handlers(self):
        for key, handler in ros_cli.DISPATCH.items():
            self.assertTrue(callable(handler), f"{key} handler is not callable")

    def test_expected_keys_exist(self):
        expected_keys = [
            ("connect", None), ("version", None),
            ("topics", "list"), ("topics", "type"), ("topics", "details"),
            ("topics", "message"), ("topics", "subscribe"), ("topics", "publish"),
            ("topics", "publish-sequence"),
            ("services", "list"), ("services", "type"), ("services", "details"),
            ("services", "call"),
            ("nodes", "list"), ("nodes", "details"),
            ("params", "list"), ("params", "get"), ("params", "set"),
            ("actions", "list"), ("actions", "details"), ("actions", "send"),
        ]
        for key in expected_keys:
            self.assertIn(key, ros_cli.DISPATCH, f"Missing dispatch key: {key}")

    def test_dispatch_count(self):
        self.assertEqual(len(ros_cli.DISPATCH), 21)


# ---------------------------------------------------------------------------
# Utility function tests
# ---------------------------------------------------------------------------

class TestOutput(unittest.TestCase):
    def test_output_prints_json(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            ros_cli.output({"key": "value"})
            result = json.loads(mock_stdout.getvalue())
            self.assertEqual(result, {"key": "value"})

    def test_output_unicode(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            ros_cli.output({"msg": "로봇"})
            result = json.loads(mock_stdout.getvalue())
            self.assertEqual(result["msg"], "로봇")

    def test_output_nested(self):
        data = {"a": {"b": [1, 2, 3]}}
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            ros_cli.output(data)
            result = json.loads(mock_stdout.getvalue())
            self.assertEqual(result, data)


class TestCheckPort(unittest.TestCase):
    @patch("socket.create_connection")
    def test_port_open(self, mock_conn):
        mock_conn.return_value.__enter__ = MagicMock()
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        self.assertTrue(ros_cli.check_port("127.0.0.1", 9090))

    @patch("socket.create_connection", side_effect=ConnectionRefusedError)
    def test_port_closed(self, mock_conn):
        self.assertFalse(ros_cli.check_port("127.0.0.1", 9090))

    @patch("socket.create_connection", side_effect=OSError("timeout"))
    def test_port_timeout(self, mock_conn):
        self.assertFalse(ros_cli.check_port("127.0.0.1", 9090))


class TestPingIp(unittest.TestCase):
    @patch("subprocess.run")
    def test_ping_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(ros_cli.ping_ip("127.0.0.1"))

    @patch("subprocess.run")
    def test_ping_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(ros_cli.ping_ip("192.168.99.99"))

    @patch("subprocess.run", side_effect=Exception("not found"))
    def test_ping_exception(self, mock_run):
        self.assertFalse(ros_cli.ping_ip("10.0.0.1"))


# ---------------------------------------------------------------------------
# WebSocket helper tests
# ---------------------------------------------------------------------------

class TestWsConnect(unittest.TestCase):
    @patch("websocket.create_connection")
    def test_success(self, mock_create):
        mock_ws = MagicMock()
        mock_create.return_value = mock_ws
        ws, err = ros_cli.ws_connect("127.0.0.1", 9090)
        self.assertIs(ws, mock_ws)
        self.assertIsNone(err)
        mock_create.assert_called_once_with("ws://127.0.0.1:9090", timeout=5.0)

    @patch("websocket.create_connection", side_effect=ConnectionRefusedError("refused"))
    def test_failure(self, mock_create):
        ws, err = ros_cli.ws_connect("127.0.0.1", 9090)
        self.assertIsNone(ws)
        self.assertIn("refused", err)


class TestWsRequest(unittest.TestCase):
    def test_success(self):
        mock_ws = MagicMock()
        mock_ws.recv.return_value = json.dumps({"values": {"topics": ["/cmd_vel"]}})
        result = ros_cli.ws_request(mock_ws, {"op": "call_service"})
        self.assertIn("values", result)
        mock_ws.send.assert_called_once()

    def test_recv_error(self):
        mock_ws = MagicMock()
        mock_ws.recv.side_effect = Exception("connection lost")
        result = ros_cli.ws_request(mock_ws, {"op": "call_service"})
        self.assertIn("error", result)


class TestWsSubscribeOnce(unittest.TestCase):
    def test_receives_message(self):
        mock_ws = MagicMock()
        mock_ws.recv.return_value = json.dumps({
            "op": "publish", "topic": "/pose",
            "msg": {"x": 1.0, "y": 2.0}
        })
        result = ros_cli.ws_subscribe_once(mock_ws, "/pose", "turtlesim/Pose", timeout=1.0)
        self.assertEqual(result["msg"], {"x": 1.0, "y": 2.0})

    def test_error_status(self):
        mock_ws = MagicMock()
        mock_ws.recv.return_value = json.dumps({
            "op": "status", "level": "error", "msg": "bad topic"
        })
        result = ros_cli.ws_subscribe_once(mock_ws, "/bad", "std_msgs/String", timeout=1.0)
        self.assertIn("error", result)

    def test_timeout(self):
        mock_ws = MagicMock()
        import websocket as ws_mod
        mock_ws.recv.side_effect = ws_mod.WebSocketTimeoutException()
        result = ros_cli.ws_subscribe_once(mock_ws, "/slow", "std_msgs/String", timeout=0.5)
        self.assertIn("error", result)
        self.assertIn("Timeout", result["error"])


class TestWsSubscribeDuration(unittest.TestCase):
    def test_collects_messages(self):
        mock_ws = MagicMock()
        msgs = [
            json.dumps({"op": "publish", "topic": "/odom", "msg": {"seq": i}})
            for i in range(3)
        ]
        import websocket as ws_mod
        # After 3 real messages, keep raising timeout until duration expires
        call_count = [0]
        def recv_side_effect():
            idx = call_count[0]
            call_count[0] += 1
            if idx < len(msgs):
                return msgs[idx]
            raise ws_mod.WebSocketTimeoutException()
        mock_ws.recv.side_effect = recv_side_effect
        result = ros_cli.ws_subscribe_duration(mock_ws, "/odom", "nav_msgs/Odometry", duration=0.5)
        self.assertEqual(result["topic"], "/odom")
        self.assertEqual(result["collected_count"], 3)
        self.assertEqual(len(result["messages"]), 3)

    def test_max_messages_limit(self):
        mock_ws = MagicMock()
        msgs = [
            json.dumps({"op": "publish", "topic": "/t", "msg": {"i": i}})
            for i in range(10)
        ]
        mock_ws.recv.side_effect = msgs
        result = ros_cli.ws_subscribe_duration(mock_ws, "/t", "std_msgs/Int32", duration=5.0, max_messages=3)
        self.assertEqual(result["collected_count"], 3)


# ---------------------------------------------------------------------------
# Command handler tests (with mocked WebSocket)
# ---------------------------------------------------------------------------

def _make_args(**kwargs):
    """Create a namespace that mimics parsed arguments."""
    defaults = {"ip": "127.0.0.1", "port": 9090, "timeout": 5.0}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


import argparse


class TestCmdConnect(unittest.TestCase):
    @patch("ros_cli.ws_connect", return_value=(MagicMock(), None))
    @patch("ros_cli.check_port", return_value=True)
    @patch("ros_cli.ping_ip", return_value=True)
    def test_all_ok(self, mock_ping, mock_port, mock_ws):
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_connect(_make_args())
            result = json.loads(out.getvalue())
        self.assertTrue(result["ping"])
        self.assertTrue(result["port_open"])
        self.assertTrue(result["websocket"])
        self.assertNotIn("error", result)

    @patch("ros_cli.ws_connect", return_value=(None, "Connection refused"))
    @patch("ros_cli.check_port", return_value=False)
    @patch("ros_cli.ping_ip", return_value=True)
    def test_ws_failure(self, mock_ping, mock_port, mock_ws):
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_connect(_make_args())
            result = json.loads(out.getvalue())
        self.assertTrue(result["ping"])
        self.assertFalse(result["port_open"])
        self.assertFalse(result["websocket"])
        self.assertEqual(result["error"], "Connection refused")


class TestCmdTopicsList(unittest.TestCase):
    @patch("ros_cli.ws_connect")
    def test_success(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        mock_ws.recv.return_value = json.dumps({
            "values": {"topics": ["/cmd_vel", "/odom"], "types": ["geometry_msgs/Twist", "nav_msgs/Odometry"]}
        })
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_topics_list(_make_args())
            result = json.loads(out.getvalue())
        self.assertEqual(result["count"], 2)
        self.assertIn("/cmd_vel", result["topics"])

    @patch("ros_cli.ws_connect", return_value=(None, "timeout"))
    def test_connection_error(self, mock_connect):
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_topics_list(_make_args())
            result = json.loads(out.getvalue())
        self.assertIn("error", result)


class TestCmdTopicsPublish(unittest.TestCase):
    @patch("ros_cli.ws_connect")
    def test_single_shot(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        args = _make_args(
            topic="/cmd_vel", msg_type="geometry_msgs/Twist",
            msg='{"linear":{"x":1.0}}', duration=None, rate=10.0
        )
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_topics_publish(args)
            result = json.loads(out.getvalue())
        self.assertTrue(result["success"])
        self.assertEqual(result["topic"], "/cmd_vel")

    @patch("ros_cli.ws_connect")
    def test_invalid_json(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        args = _make_args(
            topic="/cmd_vel", msg_type="geometry_msgs/Twist",
            msg="not json", duration=None, rate=10.0
        )
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_topics_publish(args)
            result = json.loads(out.getvalue())
        self.assertIn("error", result)
        self.assertIn("Invalid JSON", result["error"])

    @patch("ros_cli.ws_connect", return_value=(None, "refused"))
    def test_connection_error(self, mock_connect):
        args = _make_args(
            topic="/cmd_vel", msg_type="geometry_msgs/Twist",
            msg='{}', duration=None, rate=10.0
        )
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_topics_publish(args)
            result = json.loads(out.getvalue())
        self.assertIn("error", result)


class TestCmdTopicsPublishSequence(unittest.TestCase):
    @patch("ros_cli.ws_connect")
    def test_success(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        args = _make_args(
            topic="/cmd_vel", msg_type="geometry_msgs/Twist",
            messages='[{"linear":{"x":1}},{"linear":{"x":0}}]',
            durations='[0.1, 0.1]', rate=10.0
        )
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_topics_publish_sequence(args)
            result = json.loads(out.getvalue())
        self.assertTrue(result["success"])
        self.assertGreater(result["published_count"], 0)

    @patch("ros_cli.ws_connect")
    def test_length_mismatch(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        args = _make_args(
            topic="/cmd_vel", msg_type="geometry_msgs/Twist",
            messages='[{"linear":{"x":1}}]',
            durations='[1.0, 2.0]', rate=10.0
        )
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_topics_publish_sequence(args)
            result = json.loads(out.getvalue())
        self.assertIn("error", result)
        self.assertIn("same length", result["error"])

    @patch("ros_cli.ws_connect")
    def test_invalid_json(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        args = _make_args(
            topic="/cmd_vel", msg_type="geometry_msgs/Twist",
            messages="bad", durations="[1]", rate=10.0
        )
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_topics_publish_sequence(args)
            result = json.loads(out.getvalue())
        self.assertIn("error", result)
        self.assertIn("Invalid JSON", result["error"])


class TestCmdServicesCall(unittest.TestCase):
    @patch("ros_cli.ws_connect")
    def test_success(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        mock_ws.recv.return_value = json.dumps({
            "values": {"name": "turtle2"}, "result": True
        })
        args = _make_args(
            service="/spawn", service_type="turtlesim/Spawn",
            request='{"x":3.0,"y":3.0}'
        )
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_services_call(args)
            result = json.loads(out.getvalue())
        self.assertTrue(result["success"])
        self.assertEqual(result["result"]["name"], "turtle2")

    @patch("ros_cli.ws_connect")
    def test_invalid_request_json(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        args = _make_args(
            service="/spawn", service_type="turtlesim/Spawn",
            request="not-json"
        )
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_services_call(args)
            result = json.loads(out.getvalue())
        self.assertIn("error", result)
        self.assertIn("Invalid JSON", result["error"])


class TestCmdVersion(unittest.TestCase):
    @patch("ros_cli.ws_connect")
    def test_ros2_detected(self, mock_connect):
        mock_ws = MagicMock()
        mock_connect.return_value = (mock_ws, None)
        mock_ws.recv.return_value = json.dumps({
            "values": {"version": "2", "distro": "humble"}
        })
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_version(_make_args())
            result = json.loads(out.getvalue())
        self.assertEqual(result["version"], "2")
        self.assertEqual(result["distro"], "humble")

    @patch("ros_cli.ws_connect", return_value=(None, "refused"))
    def test_connection_error(self, mock_connect):
        with patch("sys.stdout", new_callable=StringIO) as out:
            ros_cli.cmd_version(_make_args())
            result = json.loads(out.getvalue())
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
