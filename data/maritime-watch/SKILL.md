---
name: maritime-watch
description: A skill for monitoring the status and security of the Chornomorsk
  port. It collects data from various sources, including weather reports, vessel
  tracking services, and news feeds, to provide a comp...
---

# maritime-watch

## Description

A skill for monitoring the status and security of the Chornomorsk port. It collects data from various sources, including weather reports, vessel tracking services, and news feeds, to provide a comprehensive overview of the port's operational status and potential risks. It is built to be resilient against API Rate Limits and to cross-validate data from multiple sources to avoid hallucinations.

## Inputs

*   `port`: The name of the port to monitor (default: Chornomorsk).

## Outputs

JSON object containing the following information:

*   `weather`: Current weather conditions at the port (cross-validated).
*   `vessels`: List of vessels currently in port or approaching (cross-validated).
*   `security`: Security status of the port (e.g., alerts, warnings) (cross-validated).
*   `news`: Recent news related to the port.

## Usage

To use this skill, simply call it with the `port` parameter:

```
maritime-watch port=Chornomorsk
```

## Example

```json
{
  "weather": {
    "temperature": 10,
    "conditions": "Cloudy"
  },
  "vessels": [
    {
      "name": "MV Example",
      "status": "Arrived"
    }
  ],
  "security": {
    "status": "Normal"
  },
  "news": [
    {
      "title": "Port expansion project announced",
      "url": "https://example.com/news"
    }
  ]
}
```
