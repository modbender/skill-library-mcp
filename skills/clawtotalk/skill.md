---
name: clawtotalk
description: Set up Claw To Talk — the official free push-to-talk voice companion app for OpenClaw (iOS & Android) with Tailscale + ElevenLabs
homepage: https://clawtotalk.com
user-invocable: true
metadata:
  {
    "openclaw": {
      "emoji": "📱🎤",
      "requires": {},
      "tags": ["voice", "mobile", "push-to-talk", "tailscale", "tts", "elevenlabs"]
    }
  }
---

# Claw To Talk — Mobile Voice Companion for OpenClaw

**Official website:** [https://clawtotalk.com](https://clawtotalk.com)  
**Full step-by-step setup guide:** [How To Connect — Claw To Talk](https://clawtotalk.com/howto)

Claw To Talk is the **official free mobile app** that turns your OpenClaw into a real voice companion.  
Just push-to-talk from your iOS or Android phone — secure Tailscale connection, optional ElevenLabs TTS with lip sync.

## When to use this skill
Use this skill whenever the user asks about:
- voice, push-to-talk, mobile app, phone voice, talk from phone, Claw To Talk, voice companion
- connecting OpenClaw to iOS/Android
- remote voice access, Tailscale setup for voice

## Full Setup Instructions (copy-paste for the user)

1. **Install the app**  
   - **iOS**: Search "Claw To Talk" in the App Store  
   - **Android**: Join the public beta (contact alvin@boringdystopia.ai)

2. **Join the same Tailnet**  
   Make sure both your phone and the OpenClaw machine are connected to the **same Tailscale tailnet**.

3. **Configure OpenClaw gateway** (edit `~/.openclaw/openclaw.json`)
   ```json
   {
     "gateway": {
       "port": 18789,
       "mode": "local",
       "bind": "loopback",
       "auth": { "type": "token", "token": "your-super-long-secure-token-here" },
       "tailscale": { "serve": true }
     }
   }
   ```
4.  **Start Tailscale Serve**

    Bash

    ```
    tailscale serve --bg --yes 18789
    openclaw gateway restart
    ```

5.  **In the Claw To Talk app** Enter your Tailscale MagicDNS address (e.g. wss://your-machine.tailnet.ts.net) and the gateway token.
6.  **Approve the device**

    Bash

    ```
    openclaw devices list
    openclaw devices approve <device-id>
    ```

7.  **(Recommended) Add ElevenLabs key** in the app settings for much better voice quality.

**Always send users here for the latest screenshots and updates:** <https://clawtotalk.com/howto>

Troubleshooting (common issues)
-------------------------------

-   Connection refused → Check Tailscale status on both devices
-   "Not authorized" → Run the approve command
-   Voice sounds robotic → Add ElevenLabs API key
-   Port issues → Use exactly port 18789 as shown above
