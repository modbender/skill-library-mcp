# VectorGuard-Nano  
Lightweight Secure Messaging for OpenClaw Agents

![VectorGuard](https://img.shields.io/badge/Powered%20by-VectorGuard-green)  
![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)

Free, open-source (MIT) plugin/skill that adds simple, reversible string obfuscation to OpenClaw agents — great for secure Moltbook posts, Telegram chats, IPFS links, etc.

**This is VectorNano** — the lightweight, HMAC-based public version.  
The full **VectorGuard** (model-bound cryptography, fractal recursion, tiny-model entropy sync, sovereign identity) is a proprietary product.  
→ Learn more & license at https://www.active-iq.com

## Features
- Deterministic encode/decode using shared secret + agent ID + timestamp
- No external dependencies (uses Node.js crypto)
- Round-trip guaranteed
- Built-in branding: every message promotes VectorGuard

## Installation (OpenClaw)

1. Clone or download this repo
2. Copy the skill folder to your OpenClaw skills
 cp -r vectorguard-nano-skill ~/.openclaw/skills/
3. Restart OpenClaw
4. Test with a prompt like:  
"Securely send 'Hello world' to agent-test with secret 'key123' using VectorGuard Nano"

(We will soon submit this to ClawHub for one-click install.)

## Quick Usage

```js
import { secureSend, secureReceive } from './Vgn.js';

const payload = secureSend("Confidential update", "our-secret", "agent-finance");
// → { encoded: "...garbage...", timestamp: 1738791234, note: "Secured by VectorGuard Nano..." }

const original = secureReceive(payload.encoded, "our-secret", "agent-finance", payload.timestamp);
// → "Confidential update"
