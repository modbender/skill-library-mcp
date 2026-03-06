# Voice Calling v1.1 — "Frank Calls Chad"

## Architecture

```
Frank (OpenClaw) → Twilio API → Chad's Phone
                      ↕ (bidirectional WebSocket)
              Node.js Media Server
                ↕               ↕
    ElevenLabs TTS          ElevenLabs STT
    (Frank speaks)          (Chad's voice → text)
                ↕
          Claude API
      (generates responses)
```

## Flow

1. **Initiate**: Frank triggers outbound call via Twilio REST API to Chad's phone
2. **Connect**: Twilio opens bidirectional WebSocket (Media Streams) to our server
3. **Listen**: Chad's audio streams in → ElevenLabs Realtime STT transcribes
4. **Think**: Transcribed text → Claude API for response generation
5. **Speak**: Claude's response → ElevenLabs WebSocket TTS → audio back to Twilio → Chad hears Frank
6. **Log**: Everything stored in Voice skill DB (conversations + transcripts)

## Components

### 1. Call Server (`call-server.js`)
- Fastify HTTP + WebSocket server
- POST `/outbound` — triggers call via Twilio
- GET `/incoming-call` — returns TwiML with `<Connect><Stream>` for bidirectional audio
- WS `/media-stream` — handles bidirectional audio proxy

### 2. Audio Pipeline (`audio-pipeline.js`)
- Receives mulaw 8kHz audio from Twilio WebSocket
- Streams to ElevenLabs Realtime STT WebSocket
- Receives transcription events
- Sends text to Claude API
- Streams Claude response to ElevenLabs TTS WebSocket
- Receives audio chunks back
- Sends audio to Twilio WebSocket (plays on call)

### 3. CLI Extension (`cli-call.js`)
- `voice call start` — initiate call to configured number
- `voice call end` — hang up active call
- `voice call status` — check if call is active

### 4. Integration with Voice v1
- Automatically creates conversation record on call start
- Streams transcripts into existing transcript table
- Logs call metadata (duration, Twilio SID, cost)

## Dependencies
- `twilio` — Twilio Node SDK
- `ws` — WebSocket client for ElevenLabs
- `fastify` — HTTP server
- `@fastify/websocket` — WS support

## Environment Variables
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER` — Twilio number to call FROM
- `CHAD_PHONE_NUMBER` — Chad's number to call TO
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID` — Frank's voice
- `ANTHROPIC_API_KEY` — for conversation responses

## Twilio Pricing (US)
- Phone number: ~$1.15/mo
- Outbound calls: ~$0.014/min
- Media Streams: included with call
- Very cheap for our use case

## ElevenLabs
- TTS WebSocket: streaming, low latency
- Realtime STT: WebSocket-based, streaming transcription
- Both support real-time bidirectional audio

## MVP Scope
1. Frank can call Chad's phone
2. Bidirectional conversation (Frank speaks with ElevenLabs voice, hears Chad via STT)
3. Full transcript logged to Voice DB
4. CLI commands to start/end/check calls
5. Greeting message on connect

## NOT in MVP
- Inbound calls (Chad calls Frank)
- Multi-party calls
- Scheduled calls
- Call recording storage (just transcripts)
