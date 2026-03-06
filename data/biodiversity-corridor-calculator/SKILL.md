---
name: biodiversity-corridor-calculator
description: "Open Claw Agent Skill: Biodiversity Corridor Analyst Description
  This skill allows an autonomous agent to analyze and value biodiversity
  corridors using advanced landscape ecology models. It proces..."
---

Open Claw Agent Skill: Biodiversity Corridor Analyst
Description
This skill allows an autonomous agent to analyze and value biodiversity corridors using advanced landscape ecology models. It processes H3 geospatial indices to calculate connectivity scores, visualize landscape resistance, and assess ecological premium values for conservation projects.

The agent can use this skill to:
1.  **Analyze Connectivity**: Evaluate a set of hexagonal land parcels (H3 indices) to determine their potential as biodiversity corridors, stepping stones, or regeneration zones.
2.  **Assess Landscape Context**: Retrieve data on surrounding land cover and ecological resistance to understand the broader environmental context of a project site.

Server Configuration
Base URL: https://www.nikhilp.online/biodiversity-corridor-calculator
API Base Path: /api

---

1. Analyze Connectivity
Endpoint: POST https://www.nikhilp.online/biodiversity-corridor-calculator/api/analyze

Description
Analyzes the connectivity and ecological potential of a specified cluster of H3 hexagons. The analysis considers local habitat quality and regional landscape structure to classify the area into scenarios like "Vital Corridor," "Habitat Expansion," or "Stepping Stone."

Input Schema (JSON)
centerLat (Number): The latitude of the center point for the analysis region (between -90 and 90).

centerLng (Number): The longitude of the center point for the analysis region (between -180 and 180).

projectHexes (Array of Strings): A list of H3 hexagonal indices (resolution 9 is standard) representing the land parcels to be analyzed. Maximum 50 hexes per request to ensure performance.

Usage Example
To analyze a small cluster of land parcels in a specific region:

JSON
{
  "centerLat": 51.5074,
  "centerLng": -0.1278,
  "projectHexes": [
    "892a100d2b3ffff",
    "892a100d2b7ffff",
    "892a100d2bbffff"
  ]
}

Response Format
JSON
{
  "results": [
    {
      "h3Index": "892a100d2b3ffff",
      "originalCode": 10,
      "natureState": 1,
      "scenario": {
        "code": "CORRIDOR",
        "label": "Vital Corridor",
        "description": "This area acts as a bridge...",
        "color": "#f59e0b",
        "priority": 1.0
      },
      "resistance": 1,
      "localNature": 0.45,
      "landscapeNature": 0.30
    }
  ],
  "context": [
    {
      "h3Index": "892a100d28fffff",
      "originalCode": 50
    }
    ...
  ]
}

Notes
-   **Rate Limiting**: The API is strictly rate-limited (approx. 5 requests per minute). Ensure you can handle 429 Too Many Requests responses gracefully by waiting before retrying.
-   **H3 Indices**: The system relies on H3 geospatial indexing. Ensure you can generate or work with valid resolution 9 H3 strings.
