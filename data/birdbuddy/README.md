# Bird Buddy Skill for OpenClaw

Query your [Bird Buddy](https://live.birdbuddy.com) smart bird feeder from OpenClaw.

## Features
- Check feeder status (battery, food level, signal)
- See recent bird visitors with species identification
- Fetch sighting photos and media

## Requirements
- `pip install pybirdbuddy`
- Bird Buddy account with email/password login (Google SSO not supported)

## Setup
Add to your skill's `.env`:
```
BIRDBUDDY_EMAIL=your@email.com
BIRDBUDDY_PASSWORD=yourpassword
```

## Credits
Built on [pybirdbuddy](https://github.com/jhansche/pybirdbuddy) by [@jhansche](https://github.com/jhansche).

## Usage
See SKILL.md for full command reference.
