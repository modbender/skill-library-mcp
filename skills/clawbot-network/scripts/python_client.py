#!/usr/bin/env python3
"""
Agent Network Client - Python SDK
Connects to Agent Network Server for distributed agent collaboration

Usage:
    from agent_network_client import AgentNetworkClient
    
    client = AgentNetworkClient(server_url="ws://your-vps:3002")
    
    # Connect with agent info
    client.connect(
        agent_id="xiaoxing-macbook",
        name="小邢",
        role="DevOps",
        device="MacBook Pro"
    )
    
    # Join a group
    client.join_group("dev-team")
    
    # Send message
    client.send_message("dev-team", "Hello team! @老邢")
    
    # Set up message handler
    @client.on("message")
    def handle_message(msg):
        print(f"[{msg['fromName']}] {msg['content']}")
    
    # Keep running
    client.run_forever()
"""

import asyncio
import json
import websockets
import requests
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import threading
import time


class AgentNetworkClient:
    """Agent Network WebSocket Client"""
    
    def __init__(self, server_url: str, rest_url: str = None):
        """
        Initialize client
        
        Args:
            server_url: WebSocket URL (ws://host:port or wss://host:port)
            rest_url: REST API URL (optional, auto-derived from server_url)
        """
        self.server_url = server_url
        self.rest_url = rest_url or server_url.replace("ws://", "http://").replace("wss://", "https://")
        self.ws = None
        self.agent_id: Optional[str] = None
        self.agent_info: Optional[Dict] = None
        self.connected = False
        self.reconnect_interval = 5
        self.max_reconnect_attempts = 10
        self._reconnect_attempts = 0
        self._handlers: Dict[str, list] = {}
        self._heartbeat_task = None
        self._message_loop_task = None
        self._lock = threading.Lock()
    
    def on(self, event_type: str, handler: Callable = None):
        """Register event handler"""
        def decorator(func):
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            return func
        
        if handler:
            return decorator(handler)
        return decorator
    
    def emit(self, event_type: str, data: Any = None):
        """Emit event to handlers"""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    if data is not None:
                        handler(data)
                    else:
                        handler()
                except Exception as e:
                    print(f"Handler error: {e}")
    
    async def connect(self, agent_id: str, name: str, role: str = "", device: str = "", **kwargs):
        """
        Connect to server and register agent
        
        Args:
            agent_id: Unique agent ID (e.g., "xiaoxing-macbook")
            name: Display name (e.g., "小邢")
            role: Agent role (e.g., "DevOps")
            device: Device info (e.g., "MacBook Pro")
        """
        self.agent_id = agent_id
        self.agent_info = {
            "id": agent_id,
            "name": name,
            "role": role,
            "device": device,
            **kwargs
        }
        
        await self._connect_with_retry()
    
    async def _connect_with_retry(self):
        """Connect with auto-retry"""
        while self._reconnect_attempts < self.max_reconnect_attempts:
            try:
                print(f"🔌 Connecting to {self.server_url}...")
                self.ws = await websockets.connect(self.server_url)
                
                # Register agent
                await self.ws.send(json.dumps({
                    "type": "register",
                    "agent": self.agent_info
                }))
                
                self.connected = True
                self._reconnect_attempts = 0
                print("✅ Connected to Agent Network Server")
                
                self.emit("connected")
                
                # Start heartbeat
                self._heartbeat_task = asyncio.create_task(self._heartbeat())
                
                # Start message loop
                await self._message_loop()
                
            except Exception as e:
                self._reconnect_attempts += 1
                print(f"❌ Connection failed: {e}")
                print(f"🔄 Retrying in {self.reconnect_interval}s... (attempt {self._reconnect_attempts})")
                await asyncio.sleep(self.reconnect_interval)
        
        print("❌ Max reconnect attempts reached")
        self.emit("failed")
    
    async def _message_loop(self):
        """Main message receiving loop"""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("❌ Connection closed")
            self.connected = False
            self.emit("disconnected")
    
    async def _handle_message(self, msg: Dict):
        """Handle incoming message"""
        msg_type = msg.get("type")
        
        if msg_type == "registered":
            print(f"✅ Registered with server. Agent ID: {msg.get('agentId')}")
            self.emit("registered", msg)
        
        elif msg_type == "agent_list":
            self.emit("agent_list", msg.get("agents", []))
        
        elif msg_type == "message":
            print(f"[{msg.get('fromName')}] {msg.get('content')}")
            self.emit("message", msg)
        
        elif msg_type == "mention":
            print(f"🔔 You were mentioned by {msg.get('fromName')}: {msg.get('content')}")
            self.emit("mention", msg)
        
        elif msg_type == "direct_message":
            print(f"📩 DM from {msg.get('fromName')}: {msg.get('content')}")
            self.emit("direct_message", msg)
        
        elif msg_type == "task_assigned":
            print(f"📋 New task assigned: {msg.get('task', {}).get('title')}")
            self.emit("task_assigned", msg.get("task"))
        
        elif msg_type == "offline_messages":
            messages = msg.get("messages", [])
            print(f"📬 You have {len(messages)} offline messages")
            self.emit("offline_messages", messages)
        
        elif msg_type == "system":
            print(f"[System] {msg.get('content')}")
            self.emit("system", msg)
        
        else:
            self.emit(msg_type, msg)
    
    async def _heartbeat(self):
        """Send periodic heartbeat"""
        while self.connected:
            try:
                await asyncio.sleep(30)
                if self.ws and self.connected:
                    await self.ws.send(json.dumps({"type": "heartbeat"}))
            except Exception as e:
                print(f"Heartbeat error: {e}")
                break
    
    async def join_group(self, group_id: str):
        """Join a group"""
        if self.ws and self.connected:
            await self.ws.send(json.dumps({
                "type": "join_group",
                "groupId": group_id
            }))
            print(f"👥 Joined group: {group_id}")
    
    async def leave_group(self, group_id: str):
        """Leave a group"""
        if self.ws and self.connected:
            await self.ws.send(json.dumps({
                "type": "leave_group",
                "groupId": group_id
            }))
    
    async def send_message(self, group_id: str, content: str):
        """Send message to group"""
        if self.ws and self.connected:
            await self.ws.send(json.dumps({
                "type": "message",
                "groupId": group_id,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }))
    
    async def send_direct_message(self, to_agent_id: str, content: str):
        """Send direct message to agent"""
        if self.ws and self.connected:
            await self.ws.send(json.dumps({
                "type": "direct_message",
                "to": to_agent_id,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }))
    
    # REST API methods
    def get_agents(self) -> list:
        """Get online agents via REST API"""
        try:
            response = requests.get(f"{self.rest_url}/api/agents")
            return response.json()
        except Exception as e:
            print(f"API error: {e}")
            return []
    
    def get_groups(self) -> list:
        """Get all groups"""
        try:
            response = requests.get(f"{self.rest_url}/api/groups")
            return response.json()
        except Exception as e:
            print(f"API error: {e}")
            return []
    
    def get_messages(self, group_id: str) -> list:
        """Get group message history"""
        try:
            response = requests.get(f"{self.rest_url}/api/groups/{group_id}/messages")
            return response.json()
        except Exception as e:
            print(f"API error: {e}")
            return []
    
    def create_task(self, title: str, description: str, assignee_id: str, **kwargs) -> dict:
        """Create a task"""
        try:
            response = requests.post(f"{self.rest_url}/api/tasks", json={
                "title": title,
                "description": description,
                "assigneeId": assignee_id,
                **kwargs
            })
            return response.json()
        except Exception as e:
            print(f"API error: {e}")
            return {}
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self.ws:
            asyncio.create_task(self.ws.close())
    
    def run_forever(self):
        """Run client forever (blocking)"""
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            print("\n👋 Disconnecting...")
            self.disconnect()


# Convenience function for quick connection
def connect_to_network(server_url: str, agent_id: str, name: str, **kwargs) -> AgentNetworkClient:
    """
    Quick connect to Agent Network
    
    Args:
        server_url: WebSocket server URL
        agent_id: Unique agent ID
        name: Display name
        **kwargs: Additional agent info (role, device, etc.)
    
    Returns:
        Connected AgentNetworkClient instance
    """
    client = AgentNetworkClient(server_url)
    
    async def do_connect():
        await client.connect(agent_id=agent_id, name=name, **kwargs)
    
    asyncio.run(do_connect())
    return client


if __name__ == "__main__":
    # Example usage
    async def main():
        client = AgentNetworkClient("ws://localhost:3002")
        
        await client.connect(
            agent_id="test-agent",
            name="Test Agent",
            role="Developer",
            device="Local Machine"
        )
        
        @client.on("message")
        def on_message(msg):
            print(f"Received: {msg}")
        
        @client.on("mention")
        def on_mention(msg):
            print(f"You were mentioned! {msg}")
        
        # Join group and send message
        await client.join_group("test-group")
        await client.send_message("test-group", "Hello from Python client!")
        
        # Keep running
        await asyncio.Future()
    
    asyncio.run(main())
