# TooToo Skill for OpenClaw

This skill integrates [TooToo](https://tootoo.ai) with [OpenClaw](https://github.com/openclaw/openclaw) to give your AI agent a personality grounded in your real values and beliefs.

## Features

- **Codex Sync**: Fetches your curated codex from TooToo and converts it into `SOUL.md` (for the agent's core personality) and `USER.md` (for deep context).
- **Alignment Monitoring**: Checks every agent response against your axiomatic beliefs and principles.
- **Drift Detection**: Periodically analyzes conversation history to ensure the agent stays true to your evolving codex.

## Setup

1. **Install the skill**
   Copy this folder to your OpenClaw skills directory or install via ClawHub (coming soon).

2. **Configure Username**
   Add your TooToo username to your `openclaw.json` or `config.json`:
   ```json
   {
     "skills": {
       "entries": {
         "tootoo": {
           "username": "your-username"
         }
       }
     }
   }
   ```

3. **Initialize**
   Run the setup command in OpenClaw:
   ```
   /tootoo setup your-username
   ```

   This will:
   - download your public codex
   - replace your `SOUL.md` with the TooToo version
   - set up the alignment monitoring hooks

## Usage

- `/tootoo sync` - Manually update if you've changed your beliefs on TooToo.
- `/tootoo status` - See when you last synced and alignment stats.
