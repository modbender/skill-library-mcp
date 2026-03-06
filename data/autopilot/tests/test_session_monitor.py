#!/usr/bin/env python3
"""
测试 Session Monitor 模块
- 状态判定边界测试
"""

import json
import os
import sys
import tempfile
import time
import unittest

# 添加 lib 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.session_monitor import (
    ACTIVE_THRESHOLD,
    IDLE_THRESHOLD,
    SessionInfo,
    SessionState,
    clear_cache,
    get_session_state,
    read_last_assistant_message,
)


class TestSessionState(unittest.TestCase):
    """测试会话状态判定"""
    
    def test_active_state_boundary(self):
        """测试 ACTIVE 状态边界 (< 120s)"""
        # 刚刚更新的 session
        session = SessionInfo(
            path="/tmp/test.jsonl",
            cwd="/test",
            mtime=time.time() - 60  # 60秒前
        )
        self.assertEqual(get_session_state(session), SessionState.ACTIVE)
        
        # 边界值：119秒
        session = SessionInfo(
            path="/tmp/test.jsonl",
            cwd="/test",
            mtime=time.time() - 119
        )
        self.assertEqual(get_session_state(session), SessionState.ACTIVE)
    
    def test_idle_state_boundary(self):
        """测试 IDLE 状态边界 (120s ~ 360s)"""
        # 刚进入 IDLE：120秒
        session = SessionInfo(
            path="/tmp/test.jsonl",
            cwd="/test",
            mtime=time.time() - 120
        )
        self.assertEqual(get_session_state(session), SessionState.IDLE)
        
        # IDLE 中间值：240秒
        session = SessionInfo(
            path="/tmp/test.jsonl",
            cwd="/test",
            mtime=time.time() - 240
        )
        self.assertEqual(get_session_state(session), SessionState.IDLE)
        
        # 边界值：359秒
        session = SessionInfo(
            path="/tmp/test.jsonl",
            cwd="/test",
            mtime=time.time() - 359
        )
        self.assertEqual(get_session_state(session), SessionState.IDLE)
    
    def test_done_state_boundary(self):
        """测试 DONE 状态边界 (>= 360s)"""
        # 刚进入 DONE：360秒
        session = SessionInfo(
            path="/tmp/test.jsonl",
            cwd="/test",
            mtime=time.time() - 360
        )
        self.assertEqual(get_session_state(session), SessionState.DONE)
        
        # 很久之前
        session = SessionInfo(
            path="/tmp/test.jsonl",
            cwd="/test",
            mtime=time.time() - 3600
        )
        self.assertEqual(get_session_state(session), SessionState.DONE)
    
    def test_threshold_constants(self):
        """确认阈值常量正确"""
        self.assertEqual(ACTIVE_THRESHOLD, 120)
        self.assertEqual(IDLE_THRESHOLD, 360)


class TestReadLastAssistantMessage(unittest.TestCase):
    """测试读取最后 assistant 消息"""
    
    def setUp(self):
        """创建临时 JSONL 文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.jsonl_path = os.path.join(self.temp_dir, "test.jsonl")
    
    def tearDown(self):
        """清理临时文件"""
        if os.path.exists(self.jsonl_path):
            os.remove(self.jsonl_path)
        os.rmdir(self.temp_dir)
        clear_cache()
    
    def _write_jsonl(self, lines):
        """写入 JSONL 文件"""
        with open(self.jsonl_path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(json.dumps(line) + '\n')
    
    def test_read_simple_message(self):
        """测试读取简单消息"""
        lines = [
            {"type": "session_meta", "payload": {"cwd": "/test"}},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Hello, world!"}]
            }}
        ]
        self._write_jsonl(lines)
        
        result = read_last_assistant_message(self.jsonl_path)
        self.assertEqual(result, "Hello, world!")
    
    def test_read_last_of_multiple(self):
        """测试读取多条消息中的最后一条"""
        lines = [
            {"type": "session_meta", "payload": {"cwd": "/test"}},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "First message"}]
            }},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "User input"}]
            }},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Last message"}]
            }}
        ]
        self._write_jsonl(lines)
        
        result = read_last_assistant_message(self.jsonl_path)
        self.assertEqual(result, "Last message")
    
    def test_skip_non_assistant_messages(self):
        """测试跳过非 assistant 消息"""
        lines = [
            {"type": "session_meta", "payload": {"cwd": "/test"}},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Assistant message"}]
            }},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "developer",
                "content": [{"type": "input_text", "text": "System message"}]
            }},
        ]
        self._write_jsonl(lines)
        
        result = read_last_assistant_message(self.jsonl_path)
        self.assertEqual(result, "Assistant message")
    
    def test_skip_function_calls(self):
        """测试跳过 function_call 类型"""
        lines = [
            {"type": "session_meta", "payload": {"cwd": "/test"}},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Text output"}]
            }},
            {"type": "response_item", "payload": {
                "type": "function_call",
                "role": "assistant",
            }},
        ]
        self._write_jsonl(lines)
        
        result = read_last_assistant_message(self.jsonl_path)
        self.assertEqual(result, "Text output")
    
    def test_truncate_long_message(self):
        """测试长消息截断"""
        long_text = "A" * 5000
        lines = [
            {"type": "session_meta", "payload": {"cwd": "/test"}},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": long_text}]
            }}
        ]
        self._write_jsonl(lines)
        
        result = read_last_assistant_message(self.jsonl_path, max_chars=4000)
        self.assertEqual(len(result), 4000)
    
    def test_empty_file(self):
        """测试空文件"""
        self._write_jsonl([])
        result = read_last_assistant_message(self.jsonl_path)
        self.assertIsNone(result)
    
    def test_no_assistant_message(self):
        """测试没有 assistant 消息的情况"""
        lines = [
            {"type": "session_meta", "payload": {"cwd": "/test"}},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "User only"}]
            }}
        ]
        self._write_jsonl(lines)
        
        result = read_last_assistant_message(self.jsonl_path)
        self.assertIsNone(result)
    
    def test_chinese_content(self):
        """测试中文内容"""
        lines = [
            {"type": "session_meta", "payload": {"cwd": "/test"}},
            {"type": "response_item", "payload": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "你好，世界！这是一条中文消息。"}]
            }}
        ]
        self._write_jsonl(lines)
        
        result = read_last_assistant_message(self.jsonl_path)
        self.assertEqual(result, "你好，世界！这是一条中文消息。")


if __name__ == '__main__':
    unittest.main()
