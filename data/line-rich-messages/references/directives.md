# LINE Directives Guide

Directives are string tags placed at the end of your response. OpenClaw strips these before sending the message and uses them to construct native LINE UI elements.

⚠️ **Configuration Requirement**: For directives to work on LINE, the capability must be enabled in `openclaw.json`:
`channels.line.capabilities.inlineButtons = "all"` (or `"dm"`, `"group"`, etc.)

## Interactive Elements

### Quick Replies (Bubbles)
Replaces the keyboard area with up to 13 horizontal bubbles (recommended: 2-4).
- **Syntax**: `[[quick_replies: Option 1, Option 2, Option 3]]`
- **Behavior**: Tapping sends the text back as a user message.

### Confirm Dialog (Yes/No)
A native pop-up for simple decisions.
- **Syntax**: `[[confirm: Question text? | Yes Label | No Label]]`
- **Note**: Triggers a system dialog; the response is sent back as text.

### Button Menu (Rich Card)
A persistent card with a title, description, and action buttons.
- **Syntax**: `[[buttons: Title | Description | BtnLabel1:action1, BtnLabel2:https://url.com]]`
- **Actions**:
  - `action`: Sent back as a message.
  - `https://...`: Opens the URL in the browser.

## Specialized Cards

### Location
Shares a point on the map.
- **Syntax**: `[[location: Name | Address | latitude | longitude]]`

### Event & Agenda
For schedule-based information.
- **Event**: `[[event: Title | Date | Time | Location | Description]]`
- **Agenda**: `[[agenda: Title | Event1:9:00 AM, Event2:12:00 PM]]`

### Media & Control
- **Media Player**: `[[media_player: Title | Artist | Source | ImgURL | status]]`
- **Device Control**: `[[device: Name | Type | Status | Control1:data1]]`
- **Apple TV**: `[[appletv_remote: Name | status]]`
