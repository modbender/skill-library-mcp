---
name: fellow-aiden
description: Control your Fellow Aiden smart coffee brewer via AI assistant. Manage brew profiles, view brewer status, create and tweak recipes, add shared brew links, and manage brewing schedules.
version: 1.0.0
metadata:
  openclaw:
    emoji: "☕"
    homepage: https://github.com/9b/fellow-aiden
    requires:
      env:
        - FELLOW_EMAIL
        - FELLOW_PASSWORD
      bins:
        - python3
    primaryEnv: FELLOW_EMAIL
    install:
      - id: pip-fellow-aiden
        kind: shell
        label: Install fellow-aiden Python library
        formula: pip3 install fellow-aiden --quiet
---

# Fellow Aiden ☕

Control your [Fellow Aiden](https://fellowproducts.com/products/aiden) smart coffee brewer via chat.

## Setup

Set your Fellow account credentials as environment variables:

```
FELLOW_EMAIL=your@email.com
FELLOW_PASSWORD=yourpassword
```

The skill will handle authentication automatically.

---

## What You Can Do

### Brewer Info

Ask things like:
- "What's my brewer called?"
- "Show me my Aiden's status"
- "What firmware is my brewer on?"

```bash
python3 {baseDir}/fellow.py info
```

---

### Profiles

Brew profiles control every parameter of your brew: water temperature, bloom, pulse intervals, and more.

**List all profiles:**
```bash
python3 {baseDir}/fellow.py profiles list
```

**Get a specific profile (by title, fuzzy match supported):**
```bash
python3 {baseDir}/fellow.py profiles get --title "Light Roast"
python3 {baseDir}/fellow.py profiles get --title "light" --fuzzy
python3 {baseDir}/fellow.py profiles get --id p3
```

**Create a new profile:**
```bash
python3 {baseDir}/fellow.py profiles create \
  --title "My Morning Brew" \
  --ratio 15 \
  --bloom \
  --bloom-ratio 2 \
  --bloom-duration 30 \
  --bloom-temp 96 \
  --ss-pulses 3 \
  --ss-interval 20 \
  --ss-temps "96,97,98" \
  --batch-pulses 2 \
  --batch-interval 30 \
  --batch-temps "96,97"
```

**Delete a profile:**
```bash
python3 {baseDir}/fellow.py profiles delete --id p3
python3 {baseDir}/fellow.py profiles delete --title "Old Recipe" --fuzzy
```

**Import a profile from a brew.link share URL:**
```bash
python3 {baseDir}/fellow.py profiles import --url "https://brew.link/p/ws98"
```

**Share a profile (generates a brew.link URL):**
```bash
python3 {baseDir}/fellow.py profiles share --id p2
python3 {baseDir}/fellow.py profiles share --title "My Favorite"
```

---

### Schedules

Schedules let the Aiden brew automatically on a weekly timer.

**List all schedules:**
```bash
python3 {baseDir}/fellow.py schedules list
```

**Create a schedule:**

Days are specified as a comma-separated list: `sun,mon,tue,wed,thu,fri,sat`

Time is specified as `HH:MM` in 24-hour format (local time is converted to seconds-from-midnight automatically).

```bash
# Brew every weekday at 7:30am, 950ml, using profile p2
python3 {baseDir}/fellow.py schedules create \
  --days "mon,tue,wed,thu,fri" \
  --time "07:30" \
  --water 950 \
  --profile-id p2

# Brew Mon/Wed/Fri at 8:00am
python3 {baseDir}/fellow.py schedules create \
  --days "mon,wed,fri" \
  --time "08:00" \
  --water 750 \
  --profile-id p0
```

**Delete a schedule:**
```bash
python3 {baseDir}/fellow.py schedules delete --id s0
```

---

## Usage Guidance for the Agent

- When the user asks to "brew" or mentions coffee, check their profiles first and suggest relevant ones.
- Profile titles support fuzzy matching — you don't need an exact match.
- Water amount is in millilitres (150–1500ml).
- Temperatures are in Celsius.
- Profile IDs look like `p0`, `p1`, etc. Schedule IDs look like `s0`, `s1`, etc.
- When creating a profile from natural language (e.g. "make me a light roast profile"), use sensible defaults:
  - ratio: 15–17 for lighter roasts, 14–15 for darker
  - bloom: enabled, bloomRatio 2, bloomDuration 30s
  - temperatures: 90–93°C for light, 93–96°C for medium, 96–98°C for dark
- Always confirm with the user before deleting profiles or schedules.
- When sharing a profile, present the brew.link URL clearly so the user can copy it.
- The `--fuzzy` flag on `profiles get` and `profiles delete` enables approximate title matching — use it when the user gives an informal name.
