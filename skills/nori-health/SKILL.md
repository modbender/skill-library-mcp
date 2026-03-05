---
name: nori-health
description: Query your personal health data and get coaching from Nori, your AI health coach. Use when the user asks about sleep, workouts, nutrition, weight, heart rate, HRV, or wants health insights. NOT for: medical diagnosis, prescriptions, or emergency health situations.
homepage: https://nori.health
metadata: {"openclaw":{"emoji":"🌿","requires":{"env":["NORI_API_KEY"],"bins":["curl","jq"]},"primaryEnv":"NORI_API_KEY"}}
---

# Nori Health Coach

Send health questions to Nori and return the response. Nori analyzes data from wearables (Apple Watch, Oura, Garmin, Whoop, etc.), meals, workouts, weight, and lab results.

## Setup

1. Install the Nori iOS app and connect your wearables
2. In the Nori app, go to Settings > Integrations > OpenClaw
3. Generate an API key (starts with `nori_`)
4. Set the environment variable:
   ```bash
   export NORI_API_KEY="nori_your_key_here"
   ```
   Or add to `~/.openclaw/openclaw.json`:
   ```json
   {
     "skills": {
       "entries": {
         "nori-health": {
           "apiKey": "nori_your_key_here"
         }
       }
     }
   }
   ```

## When to Use

- "Compare my sleep on days I work out vs rest days"
- "What should I eat to hit my protein goal today?"
- "Show me my resting heart rate trend this month"
- "How's my recovery looking after yesterday's run?"
- "I had two eggs and toast with avocado for breakfast"
- "I did 30 minutes of strength training"
- "What patterns do you see between my sleep and HRV?"

## Usage

Send the user's message to Nori via the chat endpoint. Always forward the user's exact words.

Use `jq -n` to safely escape the user's message into valid JSON, and capture the HTTP status code to handle errors:

```bash
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "https://api.nori.health/api/v1/openclaw/chat" \
  -H "Authorization: Bearer $NORI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg msg "USER_MESSAGE_HERE" '{message: $msg}')")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
  echo "$BODY" | jq -r '.reply'
elif [ "$HTTP_CODE" -eq 401 ]; then
  echo "Your Nori API key is invalid. Please regenerate it in the Nori app under Settings > Integrations > OpenClaw."
elif [ "$HTTP_CODE" -eq 429 ]; then
  echo "Rate limited. Wait a moment and try again."
else
  echo "Something went wrong connecting to Nori (HTTP $HTTP_CODE)."
fi
```

## Response Handling

- On success (200): return the `.reply` field directly to the user as plain text. Do not add markdown formatting, bullet points, or other decoration.
- On 401: tell the user their Nori API key is invalid and to regenerate it in the Nori app.
- On 429: tell the user to wait a moment and try again.
- On other errors: tell the user something went wrong connecting to Nori, including the HTTP status code.

## Important

- Forward the user's message verbatim. Do not rephrase, summarize, or add context.
- Return Nori's reply verbatim. Do not reformat, summarize, or add commentary.
- Nori handles all health data analysis, logging, and coaching. Your job is just to relay messages.
- Nori is not a medical service. If the user asks for medical diagnosis or emergency help, direct them to a doctor or emergency services instead.
