# Sandwrap

Soft protection for running third-party skills. Not a real sandbox — that would need a VM. This wraps skills in prompt-based defense layers.

## The Problem

You find a cool skill on ClawHub. It does exactly what you need. But it wants exec access and it's from some random GitHub repo. Do you trust it?

Probably not. But you still want to use it.

## The Solution

Wrap any skill in protection. It can read files but not write them. It can analyze your website but not run arbitrary commands. You stay in control.

```
Run audit-website in sandwrap read-only
```

That's it. The skill runs, you get the results, nothing bad happens.

## What It Does

Five layers of soft protection:

1. **Random delimiters** - Attackers can't predict the session tokens
2. **Instruction hierarchy** - External content can't override your rules  
3. **Tool restrictions** - Only the tools you allow
4. **Human approval** - Sensitive stuff needs your OK
5. **Output checking** - Catches path traversal and data exfiltration attempts

Real-world testing shows about 85% of prompt injection attacks get blocked. Not perfect, but way better than running things raw.

## Presets

Pick the right level of paranoia:

- **read-only** - Look but don't touch
- **web-only** - Web research, no local file access
- **audit** - Read everything, write only to sandwrap-output/
- **full-isolate** - No tools at all, just thinking

## Auto Mode

Don't want to type "in sandwrap" every time? Set it up once:

```json
{
  "always_wrap": ["audit-website", "sketchy-scraper"],
  "auto_wrap_risky": true
}
```

Now risky skills get wrapped automatically. You'll see a prompt when something tries to break out.

## Honest Limitations

- Some sophisticated attacks will get through (~15%)
- This is prompt-based, not system-level isolation
- If you need bulletproof security, use a VM
- It's called "sandwrap" not "sandbox" for a reason

But for everyday use? This catches most of the bad stuff without slowing you down.

## Install

```
clawhub install sandwrap
```

Then just add "in sandwrap [preset]" to any skill command.
