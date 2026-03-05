# openLesson Agent API Skill

You are an AI agent that can interact with the openLesson tutoring platform via API.

## Overview

openLesson is a tutoring system that uses audio-based dialogue to help users learn by asking questions rather than giving answers. The platform generates personalized learning plans as directed graphs, where each node is a session. Agents can programmatically generate learning plans, start sessions, and analyze audio chunks for reasoning gaps.

## Important: No Browser Tool Required

You do not need a browser tool. You only need shell tools (e.g., curl) to make API calls to openLesson.

## Important: Audio-Only System

**CRITICAL**: The openLesson platform is **audio-only**. The analyze endpoint accepts ONLY audio input, NOT text. 
- Always convert speech to base64-encoded audio before calling the analyze endpoint
- Supported formats: webm, mp4, ogg
- Do not send text to the analyze endpoint - it will be rejected

## Authentication

Include your API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

**Important**: Always use `https://www.openlesson.academy` for API calls. The domain `openlesson.academy` has a redirect that loses the Authorization header.

API keys can be generated from the user's dashboard at `/dashboard`.

## Credentials

This skill requires an API key for the openLesson API:
- **Environment variable**: `OPENLESSON_API_KEY`
- **How to obtain**: Generate from the user's dashboard at `/dashboard`
- **No calendar access needed**: The skill does NOT create actual calendar events. "Reminders" means the agent proactively notifies the human when a session is due — this is behavioral, not a technical integration.

## Session State

Session IDs are stored in-memory for the duration of the conversation. No persistent storage is used or required.

## Bash Command Patterns

When running API calls as shell commands, use this pattern to avoid JSON escaping issues:

### Basic POST with JSON body

```bash
bash -c 'printf "{\"topic\":\"Quantum Computing\",\"days\":60}" | curl -X POST "https://www.openlesson.academy/api/agent/plan" -H "Authorization: Bearer $OPENLESSON_API_KEY" -H "Content-Type: application/json" --data-binary @-'
```

### With variables

```bash
TOPIC="Quantum Computing"
DAYS=60
bash -c "printf '{\"topic\":\"$TOPIC\",\"days\":$DAYS}' | curl -X POST 'https://www.openlesson.academy/api/agent/plan' -H 'Authorization: Bearer $OPENLESSON_API_KEY' -H 'Content-Type: application/json' --data-binary @-"
```

### Start session

```bash
bash -c 'printf "{\"plan_node_id\":\"NODE_UUID\",\"problem\":\"Explain neural networks\"}" | curl -X POST "https://www.openlesson.academy/api/agent/session/start" -H "Authorization: Bearer $OPENLESSON_API_KEY" -H "Content-Type: application/json" --data-binary @-'
```

### Analyze audio

```bash
bash -c 'printf "{\"session_id\":\"SESSION_UUID\",\"audio_base64\":\"BASE64_DATA\",\"audio_format\":\"webm\"}" | curl -X POST "https://www.openlesson.academy/api/agent/session/analyze" -H "Authorization: Bearer $OPENLESSON_API_KEY" -H "Content-Type: application/json" --data-binary @-'
```

## Endpoints

### 1. Generate Learning Plan

Creates a directed graph of learning sessions for a given topic.

**Endpoint**: `POST /api/agent/plan`

**Request**:
```json
{
  "topic": "Machine Learning Fundamentals",
  "days": 30  // optional: number of days to spread the plan across (default: 30)
}
```

**Response**:
```json
{
  "planId": "uuid",
  "topic": "Machine Learning Fundamentals",
  "days": 30,
  "nodes": [
    {
      "id": "uuid",
      "title": "Introduction to ML",
      "description": "Basic concepts and overview",
      "is_start": true,
      "next_node_ids": ["uuid2"],
      "status": "available"
    }
  ]
}
```

**Days to Sessions**:
- 7 days: 3-5 sessions
- 14 days: 4-7 sessions
- 30 days (default): 5-10 sessions
- 60 days: 8-14 sessions
- 90 days: 10-18 sessions
- 180 days: 15-25 sessions

### 2. Start Session

Starts a new Socratic session.

**Endpoint**: `POST /api/agent/session/start`

**Request**:
```json
{
  "problem": "Explain how gradient descent works in neural networks",
  "plan_node_id": "uuid-from-plan"  // optional, links to plan node
}
```

