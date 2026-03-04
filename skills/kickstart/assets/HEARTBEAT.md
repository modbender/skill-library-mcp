# HEARTBEAT.md

<!-- Customise these checks for your setup -->

## Check Rotation (pick 1-2 per heartbeat, rotate through)
- [ ] Email — any urgent unread messages?
- [ ] Calendar — upcoming events in next 24h?
- [ ] Weather — relevant if human might go out?
- [ ] Projects — any builds failing, deploys stuck?

## Always Check
- [ ] Context usage — if any session >60%, alert immediately

## Quiet Hours
- 23:00-08:00 — HEARTBEAT_OK unless truly urgent

## Track
Use memory/heartbeat-state.json to avoid repeating checks within 2 hours.

<!-- Kickstart v1.0.2 -->
