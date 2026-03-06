# File: skills/jira-atrest/refs/app-embedding-quickref.md

# App Embedding Quickref (Jira Cloud, ADF)

This quickref explains **generic patterns** to embed app-relevant “data blobs” into Jira issue **description/comments** via REST API v3 (ADF), plus a **concrete example** for a Mermaid-diagram app.

---

## 1) Generic: How to embed app data into Jira “text bodies”

### 1.1 Where apps typically read data from
Most Jira apps integrate via one (or more) of these data carriers:

1) **Issue description** (ADF)  
2) **Issue comments** (ADF)  
3) **Custom fields** (text/textarea fields, often ADF for textarea)  
4) **Issue entity properties** (structured JSON, not visible unless surfaced by an app)  
5) **Attachments** (files referenced from description/comments or consumed by the app)

If your integration goal is “put structured data somewhere apps can parse”, **ADF code blocks** are the most universal for descriptions/comments.

---

### 1.2 Recommended pattern: “Marker + ADF codeBlock”
Embed a *stable marker* line so parsers (humans + apps) can find the payload reliably.

**Human-readable pattern (recommended):**
- Paragraph: short label + identifier
- Code block: the payload (JSON/YAML/Mermaid/etc.)

#### ADF snippet: marker paragraph + JSON code block
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "APPDATA: my-app-key v1 (do not edit marker)" }
      ]
    },
    {
      "type": "codeBlock",
      "attrs": { "language": "json" },
      "content": [
        {
          "type": "text",
          "text": "{\n  \"schema\": 1,\n  \"feature\": \"triage\",\n  \"settings\": { \"mode\": \"auto\" }\n}\n"
        }
      ]
    }
  ]
}
```
**Notes**

- Keep the marker line consistent: e.g. `APPDATA: <appKey> v<schema>`.
- Put the *entire* machine payload in the codeBlock. Avoid inline JSON in paragraphs.

* * *

### 1.3 Supported “carrier types” inside ADF you’ll use often

- `paragraph` for headings/labels
- `codeBlock` for machine-readable payloads
- `panel` / `expand` when you want to hide details (still searchable/editable)
- `inlineCard` for “smart link” URLs (when you store a link to an external artifact)

#### ADF snippet: link out to an attachment/artifact (inlineCard)
```json
{
  "type": "inlineCard",
  "attrs": { "url": "https://example.invalid/artifacts/123" }
}
```

* * *

### 1.4 “Text to ADF” rules for openClaw automation

When the user provides plain text but you need reliable formatting:

- Convert text into ADF:

    - newlines =&gt; multiple `paragraph` nodes
    - long payload =&gt; `codeBlock` node
- Do **not** assume Markdown is rendered; store structured formatting as ADF.

* * *

### 1.5 Alternative pattern: Issue entity properties (structured JSON, not in text)

If you need data that should not clutter the description/comments, store JSON via:

- `PUT /rest/api/3/issue/{issueKey}/properties/{propertyKey}`

Pros:

- clean UI, structured

Cons:
- not visible unless the app reads it or you build a panel/report

Use this if:

- you control the consumer (your own app/automation), or
- the vendor app explicitly documents a property key contract.

* * *

## 2) Concrete example: ContentCraft — Mermaid Diagrams for Jira

### 2.1 What the user does in the UI (quick)

This app is commonly used by:

- opening an issue
- enabling the **“Diagrams”** panel
- creating/editing Mermaid diagrams in that panel’s editor/viewer

(If you want diagrams *rendered* by the app, you typically manage them through the app UI unless the vendor provides a dedicated API.)

* * *

### 2.2 openClaw automation-friendly approach (store Mermaid source in the issue body)

Even if the app renders diagrams in a panel, it’s often useful to keep Mermaid source in the **issue description or a comment** as a portable “source of truth”:

**Recommended “marker + mermaid code” embedding:**

- Paragraph marker: `DIAGRAM: mermaid (ContentCraft)`
- Code block with language `mermaid`

#### ADF payload: comment body that contains a Mermaid diagram

Use this as the `body` for:

- `POST /rest/api/3/issue/{issueKey}/comment`
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "DIAGRAM: mermaid (ContentCraft) — edit in Diagrams panel or update this block" }
      ]
    },
    {
      "type": "codeBlock",
      "attrs": { "language": "mermaid" },
      "content": [
        {
          "type": "text",
          "text": "graph TD\n  A[User] --> B[Jira Issue]\n  B --> C[Diagrams Panel]\n  C --> D[Rendered SVG]\n"
        }
      ]
    }
  ]
}
```

**Why this helps**

- Humans can read/edit Mermaid quickly.
- Source is searchable in Jira.
- You can keep it versioned alongside ticket discussion.

* * *

### 2.3 Practical “two-track” workflow (best of both worlds)

1. openClaw writes/updates the Mermaid source in description/comment (ADF codeBlock, `language=mermaid`).
2. The team uses the ContentCraft **Diagrams panel** to render, inspect, and present the diagram in a polished view.

* * *

### 2.4 Mermaid syntax reference (quick)

Use standard Mermaid syntax in the code block (flowcharts, sequence, gantt, etc.).

Keep diagrams small and composable; prefer multiple diagrams over one huge graph.

```
Wenn du willst, kann ich dir auch gleich **eine kurze Standard-„Helper“-Routine** (in Skill-Textform) ergänzen, die *Plaintext → ADF* (inkl. `codeBlock`-Escaping) beschreibt, damit Agenten das immer konsistent erzeugen.
::contentReference[oaicite:2]{index=2}
```