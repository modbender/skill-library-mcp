---
name: pywayne-cross-comm
description: WebSocket-based cross-language communication service with support for multiple message types (text, JSON, dict, bytes, images, files, folders) and client management. Use when building real-time communication applications between Python and other languages, needing multi-device messaging, or requiring file transfer via Aliyun OSS. Supports both server and client roles with heartbeat, client list management, and message filtering by type or sender.
---

# Pywayne Cross Comm

`pywayne.cross_comm.CrossCommService` provides WebSocket-based real-time communication between Python and other languages, with built-in file transfer via Aliyun OSS.

## Prerequisites

**OSS Configuration** (required for file/image/folder transfer):

File transfers use Aliyun OSS. Set these environment variables:

```bash
# .env file
OSS_ENDPOINT=your-oss-endpoint
OSS_BUCKET_NAME=your-bucket-name
OSS_ACCESS_KEY_ID=your-access-key
OSS_ACCESS_KEY_SECRET=your-access-secret
```

For more OSS details, see `pywayne-aliyun-oss` skill.

## Quick Start

```python
import asyncio
from pywayne.cross_comm import CrossCommService, CommMsgType

# Server
server = CrossCommService(role='server', ip='0.0.0.0', port=9898)
await server.start_server()

# Client
client = CrossCommService(role='client', ip='localhost', port=9898, client_id='my_client')
await client.login()
```

## Server

### Initialize server

```python
server = CrossCommService(
    role='server',
    ip='0.0.0.0',        # Listen on all interfaces
    port=9898,
    heartbeat_interval=30,     # Seconds between heartbeats
    heartbeat_timeout=60       # Seconds before marking offline
)
```

### Register message listeners

```python
@server.message_listener(msg_type=CommMsgType.TEXT)
async def handle_text(message):
    print(f"From {message.from_client_id}: {message.content}")

@server.message_listener(msg_type=CommMsgType.FILE, download_directory="./downloads")
async def handle_file(message):
    print(f"File downloaded: {message.content}")
```

### Start server

```python
await server.start_server()  # Blocks until server stops
```

### Get online clients

```python
online_clients = server.get_online_clients()  # Returns list of client IDs
```

## Client

### Initialize client

```python
client = CrossCommService(
    role='client',
    ip='localhost',           # Server address
    port=9898,
    client_id='my_client',    # Optional: auto-generated if omitted
    heartbeat_interval=30,
    heartbeat_timeout=60
)
```

### Login and logout

```python
success = await client.login()
if success:
    print("Connected!")
    # ... communicate ...
    await client.logout()
```

### Send messages

```python
# Broadcast to all
await client.send_message("Hello!", CommMsgType.TEXT)

# Send to specific client
await client.send_message("Private", CommMsgType.TEXT, to_client_id='target_id')

# JSON message
await client.send_message('{"key": "value"}', CommMsgType.JSON)

# Dict message
await client.send_message({"type": "data", "value": 123}, CommMsgType.DICT)

# Bytes (auto base64 encoded)
await client.send_message(b"binary", CommMsgType.BYTES)

# File (auto uploads to OSS)
await client.send_message("/path/to/file.txt", CommMsgType.FILE)

# Image (auto uploads to OSS)
await client.send_message("/path/to/image.jpg", CommMsgType.IMAGE)

# Folder (auto uploads to OSS)
await client.send_message("/path/to/folder", CommMsgType.FOLDER)
```

### Get client list

```python
# All clients (online + offline)
all_clients = await client.list_clients(only_show_online=False)
# Returns: {'clients': [...], 'total_count': N, 'only_show_online': False}

# Online only
online = await client.list_clients(only_show_online=True)
```

## Message Types

`CommMsgType` enum (use these, not strings):

| Type | Description |
|------|-------------|
| `CommMsgType.TEXT` | Plain text |
| `CommMsgType.JSON` | JSON string |
| `CommMsgType.DICT` | Python dict |
| `CommMsgType.BYTES` | Binary data |
| `CommMsgType.IMAGE` | Image file |
| `CommMsgType.FILE` | Regular file |
| `CommMsgType.FOLDER` | Folder |

**Internal types** (auto-handled): HEARTBEAT, LOGIN, LOGOUT, LIST_CLIENTS, LIST_CLIENTS_RESPONSE, LOGIN_RESPONSE

## Message Listener Decorator

```python
# Listen to specific type
@service.message_listener(msg_type=CommMsgType.TEXT)
async def handler(message):
    pass

# Listen from specific sender
@service.message_listener(msg_type=CommMsgType.FILE, from_client_id='specific_client')
async def handler(message):
    pass

# Listen to all types
@service.message_listener()
async def handler(message):
    pass
```

**Note**: Listeners automatically filter out messages sent by yourself.

## File Download Control

File downloads are controlled via the listener's `download_directory` parameter:

```python
# Auto-download files to ./downloads
@client.message_listener(msg_type=CommMsgType.FILE, download_directory="./downloads")
async def handle_file(message):
    # message.content contains downloaded file path
    print(f"Downloaded: {message.content}")

# No auto-download - saves bandwidth
@client.message_listener(msg_type=CommMsgType.FILE, from_client_id='low_priority')
async def handle_file(message):
    # message.content contains OSS key, not downloaded
    print(f"File available: {message.oss_key}")
    # Optionally: client.download_file_manually(message.oss_key, "./manual_downloads/")
```

### Manual download

```python
success = client.download_file_manually(
    oss_key="cross_comm/sender_id/123456_file.txt",
    save_directory="./downloads"
)
```

## Message Object

```python
@dataclass
class Message:
    msg_id: str                    # Unique message ID
    from_client_id: str            # Sender ID
    to_client_id: str              # 'all' or specific client ID
    msg_type: CommMsgType           # Message type enum
    content: Any                   # Message content
    timestamp: float                # Unix timestamp
    oss_key: Optional[str]         # OSS key for file transfers

    def to_dict(self) -> Dict:      # Convert to dict
    @classmethod
    def from_dict(cls, data) -> 'Message':  # Create from dict
```

## Client ID Generation

If `client_id` is not specified, it's auto-generated using MAC address + UUID:
- Format: `{mac_address}_{uuid_suffix}`
- Example: `a1b2c3d4e5f6_abc12345`

## Command Line

```bash
# Run server
python -m pywayne.cross_comm server

# Run client
python -m pywayne.cross_comm client
```

## Important Notes

- **File transfer**: Requires OSS environment variables; files auto-upload on send
- **Async required**: All operations are async; use `asyncio.run()` or `await` in async context
- **Heartbeat**: Auto-managed; adjust intervals for network conditions
- **Message filtering**: Use `download_directory` to control auto-downloads and save bandwidth
- **State persistence**: Server saves client status to `cross_comm_clients.yaml`
- **Role-specific methods**: Server has `start_server()`, `get_online_clients()`; client has `login()`, `logout()`, `send_message()`, `list_clients()`
