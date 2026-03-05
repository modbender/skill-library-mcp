---
name: livekit
description: Build voice AI agents with LiveKit. Use when developing realtime voice applications, voice agent pipelines (STT-LLM-TTS), WebRTC communication, or deploying conversational AI. Covers LiveKit Agents SDK, provider selection (Deepgram, OpenAI, ElevenLabs, Cartesia), cloud vs self-hosted deployment.
---

# LiveKit Voice AI Skill

Build production voice agents with LiveKit's open-source platform.

## Quick Start

```bash
# Install SDK
pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram livekit-plugins-cartesia

# Or Node.js
npm install @livekit/agents @livekit/agents-plugin-openai
```

## Minimal Agent (Python)

```python
from livekit.agents import AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, cartesia

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    session = AgentSession(
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4.1-mini"),
        tts=cartesia.TTS(),
    )
    
    session.start(ctx.room)
    await session.say("Hello! How can I help?")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

## Provider Selection

| Component | Budget | Quality | Low Latency |
|-----------|--------|---------|-------------|
| **STT** | Deepgram Nova-3 | AssemblyAI | Deepgram Keychain |
| **LLM** | GPT-4.1 mini | Claude Sonnet | GPT-4.1 mini |
| **TTS** | Cartesia Sonic-3 | ElevenLabs | Cartesia Sonic-3 |

## Voice Pipeline vs Realtime

**STT-LLM-TTS Pipeline:**
- More control, mix providers
- Generally cheaper
- Easier to debug

**OpenAI Realtime API:**
- Speech-to-speech, more expressive
- Higher cost (~$0.10/min)
- Less control

## Environment Variables

```bash
LIVEKIT_URL=wss://your-app.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# Provider keys (if not using LiveKit Inference)
OPENAI_API_KEY=
DEEPGRAM_API_KEY=
CARTESIA_API_KEY=
ELEVENLABS_API_KEY=
```

## Tool Use

```python
from livekit.agents import function_tool

@function_tool()
async def get_weather(location: str) -> str:
    """Get current weather for a location."""
    # Your implementation
    return f"Weather in {location}: 72°F, sunny"

session = AgentSession(
    stt=deepgram.STT(),
    llm=openai.LLM(),
    tts=cartesia.TTS(),
    tools=[get_weather],
)
```

## Telephony (SIP)

```python
from livekit import api

# Outbound call
await lk_api.sip.create_sip_participant(
    api.CreateSIPParticipantRequest(
        sip_trunk_id="trunk-id",
        sip_call_to="+15551234567",
        room_name="my-room",
    )
)
```

## Deployment

**LiveKit Cloud:** `livekit-server-cli deploy --project my-project`

**Self-hosted:** 
```bash
docker run -d \
  -p 7880:7880 -p 7881:7881 -p 7882:7882/udp \
  -e LIVEKIT_KEYS="api-key: api-secret" \
  livekit/livekit-server
```

## Cost Estimates

| Scenario | Monthly Cost |
|----------|--------------|
| Dev/testing | Free tier |
| 100 hrs/mo voice | ~$150-250 |
| Production B2B | ~$300-500 |
| High volume | Self-host |

## Common Patterns

### Turn Detection
```python
session = AgentSession(
    turn_detection=openai.TurnDetection(
        threshold=0.5,
        silence_duration_ms=500,
    ),
    ...
)
```

### Interruption Handling
```python
@session.on("user_speech_started")
async def handle_interruption():
    session.stop_speaking()
```

### Multi-Agent Handoff
```python
await session.transfer_to(specialist_agent)
```

## References

- Docs: https://docs.livekit.io/agents/
- Examples: https://github.com/livekit/agents/tree/main/examples
- Playground: https://agents-playground.livekit.io
