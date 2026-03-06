# Ringez API for AI Agents
## Complete API Specification & Integration Guide

---

## 🎯 Overview

Transform Ringez into an AI agent skillset that enables autonomous calling capabilities with privacy-first design. This API allows AI agents to make international calls on behalf of users without requiring authentication or personal data.

**Base URL**: `https://ringez-api.vercel.app/api/v1`

**Authentication**: API Key-based (bearer token)

---

## 🔑 Authentication Model

### For AI Agents
```
Authorization: Bearer <AGENT_API_KEY>
X-Agent-ID: <unique_agent_identifier>
X-Session-ID: <optional_session_token>
```

### For Direct Users (Optional)
```
Authorization: Bearer <USER_API_KEY>
X-User-ID: <firebase_user_id>
```

---

## 📡 Core API Endpoints

### 1. Session Management

#### **POST** `/sessions/create`
Create a new calling session (guest or authenticated)

**Request:**
```json
{
  "session_type": "guest" | "authenticated",
  "agent_context": {
    "agent_name": "AssistantBot",
    "agent_version": "1.0",
    "capabilities": ["voice_calling", "sms"]
  },
  "user_consent": {
    "calling_authorized": true,
    "privacy_mode": true,
    "currency": "USD"
  }
}
```

**Response:**
```json
{
  "session_id": "sess_abc123xyz",
  "session_token": "tk_secure_random_string",
  "expires_at": "2026-02-05T18:30:00Z",
  "wallet_balance": {
    "minutes": 30,
    "currency": "USD",
    "value": 5.00
  },
  "privacy_mode": true,
  "rate_limits": {
    "calls_per_hour": 20,
    "max_call_duration": 3600
  }
}
```

---

#### **GET** `/sessions/{session_id}`
Retrieve session details and current balance

**Response:**
```json
{
  "session_id": "sess_abc123xyz",
  "active": true,
  "created_at": "2026-02-05T12:00:00Z",
  "wallet_balance": {
    "minutes": 25,
    "currency": "USD",
    "value": 4.17
  },
  "calls_made": 3,
  "total_duration": 300
}
```

---

#### **DELETE** `/sessions/{session_id}`
End session and clear call history

**Response:**
```json
{
  "success": true,
  "message": "Session terminated. All data cleared.",
  "final_balance": {
    "minutes": 25,
    "refund_available": false
  }
}
```

---

### 2. Wallet & Credits

#### **POST** `/wallet/add-credits`
Add calling minutes to wallet

**Request:**
```json
{
  "session_id": "sess_abc123xyz",
  "payment_method": "paypal" | "cashfree" | "stripe",
  "plan": "starter" | "popular" | "best_value",
  "currency": "USD" | "INR",
  "amount": 15.00,
  "payment_token": "tok_xyz789",
  "idempotency_key": "unique_transaction_id"
}
```

**Response:**
```json
{
  "transaction_id": "txn_abc123",
  "status": "completed",
  "minutes_added": 120,
  "new_balance": {
    "minutes": 145,
    "currency": "USD",
    "value": 19.17
  },
  "payment_receipt_url": "https://ringez.com/receipts/txn_abc123"
}
```

---

#### **GET** `/wallet/balance`
Check current wallet balance

**Request:**
```
GET /wallet/balance?session_id=sess_abc123xyz
```

**Response:**
```json
{
  "balance": {
    "minutes": 145,
    "currency": "USD",
    "value": 19.17
  },
  "last_transaction": {
    "id": "txn_abc123",
    "type": "credit",
    "amount": 120,
    "timestamp": "2026-02-05T12:15:00Z"
  }
}
```

---

### 3. Call Initiation & Management

#### **POST** `/calls/initiate`
Start a phone call

**Request:**
```json
{
  "session_id": "sess_abc123xyz",
  "to_number": "+14155551234",
  "from_number": "+12025551000",
  "privacy_mode": true,
  "caller_id_name": "Anonymous",
  "call_settings": {
    "max_duration": 1800,
    "record_call": false,
    "transcribe": true,
    "language": "en-US"
  },
  "webhook_url": "https://agent.example.com/webhooks/call-status",
  "metadata": {
    "purpose": "customer_support",
    "ticket_id": "TKT-12345"
  }
}
```

**Response:**
```json
{
  "call_id": "call_xyz789",
  "status": "initiated",
  "to_number": "+14155551234",
  "from_number": "+12025551000",
  "estimated_rate": 0.125,
  "currency": "USD",
  "webrtc_token": "rtc_token_secure_string",
  "connection_url": "wss://voice.ringez.com/connect/call_xyz789",
  "created_at": "2026-02-05T12:30:00Z"
}
```

