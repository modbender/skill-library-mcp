# Setting Up Canary as a Claude Project

This guide walks you through creating a Claude Project on claude.ai that acts as your personal secrets exposure advisor.

## What This Does

A Claude Project gives you a dedicated Claude conversation pre-loaded with Canary's knowledge and instructions. When you chat with it, Claude behaves as the Canary security agent â€” it knows what to look for, which commands to give you, and how to interpret the results you paste back.

Since Claude can't access your filesystem directly, this works in **advisory mode**: Canary tells you what to run, you run it on your machine, paste the output back, and Canary analyzes it and tells you what to fix.

## Requirements

- A Claude Pro, Team, or Enterprise account (Projects are not available on the free plan)
- Access to claude.ai

## Setup Steps

### 1. Create the Project

1. Go to [claude.ai](https://claude.ai)
2. In the left sidebar, click **"Projects"**
3. Click **"Create Project"**
4. Name it: **Canary â€” Secrets Scanner**
5. Optionally add a description: *"Security advisor that helps find and fix exposed credentials on your machine."*

### 2. Add the System Prompt

1. Inside your new project, click **"Project Instructions"** (or the settings/gear icon)
2. Copy the entire contents of the `system-prompt.md` file from this folder
3. Paste it into the **Custom Instructions** field
4. Click **Save**

### 3. Add the Knowledge File

1. Still in project settings, find the **"Knowledge"** or **"Files"** section
2. Upload the `SKILL.md` file from the root of this repository
3. This gives Claude access to all of Canary's detection patterns, file locations, regex, and severity rules as reference material

### 4. Start Using It

1. Open a new conversation within the project
2. Try one of these prompts:
   - *"Run a security check on my machine"*
   - *"Am I leaking any secrets?"*
   - *"Help me check if my API keys are safe"*
   - *"I just set up AWS CLI â€” is everything locked down?"*
3. Canary will ask your OS, give you commands to run, and analyze whatever you paste back

## Example Conversation

**You:** I want to check if my machine has any exposed secrets.

**Canary:** Sure â€” what operating system are you on? (macOS, Linux, or Windows?)

**You:** macOS

**Canary:** Let's start with the most important checks. Open your Terminal and run these three commands, then paste back the output:

```bash
find ~ -name ".env" -not -path "*/node_modules/*" -exec ls -la {} \; 2>/dev/null
ls -la ~/.aws/credentials 2>/dev/null
ls -la ~/.ssh/ 2>/dev/null
```

**You:** [pastes output]

**Canary:** ðŸ”´ Your `.env` file at `~/projects/my-app/.env` is world-readable â€” anyone logged into your Mac can see your API keys. Want me to give you the command to fix that?

## Tips

- **Don't paste actual secret values.** If Canary needs to check a file's contents, it will ask you to run `grep` commands that look for patterns without showing the full values.
- **Work in batches.** Canary will give you a few commands at a time rather than overwhelming you with 20 things to run.
- **You can come back anytime.** Your project persists, so you can run a check whenever you want â€” after setting up a new tool, before sharing your machine, or just as a routine check.

## Files in This Folder

| File | Purpose |
|------|---------|
| `system-prompt.md` | The custom instructions to paste into your Claude Project settings |
| `project-instructions.md` | This setup guide (you're reading it) |

The `SKILL.md` in the repo root is uploaded as a knowledge file to give Claude the full detection reference.
