# Ringez API - Quick Start Guide for AI Developers
## Get Your AI Agent Calling in 15 Minutes

---

## 🎯 What You'll Build

By the end of this guide, your AI agent will be able to:
- ✅ Make international phone calls
- ✅ Transcribe conversations in real-time
- ✅ Detect caller intent and sentiment
- ✅ Route calls intelligently
- ✅ Handle callbacks and webhooks

---

## 📋 Prerequisites

- Basic knowledge of REST APIs
- Python 3.8+ or Node.js 14+ installed
- A Ringez API account ([sign up here](https://ringez.com/api/signup))

---

## Step 1: Get Your API Key (2 minutes)

1. Sign up at https://ringez.com/api/signup
2. Verify your email
3. Navigate to Dashboard → API Keys
4. Generate a new API key
5. Save your key securely: `sk_live_xxxxxxxxxxxx`

```bash
# Set as environment variable
export RINGEZ_API_KEY="sk_live_your_key_here"
```

---

## Step 2: Install SDK (1 minute)

### Python
```bash
pip install ringez-sdk
```

### Node.js
```bash
npm install @ringez/sdk
```

### Direct REST API
No installation needed - just use `curl` or your HTTP client.

---

## Step 3: Make Your First Call (5 minutes)

### Python Example

```python
from ringez import RingezClient
import os

# Initialize client
client = RingezClient(api_key=os.getenv('RINGEZ_API_KEY'))

# Create a session
session = client.sessions.create({
    "session_type": "authenticated",
    "user_consent": {
        "calling_authorized": True,
        "privacy_mode": False
    }
})

print(f"Session created: {session.id}")
print(f"Balance: {session.wallet_balance.minutes} minutes")

# Make a call
call = client.calls.initiate({
    "session_id": session.id,
    "to_number": "+14155551234",  # Replace with actual number
    "from_number": "+12025551000",
    "call_settings": {
        "transcribe": True,
        "max_duration": 300
    }
})

print(f"Call initiated: {call.id}")
print(f"Status: {call.status}")

# Monitor call status
import time
while True:
    status = client.calls.get(call.id)
    print(f"Current status: {status.status}")
    
    if status.status in ["completed", "failed"]:
        print(f"Call ended. Duration: {status.duration}s")
        print(f"Cost: ${status.cost.amount}")
        break
    
    time.sleep(2)
```

### Node.js Example

```javascript
const Ringez = require('@ringez/sdk');

const client = new Ringez({
  apiKey: process.env.RINGEZ_API_KEY
});

async function makeFirstCall() {
  try {
    // Create session
    const session = await client.sessions.create({
      sessionType: 'authenticated',
      userConsent: {
        callingAuthorized: true,
        callingAuthorized: true,
        privacyMode: false
      }
    });

    console.log(`Session: ${session.id}`);
    console.log(`Balance: ${session.walletBalance.minutes} minutes`);

    // Make call
    const call = await client.calls.initiate({
      sessionId: session.id,
      toNumber: '+14155551234', // Replace with actual number
      fromNumber: '+12025551000',
      settings: {
        transcribe: true,
        maxDuration: 300
      }
    });

    console.log(`Call initiated: ${call.id}`);

    // Monitor status
    const checkStatus = setInterval(async () => {
      const status = await client.calls.get(call.id);
      console.log(`Status: ${status.status}`);

      if (['completed', 'failed'].includes(status.status)) {
        console.log(`Duration: ${status.duration}s`);
        console.log(`Cost: $${status.cost.amount}`);
        clearInterval(checkStatus);
      }
    }, 2000);

  } catch (error) {
    console.error('Error:', error.message);
  }
}

makeFirstCall();
```

### cURL Example

```bash
# Create session
curl -X POST https://ringez-api.vercel.app/api/v1/sessions/create \
  -H "Authorization: Bearer $RINGEZ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_type": "authenticated",
    "user_consent": {
      "calling_authorized": true
    }
  }'

# Response: {"session_id": "sess_abc123", ...}

# Initiate call
curl -X POST https://ringez-api.vercel.app/api/v1/calls/initiate \
  -H "Authorization: Bearer $RINGEZ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123",
    "to_number": "+14155551234",
    "from_number": "+12025551000",
    "call_settings": {
      "transcribe": true
    }
  }'

# Check status
curl https://ringez-api.vercel.app/api/v1/calls/call_xyz789 \
  -H "Authorization: Bearer $RINGEZ_API_KEY"
```

---

## Step 4: Add Wallet Credits (2 minutes)

Before making production calls, you need to add credits:

### Python
```python
# Add $15 (120 minutes)
transaction = client.wallet.add_credits({
    "session_id": session.id,
    "payment_method": "paypal",
    "plan": "popular",
    "currency": "USD",
    "amount": 15.00,
    "payment_token": "tok_from_paypal"
})

print(f"Credits added: {transaction.minutes_added} minutes")
print(f"New balance: {transaction.new_balance.minutes} minutes")
```

### Node.js
```javascript
const transaction = await client.wallet.addCredits({
  sessionId: session.id,
  paymentMethod: 'paypal',
  plan: 'popular',
  currency: 'USD',
  amount: 15.00,
  paymentToken: 'tok_from_paypal'
});

console.log(`Credits added: ${transaction.minutesAdded}`);
```

---

## Step 5: Real-Time Transcription (5 minutes)

### Python with WebSocket

```python
from ringez import RingezClient
import asyncio
import websockets
import json

client = RingezClient(api_key=os.getenv('RINGEZ_API_KEY'))

async def transcribe_call(call_id):
    # Enable transcription
    transcription = client.transcripts.enable(call_id, {
        "language": "en-US",
        "interim_results": True,
        "speaker_labels": True
    })
    
    # Connect to WebSocket
    async with websockets.connect(transcription.websocket_url) as ws:
        print("Connected to transcription stream")
        
        async for message in ws:
            data = json.loads(message)
            
            if data['type'] == 'transcript':
                speaker = data['speaker']
                text = data['text']
                confidence = data['confidence']
                
                print(f"{speaker}: {text} (confidence: {confidence:.2f})")
                
                # Process with AI
                await analyze_transcript(text)

async def analyze_transcript(text):
    # Detect intent
    intent = client.agents.detect_intent({
        "transcript_segment": text
    })
    
    if intent.intent == "escalation_request":
        print("⚠️  Customer wants to escalate!")
        # Take action...

# Usage
asyncio.run(transcribe_call("call_xyz789"))
```

### Node.js with WebSocket

```javascript
const WebSocket = require('ws');

async function transcribeCall(callId) {
  // Enable transcription
  const transcription = await client.transcripts.enable(callId, {
    language: 'en-US',
    interimResults: true,
    speakerLabels: true
  });

  // Connect WebSocket
  const ws = new WebSocket(transcription.websocketUrl);

  ws.on('open', () => {
    console.log('Connected to transcription stream');
  });

  ws.on('message', async (data) => {
    const message = JSON.parse(data);

    if (message.type === 'transcript') {
      console.log(`${message.speaker}: ${message.text}`);

      // Analyze with AI
      const intent = await client.agents.detectIntent({
        transcriptSegment: message.text
      });

      if (intent.intent === 'escalation_request') {
        console.log('⚠️  Customer wants to escalate!');
        // Transfer to supervisor
        await client.calls.transfer(callId, {
          transferTo: '+14155559999'
        });
      }
    }
  });
}

transcribeCall('call_xyz789');
```

---

## 🎓 Common Use Cases

### Use Case 1: Customer Support Bot

```python
class CustomerSupportBot:
    def __init__(self):
        self.client = RingezClient(api_key=os.getenv('RINGEZ_API_KEY'))
        
    async def handle_support_call(self, customer_number):
        # Create session
        session = self.client.sessions.create({
            "session_type": "authenticated"
        })
        
        # Call customer
        call = self.client.calls.initiate({
            "session_id": session.id,
            "to_number": customer_number,
            "call_settings": {
                "transcribe": True,
                "max_duration": 600
            }
        })
        
        # Stream transcript
        async for segment in self.client.transcripts.stream(call.id):
            # Detect sentiment
            sentiment = await self.client.agents.analyze_sentiment({
                "call_id": call.id,
                "transcript_segment": segment.text
            })
            
            if sentiment.sentiment == "negative":
                print(f"😠 Negative sentiment detected: {sentiment.score}")
                
                # Escalate if very negative
                if sentiment.score < -0.7:
                    await self.escalate_call(call.id)
    
    async def escalate_call(self, call_id):
        # Find available agent
        routing = await self.client.agents.route_call({
            "routing_criteria": {
                "department": "escalations",
                "priority": "high"
            }
        })
        
        # Transfer
        await self.client.calls.transfer(call_id, {
            "transfer_to": routing.route_to
        })
```

### Use Case 2: Appointment Reminder System

```javascript
class AppointmentReminder {
  constructor() {
    this.client = new Ringez({ apiKey: process.env.RINGEZ_API_KEY });
  }

  async sendReminders(appointments) {
    const session = await this.client.sessions.create({
      sessionType: 'authenticated'
    });

    for (const apt of appointments) {
      await this.callAndRemind(session.id, apt);
    }
  }

  async callAndRemind(sessionId, appointment) {
    const call = await this.client.calls.initiate({
      sessionId,
      toNumber: appointment.phoneNumber,
      settings: { transcribe: true }
    });

    // Play reminder message
    const audio = await this.client.agents.synthesizeVoice({
      text: `Hello, this is a reminder for your appointment on ${appointment.date} at ${appointment.time}.`,
      voice: 'en-US-Neural2-A'
    });

    await this.client.calls.playAudio(call.id, audio.audioUrl);

    // Collect confirmation
    const response = await this.client.calls.collectInput(call.id, {
      type: 'dtmf',
      prompt: 'Press 1 to confirm, 2 to reschedule',
      timeout: 10
    });

    if (response.digits === '1') {
      console.log(`✅ ${appointment.patientName} confirmed`);
    } else if (response.digits === '2') {
      console.log(`📅 ${appointment.patientName} wants to reschedule`);
    }

    await this.client.calls.hangup(call.id);
  }
}
```

### Use Case 3: Sales Outreach Bot

```python
class SalesOutreachBot:
    def __init__(self):
        self.client = RingezClient(api_key=os.getenv('RINGEZ_API_KEY'))
    
    async def run_campaign(self, leads):
        session = self.client.sessions.create({
            "session_type": "authenticated",
            "user_consent": {
            }
        })
        
        # Batch calls
        batch = await self.client.batch.calls({
            "session_id": session.id,
            "calls": [
                {
                    "to_number": lead['phone'],
                    "metadata": {"lead_id": lead['id']}
                }
                for lead in leads
            ],
            "call_settings": {
                "transcribe": True,
                "max_duration": 300
            }
        })
        
        # Monitor each call
        for call in batch.calls:
            asyncio.create_task(self.monitor_call(call.call_id))
    
    async def monitor_call(self, call_id):
        async for segment in self.client.transcripts.stream(call_id):
            # Detect buying signals
            intent = await self.client.agents.detect_intent({
                "transcript_segment": segment.text
            })
            
            if intent.intent == "interested":
                print(f"🎯 Lead interested! Call: {call_id}")
                # Schedule follow-up, send materials, etc.
```

---

## 🪝 Setting Up Webhooks

Webhooks let you receive real-time notifications about call events.

### Step 1: Create Webhook Endpoint

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_your_secret"

@app.route('/webhooks/ringez', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-Ringez-Signature')
    payload = request.data
    
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Process event
    event = request.json
    event_type = event['event']
    
    if event_type == 'call.answered':
        handle_call_answered(event['data'])
    elif event_type == 'call.completed':
        handle_call_completed(event['data'])
    
    return jsonify({"received": True}), 200

def handle_call_answered(data):
    print(f"Call {data['call_id']} was answered!")
    # Start transcription, analytics, etc.

def handle_call_completed(data):
    print(f"Call {data['call_id']} completed: {data['duration']}s")
    # Update CRM, generate report, etc.

if __name__ == '__main__':
    app.run(port=3000)
```

### Step 2: Register Webhook

```python
webhook = client.webhooks.subscribe({
    "session_id": session.id,
    "webhook_url": "https://your-domain.com/webhooks/ringez",
    "events": [
        "call.initiated",
        "call.answered",
        "call.completed",
        "transcription.updated"
    ],
    "secret": "whsec_your_secret"
})

print(f"Webhook registered: {webhook.webhook_id}")
```

---

## 🎛️ Testing with Sandbox

Use sandbox mode for testing without charges:

```python
# Initialize with test key
client = RingezClient(
    api_key="sk_test_your_test_key",
    environment="sandbox"
)

# Test numbers (automatically answer)
test_numbers = {
    "success": "+15005550006",  # Answers and stays connected
    "busy": "+15005550001",     # Returns busy signal
    "no_answer": "+15005550002" # Rings but doesn't answer
}

# Make test call
call = client.calls.initiate({
    "session_id": session.id,
    "to_number": test_numbers["success"]
})
```

---

## 📊 Monitoring & Analytics

```python
# Get call metrics
metrics = client.analytics.call_metrics({
    "session_id": session.id,
    "start_date": "2026-02-01T00:00:00Z",
    "end_date": "2026-02-05T23:59:59Z"
})

print(f"Total calls: {metrics.total_calls}")
print(f"Success rate: {metrics.success_rate * 100}%")
print(f"Average duration: {metrics.average_duration}s")
print(f"Total cost: ${metrics.total_cost}")

# Get spending analysis
spending = client.analytics.spending({
    "session_id": session.id
})

print(f"Current spend: ${spending.current_period.total_spent}")
print(f"Budget remaining: ${spending.current_period.budget_remaining}")
print(f"Projected month-end: ${spending.predictions.estimated_month_end_spend}")
```

---

## 🔒 Security Best Practices

1. **Never hardcode API keys**
   ```python
   # ❌ BAD
   client = RingezClient(api_key="sk_live_abc123")
   
   # ✅ GOOD
   client = RingezClient(api_key=os.getenv('RINGEZ_API_KEY'))
   ```

2. **Always verify webhook signatures**
   ```python
   def verify_webhook(payload, signature, secret):
       expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
       return hmac.compare_digest(signature, expected)
   ```

3. **Use HTTPS for webhooks**
   ```
   ✅ https://your-domain.com/webhooks
   ❌ http://your-domain.com/webhooks
   ```

4. **Validate phone numbers**
   ```python
   import phonenumbers
   
   def validate_number(number):
       try:
           parsed = phonenumbers.parse(number)
           return phonenumbers.is_valid_number(parsed)
       except:
           return False
   ```

---

## 🐛 Troubleshooting

### Issue: Call fails immediately
```python
# Check balance
balance = client.wallet.balance(session_id=session.id)
if balance.minutes < 1:
    print("❌ Insufficient balance")
    # Add credits...

# Validate number
validation = client.numbers.validate(phone_number="+14155551234")
if not validation.is_callable:
    print(f"❌ Number not callable: {validation.reason}")
```

### Issue: Transcription not working
```python
# Check transcription status
transcript = client.transcripts.get(call_id)
if transcript.status == "failed":
    print(f"❌ Transcription failed: {transcript.error}")

# Ensure transcription was enabled
call = client.calls.initiate({
    "session_id": session.id,
    "to_number": "+14155551234",
    "call_settings": {
        "transcribe": True  # ← Make sure this is True
    }
})
```

### Issue: Webhook not receiving events
```python
# Verify webhook is active
webhooks = client.webhooks.list(session_id=session.id)
for wh in webhooks:
    print(f"Webhook: {wh.webhook_id}, Status: {wh.status}")
    if wh.status != "active":
        print(f"⚠️  Webhook is {wh.status}")

# Check webhook delivery stats
stats = client.webhooks.get_stats(webhook_id="wh_abc123")
print(f"Success rate: {stats.successful_deliveries / stats.total_attempts * 100}%")
```

---

## 📚 Next Steps

1. **Read Full API Documentation**: https://docs.ringez.com/api
2. **Explore Example Projects**: https://github.com/ringez/examples
3. **Join Developer Community**: https://discord.gg/ringez
4. **Check Status Page**: https://status.ringez.com

---

## 💬 Get Help

- **Documentation**: https://docs.ringez.com
- **Email Support**: developers@ringez.com
- **Discord**: https://discord.gg/ringez
- **GitHub Issues**: https://github.com/ringez/sdk/issues

---

## 🎉 You're Ready!

You now have everything you need to integrate Ringez into your AI agent. Start building amazing voice-powered applications!

**Happy Calling! 📞**
