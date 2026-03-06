WORKSHOP → MIRO (OpenClaw Skill)
README (plain TXT copy)

Turn workshop whiteboard photos (or raw notes) into a clean, editable MIRO diagram with:
- Real containers (MIRO Frames)
- Grouped stickies
- Smart connectors (including frame → frame flows)
- Idempotent updates (no duplicates)
- Undo / rollback support


1) REQUIREMENTS
- OpenClaw installed and working
- Node.js with ESM support (Node 18+ recommended)
- A MIRO Developer App with an Access Token
- Access to the target MIRO board


2) MIRO SETUP (ACCESS TOKEN)
You need a MIRO access token. Do NOT use cookies or browser session tokens.

Steps:
1. Create a MIRO Developer App (MIRO Developers portal)
2. Generate an Access Token (OAuth or personal access token depending on your setup)
3. Ensure the token has permissions to create:
   - frames
   - sticky notes
   - connectors

SECURITY NOTE:
Never paste tokens into public repos. Always use environment variables.


3) CONFIGURE ENVIRONMENT VARIABLES
You must set these 2 env vars:
- MIRO_ACCESS_TOKEN
- MIRO_BOARD_ID

Windows PowerShell:
  $env:MIRO_ACCESS_TOKEN="YOUR_TOKEN_HERE"
  $env:MIRO_BOARD_ID="uXjVxxxxxxxxxxxx="

macOS / Linux:
  export MIRO_ACCESS_TOKEN="YOUR_TOKEN_HERE"
  export MIRO_BOARD_ID="uXjVxxxxxxxxxxxx="

How to find MIRO_BOARD_ID:
From the board URL:
  https://miro.com/app/board/uXjVGBqEKoA=/
                       ^^^^^^^^^^^^^^^
                       this is the board id


4) SKILL FOLDER STRUCTURE
Expected structure:
  workshop-miro/
    SKILL.md
    miro-push.mjs
    _out/
      .state.json           (auto-created)
      miro-ready-*.json     (auto-created)

_out/.state.json tracks the latest run per sessionKey (for idempotency + undo).


5) HOW TO RUN

A) APPLY (push JSON to MIRO)
  node miro-push.mjs apply ./_out/miro-ready-YYYYMMDD-HHMMSS.json

What happens:
- If the same sessionKey exists → the script auto-undoes the previous run first
- Creates frames, stickies, connectors
- Saves created IDs to _out/.state.json

B) UNDO (rollback last run for a session)
  node miro-push.mjs undo product-a-b-diagram-side-by-side


6) JSON SCHEMA (MIRO-READY)
Your skill should output JSON like:

{
  "meta": {
    "title": "string",
    "source": "photo|notes",
    "language": "en|it|de",
    "createdAt": "ISO-8601",
    "sessionKey": "stable-key",
    "runId": "unique-run-id"
  },
  "frames": [
    { "id": "F1", "title": "Product A", "x": -1000, "y": 0, "w": 1800, "h": 1100 },
    { "id": "F2", "title": "Product B", "x": 1000, "y": 0, "w": 1800, "h": 1100 }
  ],
  "stickies": [
    { "id": "S1", "frameId": "F1", "text": "feature x", "color": "light_blue", "x": -1200, "y": -100, "unclear": false }
  ],
  "connectors": [
    { "from": "S1", "to": "S2", "label": null, "shape": "elbowed" }
  ],
  "warnings": []
}

NOTES:
- Stickies use BOARD coordinates (x,y).
- Parenting into frames is handled by the script (it converts coordinates safely).
- Arrow-only notes like "→" are ignored (arrows must be connectors).


7) CONTAINERS / FRAMES BEHAVIOR (IMPORTANT)
This agent always tries to create real Frames.

If frames[] is missing or empty, the script auto-creates frames using:
1) Title stickies (e.g., "Product A", "Product B") → turns them into frame titles
2) X-axis clustering (left vs right) fallback → creates 2 frames

Connector policy:
- When there are exactly 2 frames, the agent creates a single container-to-container flow:
  - It will NOT create cross-frame sticky connectors from the JSON
  - It will create one clean frame → frame connector instead
    (native if possible; otherwise with hidden edge anchors)


8) TROUBLESHOOTING

ERROR: "SyntaxError: Identifier 'usage' has already been declared"
Cause: duplicated function declarations in miro-push.mjs.
Fix: ensure "function usage(){...}" exists only once.

ERROR: "Miro API error 400: new position is outside of parent boundaries"
Cause: wrong coordinates when parenting items into frames.
Fix: use the current miro-push.mjs approach:
  - create stickies on board first
  - PATCH them into frames with correct frame-relative coordinates + clamping

No frames created / wrong grouping:
- Ensure your photo includes visible container titles
- Or rely on clustering fallback (left/right)
- Ensure stickies have meaningful text (not just arrows)

Duplicates after re-running:
- Use the same meta.sessionKey for the same diagram
- The script uses sessionKey to auto-undo the previous run


9) SECURITY
- Never commit tokens
- Use only environment variables:
  - MIRO_ACCESS_TOKEN
  - MIRO_BOARD_ID
- Do not use browser cookies/session tokens for API calls


10) EXAMPLE WORKFLOW
1) Take a photo of a whiteboard
2) Ask the skill: "Transfer this into MIRO with containers + clean arrows"
3) The skill generates JSON in _out/
4) The script pushes it to MIRO (apply)
5) If not perfect: undo <sessionKey> and re-run with improved input


LICENSE / DISCLAIMER
This is a community automation script using MIRO public APIs.
You are responsible for permissions and API usage within your organization.