---

#### **GET** `/calls/{call_id}`
Get call status and details

**Response:**
```json
{
  "call_id": "call_xyz789",
  "status": "in-progress",
  "to_number": "+14155551234",
  "from_number": "+12025551000",
  "started_at": "2026-02-05T12:30:15Z",
  "duration": 127,
  "estimated_cost": {
    "minutes": 3,
    "amount": 0.375,
    "currency": "USD"
  },
  "quality_metrics": {
    "mos_score": 4.2,
    "latency_ms": 85,
    "packet_loss": 0.02
  }
}
```

---

#### **POST** `/calls/{call_id}/actions`
Perform call actions (hold, transfer, hangup, DTMF)

**Request:**
```json
{
  "action": "dtmf" | "hold" | "unhold" | "transfer" | "hangup",
  "parameters": {
    "digits": "1234#",
    "transfer_to": "+14155559999"
  }
}
```

**Response:**
```json
{
  "call_id": "call_xyz789",
  "action": "dtmf",
  "status": "executed",
  "timestamp": "2026-02-05T12:32:00Z"
}
```

---

#### **DELETE** `/calls/{call_id}`
End/hangup a call

**Response:**
```json
{
  "call_id": "call_xyz789",
  "status": "completed",
  "duration": 245,
  "cost": {
    "minutes": 5,
    "amount": 0.625,
    "currency": "USD"
  },
  "remaining_balance": {
    "minutes": 140,
    "value": 18.545
  },
  "ended_at": "2026-02-05T12:34:20Z"
}
```

---

### 4. Call History & Logs

#### **GET** `/calls/history`
Retrieve call history for session

**Query Parameters:**
- `session_id` (required)
- `limit` (default: 50, max: 200)
- `offset` (default: 0)
- `start_date` (ISO 8601)
- `end_date` (ISO 8601)
- `status` (all, completed, failed, in-progress)

