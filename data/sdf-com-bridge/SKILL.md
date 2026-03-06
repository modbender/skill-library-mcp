---
name: sdf-com-bridge
description: Bridge between SDF COM chatroom and Feishu-Lark messaging platform. Supports bi-directional message translation between English and Chinese, command execution, and real-time chat synchronization. Use when connecting to SDF Public Access UNIX System COM chat and relaying messages to Feishu or Lark.
---

# SDF COM Bridge

SDF COM chatroom to Feishu bridge with real-time message sync and translation.

## Architecture

- SSH Socket connects to SDF
- COM runs on remote
- Terminal Parser extracts messages
- Translator handles EN-ZH bidirectional translation
- Feishu Integration sends formatted messages

## Components

### 1. SSH Connection (scripts/ssh_connection.py)
Reuses ControlMaster socket for connection.

```python
from ssh_connection import SSHConnection

conn = SSHConnection(user="yupeng", host="sdf.org")
conn.connect("com -c")  # Start COM
conn.send("g anonradio\n")  # Enter room
```

### 2. COM Interaction (scripts/com_interaction.py)
COM command wrapper.

| Command | Function | Description |
|---------|----------|-------------|
| w | get_users() | List users |
| l | list_rooms() | List rooms |
| g | join_room("name") | Join room |
| r/R | get_history(n) | View history |
| s | send_private(user, host, msg) | Private message |
| e | emote(action) | Emote action |
| q | quit() | Exit COM |

### 3. Terminal Parser (scripts/terminal_parser.py)
Extracts chat messages from terminal output.

```python
from terminal_parser import SimpleTextParser

parser = SimpleTextParser()
messages = parser.feed(raw_text)
```

### 4. Translator (scripts/translator.py)
English to Chinese translation.

```python
from translator import LLMTranslator

translator = LLMTranslator()
zh = translator.quick_translate_en_to_zh("hello")
```

### 5. Feishu Bridge (scripts/feishu_bridge.py)
Parse Feishu commands.

| Command | Format | Function |
|---------|--------|----------|
| Send | com: message | Send to COM |
| Status | com:pwd | Check connection |
| Privmsg | s: user@host message | Private message |

### 6. Main Bridge (scripts/main.py)
Complete runtime example.

```python
from main import SDFComBridge

bridge = SDFComBridge(
    user="yupeng",
    host="sdf.org",
    target_room="anonradio"
)

bridge.start()
bridge.handle_feishu_message("com: hello")
bridge.stop()
```

## Usage

Install dependencies:
```bash
pip install -r requirements.txt
```

Run directly:
```bash
python scripts/main.py
```

Test connection:
```bash
python -c "from scripts.ssh_connection import SSHConnection; c = SSHConnection(); print(c._check_socket())"
```

## Configuration

Edit main.py:

```python
bridge = SDFComBridge(
    user="yupeng",
    host="sdf.org",
    target_room="anonradio"
)
```

## Default Room

Auto-joins anonradio chatroom.

## Message Flow

**COM to Feishu:**
- English messages auto-translated to Chinese

**Feishu to COM:**  
- Messages prefixed with "com:" sent to COM

## Notes

- Requires existing SSH ControlMaster socket
- Socket path: ~/.ssh/sockets/yupeng@sdf.org
- com command must be available on remote
- pyte requires correct terminal size (80x24 default)
