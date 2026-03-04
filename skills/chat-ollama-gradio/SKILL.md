---
name: pywayne-llm-chat-ollama-gradio
description: Gradio-based chat interface for Ollama with multi-session management. Use when working with pywayne.llm.chat_ollama_gradio module to create a web-based chat UI that connects to Ollama models, supports multiple chat sessions, model selection, and streaming responses. Integrates with ChatManager for session management.
---

# Pywayne Chat Ollama Gradio

This module provides a Gradio-based web chat interface for Ollama models with multi-session support.

## Quick Start

```python
from pywayne.llm.chat_ollama_gradio import OllamaChatGradio

# Create and launch chat interface
app = OllamaChatGradio(
    base_url="http://localhost:11434/v1",
    server_port=7870
)
app.launch()
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_url` | `"http://localhost:11434/v1"` | Ollama API base URL |
| `server_name` | `"0.0.0.0"` | Server host name |
| `server_port` | `7870` | Server port |
| `root_path` | `""` | Root path for reverse proxy |
| `api_key` | `"ollama"` | API key (for Ollama compatibility) |

## Model Discovery

Automatically discovers available Ollama models by running `ollama list`:

- Excludes models with 'embed' in the name
- Falls back to `qwen2.5:0.5b` if no models found

## Session Management

### Creating New Sessions

```python
# UI method: Click "新建会话" button
new_chat_id, new_history, new_choices = app.create_new_chat()
```

### Switching Sessions

```python
# UI method: Select from "历史会话" radio list
history = app.switch_chat(selected_chat_id)
```

## API Reference

### OllamaChatGradio

| Method | Description |
|---------|-------------|
| `get_ollama_models()` | Get list of available Ollama models |
| `init_chat_manager()` | Initialize ChatManager instance |
| `create_new_chat()` | Create new chat session, returns (chat_id, history, radio_update) |
| `switch_chat(chat_id)` | Switch to specified chat session |
| `format_history(history)` | Format history for display |
| `chat(message, history, model_name)` | Process chat message with streaming |
| `create_demo()` | Create Gradio interface |
| `launch()` | Launch Gradio server |

## UI Components

| Component | Description |
|-----------|-------------|
| `chatbot` | Main chat display area |
| `msg` | Message input textbox |
| `model_dropdown` | Model selection dropdown |
| `chat_id_text` | Current session ID (read-only) |
| `new_chat_btn` | Button to create new session |
| `chat_history_list` | Radio list for session switching |

## Requirements

- `gradio` - Web UI framework
- `pywayne.llm.chat_bot` - ChatManager and LLMConfig
- `ollama` CLI - Must be installed and accessible

## Notes

- Uses ChatManager for multi-session support
- Streaming responses update UI in real-time
- Session history persists in memory (not persistent)
- Requires Ollama to be running before launching
