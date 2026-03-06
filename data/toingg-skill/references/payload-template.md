# Toingg Campaign Payload Template

Use this template when constructing the JSON passed to `create_campaign.py`. Remove
any keys you do not need; unspecified values follow Toingg defaults.

```json
{
  "title": "testclaw",
  "voice": "emily",
  "language": "english",
  "script": "",
  "purpose": "You are a Sales Expert and your goals are to Cold lead qualification for Cold Leads in a Professional tone.",
  "knowledgeBase": "",
  "calendar": "",
  "firstLine": "",
  "flowName": "",
  "systemPrompt": "",
  "tone": "Professional",
  "maxCallTimeout": 3,
  "inactiveCallTimeout": 15,
  "postCallAnalysis": true,
  "postCallAnalysisSchema": {
    "lead_type": "Classify leads as Hot, Warm, or Cold based on buying intent",
    "location": "Auto-extract geographic location from conversation",
    "customer_sentiment": "Track emotional tone throughout the conversation"
  },
  "successParameter": {
    "successKey": "",
    "desc": "",
    "success_fields": []
  },
  "totalCallTime": 0,
  "totalNumCall": 0,
  "totalSpent": 0,
  "totalCallSpent": 0,
  "totalTextSpent": 0,
  "averageCallCost": 0,
  "timeZone": "UTC",
  "isFreeflow": true,
  "public": false,
  "sampleSid": "",
  "description": "",
  "asr": "AZURE",
  "startMessage": true,
  "clearMemory": false,
  "leadNotificationPhone": "+918179259307",
  "leadNotification": true,
  "campaignType": {
    "textPipeline": false,
    "callPipeline": true
  },
  "campaignMode": {
    "inbound": false,
    "outbound": true
  },
  "integrations": [
    {
      "provider": "handoff",
      "providerType": "handoff",
      "enabled": true
    }
  ],
  "autoPilot": true,
  "humanHandoff": true
}
```

## Field notes

- **title** *(string, required)* — Human-friendly campaign name.
- **voice/language/tone** — Must match choices available inside Toingg.
- **script/systemPrompt/purpose** — Provide the conversational copy and guardrails.
- **postCallAnalysisSchema** — Define structured outputs you want Toingg to return.
- **leadNotificationPhone** — E.164-formatted phone number for alerts.
- **campaignType/campaignMode** — Control whether the campaign makes outbound calls.
- **integrations** — Enable downstream workflows (handoff, CRMs, etc.).

Any additional keys supported by the API can be added; the backend ignores unkown
fields that are not part of the schema.