**Response:**
```json
{
  "calls": [
    {
      "call_id": "call_xyz789",
      "to_number": "+14155551234",
      "status": "completed",
      "duration": 245,
      "cost": 0.625,
      "started_at": "2026-02-05T12:30:15Z",
      "ended_at": "2026-02-05T12:34:20Z",
      "recording_url": null,
      "transcript_url": "https://ringez.com/transcripts/call_xyz789.json"
    }
  ],
  "pagination": {
    "total": 15,
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

---

### 5. Contact Management

#### **POST** `/contacts`
Add a contact to the address book

**Request:**
```json
{
  "session_id": "sess_abc123xyz",
  "name": "John Doe",
  "phone_number": "+14155551234",
  "labels": ["customer", "priority"],
  "notes": "Main contact for ABC Corp",
  "metadata": {
    "company": "ABC Corp",
    "department": "Sales"
  }
}
```

**Response:**
```json
{
  "contact_id": "cnt_abc123",
  "name": "John Doe",
  "phone_number": "+14155551234",
  "created_at": "2026-02-05T12:35:00Z"
}
```

---

#### **GET** `/contacts`
List all contacts

**Query Parameters:**
- `session_id` (required)
- `search` (optional, search by name or number)
- `label` (optional, filter by label)

**Response:**
```json
{
  "contacts": [
    {
      "contact_id": "cnt_abc123",
      "name": "John Doe",
      "phone_number": "+14155551234",
      "labels": ["customer", "priority"],
      "last_called": "2026-02-05T12:30:15Z",
      "call_count": 3
    }
  ],
  "total": 15
}
```

---

#### **GET** `/contacts/{contact_id}`
Get contact details

#### **PUT** `/contacts/{contact_id}`
Update contact information

#### **DELETE** `/contacts/{contact_id}`
Remove contact

---

### 6. Number Validation & Information

#### **POST** `/numbers/validate`
Validate phone number and get carrier info

**Request:**
```json
{
  "phone_number": "+14155551234"
}
```

**Response:**
```json
{
  "valid": true,
  "phone_number": "+14155551234",
  "country": "US",
  "country_code": "+1",
  "national_format": "(415) 555-1234",
  "type": "mobile",
  "carrier": "AT&T Mobility",
  "is_callable": true,
  "is_emergency": false,
  "is_premium": false,
  "estimated_rate": {
    "per_minute": 0.125,
    "currency": "USD"
  },
  "timezone": "America/Los_Angeles"
}
```

---

#### **GET** `/numbers/rates`
Get calling rates by country

**Query Parameters:**
- `country_code` (ISO 2-letter code, e.g., "US", "IN", "GB")
- `currency` (USD or INR)

**Response:**
```json
{
  "country": "United States",
  "country_code": "US",
  "dial_prefix": "+1",
  "rates": {
    "mobile": {
      "per_minute": 0.125,
      "currency": "USD"
    },
    "landline": {
      "per_minute": 0.10,
      "currency": "USD"
    }
  }
}
```

---

### 7. Transcription & Recording

#### **POST** `/calls/{call_id}/transcribe`
Enable real-time transcription for a call

**Request:**
```json
{
  "language": "en-US",
  "webhook_url": "https://agent.example.com/webhooks/transcription",
  "interim_results": true,
  "speaker_labels": true
}
```

**Response:**
```json
{
  "call_id": "call_xyz789",
  "transcription_enabled": true,
  "transcription_id": "trans_abc123",
  "websocket_url": "wss://transcribe.ringez.com/call_xyz789"
}
```

---

#### **GET** `/transcripts/{call_id}`
Get call transcript

**Response:**
```json
{
  "call_id": "call_xyz789",
  "transcript": [
    {
      "speaker": "caller",
      "text": "Hello, is this customer service?",
      "timestamp": 2.5,
      "confidence": 0.98
    },
    {
      "speaker": "recipient",
      "text": "Yes, how can I help you today?",
      "timestamp": 5.2,
      "confidence": 0.95
    }
  ],
  "language": "en-US",
  "duration": 245,
  "download_url": "https://ringez.com/transcripts/call_xyz789.json"
}
```

---

### 8. Webhooks & Real-time Events

#### **POST** `/webhooks/subscribe`
Subscribe to call events

**Request:**
```json
{
  "session_id": "sess_abc123xyz",
  "webhook_url": "https://agent.example.com/webhooks/ringez",
  "events": [
    "call.initiated",
    "call.ringing",
    "call.answered",
    "call.completed",
    "call.failed",
    "transcription.updated",
    "balance.low"
  ],
  "secret": "webhook_secret_key"
}
```

**Response:**
```json
{
  "webhook_id": "wh_abc123",
  "status": "active",
  "events": ["call.initiated", "call.answered", "call.completed"],
  "created_at": "2026-02-05T12:40:00Z"
}
```

---

#### Webhook Payload Example
```json
{
  "event": "call.answered",
  "timestamp": "2026-02-05T12:30:30Z",
  "data": {
    "call_id": "call_xyz789",
    "session_id": "sess_abc123xyz",
    "to_number": "+14155551234",
    "from_number": "+12025551000",
    "answered_at": "2026-02-05T12:30:30Z"
  },
  "signature": "sha256_hmac_signature"
}
```

---

### 9. AI Agent-Specific Features

#### **POST** `/agents/intent-detection`
Analyze conversation intent and extract entities

**Request:**
```json
{
  "call_id": "call_xyz789",
  "transcript_segment": "I need to speak with someone about my order #12345",
  "context": {
    "previous_intents": ["greeting"],
    "customer_id": "cust_abc"
  }
}
```

**Response:**
```json
{
  "intent": "customer_support",
  "sub_intent": "order_inquiry",
  "entities": {
    "order_number": "12345",
    "department": "customer_service"
  },
  "confidence": 0.92,
  "suggested_action": "transfer_to_department",
  "suggested_parameters": {
    "department": "orders",
    "priority": "medium"
  }
}
```

---

#### **POST** `/agents/call-routing`
Intelligent call routing based on context

**Request:**
```json
{
  "caller_info": {
    "phone_number": "+14155551234",
    "language": "en-US",
    "timezone": "America/Los_Angeles"
  },
  "routing_criteria": {
    "department": "sales",
    "skill_required": "spanish",
    "priority": "high"
  },
  "business_hours": true
}
```

**Response:**
```json
{
  "route_to": "+14155559999",
  "route_type": "direct" | "ivr" | "voicemail",
  "estimated_wait_time": 120,
  "agent_available": true,
  "fallback_options": [
    {
      "type": "voicemail",
      "number": "+14155559998"
    },
    {
      "type": "callback",
      "eta": "15 minutes"
    }
  ]
}
```

---

#### **POST** `/agents/sentiment-analysis`
Analyze call sentiment in real-time

**Request:**
```json
{
  "call_id": "call_xyz789",
  "transcript_segment": "This is extremely frustrating! I've been waiting for 3 weeks!",
  "include_recommendations": true
}
```

**Response:**
```json
{
  "sentiment": "negative",
  "sentiment_score": -0.78,
  "emotion": "frustrated",
  "urgency": "high",
  "escalation_recommended": true,
  "key_phrases": ["extremely frustrating", "waiting for 3 weeks"],
  "recommended_response_tone": "empathetic_and_solution_focused",
  "suggested_actions": [
    "acknowledge_frustration",
    "offer_immediate_solution",
    "escalate_to_supervisor"
  ]
}
```

---

#### **POST** `/agents/voice-synthesis`
Generate AI voice responses for callback or IVR

**Request:**
```json
{
  "text": "Thank you for calling. Please hold while we connect you.",
  "voice": "en-US-Neural2-A",
  "speed": 1.0,
  "pitch": 0,
  "output_format": "mp3" | "wav" | "webm"
}
```

**Response:**
```json
{
  "audio_id": "audio_abc123",
  "audio_url": "https://ringez.com/audio/audio_abc123.mp3",
  "duration": 4.5,
  "format": "mp3",
  "expires_at": "2026-02-05T18:40:00Z"
}
```

---

### 10. Analytics & Reporting

#### **GET** `/analytics/call-metrics`
Get detailed call analytics

**Query Parameters:**
- `session_id` (required)
- `start_date` (ISO 8601)
- `end_date` (ISO 8601)
- `group_by` (day, week, month)

**Response:**
```json
{
  "period": {
    "start": "2026-02-01T00:00:00Z",
    "end": "2026-02-05T23:59:59Z"
  },
  "metrics": {
    "total_calls": 47,
    "total_duration": 3420,
    "total_cost": 42.75,
    "average_duration": 72.76,
    "success_rate": 0.94,
    "call_quality_avg": 4.3
  },
  "breakdown": {
    "by_country": {
      "US": 30,
      "IN": 10,
      "GB": 7
    },
    "by_type": {
      "mobile": 35,
      "landline": 12
    },
    "by_status": {
      "completed": 44,
      "failed": 2,
      "no_answer": 1
    }
  }
}
```

---

#### **GET** `/analytics/spending`
Track spending and budget usage

**Response:**
```json
{
  "current_period": {
    "start": "2026-02-01T00:00:00Z",
    "end": "2026-02-05T23:59:59Z",
    "total_spent": 42.75,
    "budget_limit": 100.00,
    "budget_remaining": 57.25,
    "utilization_percentage": 42.75
  },
  "predictions": {
    "estimated_month_end_spend": 258.00,
    "over_budget_risk": "high",
    "recommended_top_up": 200.00
  }
}
```

---

## 🔐 Security & Compliance

### API Rate Limits
```
Standard Tier: 1000 requests/hour
Premium Tier: 10,000 requests/hour
Enterprise: Custom limits
```

### IP Whitelisting
```json
POST /security/whitelist
{
  "ip_addresses": ["203.0.113.0/24"],
  "description": "Agent server IPs"
}
```

### API Key Rotation
```json
POST /security/rotate-key
{
  "current_key": "sk_live_abc123",
  "revoke_immediately": false
}
```

---

## 🚀 AI Agent Integration Examples

### Example 1: Voice Assistant Making Support Call

```python
import requests

