---
name: voice-agent-builder
description: Build and manage Voice AI agents using Vapi, Bland.ai, or Retell. Create agents, configure voices, set prompts, make outbound calls, and retrieve transcripts. Includes platform comparison guide. Use when building phone agents, IVR systems, or voice-first customer service.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+, Vapi API key
metadata: {"openclaw": {"emoji": "\ud83d\udde3\ufe0f", "requires": {"env": ["VAPI_API_KEY"]}, "primaryEnv": "VAPI_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# Voice Agent Builder

Build, configure, and manage Voice AI agents. Supports **Vapi** (primary), **Bland.ai**, and **Retell** platforms.

## Quick Start

```bash
export VAPI_API_KEY="your-vapi-api-key"

# Create a voice agent
python3 {baseDir}/scripts/vapi_agent.py create-agent '{"name":"Sales Agent","firstMessage":"Hi! How can I help you today?","systemPrompt":"You are a helpful sales assistant for Acme Corp."}'

# Make an outbound call
python3 {baseDir}/scripts/vapi_agent.py call '{"assistantId":"asst_xxx","phoneNumberId":"pn_xxx","customer":{"number":"+15551234567"}}'

# List agents
python3 {baseDir}/scripts/vapi_agent.py list-agents

# List calls
python3 {baseDir}/scripts/vapi_agent.py list-calls
```

## Platform Comparison

| Feature | Vapi | Bland.ai | Retell |
|---------|------|----------|--------|
| **Best For** | Custom agents, dev-friendly | Simple outbound campaigns | Enterprise, low latency |
| **Latency** | ~800ms | ~500ms | ~500ms |
| **Languages** | 100+ | 30+ | 30+ |
| **Custom LLM** | ✅ Any OpenAI-compatible | ✅ Limited | ✅ Via API |
| **Phone Numbers** | Buy/import | Buy/import | Buy/import |
| **Pricing** | $0.05/min + provider costs | $0.09/min all-in | $0.07-0.15/min |
| **WebSocket** | ✅ | ❌ | ✅ |
| **Knowledge Base** | ✅ Built-in | ✅ | ✅ |
| **Transfers** | ✅ | ✅ | ✅ |

**Recommendation:** Start with **Vapi** — most flexible, best docs, largest community. Use **Bland** for simple high-volume outbound. Use **Retell** for enterprise low-latency needs.

See `{baseDir}/scripts/voice_comparison.md` for detailed breakdown.

## Agent Creation Workflow

### 1. Choose a Voice
Vapi supports multiple TTS providers:
- **ElevenLabs** — Best quality, most natural (recommended)
- **PlayHT** — Good quality, lower cost
- **Deepgram** — Fast, good for real-time
- **Azure** — Enterprise, many languages

### 2. Configure the Agent
```json
{
  "name": "Appointment Setter",
  "firstMessage": "Hi! This is Sarah from Dr. Smith's office. I'm calling to help you schedule your appointment.",
  "systemPrompt": "You are Sarah, a friendly appointment scheduler...",
  "voice": {
    "provider": "11labs",
    "voiceId": "21m00Tcm4TlvDq8ikWAM"
  },
  "model": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7
  },
  "endCallFunctionEnabled": true,
  "maxDurationSeconds": 300,
  "silenceTimeoutSeconds": 30
}
```

### 3. Prompt Engineering for Voice

Voice prompts differ from text. Key principles:
- **Keep responses SHORT** — 1-2 sentences max per turn
- **Be conversational** — use filler words naturally ("Sure thing!", "Got it!")
- **Handle interruptions** — voice agents get cut off, design for it
- **Confirm understanding** — repeat back key info (names, numbers, dates)
- **Include fallback** — "I didn't catch that, could you repeat?"

### 4. Phone Number Setup
```bash
# List available phone numbers
python3 {baseDir}/scripts/vapi_agent.py list-phones

# Buy a number (via Vapi dashboard or API)
# Import existing number (Twilio, Vonage)
python3 {baseDir}/scripts/vapi_agent.py import-phone '{"provider":"twilio","number":"+15551234567","twilioAccountSid":"AC...","twilioAuthToken":"..."}'
```

### 5. Call Handling

**Outbound calls:**
```bash
python3 {baseDir}/scripts/vapi_agent.py call '{"assistantId":"asst_xxx","phoneNumberId":"pn_xxx","customer":{"number":"+15551234567"}}'
```

**Inbound:** Assign agent to phone number in Vapi dashboard, or via API:
```bash
python3 {baseDir}/scripts/vapi_agent.py update-phone '{"id":"pn_xxx","assistantId":"asst_xxx"}'
```

## Integration Patterns

### Voice + CRM (GHL)
1. Voice agent qualifies lead on call
2. Use Vapi's `serverUrl` webhook to capture call data
3. On call end → create/update GHL contact
4. Move opportunity to appropriate pipeline stage
5. Schedule follow-up if needed

### Voice + Calendar Booking
1. Agent checks availability via calendar API
2. Uses function calling to book appointment
3. Confirms date/time verbally
4. Sends SMS confirmation after call

### Voice + Knowledge Base
Upload documents to Vapi's knowledge base for RAG:
```bash
python3 {baseDir}/scripts/vapi_agent.py create-kb '{"name":"Product FAQ","files":["faq.pdf"]}'
```

## Available Commands

```bash
python3 {baseDir}/scripts/vapi_agent.py create-agent '{...}'     # Create new agent
python3 {baseDir}/scripts/vapi_agent.py get-agent <id>            # Get agent details
python3 {baseDir}/scripts/vapi_agent.py list-agents               # List all agents
python3 {baseDir}/scripts/vapi_agent.py update-agent <id> '{...}' # Update agent
python3 {baseDir}/scripts/vapi_agent.py delete-agent <id>         # Delete agent
python3 {baseDir}/scripts/vapi_agent.py call '{...}'              # Make outbound call
python3 {baseDir}/scripts/vapi_agent.py get-call <id>             # Get call details
python3 {baseDir}/scripts/vapi_agent.py list-calls                # List all calls
python3 {baseDir}/scripts/vapi_agent.py list-phones               # List phone numbers
python3 {baseDir}/scripts/vapi_agent.py import-phone '{...}'      # Import phone number
python3 {baseDir}/scripts/vapi_agent.py update-phone '{...}'      # Update phone config
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
