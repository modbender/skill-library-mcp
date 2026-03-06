# ClawHQ Dashboard Setup

## Quick Start

1. **Sign up** at [app.clawhq.co](https://app.clawhq.co)
2. Go to **Settings → API Keys → Generate**
3. Copy the key (you only see it once!)
4. Set the environment variable:
   ```
   CLAWHQ_API_KEY=chq_your_key_here
   ```
5. Install this skill
6. Done — your agents will appear on your dashboard

## Verify Connection

```bash
curl -X POST "https://app.clawhq.co/api/agents/report" \
  -H "Authorization: Bearer $CLAWHQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent":"test","status":"idle"}'
```

Should return `{"ok":true}`.
