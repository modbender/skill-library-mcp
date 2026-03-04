---
name: workshop-miro
description: Workshop photos/notes -> an editable Miro diagram (real FRAMES as containers + stickies + connectors) with idempotent dedupe, rollback, undo and change commands, using the local script miro-push.mjs and env vars.
---

# Workshop → Miro (Top Mode vNext)

## Goal
Produce a workshop output on Miro that is:
- readable as a diagram (not “scattered post-its”)
- easy to edit (real containers)
- idempotent (no duplicates)
- correctable (undo / delete / update)

## Security (mandatory)
- Never print MIRO_ACCESS_TOKEN
- Use only env vars: MIRO_ACCESS_TOKEN and MIRO_BOARD_ID
- Never use browser cookies/session tokens

## Key rule: a container = a FRAME (not a shape)
A “workshop container” must be a FRAME when:
- there is a large rectangle/square with a clear title (e.g., “Easy vision”, “Milestone”, “VMS”, “Data Hub”, “Vico Insider”)
- or there is a swimlane/column with a title
- or a box is clearly grouping multiple elements (stickies or sub-boxes)

Do NOT create a frame if:
- it’s just blank space without a title
- it’s only a decorative border without grouping meaning

## HARD REQUIREMENT (do not violate)
- You MUST create frames[] when the board contains categories/areas.
- You MUST assign a non-null frameId to each sticky (except explicit "outside notes").
- If frames[] is empty OR if >10% stickies have frameId=null:
  - DO NOT run the push command.
  - Regenerate the structure (max 2 attempts).

## Quality Gate — Container sanity check (mandatory)
If the image contains >=2 titled containers:
- frames.length MUST be >= 2
- at least 95% of stickies MUST have a non-null frameId
If not satisfied:
- DO NOT push
- Regenerate structure (max 2 attempts)

## Mandatory planning (do not print)
Before generating JSON and before running DIRECT PUSH:
1) Identify candidate FRAMES:
   - any large rectangle with a title
   - any area labeled on the side or centered above/below
2) Assign every sticky to a candidate frame.
3) If a sticky is ambiguous, add a warning and assign it to the closest/most plausible frame.
4) Only after that, generate the final JSON.

## Quality Gate (mandatory)
Before executing `node ... apply`:
- At least 1 frame must exist.
- At least 90% of stickies must have a non-null frameId.
- No frame should be “giant” if the image clearly contains multiple distinct areas.
- If the gate fails, DO NOT push: regenerate the structure (max 2 attempts).

## Dedup / Idempotency (mandatory)
- Every push must include a STABLE `meta.sessionKey` for the same diagram/topic (e.g., "easy-vision-workshop").
- Every push must include a unique `meta.runId` (timestamp).
- If the sessionKey is the same:
  - first remove the previous run (automatic undo)
  - then apply the new one
This prevents duplicates and repeated runs.

## Operating modes
### A) DIRECT PUSH (default if the user asks)
1) Generate a Miro-ready JSON (schema below) including:
   - meta.sessionKey (stable)
   - meta.runId (unique)
2) Save the JSON to:
   - `...\workshop-miro\_out\miro-ready-YYYYMMDD-HHMMSS.json`
3) Execute:
   - `node ...\miro-push.mjs apply <PATH_JSON>`
4) Reply with:
   - frames created: N
   - stickies created: N
   - connectors created: N
   - sessionKey + runId
   - warnings (if any)

### B) CORRECTIONS (when the user wants changes)
- UNDO (per session): `node ...\miro-push.mjs undo <sessionKey>`
- If the user says “redo it better / wrong category / move things”:
  - regenerate a corrected JSON with the same sessionKey
  - run APPLY again (it replaces the previous run)

> Note: fine-grained edits (delete/update a single sticky) are a next step if the script supports them.
> Otherwise, recommended: full regeneration with the same sessionKey (cleaner and usually faster).

## Smart layout rules
- Inside each frame:
  - left: inputs/sources
  - center: processing / API / platforms
  - right: outputs/UI/external integrations
- Spacing guideline: x += 420, y += 260
- If there is a long arrow crossing the whole diagram:
  - prefer 2 shorter connectors via an intermediate node (e.g., sticky “API” or “Integration”) if it improves readability

## Connector / relationship rules
Create a connector when:
- you see an arrow/line on the whiteboard
- or the text implies a flow: "API", "sensoren", "data", "->", "integration"
- connector label: use the word that describes the flow (e.g., “API”, “Sensoren”, “Data”, “Milestone”)

Default connector shape: "elbowed" (more readable for architecture diagrams).

## Anti-overlap rules (clean arrows)
Goal: avoid connectors crossing over stickies/notes.

- Use default connector shape = "elbowed".
- Always keep a free “routing lane”:
  - Do not place stickies close to frame borders.
  - Minimum inner frame padding: 160px.
- If a connector would be long or would cross a cluster:
  - create one or more “router nodes” (gray sticky with "." or empty text) placed outside clusters
  - split the connection into segments: A -> R1 -> R2 -> B
- For connections between different frames:
  - use a router node near the right border of the source frame
  - and a router node near the left border of the target frame

## JSON Output (FRAME-based)
{
  "meta": {
    "title": "string",
    "source": "photo|notes",
    "language": "it|de|en",
    "createdAt": "ISO-8601",
    "sessionKey": "string (stable)",
    "runId": "string (unique)"
  },
  "frames": [
    { "id": "F1", "title": "string", "x": 0, "y": 0, "w": 1400, "h": 900 }
  ],
  "stickies": [
    {
      "id": "S1",
      "frameId": "F1|null",
      "text": "string",
      "color": "light_yellow|light_blue|light_green|light_pink|gray",
      "x": 0,
      "y": 0,
      "unclear": false
    }
  ],
  "connectors": [
    { "from": "S1", "to": "S2", "label": "string|null", "shape": "straight|elbowed|curved" }
  ],
  "warnings": [ "string" ]
}

## HARD Containment Detection (mandatory)
A "container" is a large rectangle that encloses other notes and has a title (e.g. "Product A", "Product B").

You MUST do this:
1) Create one FRAME per container rectangle (title = the container title).
2) Assign EVERY inner note to that frame via frameId.
3) Only outer notes (explicitly outside all containers) may have frameId=null.

Containment must be interpreted literally:
- If an element is visually inside the container boundaries, it belongs to that container.
- If unsure, assign to the nearest container and add a warning.

## Quality checklist (before pushing)
- sessionKey present and stable
- no giant “Workshop” frame unless the photo truly shows a single big box
- every sticky belongs to the correct frame (category)
- no duplicate stickies with identical text inside the same frame
- connectors only where they make sense (not between every pair)
