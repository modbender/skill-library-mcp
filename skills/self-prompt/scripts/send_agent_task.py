#!/usr/bin/env python3
"""
send_agent_task.py - Force agent to respond and deliver to chat

Usage as module:
    from send_agent_task import send_and_deliver
    success, response = send_and_deliver("agent-id", "-123456789", "Task message")

Usage as CLI:
    python send_agent_task.py AGENT_ID GROUP_ID "message" [timeout]
"""

import subprocess
import sys
import os
from datetime import datetime

OPENCLAW_PATH = os.environ.get('OPENCLAW_PATH', '/home/eliran/.nvm/current/bin/openclaw')


def send_agent_task(agent_id: str, group_id: str, message: str, 
                    timeout: int = 180, channel: str = "telegram") -> tuple[bool, str]:
    """
    Send task to agent via openclaw agent (forces response).
    
    Args:
        agent_id: The agent identifier (e.g., "stock-trading")
        group_id: The group/channel ID (e.g., "-5283045656")
        message: The task message to send
        timeout: Timeout in seconds (default 180)
        channel: Channel type (default "telegram")
    
    Returns:
        Tuple of (success: bool, response: str)
    """
    session_key = f"agent:{agent_id}:{channel}:group:{group_id}"
    
    try:
        result = subprocess.run([
            OPENCLAW_PATH, 'agent',
            '--agent', agent_id,
            '--session-id', session_key,
            '--channel', channel,
            '--message', message,
            '--timeout', str(timeout)
        ], capture_output=True, text=True, timeout=timeout + 30)
        
        response = result.stdout.strip() if result.stdout else result.stderr.strip()
        return (True, response) if response else (False, "No response")
        
    except subprocess.TimeoutExpired:
        return (False, "Timeout")
    except Exception as e:
        return (False, str(e))


def send_and_deliver(agent_id: str, group_id: str, message: str,
                     timeout: int = 180, channel: str = "telegram") -> tuple[bool, str]:
    """
    Send task to agent AND deliver response to chat.
    
    This is the recommended function - it handles the full workflow:
    1. Send task via openclaw agent
    2. Capture response
    3. Send response to chat via message send
    
    Args:
        agent_id: The agent identifier
        group_id: The group/channel ID  
        message: The task message
        timeout: Timeout in seconds
        channel: Channel type
    
    Returns:
        Tuple of (success: bool, response: str)
    """
    # Get agent response
    success, response = send_agent_task(agent_id, group_id, message, timeout, channel)
    
    # Deliver to chat
    try:
        if success and response:
            delivery_msg = f"📊 **Agent Response:**\n\n{response}"
        else:
            delivery_msg = f"⚠️ Agent task failed: {response}"
        
        subprocess.run([
            OPENCLAW_PATH, 'message', 'send',
            '--channel', channel,
            '--target', group_id,
            '--message', delivery_msg
        ], capture_output=True, text=True, timeout=30)
        
    except Exception as e:
        print(f"Failed to deliver response: {e}", file=sys.stderr)
    
    return (success, response)


def log(message: str):
    """Log to ~/agent_task.log"""
    try:
        log_path = os.path.expanduser("~/agent_task.log")
        with open(log_path, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: send_agent_task.py AGENT_ID GROUP_ID 'message' [timeout]")
        print("\nExample:")
        print("  send_agent_task.py stock-trading -5283045656 'Analyze positions' 180")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    group_id = sys.argv[2]
    message = sys.argv[3]
    timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 180
    
    log(f"Sending task to {agent_id}")
    success, response = send_and_deliver(agent_id, group_id, message, timeout)
    
    log(f"Result: success={success}, response_len={len(response)}")
    print(f"Success: {success}")
    print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
    
    sys.exit(0 if success else 1)
