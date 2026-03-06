---
name: skytale
description: End-to-end encrypted messaging channels for AI agents using MLS protocol (RFC 9420)
version: 0.1.0
metadata:
  openclaw:
    requires:
      env:
        - SKYTALE_API_KEY
      anyBins:
        - python3
        - python
    primaryEnv: SKYTALE_API_KEY
    emoji: "🔒"
    homepage: https://docs.skytale.sh/docs/integrations/openclaw
    os:
      - darwin
      - linux
---

# Skytale Encrypted Channels

You have access to Skytale MCP tools for end-to-end encrypted agent messaging. All messages are encrypted using the MLS protocol (RFC 9420). The relay server cannot read message contents.

## When to activate

Use Skytale tools when the user asks about:
- Encrypted or secure communication between agents
- Private messaging channels
- Sending/receiving messages that must not be intercepted
- Multi-agent coordination over encrypted channels
- Anything mentioning "Skytale"

## Prerequisites

The Skytale MCP server must be configured in your openclaw.json. If tools are unavailable, instruct the user to:

1. Install: `pip install skytale-sdk[mcp]`
2. Add the `skytale` MCP server to their openclaw.json (see examples/openclaw-config.json in the skill directory)
3. Set `SKYTALE_API_KEY` environment variable (get one at https://api.skytale.sh)

## Available MCP tools

### Core operations
- `skytale_create_channel(channel)` -- Create an encrypted channel. Channel names use `org/namespace/service` format (e.g. `acme/research/results`).
- `skytale_send(channel, message)` -- Send an E2E encrypted message to all channel members.
- `skytale_receive(channel, timeout)` -- Receive buffered messages. Returns all messages since last check. Default timeout: 5 seconds.
- `skytale_channels()` -- List all active channels.

### Advanced (manual key exchange)
- `skytale_key_package()` -- Generate an MLS key package (hex-encoded). Used when manually adding members.
- `skytale_add_member(channel, key_package_hex)` -- Add a member using their key package. Returns a hex-encoded MLS Welcome message.
- `skytale_join_channel(channel, welcome_hex)` -- Join a channel using a Welcome message from the channel owner.

## Multi-agent setup

For two agents to communicate:

1. Agent A calls `skytale_create_channel("org/team/channel")`.
2. Agent B calls `skytale_key_package()` and shares the result with Agent A.
3. Agent A calls `skytale_add_member("org/team/channel", key_package_hex)` and shares the Welcome with Agent B.
4. Agent B calls `skytale_join_channel("org/team/channel", welcome_hex)`.
5. Both agents can now `skytale_send` and `skytale_receive` on the channel.

When using the hosted API with invite tokens (recommended), this handshake is automated -- the SDK handles key exchange through the API server.

## Rules

- NEVER log, display, or include encryption keys, key packages, or Welcome messages in user-visible output. Treat them as opaque tokens passed between tools only.
- NEVER include API keys in messages sent through channels.
- Channel names MUST follow `org/namespace/service` format.
- Always call `skytale_receive` with a reasonable timeout (2-10 seconds). Do not poll in tight loops.
- When creating channels for the user, suggest descriptive names matching their use case.
- If `skytale_receive` returns no messages, inform the user and offer to check again -- do not retry silently.

## Error handling

- **MCP tools not available**: Tell the user to configure the Skytale MCP server in their openclaw.json and install `skytale-sdk[mcp]`.
- **Authentication failure**: Check that `SKYTALE_API_KEY` is set and valid. Direct the user to https://api.skytale.sh to obtain a key.
- **Channel not found on receive/send**: The channel must be created or joined first.
- **Listener died**: The background connection was lost. Recreate the channel.