**Response**:
```json
{
  "sessionId": "uuid",
  "problem": "Explain how gradient descent works...",
  "nodeTitle": "Gradient Descent",
  "planId": "uuid",
  "status": "active",
  "instructions": {
    "audioFormat": "webm",
    "submitEndpoint": "/api/agent/session/analyze",
    "maxChunkDuration": 60000
  }
}
```

### 3. Analyze Audio Chunk

Submits an audio chunk for Socratic analysis. Returns reasoning gap score and follow-up questions.

**Endpoint**: `POST /api/agent/session/analyze`

**Request**:
```json
{
  "session_id": "uuid-from-start",
  "audio_base64": "base64-encoded-audio-data",
  "audio_format": "webm"
}
```

**Response**:
```json
{
  "sessionId": "uuid",
  "gapScore": 0.7,
  "signals": [
    "Missing consideration of local minima",
    "No mention of learning rate impact"
  ],
  "transcript": "transcribed audio...",
  "followUpQuestion": "What happens when the gradient becomes very small?",
  "requiresFollowUp": true
}
```

### 4. End Session

Ends an agent session and generates a summary report.

**Endpoint**: `POST /api/agent/session/end`

**Request**:
```json
{
  "session_id": "uuid-from-start"
}
```

**Response**:
```json
{
  "success": true,
  "sessionId": "uuid",
  "message": "Session ended and report generated",
  "chunkCount": 5,
  "wordCount": 1200
}
```

### 5. Get Session Summary

Retrieves the summary report of a completed session.

**Endpoint**: `GET /api/agent/session/summary?session_id=xxx`

**Response (if ready)**:
```json
{
  "ready": true,
  "sessionId": "uuid",
  "report": "# Session Report\n\n## Overview\n...",
  "createdAt": "2026-02-24T12:00:00Z",
  "status": "completed"
}
```

**Response (if not ready)**:
```json
{
  "ready": false,
  "message": "Session report not ready yet. Call /session/end first to generate the report.",
  "sessionId": "uuid",
  "status": "active"
}
```

## Complete Agent Workflow

```python
import base64
import requests

API_KEY = "your_api_key"
BASE_URL = "https://openlesson.academy"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Step 1: Generate a learning plan (optional: specify days)
plan_response = requests.post(
    f"{BASE_URL}/api/agent/plan",
    json={
        "topic": "Quantum Computing",
        "days": 14  # optional: number of days for the plan
    },
    headers=HEADERS
)
plan = plan_response.json()

# Step 2: Start a session for the first node
first_node = next(n for n in plan["nodes"] if n["is_start"])
session_response = requests.post(
    f"{BASE_URL}/api/agent/session/start",
    json={"plan_node_id": first_node["id"], "problem": first_node["title"]},
    headers=HEADERS
)
session = session_response.json()

# Step 3: Record and analyze audio
# 1. Record audio from user (use browser MediaRecorder or similar)
# 2. Convert to base64
with open("audio.webm", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode()

analyze_response = requests.post(
    f"{BASE_URL}/api/agent/session/analyze",
    json={
        "session_id": session["sessionId"],
        "audio_base64": audio_base64,
        "audio_format": "webm"
    },
    headers=HEADERS
)
analysis = analyze_response.json()

print(f"Gap Score: {analysis['gapScore']}")
print(f"Follow-up: {analysis['followUpQuestion']}")
```

## Error Handling

- **401**: Invalid or inactive API key
- **403**: Session doesn't belong to this key or wrong endpoint
- **404**: Session not found
- **500**: Internal server error

## Tips for Agents

1. **Always use audio**: The analyze endpoint ONLY accepts audio. Never send text.
2. **Record in webm format**: This is the preferred format (Opus codec)
3. **Chunk audio**: Send 30-60 second chunks for analysis
4. **Follow up**: If `requiresFollowUp` is true, ask the follow-up question and record response
5. **Track gap scores**: Use gap score to determine when user has mastered a concept
6. **Use bash -c for curl**: When running API calls in shell scripts, use the `bash -c 'printf "..." | curl ... --data-binary @-'` pattern to avoid JSON escaping issues
7. **Schedule all sessions**: When you generate a learning plan, it is important to schedule all the sessions suggested in the plan for your human. Create calendar events or reminders for each session so they can follow the plan. **Always remind your human when a session is due** - don't wait for them to ask.
