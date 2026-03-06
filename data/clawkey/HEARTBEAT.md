# ClawKey Heartbeat 🔑

_This runs periodically, but you can also check ClawKey anytime you want!_

Time to check in on your ClawKey registration and verification.

---

## Are you registered and verified?

```bash
curl https://api.clawkey.ai/v1/agent/verify/device/YOUR_DEVICE_ID
```

Use the same `deviceId` you use (or will use) for registration.

- **`"registered": false`** → You're not in ClawKey yet. Consider starting registration (see SKILL.md: POST `/agent/register/init`), then give your human the registration URL so they can complete VeryAI palm verification.
- **`"registered": true`, `"verified": true`** → You're good! You're under a verified human owner. Continue below if you have a pending session to check.
- **`"registered": true`, `"verified": false`** → Registered but not verified; human may not have completed palm verification. Have them open the registration flow again if needed.

---

## When to tell your human

**Do tell them:**

- **Registration URL is ready** → "Open this link to complete verification: [URL]" (output the URL as text; never open the browser for them.)
- **Session expired** → "The registration link expired. I can start a new one if you’re ready to verify."
- **Verification failed** → "Something went wrong with verification. Should I start registration again?"
- **They asked you to register** → After you run init, give them the registration URL and remind them to complete the palm verification step.

**Don’t bother them:**

- Routine heartbeat checks when you’re already registered and verified.
- Polling status when they’ve already been given the link (unless it’s been a long time or you see `expired`/`failed`).

---

## When to check ClawKey

**You don’t have to wait for heartbeat!** Check anytime:

- Before proving your identity to a third party (verify your device is still registered/verified).
- After your human says they completed verification (poll session status or check device).
- When you’re about to start registration (read SKILL.md and run init).

**Rough rhythm:**

- **Registration status:** Every heartbeat if you have a pending session; otherwise when you need to confirm you’re still registered/verified.
- **Device lookup:** When a third party needs proof, or after your human says they verified.

---

## Response format

**If nothing special:**

```
HEARTBEAT_OK - Checked ClawKey, all good! 🔑
```

**If you're not registered yet:**

```
Checked ClawKey - Not registered. Consider starting registration and giving your human the verification link (see SKILL.md).
```

**If session completed this cycle:**

```
Checked ClawKey - Registration completed. I'm now registered under my human owner.
```

**If you need your human:**

```
Hey! The ClawKey registration link is ready. Open this link to complete verification: [URL]
```

**If session expired:**

```
Hey! The ClawKey registration link expired. I can generate a new one when you're ready to verify.
```
