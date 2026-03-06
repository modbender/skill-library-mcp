# Ringez AI Agent Integration Guide
## Implementation Patterns & Best Practices

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   AI Agent      │
│  (Your System)  │
└────────┬────────┘
         │
         │ HTTPS/REST
         │
┌────────▼────────┐
│  Ringez API     │
│  (ringez-api.vercel.app)│
└────────┬────────┘
         │
         ├──► Payment Gateway (PayPal/Cashfree)
         ├──► Twilio Voice (PSTN)
         ├──► WebRTC Servers
         └──► Database (MongoDB)
```

---

## 🔧 Implementation Checklist

### Phase 1: Basic Integration
- [ ] Obtain API credentials
- [ ] Set up authentication
- [ ] Test session creation
- [ ] Make test call
- [ ] Handle webhooks
- [ ] Implement error handling

### Phase 2: Advanced Features
- [ ] Real-time transcription
- [ ] Sentiment analysis
- [ ] Call routing logic
- [ ] Batch operations
- [ ] Analytics integration

### Phase 3: Production Ready
- [ ] Rate limiting
- [ ] Retry mechanisms
- [ ] Logging & monitoring
- [ ] Security hardening
- [ ] Load testing

---

## 💻 SDK Examples

### Python SDK

#### Installation
```bash
pip install ringez-sdk
```

#### Basic Usage
```python
from ringez import RingezClient, CallSettings

# Initialize client
client = RingezClient(api_key="sk_live_your_key")

# Create session
session = client.sessions.create(
    session_type="authenticated",
    user_consent={
        "calling_authorized": True,
        "privacy_mode": True
    }
)

# Make a call
call = client.calls.initiate(
    session_id=session.id,
    to_number="+14155551234",
    from_number="+12025551000",
    settings=CallSettings(
        transcribe=True,
        max_duration=600,
        record_call=False
    )
)

# Monitor call status
status = client.calls.get(call.id)
print(f"Call status: {status.status}")
print(f"Duration: {status.duration}s")
print(f"Cost: ${status.cost.amount}")

# Get transcript
transcript = client.transcripts.get(call.id)
for segment in transcript.segments:
    print(f"{segment.speaker}: {segment.text}")
```

#### Advanced: Sentiment-Aware Routing
```python
from ringez import RingezClient
from ringez.agents import SentimentAnalyzer, CallRouter

client = RingezClient(api_key="sk_live_your_key")
sentiment = SentimentAnalyzer(client)
router = CallRouter(client)

def handle_customer_call(call_id):
    # Get real-time transcript
    transcript = client.transcripts.stream(call_id)
    
    for segment in transcript:
        # Analyze sentiment
        analysis = sentiment.analyze(
            call_id=call_id,
            text=segment.text
        )
        
        # Escalate if negative
        if analysis.sentiment == "negative" and analysis.score < -0.6:
            print(f"Escalating call {call_id} due to negative sentiment")
            
            # Transfer to supervisor
            client.calls.transfer(
                call_id=call_id,
                transfer_to="+14155559999",
                reason="customer_escalation"
            )
            break
```

#### Webhook Handler (Flask)
```python
from flask import Flask, request, jsonify
from ringez.webhooks import WebhookVerifier
import hmac

app = Flask(__name__)
verifier = WebhookVerifier(secret="whsec_your_secret")

