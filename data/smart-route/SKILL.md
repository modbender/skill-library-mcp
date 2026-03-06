---
name: smart-route
description: Calculate traffic-aware routes, travel times, and distances between locations using Google Routes API. Use when the user asks for "traffic to X", "how long to get to Y", "best route to Z", or "drive time". Returns JSON with duration, distance, and a direct Google Maps navigation link.
metadata:
  openclaw:
    emoji: 🚦
    requires:
      bins:
        - node
      env:
        - GOOGLE_ROUTES_API_KEY
---

# Google Routes Calculator

Get real-time traffic and routing information via Google Routes API (v2).

## When to use

Use this skill immediately when the user asks:
- "How is the traffic to X?"
- "How long does it take to drive to Y?"
- "Give me the route to Z."
- "What's the distance between A and B?"

## Usage

This skill executes a Node.js script. It requires an API Key with "Routes API" enabled.

### Command

```bash
node skills/smart-route/scripts/get_route.js --origin "Origin Address" --destination "Destination Address" [--mode DRIVE|BICYCLE|WALK]
```

### Output Format

The script returns a JSON object:

```json
{
  "origin": "Union Square, San Francisco, CA",
  "destination": "Golden Gate Bridge, San Francisco, CA",
  "mode": "DRIVE",
  "duration": "30 min",
  "distance": "13.5 km",
  "traffic_duration_seconds": 1835,
  "route_link": "https://www.google.com/maps/dir/?api=1&origin=...&destination=...&travelmode=driving"
}
```

### Examples

- **Check traffic in San Francisco:**
  `node skills/smart-route/scripts/get_route.js --origin "Union Square, San Francisco, CA" --destination "Golden Gate Bridge, San Francisco, CA"`

- **Drive time in Los Angeles:**
  `node skills/smart-route/scripts/get_route.js --origin "Los Angeles, CA" --destination "Santa Monica, CA" --mode DRIVE`

## Configuration

### Privacy & Security
- **Scope**: This skill only communicates with `routes.googleapis.com`.
- **Data Handling**:
  - It does not read local files or other environment variables besides the ones specified below.
  - **PII Notice**: User-supplied origin and destination addresses are sent to Google Routes API and printed to stdout in the JSON response. Users should consider these addresses as potentially sensitive information (PII).
- **Credentials**: API keys must be provided via environment variables. Providing keys via CLI flags is disabled for security reasons (to avoid exposing secrets in process lists).

### API Credentials
This skill requires a **Google Cloud API Key** with the **Routes API** enabled.

- **Variable**: `GOOGLE_ROUTES_API_KEY`
- **Detection**: The skill will check for this environment variable at runtime.
- **Strict Mode**: If the variable is missing, the script will exit with an error rather than falling back to other keys, ensuring no accidental usage of incorrect credentials.

### Setup Instructions
1.  Open the [Google Cloud Console](https://console.cloud.google.com/).
2.  Enable the **Routes API** for your project.
3.  Generate an API Key under **Credentials**.
4.  Export the key to your environment:
    ```bash
    export GOOGLE_ROUTES_API_KEY="your_api_key_here"
    ```
