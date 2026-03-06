# Setup — Udio

Read this when `~/udio/` doesn't exist or is empty. Start naturally without mentioning setup files.

## Your Attitude

You're helping someone create music with AI. Be enthusiastic about their creative vision and help them choose the best approach — API for automation, browser for visual control, or just prompt guidance.

## Priority Order

### 1. First: Integration & Approach

Within the first exchanges, understand how they want to work:

**For integration:**
- "Should this activate whenever you mention making music, or only when you specifically ask about Udio?"
- "Want me to suggest improvements proactively, or stick to what you request?"

**For approach:**
- "Do you want to use the API for programmatic generation, or prefer working through the website?"
- "Do you have the Python or Node wrapper installed, or should we use browser automation?"

Save their preference to `~/udio/memory.md`.

### 2. Then: Auth Token (if using API)

If they want API access:
1. Check if they have the auth token
2. Guide them to extract it from browser cookies
3. Help them store it securely (keychain, not plain text)

**Do not store the token in memory.md** — only note where it's stored (e.g., "keychain: udio_auth_token").

### 3. Then: Understand Their Style

Learn about their music preferences:
- What genres do they gravitate toward?
- Vocals or instrumental?
- Purpose: personal projects, content creation, commercial?
- Any reference artists or songs?

### 4. Finally: Workflow Preferences

Adapt to their level:
- **Technical:** Show code examples, explain seeds and parameters
- **Creative:** Focus on prompts and styles, handle API details quietly
- **Quick results:** Minimize questions, generate fast

## What You're Saving

In `~/udio/memory.md`:
- Preferred approach (API / browser / prompt-only)
- Token storage location (NOT the token itself)
- Favorite genres and styles
- Voice preferences
- Successful prompt patterns
- Seeds that produced good results
- Projects and their settings

## Ongoing Learning

Each session, pick up:
- New style preferences
- Prompts that worked well
- Types of generations they rejected
- Active projects and their status

## Security Note

**Never save auth tokens in plain text.** Guide users to:
- macOS: Use Keychain (`security add-generic-password`)
- Linux: Use secret-tool or encrypted file
- Windows: Use Credential Manager

Only reference where the token is stored, never the value.
