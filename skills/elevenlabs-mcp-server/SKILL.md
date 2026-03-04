---
name: elevenlabs-mcp-server
description: Provides a full suite of ElevenLabs audio tools (TTS, SFX, Music, etc.) via a standard MCP server. This skill starts the server and makes the tools available to the agent.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🛠️"
    tags: ["elevenlabs", "mcp", "server", "tools", "audio"]
---

# ElevenLabs MCP Server

This skill provides a comprehensive suite of **24 audio tools** from ElevenLabs, exposed through a standard Model Context Protocol (MCP) server. When this skill is used, it starts the server, allowing the agent to directly call powerful audio generation and manipulation capabilities.

## When to Use

This skill should be loaded by an agent platform (like OpenClaw) at startup. It is not meant to be called directly in a conversation but rather to **provide the tools** that other skills or the agent itself will use.

- **For Agent Developers**: Include this skill in your agent's default toolkit to give it a full range of audio abilities.
- **For Users**: You don't need to call this skill directly. Instead, use a skill like `audio-conductor` which will intelligently use the tools provided by this server.

## How It Works

1.  **Server Initialization**: When the skill is loaded, it executes the `tools/start_server.sh` script.
2.  **Environment Setup**: The script sets the `ELEVENLABS_API_KEY` from the agent's environment variables.
3.  **Start MCP Server**: It launches the `elevenlabs-mcp` server process in the background on a designated port (e.g., 8124).
4.  **Tool Registration**: The server automatically registers all 24 of its tools (e.g., `text_to_speech`, `compose_music`) with the agent's MCP client.
5.  **Ready for Use**: The agent can now see and call these tools directly as part of its decision-making process.

## Provided Tools (Partial List)

| Tool Name | Description |
| :--- | :--- |
| `text_to_speech` | Converts text to speech. |
| `text_to_sound_effects` | Generates a sound effect from a description. |
| `compose_music` | Creates a full music track from a prompt. |
| `voice_clone` | Clones a voice from audio samples. |
| `speech_to_text` | Transcribes audio to text. |
| `search_voices` | Searches for available voices. |

For a full list, see the `references/tool_list.md`.

## Usage in Other Skills

An orchestrator skill like `audio-conductor` would use these tools like this (conceptual example):

```python
# Inside audio-conductor logic
if audio_type == 'sfx':
    # Directly call the MCP tool provided by this server
    result = await mcp.call_tool('text_to_sound_effects', {'text': prompt})
```

## References

- **[tool_list.md](references/tool_list.md)**: A complete list and description of all 24 tools provided by the server.
- **[start_server.sh](tools/start_server.sh)**: The script responsible for launching the MCP server.