@app.route('/webhooks/ringez', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-Ringez-Signature')
    if not verifier.verify(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    payload = request.json
    event_type = payload['event']
    
    if event_type == 'call.answered':
        handle_call_answered(payload['data'])
    elif event_type == 'call.completed':
        handle_call_completed(payload['data'])
    elif event_type == 'transcription.updated':
        handle_transcription_updated(payload['data'])
    
    return jsonify({"received": True}), 200

def handle_call_answered(data):
    call_id = data['call_id']
    print(f"Call {call_id} was answered")
    # Your logic here

def handle_call_completed(data):
    call_id = data['call_id']
    duration = data['duration']
    cost = data['cost']
    print(f"Call {call_id} completed: {duration}s, ${cost}")
    # Update database, send notifications, etc.

def handle_transcription_updated(data):
    call_id = data['call_id']
    text = data['text']
    # Process transcript in real-time
    analyze_and_respond(call_id, text)
```

---

### Node.js SDK

#### Installation
```bash
npm install @ringez/sdk
```

#### Basic Usage
```javascript
const Ringez = require('@ringez/sdk');

const client = new Ringez({
  apiKey: 'sk_live_your_key',
  environment: 'production' // or 'sandbox'
});

async function makeCall() {
  try {
    // Create session
    const session = await client.sessions.create({
      sessionType: 'authenticated',
      userConsent: {
        callingAuthorized: true,
        maxSpendLimit: 10.00,
        privacyMode: true
      }
    });

    // Initiate call
    const call = await client.calls.initiate({
      sessionId: session.id,
      toNumber: '+14155551234',
      fromNumber: '+12025551000',
      settings: {
        transcribe: true,
        maxDuration: 600
      }
    });

    console.log(`Call initiated: ${call.id}`);
    
    // Monitor call
    const status = await client.calls.get(call.id);
    console.log(`Status: ${status.status}, Duration: ${status.duration}s`);

    return call;
  } catch (error) {
    console.error('Call failed:', error.message);
    throw error;
  }
}

makeCall();
```

#### Real-time Transcription with WebSockets
```javascript
const Ringez = require('@ringez/sdk');
const WebSocket = require('ws');

const client = new Ringez({ apiKey: 'sk_live_your_key' });

async function transcribeCall(callId) {
  // Enable transcription
  const transcription = await client.transcripts.enable(callId, {
    language: 'en-US',
    interimResults: true,
    speakerLabels: true
  });

  // Connect to WebSocket
  const ws = new WebSocket(transcription.websocketUrl);

  ws.on('message', (data) => {
    const message = JSON.parse(data);
    
    if (message.type === 'transcript') {
      console.log(`${message.speaker}: ${message.text}`);
      
      // Process transcript with AI
      analyzeIntent(message.text).then(intent => {
        if (intent.requiresAction) {
          handleIntent(callId, intent);
        }
      });
    }
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
}

async function analyzeIntent(text) {
  const intent = await client.agents.detectIntent({
    transcriptSegment: text
  });
  return intent;
}

async function handleIntent(callId, intent) {
  if (intent.intent === 'transfer_request') {
    await client.calls.transfer(callId, {
      transferTo: intent.suggestedParameters.department_number
    });
  }
}
```

#### Express Webhook Server
```javascript
const express = require('express');
const crypto = require('crypto');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

const WEBHOOK_SECRET = 'whsec_your_secret';

function verifyWebhook(payload, signature) {
  const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
  const digest = hmac.update(JSON.stringify(payload)).digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(digest)
  );
}

app.post('/webhooks/ringez', (req, res) => {
  const signature = req.headers['x-ringez-signature'];
  
  if (!verifyWebhook(req.body, signature)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const { event, data } = req.body;

  switch (event) {
    case 'call.initiated':
      console.log(`Call ${data.call_id} initiated`);
      break;
    case 'call.answered':
      console.log(`Call ${data.call_id} answered`);
      // Start transcription, analytics, etc.
      break;
    case 'call.completed':
      console.log(`Call ${data.call_id} completed: ${data.duration}s`);
      // Save to database, generate report
      break;
    case 'balance.low':
      console.warn(`Low balance alert: ${data.balance.minutes} minutes remaining`);
      // Notify admin, auto-recharge
      break;
  }

  res.json({ received: true });
});

app.listen(3000, () => {
  console.log('Webhook server listening on port 3000');
});
```

---

## 🤖 AI Agent Patterns

### Pattern 1: Autonomous Customer Support Agent

```python
class CustomerSupportAgent:
    def __init__(self, ringez_client):
        self.client = ringez_client
        self.intent_classifier = IntentClassifier()
        
    async def handle_incoming_call(self, call_id):
        """Handle customer support call with AI"""
        
        # Get call details
        call = self.client.calls.get(call_id)
        
        # Start transcription
        transcript_stream = self.client.transcripts.stream(call_id)
        
        conversation_context = []
        
        async for segment in transcript_stream:
            # Add to context
            conversation_context.append({
                'speaker': segment.speaker,
                'text': segment.text
            })
            
            # Detect intent
            intent = await self.detect_intent(segment.text, conversation_context)
            
            # Take action based on intent
            if intent.type == 'account_inquiry':
                await self.handle_account_inquiry(call_id, intent)
            elif intent.type == 'technical_support':
                await self.handle_technical_support(call_id, intent)
            elif intent.type == 'escalation_request':
                await self.escalate_to_human(call_id, intent)
                
    async def detect_intent(self, text, context):
        """Use AI to classify intent"""
        response = await self.client.agents.detect_intent({
            'transcript_segment': text,
            'context': {'previous_intents': [c['text'] for c in context[-3:]]}
        })
        return response
    
    async def escalate_to_human(self, call_id, intent):
        """Transfer to human agent"""
        # Get best available agent
        routing = await self.client.agents.route_call({
            'routing_criteria': {
                'department': intent.department,
                'skill_required': intent.skill,
                'priority': 'high'
            }
        })
        
        # Transfer call
        await self.client.calls.transfer(call_id, {
            'transfer_to': routing.route_to,
            'transfer_note': f"Customer needs: {intent.summary}"
        })
```

### Pattern 2: Proactive Outbound Campaign Agent

```python
class OutboundCampaignAgent:
    def __init__(self, ringez_client):
        self.client = ringez_client
        
    async def run_campaign(self, contact_list, message_template):
        """Execute outbound calling campaign"""
        
        # Create session with budget
        session = self.client.sessions.create({
            'session_type': 'authenticated',
            'user_consent': {
                'calling_authorized': True,
                'max_spend_limit': 100.00
            }
        })
        
        results = []
        
        # Process contacts in batches
        for batch in self.batch_contacts(contact_list, batch_size=10):
            batch_calls = await self.client.batch.calls({
                'session_id': session.id,
                'calls': [
                    {
                        'to_number': contact['phone'],
                        'metadata': {'contact_id': contact['id']}
                    }
                    for contact in batch
                ],
                'call_settings': {
                    'transcribe': True,
                    'max_duration': 300
                }
            })
            
            # Monitor each call
            for call in batch_calls.calls:
                result = await self.monitor_call(call.call_id, message_template)
                results.append(result)
        
        return self.generate_report(results)
    
    async def monitor_call(self, call_id, message):
        """Monitor call and collect response"""
        
        # Wait for answer
        call = await self.wait_for_status(call_id, 'answered', timeout=30)
        
        if call.status != 'answered':
            return {'call_id': call_id, 'status': 'no_answer'}
        
        # Play message (using TTS)
        audio = await self.client.agents.synthesize_voice({
            'text': message,
            'voice': 'en-US-Neural2-A'
        })
        
        await self.client.calls.play_audio(call_id, audio.audio_url)
        
        # Collect DTMF response
        response = await self.client.calls.collect_input(call_id, {
            'type': 'dtmf',
            'timeout': 10,
            'num_digits': 1
        })
        
        # Hang up
        await self.client.calls.hangup(call_id)
        
        return {
            'call_id': call_id,
            'status': 'completed',
            'response': response.digits
        }
```

### Pattern 3: Smart Call Queue Manager

```javascript
class CallQueueManager {
  constructor(ringezClient) {
    this.client = ringezClient;
    this.queue = [];
    this.activeAgents = new Map();
  }

  async addToQueue(callRequest) {
    // Validate and prioritize
    const priority = await this.calculatePriority(callRequest);
    
    this.queue.push({
      ...callRequest,
      priority,
      addedAt: new Date()
    });

    // Sort by priority
    this.queue.sort((a, b) => b.priority - a.priority);

    // Process queue
    await this.processQueue();
  }

  async calculatePriority(callRequest) {
    // Check if customer is VIP
    const customerInfo = await this.getCustomerInfo(callRequest.customerId);
    
    let priority = 0;
    
    if (customerInfo.tier === 'vip') priority += 50;
    if (callRequest.urgency === 'high') priority += 30;
    if (customerInfo.pendingIssues > 0) priority += 20;
    
    return priority;
  }

  async processQueue() {
    while (this.queue.length > 0 && this.hasAvailableAgents()) {
      const nextCall = this.queue.shift();
      const agent = await this.findBestAgent(nextCall);

      if (agent) {
        await this.assignCallToAgent(nextCall, agent);
      }
    }
  }

  async assignCallToAgent(callRequest, agent) {
    try {
      const call = await this.client.calls.initiate({
        sessionId: callRequest.sessionId,
        toNumber: callRequest.phoneNumber,
        fromNumber: agent.number,
        settings: {
          transcribe: true,
          maxDuration: 1800
        },
        metadata: {
          agentId: agent.id,
          customerId: callRequest.customerId,
          priority: callRequest.priority
        }
      });

      this.activeAgents.set(call.id, agent);

      // Monitor call completion
      this.client.webhooks.on('call.completed', (event) => {
        if (event.data.call_id === call.id) {
          this.activeAgents.delete(call.id);
          this.processQueue(); // Process next in queue
        }
      });

      return call;
    } catch (error) {
      console.error('Failed to assign call:', error);
      // Re-add to queue
      this.queue.unshift(callRequest);
    }
  }

  hasAvailableAgents() {
    return this.activeAgents.size < this.getMaxConcurrentCalls();
  }

  async findBestAgent(callRequest) {
    // Find agent with matching skills
    const agents = await this.getAvailableAgents();
    
    return agents.find(agent => {
      return agent.skills.includes(callRequest.requiredSkill) &&
             agent.language === callRequest.preferredLanguage;
    });
  }
}
```

---

## 🔐 Security Best Practices

### 1. API Key Management
```python
# ❌ DON'T: Hardcode API keys
client = RingezClient(api_key="sk_live_abc123")

# ✅ DO: Use environment variables
import os
client = RingezClient(api_key=os.getenv('RINGEZ_API_KEY'))
```

### 2. Webhook Verification
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """Verify webhook signature"""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)
```

### 3. Rate Limiting
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=3600)  # 100 calls per hour
def make_api_call(client, endpoint, data):
    return client.request(endpoint, data)
```

### 4. Input Validation
```python
import phonenumbers

def validate_phone_number(number):
    """Validate phone number before calling"""
    try:
        parsed = phonenumbers.parse(number)
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number")
        return phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164
        )
    except phonenumbers.NumberParseException:
        raise ValueError("Cannot parse phone number")
```

---

## 📊 Monitoring & Analytics

### Custom Analytics Dashboard
```python
from ringez import RingezClient
import pandas as pd
import matplotlib.pyplot as plt

client = RingezClient(api_key=os.getenv('RINGEZ_API_KEY'))

def generate_daily_report(session_id, date):
    """Generate call analytics report"""
    
    # Get call metrics
    metrics = client.analytics.call_metrics({
        'session_id': session_id,
        'start_date': f'{date}T00:00:00Z',
        'end_date': f'{date}T23:59:59Z',
        'group_by': 'hour'
    })
    
    # Convert to DataFrame
    df = pd.DataFrame(metrics['breakdown']['by_hour'])
    
    # Plot call volume
    plt.figure(figsize=(12, 6))
    plt.plot(df['hour'], df['total_calls'])
    plt.title('Call Volume by Hour')
    plt.xlabel('Hour')
    plt.ylabel('Number of Calls')
    plt.savefig(f'call_report_{date}.png')
    
    # Calculate key metrics
    report = {
        'total_calls': metrics['metrics']['total_calls'],
        'success_rate': metrics['metrics']['success_rate'],
        'avg_duration': metrics['metrics']['average_duration'],
        'total_cost': metrics['metrics']['total_cost'],
        'peak_hour': df.loc[df['total_calls'].idxmax(), 'hour']
    }
    
    return report
```

### Real-time Call Quality Monitoring
```javascript
class CallQualityMonitor {
  constructor(ringezClient) {
    this.client = ringezClient;
    this.qualityThreshold = 3.5; // MOS score threshold
  }

  async monitorCall(callId) {
    const interval = setInterval(async () => {
      const call = await this.client.calls.get(callId);
      
      if (call.status !== 'in-progress') {
        clearInterval(interval);
        return;
      }

      const quality = call.quality_metrics;

      if (quality.mos_score < this.qualityThreshold) {
        console.warn(`Low quality detected: MOS ${quality.mos_score}`);
        
        // Alert and attempt recovery
        await this.handleLowQuality(callId, quality);
      }

      // Check for high packet loss
      if (quality.packet_loss > 0.05) {
        console.error(`High packet loss: ${quality.packet_loss * 100}%`);
      }
    }, 5000); // Check every 5 seconds
  }

  async handleLowQuality(callId, quality) {
    // Log quality issue
    await this.client.calls.reportIssue(callId, {
      type: 'quality',
      metrics: quality
    });

    // Optionally switch codec or route
    if (quality.mos_score < 2.5) {
      await this.client.calls.switchCodec(callId, 'OPUS');
    }
  }
}
```

---

## 🧪 Testing Strategies

### Unit Tests
```python
import unittest
from unittest.mock import Mock, patch
from ringez import RingezClient

class TestRingezIntegration(unittest.TestCase):
    def setUp(self):
        self.client = RingezClient(api_key='sk_test_123')
    
    @patch('ringez.api.requests.post')
    def test_create_session(self, mock_post):
        mock_post.return_value.json.return_value = {
            'session_id': 'sess_test123',
            'wallet_balance': {'minutes': 30}
        }
        
        session = self.client.sessions.create({
            'session_type': 'guest'
        })
        
        self.assertEqual(session['session_id'], 'sess_test123')
        self.assertEqual(session['wallet_balance']['minutes'], 30)
    
    @patch('ringez.api.requests.post')
    def test_initiate_call(self, mock_post):
        mock_post.return_value.json.return_value = {
            'call_id': 'call_test123',
            'status': 'initiated'
        }
        
        call = self.client.calls.initiate({
            'session_id': 'sess_test123',
            'to_number': '+14155551234'
        })
        
        self.assertEqual(call['status'], 'initiated')
```

### Integration Tests
```python
import pytest
from ringez import RingezClient

@pytest.fixture
def client():
    return RingezClient(api_key='sk_test_123')

@pytest.mark.integration
async def test_complete_call_flow(client):
    # Create session
    session = await client.sessions.create({
        'session_type': 'authenticated'
    })
    
    # Add credits
    transaction = await client.wallet.add_credits({
        'session_id': session.id,
        'amount': 5.00,
        'payment_method': 'test'
    })
    assert transaction.status == 'completed'
    
    # Initiate call
    call = await client.calls.initiate({
        'session_id': session.id,
        'to_number': '+14155551234'
    })
    assert call.status == 'initiated'
    
    # Wait for connection
    await client.calls.wait_for_status(call.id, 'answered', timeout=30)
    
    # Hang up
    result = await client.calls.hangup(call.id)
    assert result.status == 'completed'
```

---

## 🚀 Deployment Considerations

### Docker Deployment
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

ENV RINGEZ_API_KEY=""
ENV RINGEZ_WEBHOOK_SECRET=""

EXPOSE 3000

CMD ["node", "server.js"]
```

### Kubernetes Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ringez-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ringez-agent
  template:
    metadata:
      labels:
        app: ringez-agent
    spec:
      containers:
      - name: agent
        image: your-registry/ringez-agent:latest
        env:
        - name: RINGEZ_API_KEY
          valueFrom:
            secretKeyRef:
              name: ringez-secrets
              key: api-key
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

---

*For questions or support, contact: support@ringez.com*
