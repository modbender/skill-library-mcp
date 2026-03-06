---
name: Weather&Webcam
description: Fetches current weather from wttr.in and automatically captures a live webcam image from Meteoblue or Windy for the requested location. Use it when the user asks for the weather and wants to see a real image of the current conditions.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["agent-browser", "curl"] },
      },
  }
---

# Weather Location

This skill automates weather data retrieval and live webcam image capture using **agent-browser** for maximum quality.

## Workflow

1.  **Get weather (wttr.in)**:
    - Execute `curl -s "wttr.in/[Location]?format=%l:+%c+%t+%h+%w"` to get basic data.
    - Note: Encode spaces (e.g., `Sant+Adria+de+Besos`).

2.  **Search for Webcam**:
    - Web search for `site:meteoblue.com [Location] webcam` or `site:windy.com [Location] webcam`.
    - Select the direct link to the location's webcam page.

3.  **Capture Image (Agent Browser Method)**:
    - Use **agent-browser** to navigate and interact:
      ```bash
      /home/user/.npm-global/bin/agent-browser --session-name webcam open "[URL]"
      ```
    - **Interaction**:
      - Click "OK/Accept" on cookie banners using `snapshot` + `click @ref`.
      - Click the specific location link to open the large view/gallery.
    - **Extraction**:
      - Use `eval` to find the highest resolution URL (look for `/full/` and `original.jpg`):
        ```javascript
        Array.from(document.querySelectorAll('img')).map(img => img.src).filter(src => src.includes('original.jpg') && src.includes('/full/'))[0]
        ```
    - **Download**:
      - Download with `curl` to `/home/user/.openclaw/workspace/webcam.jpg`.

4.  **User Response**:
    - Send with `message(action=send, media="/home/user/.openclaw/workspace/webcam.jpg", caption="[wttr.in data]\n[Comment]")`.
    - Respond with `NO_REPLY`.

## Optimization (Token Saving)

1. **Agent Browser**: Priority method for Alex to ensure interaction (cookies) and high-quality images.
2. **Session Persistence**: Use `--session-name webcam` to keep cookies.
3. **Scrapling (Fallback)**: Use only if `agent-browser` fails.

## Usage Examples

- "What's the weather like in London?"
- "Show me the webcam in Barcelona"
- "How's the sky in Vilassar de Mar?"
