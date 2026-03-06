---
name: Capital Equipment Platform
description: Find, book, and manage scientific research equipment through your
  AI assistant. Search 10,000+ instruments across 500+ core facilities at 200+
  institutions.
---

# Capital Equipment Platform

Find, book, and manage scientific research equipment through your AI assistant. Search 10,000+ instruments across 500+ core facilities at 200+ institutions.

## What This Skill Does

- **Search Equipment**: Find microscopes, spectrometers, sequencers, and more near any location
- **Check Availability**: Real-time booking windows for shared instruments
- **Book Equipment**: Reserve time slots directly through your assistant
- **Submit Service Requests**: Describe your research needs and get quotes from facility providers
- **Find Collaborators**: Discover researchers with expertise in specific techniques or equipment
- **Track Papers**: Find published research linked to specific instruments and methods
- **Compatibility Check**: Verify equipment combinations work for your experimental workflow
- **Price Intelligence**: Fair market values, institutional rates, and depreciation data for equipment purchases
- **Compliance**: Get IP agreement and safety requirements for cross-institutional equipment use

## Setup

Capital Equipment supports auto-discovery and secure OAuth 2.1.

1. **Connect the Server**: Add the Server-Sent Events (SSE) endpoint to your OpenClaw config:

```json
{
  "mcp": {
    "servers": [
      {
        "name": "capital-equipment",
        "type": "sse",
        "url": "[https://us-central1-capital-equipment-dev.cloudfunctions.net/mcpServer/mcp](https://us-central1-capital-equipment-dev.cloudfunctions.net/mcpServer/mcp)"
      }
    ]
  }
}
```
