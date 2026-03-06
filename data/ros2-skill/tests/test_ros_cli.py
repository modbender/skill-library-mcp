#!/usr/bin/env python3
"""Unit tests for ros2_cli.py.

Tests cover argument parsing, dispatch table, JSON handling,
and utility functions.
"""

import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def check_rclpy_available():
    """Check if rclpy is available without importing the full module."""
    try:
        import rclpy
        return True
    except ImportError:
        return False


class TestBuildParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not check_rclpy_available():
            raise unittest.SkipTest("rclpy not available - requires ROS 2 environment")
        import ros2_cli
        cls.ros2_cli = ros2_cli

    def setUp(self):
        self.parser = self.ros2_cli.build_parser()

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
        args = self.parser.parse_args(["topics", "subscribe", "/scan"])
        self.assertEqual(args.topic, "/scan")
        self.assertIsNone(args.duration)
        self.assertEqual(args.max_messages, 100)

    def test_topics_subscribe_with_duration(self):
        args = self.parser.parse_args([
            "topics", "subscribe", "/odom",
            "--duration", "10", "--max-messages", "50"
        ])
        self.assertEqual(args.duration, 10.0)
        self.assertEqual(args.max_messages, 50)

    def test_topics_publish(self):
        msg = '{"linear":{"x":1.0}}'
        args = self.parser.parse_args(["topics", "publish", "/cmd_vel", msg])
        self.assertEqual(args.topic, "/cmd_vel")
        self.assertEqual(args.msg, msg)
        self.assertIsNone(args.duration)
        self.assertEqual(args.rate, 10.0)

    def test_topics_publish_with_duration_and_rate(self):
        args = self.parser.parse_args([
            "topics", "publish", "/cmd_vel", '{}',
            "--duration", "3", "--rate", "20"
        ])
        self.assertEqual(args.duration, 3.0)
        self.assertEqual(args.rate, 20.0)

    def test_topics_publish_sequence(self):
        msgs = '[{"linear":{"x":1}},{"linear":{"x":0}}]'
        durs = '[2.0, 0.5]'
        args = self.parser.parse_args([
            "topics", "publish-sequence", "/cmd_vel", msgs, durs
        ])
        self.assertEqual(args.subcommand, "publish-sequence")
        self.assertEqual(args.messages, msgs)
        self.assertEqual(args.durations, durs)

    def test_services_call(self):
        args = self.parser.parse_args([
            "services", "call", "/spawn",
            '{"x":3.0,"y":3.0}'
        ])
        self.assertEqual(args.command, "services")
        self.assertEqual(args.subcommand, "call")
        self.assertEqual(args.service, "/spawn")

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
            '{"theta":3.14}'
        ])
        self.assertEqual(args.action, "/turtle1/rotate_absolute")
        self.assertEqual(args.goal, '{"theta":3.14}')


class TestDispatchTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not check_rclpy_available():
            raise unittest.SkipTest("rclpy not available - requires ROS 2 environment")
        import ros2_cli
        cls.ros2_cli = ros2_cli

    def test_all_keys_have_callable_handlers(self):
        for key, handler in self.ros2_cli.DISPATCH.items():
            self.assertTrue(callable(handler), f"{key} handler is not callable")

    def test_expected_keys_exist(self):
        expected_keys = [
            ("version", None),
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
            self.assertIn(key, self.ros2_cli.DISPATCH, f"Missing dispatch key: {key}")

    def test_dispatch_count(self):
        self.assertEqual(len(self.ros2_cli.DISPATCH), 20)


class TestOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not check_rclpy_available():
            raise unittest.SkipTest("rclpy not available - requires ROS 2 environment")
        import ros2_cli
        cls.ros2_cli = ros2_cli

    def test_output_prints_json(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ros2_cli.output({"key": "value"})
            result = json.loads(mock_stdout.getvalue())
            self.assertEqual(result, {"key": "value"})

    def test_output_unicode(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ros2_cli.output({"msg": "로봇"})
            result = json.loads(mock_stdout.getvalue())
            self.assertEqual(result["msg"], "로봇")

    def test_output_nested(self):
        data = {"a": {"b": [1, 2, 3]}}
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ros2_cli.output(data)
            result = json.loads(mock_stdout.getvalue())
            self.assertEqual(result, data)


class TestMsgConversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not check_rclpy_available():
            raise unittest.SkipTest("rclpy not available - requires ROS 2 environment")
        import ros2_cli
        cls.ros2_cli = ros2_cli

    def test_msg_to_dict(self):
        mock_msg = MagicMock()
        mock_msg.get_fields_and_field_types.return_value = ["field1", "field2"]
        mock_msg.field1 = "value1"
        mock_msg.field2 = 42
        
        result = self.ros2_cli.msg_to_dict(mock_msg)
        self.assertEqual(result, {"field1": "value1", "field2": 42})

    def test_dict_to_msg(self):
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        result = self.ros2_cli.dict_to_msg(mock_class, {"key": "value"})
        self.assertEqual(result, mock_instance)
        mock_instance.key = "value"


class TestParseNodeParam(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not check_rclpy_available():
            raise unittest.SkipTest("rclpy not available - requires ROS 2 environment")
        import ros2_cli
        cls.ros2_cli = ros2_cli

    def test_with_colon(self):
        node, param = self.ros2_cli.parse_node_param("/turtlesim:background_r")
        self.assertEqual(node, "/turtlesim")
        self.assertEqual(param, "background_r")

    def test_without_colon(self):
        node, param = self.ros2_cli.parse_node_param("/turtlesim")
        self.assertEqual(node, "/turtlesim")
        self.assertIsNone(param)


if __name__ == "__main__":
    unittest.main()
