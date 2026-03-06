# Sentry Mode - Natural Language Interface

Conversational BOLO activation. Just attach an image and say what you want.

## How It Works

### User Says:
```
"be on the lookout for this"
[image attached]
```

### Clawd Responds:
```
✅ Got it. I'm looking out for Sarah.

🔍 I'll focus on:
  • Small mole on left cheek
  • Freckles across nose and cheeks
  • Blonde, shoulder-length hair

📌 And I'll note:
  • Blue eyes
  • Slim build

👀 Monitoring active. I'll alert you if I see a match.
```

---

## What It Does

1. **Receives image + message**
2. **Auto-detects BOLO type** (person, vehicle, object)
3. **Analyzes image** → Extracts critical & high-priority features
4. **Generates BOLO** → Saves with unique fingerprint
5. **Starts monitoring** → Watches for matches
6. **Responds naturally** → Confirms what it's looking for

---

## Example Conversations

### Person

```
You: "be on the lookout for this" [sarah.jpg]

Clawd: 
✅ Got it. I'm looking out for Sarah.

🔍 I'll focus on:
  • Small mole on left cheek
  • Freckles
  • Blue eyes

👀 Monitoring active. I'll alert you if I see a match.
```

### Vehicle

```
You: "watch for my car" [blue-car.jpg]

Clawd:
✅ Got it. I'm looking out for this vehicle.

🔍 I'll focus on:
  • License plate ABC123
  • Blue color
  • Small dent on front fender

👀 Monitoring active. I'll alert you if I see a match.
```

### Object

```
You: "be on the lookout for weapons" [gun.jpg]

Clawd:
✅ Got it. I'm looking out for this object.

🔍 I'll focus on:
  • Firearm/pistol type
  • Black/dark color
  • Compact size

👀 Monitoring active. I'll alert you if I see a match.
```

---

## Natural Language Variants

All of these work:

```
"be on the lookout for this"
"watch for this person"
"look out for my car"
"monitor for this"
"keep an eye out for this"
"find this person"
"track this vehicle"
"watch for threats"
```

---

## Stopping a BOLO

```
You: "stop looking for Sarah"
Clawd: ✋ Stopped looking out for Sarah
```

or

```
You: "forget about that"
Clawd: ✋ Stopped monitoring
```

---

## Checking Status

```
You: "who are you looking for?"
Clawd: 👀 Currently looking out for:
📌 Sarah
  • Small mole on left cheek
  • Freckles
  • Blue eyes

You: "what are you watching?"
Clawd: ✓ Actively looking for: Sarah
  • Mole on left cheek
  • Freckles
```

---

## How It Detects Type

The system auto-detects from your message:

**Person:** Default unless message says otherwise
- "person", "girl", "man", "woman", "guy", "looking for", "find"

**Vehicle:** If message includes
- "car", "vehicle", "truck", "sedan", "license plate", "plate", "auto"

**Object:** If message includes
- "gun", "weapon", "knife", "object", "thing", "device"

---

## Behind the Scenes

1. **Image Analysis**
   - Analyzes photo with vision AI
   - Extracts facial features, colors, marks, damage, etc.
   - Creates matching rubric

2. **Feature Prioritization**
   - CRITICAL: Must match exactly (moles, scars, plates, damage)
   - HIGH: Should match (hair color, vehicle type, eye color)
   - MEDIUM: Helpful (clothing, accessories)
   - LOW: Can vary (pose, expression)

3. **BOLO Creation**
   - Generates unique fingerprint
   - Saves with timestamp
   - Stores in `active-bolos/` directory

4. **Monitoring Activation**
   - Starts background watcher
   - Continuously monitors video feed
   - Alerts when match found

---

## Configuration (Advanced)

If you want custom settings:

```
"watch for this, alert me every 30 seconds"
[image]

"keep looking for this but check every second"
[image]

"find this person, don't alert me for 5 minutes"
[image]
```

Parsed from message and applied.

---

## Privacy & Legal

⚠️ **Important:**
- Only use for legitimate purposes
- Comply with local laws
- Respect privacy
- Don't use for stalking
- Delete BOLOs when done

---

## Integration With Clawdbot

In Clawdbot message handler:

```javascript
// When user sends message with image attachment
if (message.attachments.length > 0) {
  const { handleClawdbotMessage } = require('./sentry-natural-language');
  
  const result = await handleClawdbotMessage(
    message.attachments[0].path,
    message.text
  );
  
  // Reply with natural response
  sendReply(result.message);
}
```

---

## What Gets Stored

Each BOLO creates a JSON file with:
- Image reference
- Extracted features (critical, high, medium, low)
- Matching rubric
- Confidence thresholds
- Timestamp

Example:
```json
{
  "name": "Sarah",
  "type": "person",
  "imagePath": "/path/to/sarah.jpg",
  "createdAt": "2026-01-27T12:45:00Z",
  "features": {
    "critical": [
      {
        "description": "Small mole on left cheek",
        "details": "...",
        "angleInvariant": true
      }
    ],
    "high": [...],
    "medium": [...],
    "low": [...]
  }
}
```

All stored in `active-bolos/` directory with timestamp.

---

## Supported Platforms

Works with any Clawdbot-integrated channel that supports:
- Text messages
- Image attachments

Examples:
- Telegram (✅ image + text)
- WhatsApp (✅ image + text)
- Discord (✅ image + text)
- Signal (✅ image + text)
- iMessage (✅ image + text)

---

## Examples

### Finding Someone

```
You: "this is the person i'm looking for" [photo.jpg]
Clawd: ✅ Got it. I'm looking out for this person.
🔍 I'll focus on: [extracted features]
👀 Monitoring active.

[Later, if detected]
Clawd: 🚨 Found them! Detected at [location/time]
```

### Tracking a Vehicle

```
You: "watch for my stolen car" [car-photo.jpg]
Clawd: ✅ Got it. I'm looking out for this vehicle.
🔍 License plate ABC123, blue sedan
👀 Monitoring active.

[Later, if detected]
Clawd: 🚨 Spotted your car! [details]
```

### Security Alert

```
You: "alert me if you see weapons" [gun.jpg]
Clawd: ✅ Got it. Watching for weapons.
🔍 Firearm detection active
👀 Will alert immediately.

[If detected]
Clawd: ⚠️ THREAT: Weapon detected! [details]
```

---

## Status: ✅ READY

Natural language interface for Sentry Mode is complete and ready to integrate with Clawdbot!

Just attach an image + speak naturally. Done.
