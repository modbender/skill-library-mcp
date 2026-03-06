---
name: veo-video-generator
description: Generates high-fidelity 1080p videos with synced audio using Google Veo 3.1. Use for creating cinematic clips from text descriptions.
metadata:
  clawdbot:
    emoji: "🎬"
    requires:
      env: ["GEMINI_API_KEY"]
      bins: ["node", "npm"]
    install: "npm install"
    primaryEnv: "GEMINI_API_KEY"
    category: "Video & Media"
---

# Veo Video Generator

Generates short video clips with native audio using Google's state-of-the-art Veo 3.1 model.

## Instructions

1. **Trigger**: Activate when the user wants to create or render a video.
2. **Setup**: The agent must run `npm install` once before the first execution to fetch dependencies.
3. **Execution**: Invoke the script by passing the user prompt as a **separate argument**, never by interpolating it into a shell command string. Use an argument array / `execFile`-style invocation so the shell never parses the prompt value. Example (Node-style pseudo-code):

   ```javascript
   execFile('node', ['generate.js', '--prompt', userPrompt])
   ```

   Do **not** construct the command as a single concatenated string such as `"node generate.js --prompt " + userPrompt`.

4. **Resolution**: Outputs 1080p video in 9:16 aspect ratio by default.
5. **Completion**: Provide the user with the filename of the generated .mp4 in the workspace.

## Security & Privacy

- **Shell Injection Prevention**: The user prompt **must** be passed as a discrete argument (e.g. via `execFile` or an argv array), never interpolated into a shell command string. Concatenating user input into a shell string (e.g. `shell: true` with template literals) enables shell injection and is strictly forbidden.
- **Instruction Scope**: This skill only sends text prompts to the Google GenAI API.
- **Environment**: It uses the `GEMINI_API_KEY` provided by the OpenClaw environment.
- **Data Access**: It does not read local files or .env files. All configuration is handled by the agent.