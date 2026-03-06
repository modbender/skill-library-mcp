---
name: jarvis-monitor
description: JARVIS-style system monitor with sci-fi HUD interface. Displays server health, gateway connectivity, response times, and activity logs. Supports Chinese/English bilingual.
---

# jarvis-monitor

Sci-fi style system monitor with real-time status display.

## What It Does

Provides a visual dashboard for monitoring:
- Service health status
- Gateway connection status
- Last command/event timestamp
- Response time metrics
- System component status
- Activity log

## Features

- 🎨 Sci-fi HUD interface (Orbitron font, neon green theme)
- 🌐 Chinese/English bilingual toggle
- 🔄 Auto-refresh every 10 seconds
- 📱 Responsive design

## Installation

### Prerequisites

- Any web service with `/healthz` endpoint returning JSON like:
```json
{
  "status": "ok",
  "gateway": "connected",
  "gateway_last_event_ts": 1234567890
}
```

### Setup

1. Host `monitor.html` on your web server:
   ```bash
   cp monitor.html /path/to/your/server/templates/
   ```

2. Add endpoint to your server:
   ```python
   from fastapi.responses import HTMLResponse
   
   @app.get("/monitor")
   async def monitor():
       with open("templates/monitor.html", "r") as f:
           return HTMLResponse(content=f.read())
   ```

3. Update the API endpoint in the HTML:
   - Find `http://192.168.31.19:8000/healthz` and replace with your server URL

## Usage

Open in browser:
```
http://your-server:port/monitor
```

### Language Toggle

Click the button in top-right corner to switch between Chinese and English.

## Customization

### Colors

Edit CSS variables:
```css
--primary: #00ff88;    /* Neon green */
--secondary: #00ccff; /* Cyan */
--bg: #0a0a0f;        /* Dark background */
```

### API Endpoint

Find and replace:
```javascript
const res = await fetch('http://192.168.31.19:8000/healthz');
```

Expected JSON response:
```json
{
  "status": "ok",
  "gateway": "connected",
  "gateway_last_event_ts": 1234567890
}
```

## Files

- `monitor.html` - Main dashboard (single file, no dependencies except Google Fonts)

## Credit

Inspired by JARVIS from Iron Man / Marvel movies.
