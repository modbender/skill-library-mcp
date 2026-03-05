# Echo AI Skill for OpenClaw

Query and interact with [Echo AI](https://echoai.so) assistants directly from your OpenClaw agent.

## Installation

1. Copy the `openclaw-skill/` folder to your OpenClaw skills directory:
   ```bash
   cp -r openclaw-skill/ ~/.openclaw/workspace/skills/echo-assistant/
   ```

2. Get an API key from [echoai.so](https://echoai.so) → Settings → API Keys

3. Set the environment variable:
   ```bash
   export ECHO_API_KEY="ek_your_api_key_here"
   ```

4. Enable the skill in `~/.openclaw/openclaw.json`:
   ```json
   {
     "skills": {
       "entries": [
         {
           "path": "~/.openclaw/workspace/skills/echo-assistant/SKILL.md",
           "enabled": true
         }
       ]
     }
   }
   ```

5. Restart OpenClaw

## Usage

Once installed, you can ask your OpenClaw agent:

- "List my Echo assistants"
- "What can my Echo assistant do?"
- "Tell me about my Echo named [name]"
- "Chat with my Echo assistant about [topic]"

## Safety

- **Read-only by default**: Listing and viewing assistants costs zero credits
- **Chat requires confirmation**: The agent will always ask before sending chat messages (which consume credits)
- **Rate limited**: Respects the per-key rate limits set by the Echo owner
- **API key scoped**: Assistant-scoped keys can only access their assigned Echo

## Links

- [Echo AI](https://echoai.so)
- [Echo API Documentation](https://echoai.so/help)
- [OpenClaw Skills Documentation](https://docs.openclaw.ai/skills)
