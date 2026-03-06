---
name: pywayne-llm-chat-window
description: PyQt5-based GUI chat window for LLM conversations with streaming responses and stop functionality. Use when working with pywayne.llm.chat_window module to create desktop chat applications with customizable window configuration, system message management, and real-time streaming display.
---

# Pywayne Chat Window

This module provides a PyQt5-based desktop GUI chat window for LLM conversations.

## Quick Start

```python
from pywayne.llm.chat_window import ChatWindow

# Basic usage - quick launch
ChatWindow.launch(
    base_url="https://api.deepseek.com/v1",
    api_key="your_api_key",
    model="deepseek-chat"
)
```

## Configuration

Using `ChatConfig` dataclass for full customization:

```python
from pywayne.llm.chat_window import ChatWindow, ChatConfig

config = ChatConfig(
    base_url="https://api.deepseek.com/v1",
    api_key="your_api_key",
    model="deepseek-chat",
    temperature=0.8,
    window_title="AI Assistant",
    window_width=800,
    window_height=600
)

chat = ChatWindow(config)
chat.run()
```

### ChatConfig Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_url` | required | API base URL |
| `api_key` | required | API key |
| `model` | `"deepseek-chat"` | Model name |
| `temperature` | `0.7` | Temperature (0-2) |
| `max_tokens` | `2048` | Max output tokens |
| `top_p` | `1.0` | Nucleus sampling |
| `frequency_penalty` | `0.0` | Frequency penalty (-2 to 2) |
| `presence_penalty` | `0.0` | Presence penalty (-2 to 2) |
| `system_prompt` | `"你是一个严谨的助手"` | System prompt |
| `window_title` | `"AI Chat"` | Window title |
| `window_width` | `600` | Window width |
| `window_height` | `800` | Window height |
| `window_x` | `300` | Window X position |
| `window_y` | `300` | Window Y position |

## System Messages

Set custom system prompts:

```python
# Replace all system messages
chat.set_system_messages([
    {"role": "system", "content": "You are a Python expert"},
    {"role": "system", "content": "Provide code examples"}
])

# Add single system message
chat.add_system_message("You are now a creative writer")
```

## Quick Launch with System Messages

```python
ChatWindow.launch(
    base_url="https://api.deepseek.com/v1",
    api_key="your_api_key",
    model="deepseek-coder",
    system_messages=[
        {"role": "system", "content": "You are a Python expert"},
        {"role": "system", "content": "Keep answers concise with code"}
    ],
    window_title="Python Assistant"
)
```

## Features

- **Streaming responses**: Real-time token-by-token display
- **Stop generation**: Button toggles between "发送" (Send) and "停止" (Stop)
- **Message history**: Maintains conversation context
- **Enter to send**: Press Enter in input field to send message
- **System messages**: Support for multiple system prompts

## Requirements

- `PyQt5` - GUI framework
- `openai` - OpenAI-compatible API client

## API Reference

### ChatWindow

| Method | Description |
|---------|-------------|
| `__init__(config)` | Initialize with ChatConfig |
| `set_system_messages(messages)` | Replace all system messages |
| `add_system_message(content)` | Add single system message |
| `run()` | Show window and start event loop |
| `launch(base_url, api_key, ...)` | Class method to quickly launch chat window |

### ChatConfig

Dataclass for window and LLM configuration. All parameters optional except `base_url` and `api_key`.
