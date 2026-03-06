#!/usr/bin/env python3
"""
Basic tests for Unified Logger
"""

import json
import os
import sys
import tempfile
import unittest
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import log


class TestLogToJsonl(unittest.TestCase):
    """Test JSONL logging functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_path = os.path.join(self.temp_dir, "test.jsonl")
        log.LOG_PATH = self.test_log_path
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_to_jsonl_creates_file(self):
        """Test that logging creates the JSONL file."""
        entry = {
            "timestamp": "2026-02-19T12:00:00Z",
            "session_id": "test123",
            "role": "user",
            "content": "Hello world",
            "tool_calls": None
        }
        
        result = log.log_to_jsonl(entry)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_log_path))
        
        # Verify content
        with open(self.test_log_path, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            data = json.loads(lines[0])
            self.assertEqual(data['content'], "Hello world")
            self.assertEqual(data['role'], "user")


class TestMainFunction(unittest.TestCase):
    """Test main entry point."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_path = os.path.join(self.temp_dir, "test.jsonl")
        log.LOG_PATH = self.test_log_path
        
        # Save original stdin
        self.original_stdin = sys.stdin
    
    def tearDown(self):
        sys.stdin = self.original_stdin
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_main_with_valid_input(self):
        """Test main function with valid JSON input."""
        test_input = json.dumps({
            "timestamp": "2026-02-19T12:00:00Z",
            "session_id": "test123",
            "role": "assistant",
            "content": "Test response",
            "tool_calls": None
        })
        
        sys.stdin = StringIO(test_input)
        log.main()
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.test_log_path))
    
    def test_main_with_empty_input(self):
        """Test main function handles empty input gracefully."""
        sys.stdin = StringIO("")
        log.main()  # Should not raise
        self.assertFalse(os.path.exists(self.test_log_path))


class TestConfiguration(unittest.TestCase):
    """Test configuration handling."""
    
    def test_default_paths(self):
        """Test that default paths are set."""
        # These should be strings, not None
        self.assertIsInstance(log.LOG_PATH, str)
        self.assertIsInstance(log.MEMVID_PATH, str)
        self.assertIsInstance(log.MEMVID_BIN, str)
    
    def test_env_override(self):
        """Test that environment variables override defaults."""
        original = os.environ.get('JSONL_LOG_PATH')
        
        try:
            os.environ['JSONL_LOG_PATH'] = '/custom/path.jsonl'
            # Reload module to pick up env var
            import importlib
            importlib.reload(log)
            self.assertEqual(log.LOG_PATH, '/custom/path.jsonl')
        finally:
            if original:
                os.environ['JSONL_LOG_PATH'] = original
            else:
                del os.environ['JSONL_LOG_PATH']


if __name__ == '__main__':
    unittest.main()