class RingezAgent:
    def __init__(self, api_key):
        self.base_url = "https://ringez-api.vercel.app/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Agent-ID": "voice-assistant-v1"
        }
    
    def make_support_call(self, customer_number, issue_description):
        # Create session
        session = requests.post(
            f"{self.base_url}/sessions/create",
            headers=self.headers,
            json={
                "session_type": "authenticated",
                "user_consent": {
                    "calling_authorized": True,
                    "max_spend_limit": 5.00
                }
            }
        ).json()
        
        # Initiate call
        call = requests.post(
            f"{self.base_url}/calls/initiate",
            headers=self.headers,
            json={
                "session_id": session["session_id"],
                "to_number": customer_number,
                "from_number": "+12025551000",
                "call_settings": {
                    "transcribe": True,
                    "max_duration": 600
                },
                "metadata": {
                    "purpose": "customer_support",
                    "issue": issue_description
                }
            }
        ).json()
        
        return call["call_id"]
    
    def monitor_call(self, call_id):
        response = requests.get(
            f"{self.base_url}/calls/{call_id}",
            headers=self.headers
        )
        return response.json()
```

### Example 2: Autonomous Call Routing Agent

```javascript
class CallRoutingAgent {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://ringez-api.vercel.app/api/v1';
  }

  async routeCall(incomingCall) {
    // Analyze intent
    const intent = await this.detectIntent(incomingCall.transcript);
    
    // Get routing recommendation
    const routing = await fetch(`${this.baseUrl}/agents/call-routing`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        caller_info: incomingCall.caller,
        routing_criteria: {
          department: intent.department,
          priority: intent.urgency
        }
      })
    }).then(r => r.json());

    // Transfer call
    await fetch(`${this.baseUrl}/calls/${incomingCall.id}/actions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        action: 'transfer',
        parameters: {
          transfer_to: routing.route_to
        }
      })
    });
  }

  async detectIntent(transcript) {
    const response = await fetch(`${this.baseUrl}/agents/intent-detection`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        transcript_segment: transcript
      })
    });
    return response.json();
  }
}
```

---

## 📊 Additional Agent Features

### 11. Batch Operations

#### **POST** `/batch/calls`
Initiate multiple calls simultaneously

**Request:**
```json
{
  "session_id": "sess_abc123xyz",
  "calls": [
    {
      "to_number": "+14155551234",
      "metadata": {"customer_id": "cust_001"}
    },
    {
      "to_number": "+14155555678",
      "metadata": {"customer_id": "cust_002"}
    }
  ],
  "call_settings": {
    "max_duration": 300,
    "transcribe": true
  }
}
```

**Response:**
```json
{
  "batch_id": "batch_xyz789",
  "status": "processing",
  "total_calls": 2,
  "calls": [
    {
      "call_id": "call_001",
      "to_number": "+14155551234",
      "status": "initiated"
    },
    {
      "call_id": "call_002",
      "to_number": "+14155555678",
      "status": "initiated"
    }
  ]
}
```

---

### 12. Scheduled Calls

#### **POST** `/scheduled-calls`
Schedule a call for future execution

**Request:**
```json
{
  "session_id": "sess_abc123xyz",
  "to_number": "+14155551234",
  "scheduled_time": "2026-02-06T09:00:00Z",
  "timezone": "America/Los_Angeles",
  "retry_policy": {
    "max_attempts": 3,
    "retry_interval": 300
  },
  "call_settings": {
    "transcribe": true
  }
}
```

**Response:**
```json
{
  "scheduled_call_id": "sched_abc123",
  "to_number": "+14155551234",
  "scheduled_time": "2026-02-06T09:00:00Z",
  "status": "scheduled",
  "created_at": "2026-02-05T12:45:00Z"
}
```

---

### 13. Call Queuing & Retry Logic

#### **POST** `/queue/add`
Add calls to queue with priority

**Request:**
```json
{
  "session_id": "sess_abc123xyz",
  "calls": [
    {
      "to_number": "+14155551234",
      "priority": 1,
      "max_wait_time": 300
    }
  ],
  "queue_settings": {
    "concurrent_limit": 5,
    "retry_failed": true
  }
}
```

---

## 🎛️ Advanced Configuration

### Environment Variables for Agents
```env
RINGEZ_API_KEY=sk_live_your_key_here
RINGEZ_API_URL=https://ringez-api.vercel.app/api/v1
RINGEZ_WEBHOOK_SECRET=whsec_your_secret
RINGEZ_MAX_CONCURRENT_CALLS=10
RINGEZ_DEFAULT_CALLER_ID=+12025551000
```

### SDK Support
- **Python**: `pip install ringez-sdk`
- **Node.js**: `npm install @ringez/sdk`
- **Go**: `go get github.com/ringez/go-sdk`
- **REST**: Direct HTTP API calls

---

## 🎯 Use Cases for AI Agents

1. **Customer Support Automation**
   - Autonomous call routing based on intent
   - Real-time sentiment analysis
   - Automatic escalation to human agents

2. **Appointment Reminders**
   - Scheduled call campaigns
   - Confirmation collection via DTMF
   - Reschedule handling

3. **Survey & Feedback Collection**
   - Automated survey calls
   - Voice response collection
   - Transcription and analysis

4. **Emergency Notifications**
   - Batch alert calls
   - Priority routing
   - Delivery confirmation

5. **Sales Outreach**
   - Lead qualification calls
   - Follow-up automation
   - CRM integration

6. **Voice-Enabled Chatbots**
   - Seamless text-to-voice transition
   - Context preservation
   - Multi-channel support

---

## 📖 API Versioning

Current Version: `v1`

Breaking changes will result in new version: `v2`, `v3`, etc.

Deprecation notices: 6 months minimum before removal

---

## 🔍 Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Verify API key |
| 402 | Insufficient Balance | Add credits to wallet |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify resource exists |
| 429 | Rate Limit Exceeded | Reduce request frequency |
| 500 | Server Error | Contact support |
| 503 | Service Unavailable | Retry with backoff |

---

## 📞 Support & Documentation
- **Developer Support**: support@ringez.com
