#!/opt/playwright/bin/python
"""
OneBot WebSocket Event Listener
Connect to OneBot WebSocket server and receive events
"""

import asyncio
import websockets
import json
import os
from typing import Optional, Callable

class OneBotWebSocketListener:
    """OneBot WebSocket Event Listener"""
    
    def __init__(self, 
                 ws_url: Optional[str] = None,
                 token: Optional[str] = None):
        """
        Initialize WebSocket listener
        
        Args:
            ws_url: OneBot WebSocket URL (default: ws://127.0.0.1:3001)
            token: Authorization token (optional)
        """
        self.ws_url = ws_url or os.getenv("ONEBOT_WS_URL", "ws://127.0.0.1:3001")
        self.token = token or os.getenv("ONEBOT_TOKEN", "")
        self.running = False
        self.handlers: dict[str, list[Callable]] = {}
    
    def on(self, event_type: str, handler: Callable):
        """
        Register event handler
        
        Args:
            event_type: Event type (e.g., 'message', 'notice', 'request')
            handler: Callback function
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def _handle_event(self, event: dict):
        """Handle incoming event"""
        # Get event type
        post_type = event.get("post_type")
        
        # Call general handlers
        if post_type in self.handlers:
            for handler in self.handlers[post_type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Handler error: {e}")
        
        # Call specific message type handlers
        if post_type == "message":
            message_type = event.get("message_type")
            if message_type in self.handlers:
                for handler in self.handlers[message_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        print(f"Handler error: {e}")
    
    async def _listen(self):
        """WebSocket connection loop"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        while self.running:
            try:
                print(f"Connecting to {self.ws_url}...")
                async with websockets.connect(self.ws_url, extra_headers=headers) as ws:
                    print("Connected to OneBot WebSocket server")
                    
                    while self.running:
                        try:
                            message = await ws.recv()
                            event = json.loads(message)
                            
                            # Print event for debugging
                            print(f"\n[Event] {json.dumps(event, ensure_ascii=False, indent=2)}")
                            
                            # Handle event
                            await self._handle_event(event)
                            
                        except websockets.exceptions.ConnectionClosed:
                            print("Connection closed, reconnecting...")
                            break
                        except json.JSONDecodeError as e:
                            print(f"Invalid JSON: {e}")
                        except Exception as e:
                            print(f"Error handling message: {e}")
                            
            except websockets.exceptions.InvalidURI:
                print(f"Invalid WebSocket URL: {self.ws_url}")
                break
            except Exception as e:
                print(f"Connection error: {e}")
                if self.running:
                    print("Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)
    
    def start(self):
        """Start listening"""
        self.running = True
        asyncio.run(self._listen())
    
    def stop(self):
        """Stop listening"""
        self.running = False


# Example handlers
async def handle_private_message(event: dict):
    """Handle private messages"""
    user_id = event.get("user_id")
    message = event.get("message")
    print(f"[Private] {user_id}: {message}")
    
    # Auto-reply example
    if message == "ping":
        # Send reply via HTTP API
        from onebot_client import OneBotClient
        client = OneBotClient()
        client.send_private_msg(user_id, "pong")


async def handle_group_message(event: dict):
    """Handle group messages"""
    group_id = event.get("group_id")
    user_id = event.get("user_id")
    message = event.get("message")
    print(f"[Group {group_id}] {user_id}: {message}")


async def handle_notice(event: dict):
    """Handle notices (group join, ban, etc.)"""
    notice_type = event.get("notice_type")
    print(f"[Notice] {notice_type}: {event}")


def main():
    """Start WebSocket listener"""
    listener = OneBotWebSocketListener()
    
    # Register handlers
    listener.on("message", handle_private_message)
    listener.on("private", handle_private_message)
    listener.on("group", handle_group_message)
    listener.on("notice", handle_notice)
    
    print("OneBot WebSocket Listener started")
    print("Press Ctrl+C to stop")
    
    try:
        listener.start()
    except KeyboardInterrupt:
        print("\nStopping...")
        listener.stop()


if __name__ == "__main__":
    main()
