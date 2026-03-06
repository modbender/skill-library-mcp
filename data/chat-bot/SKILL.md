---
name: pywayne-llm-chat-bot
description: LLM chat interface using OpenAI-compatible APIs with streaming support and session management. Use when working with pywayne.llm.chat_bot module for creating LLM chat instances with custom configuration, managing multi-turn conversations with history, handling streaming responses, or managing multiple chat sessions with ChatManager
---

# Pywayne LLM Chat Bot

This module provides a synchronous LLM chat interface compatible with OpenAI APIs (including local servers like Ollama).

## Quick Start

```python
from pywayne.llm.chat_bot import LLMChat

# Create chat instance
chat = LLMChat(
    base_url="https://api.example.com/v1",
    api_key="your_api_key",
    model="deepseek-chat"
)

# Single-turn conversation (non-streaming)
response = chat.ask("Hello, LLM!", stream=False)
print(response)

# Streaming response
for token in chat.ask("Explain recursion", stream=True):
    print(token, end='', flush=True)
```

## Multi-turn Conversation

```python
# Use chat() for history tracking
for token in chat.chat("What is a class in Python?"):
    print(token, end='', flush=True)

# Continuation - remembers previous context
for token in chat.chat("How do I define a constructor?"):
    print(token, end='', flush=True)

# View history
for msg in chat.history:
    print(f"{msg['role']}: {msg['content']}")

# Clear history
chat.clear_history()
```

## Configuration

### LLMConfig Class

```python
from pywayne.llm.chat_bot import LLMConfig

config = LLMConfig(
    base_url="https://api.example.com/v1",
    api_key="your_api_key",
    model="deepseek-chat",
    temperature=0.7,
    max_tokens=8192,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    system_prompt="You are a helpful assistant"
)

chat = LLMChat(**config.to_dict())
```

### Dynamic System Prompt Update

```python
chat.update_system_prompt("You are now a Python expert, provide code examples")
```

## Managing Multiple Sessions

```python
from pywayne.llm.chat_bot import ChatManager

manager = ChatManager(
    base_url="https://api.example.com/v1",
    api_key="your_api_key",
    model="deepseek-chat",
    timeout=300  # Session timeout in seconds
)

# Get or create chat instance (maintains per-session history)
chat1 = manager.get_chat("user1")
chat2 = manager.get_chat("user2")

# Sessions are independent
chat1.chat("Hello from user1")
chat2.chat("Hello from user2")

# Remove a session
manager.remove_chat("user1")
```

### Custom Configuration per Session

```python
custom_config = LLMConfig(
    base_url=base_url,
    api_key=api_key,
    model="deepseek-chat",
    temperature=0.9,
    system_prompt="You are a creative writer"
)

chat3 = manager.get_chat("user3", config=custom_config)
```

## API Reference

### LLMChat

| Method | Description |
|--------|-------------|
| `ask(prompt, stream=False)` | Single-turn conversation without history |
| `chat(prompt, stream=True)` | Multi-turn conversation with history tracking |
| `update_system_prompt(prompt)` | Update system prompt in-place |
| `clear_history()` | Clear conversation history (keeps system prompt) |
| `history` (property) | Get copy of current conversation history |

### ChatManager

| Method | Description |
|--------|-------------|
| `get_chat(chat_id, stream=True, config=None)` | Get or create chat instance by ID |
| `remove_chat(chat_id)` | Remove chat session |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_url` | required | API base URL (e.g., `https://api.deepseek.com/v1`) |
| `api_key` | required | API authentication key |
| `model` | `"deepseek-chat"` | Model name |
| `temperature` | `0.7` | Controls randomness (0-2) |
| `max_tokens` | `2048`/`8192` | Maximum output tokens |
| `top_p` | `1.0` | Nucleus sampling (0-1) |
| `frequency_penalty` | `0.0` | Reduces repetition (-2 to 2) |
| `presence_penalty` | `0.0` | Encourages new topics (-2 to 2) |
| `system_prompt` | `"你是一个严谨的助手"` | System message |
| `timeout` | `inf` | Session timeout in seconds (ChatManager only) |
