# Twilio WebSocket Setup

## What is WebSocket?

**WebSocket** is a persistent, bidirectional connection between your server and Twilio. This allows:
- Real-time audio streaming (phone call audio comes to you)
- You process it (transcribe, think, generate response)
- Send audio back in real-time

Without WebSocket, you'd be limited to playing pre-recorded audio.

## Architecture

```
Your Phone Call:
  ↓
Twilio Phone Network
  ↓
Twilio Service (dials number, gets answer)
  ↓
TwiML Response: "Connect to WebSocket at ws://my-server/media-stream"
  ↓
WebSocket Connection Established
  ↓
Audio Streams from both parties → Your Server
  ↓
Your Server Processes:
  - Groq Whisper: Transcribe what they said
  - Haiku: Think of response
  - ElevenLabs: Generate audio response
  ↓
Audio Streams Back to Twilio
  ↓
Twilio Plays Audio to Other Party
```

## Setup Steps

### 1. Start the WebSocket Server

```bash
node universal-voice-agent/scripts/websocket-server.js
```

Output:
```
🚀 WebSocket server running on port 5000
📍 Webhook URL: http://localhost:5000/call-webhook
🔌 WebSocket URL: wss://localhost:5000/media-stream
```

### 2. Expose Server to Internet (ngrok)

Twilio needs to reach your server from the internet. Use **ngrok** (free):

```bash
# Install ngrok
brew install ngrok

# Start ngrok, expose port 5000
ngrok http 5000
```

Output:
```
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
```

### 3. Update Twilio Configuration

Go to Twilio Console → Phone Numbers → Your Number → Voice Configuration

Set:
- **Webhook URL**: `https://abc123.ngrok.io/call-webhook`
- **HTTP Method**: POST

### 4. Make a Call

```bash
curl -X POST http://localhost:5000/make-call \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+1-555-123-4567",
    "goal": "Order 2 large pepperonis"
  }'
```

The server will:
1. Dial the number
2. When they answer, connect them to your WebSocket
3. Stream audio in real-time

## Real-Time Processing Pipeline

### Step 1: Receive Audio from Twilio

```javascript
ws.on('message', (message) => {
  const data = JSON.parse(message);
  if (data.event === 'media') {
    // Audio payload from other party
    const audioBase64 = data.media.payload;
    session.audioBuffer.push(audioBase64);
  }
});
```

### Step 2: Transcribe with Groq

```javascript
const transcription = await transcribeWithGroq(audioBase64);
// e.g., "Sure, what size?"
```

### Step 3: Haiku Thinks

```javascript
const response = await thinkWithHaiku(
  goal,
  conversationHistory,
  transcription
);
// e.g., "Large, please"
```

### Step 4: Generate Audio with ElevenLabs

```javascript
const audioBase64 = await generateSpeechWithElevenLabs(response);
```

### Step 5: Send Back to Twilio

```javascript
session.ws.send(JSON.stringify({
  event: 'media',
  sequenceNumber: turnNumber,
  media: {
    payload: audioBase64
  }
}));
```

## Implementation Steps (Pseudo-code)

In `scripts/websocket-server.js`, the `processAudio()` function needs to implement this:

```javascript
async function processAudio(session) {
  // 1. Get audio buffer
  const audioBuffer = session.audioBuffer;
  session.audioBuffer = []; // Clear

  // 2. Transcribe
  const transcript = await groqWhisper(audioBuffer);
  if (!transcript) return; // Silent, skip

  session.recordMessage('other', transcript);
  console.log(`🔊 Them: ${transcript}`);

  // 3. Check timeout
  const timeout = session.checkTimeout();
  if (timeout.checkIn) {
    const response = "Hello? Are you still there?";
    session.recordMessage('you', response);
    console.log(`🎤 You: ${response}`);
    
    const audio = await elevenLabsTTS(response);
    sendAudioToTwilio(session, audio);
    return;
  }
  if (timeout.timeout) {
    console.log(`⏰ Call timeout: ${timeout.reason}`);
    session.ws.close();
    return;
  }

  // 4. Think
  const response = await haikuThink({
    goal: session.goal,
    history: session.conversationHistory,
    lastMessage: transcript
  });

  session.recordMessage('you', response);
  console.log(`🎤 You: ${response}`);

  // 5. Check if goal achieved
  if (isSpeechLike(response, ['thank', 'goodbye', 'confirm'])) {
    session.goalAchieved = true;
  }

  // 6. Speak
  const audio = await elevenLabsTTS(response);
  sendAudioToTwilio(session, audio);
}
```

## Audio Format

Twilio sends audio as:
- **Codec**: μ-law (mu-law) or PCM
- **Sample Rate**: 8000 Hz (standard phone audio)
- **Channels**: Mono
- **Frame Rate**: ~20ms chunks

Groq expects: WAV or raw audio files
ElevenLabs outputs: MP3 or WAV

You'll need to convert between formats.

## Troubleshooting

### WebSocket Won't Connect
- Check ngrok is running: `ngrok http 5000`
- Check webhook URL in Twilio console matches ngrok URL
- Check firewall allows port 5000

### No Audio Coming Through
- Check `ws.on('message')` is firing
- Verify audio payload is not null/empty
- Check Groq API key is valid

### Audio Doesn't Play Back
- Check `sendAudioToTwilio()` is being called
- Verify audio format matches Twilio's expected codec
- Check WebSocket connection is still open (ws.readyState === 1)

### Latency Issues
- Keep Groq → Haiku → ElevenLabs pipeline under 2 seconds
- Reduce Haiku prompt complexity
- Use streaming for faster responses

## Production Deployment

For production, instead of ngrok:

1. Deploy server to cloud (AWS, Google Cloud, Heroku)
2. Get permanent HTTPS domain
3. Update Twilio webhook to production URL
4. Monitor WebSocket connections and latency
5. Set up logging/alerting

Example: Deploy to Heroku:
```bash
heroku create my-voice-agent
git push heroku main
# Update Twilio webhook to: https://my-voice-agent.herokuapp.com/call-webhook
```
