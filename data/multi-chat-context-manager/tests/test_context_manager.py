#!/usr/bin/env python3
"""
Test script for multi-chat-context-manager.
"""

import os
import sys
import json
import tempfile
import subprocess

# Add parent directory to path so we can import the script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from context_manager import load_contexts, save_contexts, store_context, retrieve_context, clear_context

def test_basic():
    """Test store, retrieve, clear."""
    # Use a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        os.environ['CONTEXT_STORAGE_PATH'] = temp_path
        
        # Store a context
        ctx = store_context(
            channel_id='test-channel',
            user_id='test-user',
            message='Hello',
            response='Hi there'
        )
        assert ctx['channel_id'] == 'test-channel'
        assert ctx['user_id'] == 'test-user'
        assert len(ctx['history']) == 1
        assert ctx['history'][0]['message'] == 'Hello'
        assert ctx['history'][0]['response'] == 'Hi there'
        print("✓ Store passed")
        
        # Retrieve
        retrieved = retrieve_context('test-channel', user_id='test-user')
        assert retrieved['channel_id'] == 'test-channel'
        assert retrieved['user_id'] == 'test-user'
        assert len(retrieved['history']) == 1
        print("✓ Retrieve passed")
        
        # Clear
        clear_context('test-channel', user_id='test-user')
        cleared = retrieve_context('test-channel', user_id='test-user')
        assert cleared == {}
        print("✓ Clear passed")
        
        # List contexts (empty)
        contexts = load_contexts()
        assert contexts == {}
        print("✓ List passed")
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_cli():
    """Test command-line interface."""
    # Test store via subprocess
    result = subprocess.run([
        sys.executable, 
        os.path.join(os.path.dirname(__file__), '..', 'scripts', 'context_manager.py'),
        'store',
        '--channel', 'cli-channel',
        '--user', 'cli-user',
        '--message', 'test message',
        '--response', 'test response'
    ], capture_output=True, text=True)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['channel_id'] == 'cli-channel'
    print("✓ CLI store passed")
    
    # Test retrieve
    result = subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), '..', 'scripts', 'context_manager.py'),
        'retrieve',
        '--channel', 'cli-channel',
        '--user', 'cli-user'
    ], capture_output=True, text=True)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['channel_id'] == 'cli-channel'
    print("✓ CLI retrieve passed")
    
    # Clean up
    subprocess.run([
        sys.executable,
        os.path.join(os.path.dirname(__file__), '..', 'scripts', 'context_manager.py'),
        'clear',
        '--channel', 'cli-channel',
        '--user', 'cli-user'
    ])

if __name__ == '__main__':
    print("Running tests for multi-chat-context-manager...")
    test_basic()
    test_cli()
    print("All tests passed!")