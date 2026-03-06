# Browser Automation — Udio

Use browser automation when API wrappers aren't available or user prefers visual interaction.

## Prerequisites

- Browser tool available (openclaw profile)
- User has Udio account (free tier works)

## Opening Udio

```
browser action=open targetUrl="https://www.udio.com" profile=openclaw
```

Wait for page load, then take snapshot:
```
browser action=snapshot profile=openclaw
```

## Authentication

### Check Login Status
After snapshot, look for:
- "Sign In" or "Log In" button = not logged in
- User avatar/profile = logged in
- "Create" button visible = logged in

### Login Flow
If not logged in:
1. Click "Sign In" button
2. User completes OAuth (Google/Discord/etc.)
3. Wait for redirect back to udio.com
4. Verify logged in via snapshot

```
browser action=act request={"kind":"click","ref":"Sign In button ref"} profile=openclaw
```

Note: OAuth requires user interaction. Pause and wait for user to complete.

## Creating Music

### Navigate to Create Page
```
browser action=navigate targetUrl="https://www.udio.com/create" profile=openclaw
```

### Enter Prompt
1. Take snapshot to find prompt input field
2. Type prompt into the field:
```
browser action=act request={"kind":"type","ref":"prompt input ref","text":"electronic ambient chill synth pads warm analog"} profile=openclaw
```

### Configure Options

**Instrumental Only:**
Look for "Instrumental" toggle or checkbox and enable if needed.

**Custom Lyrics:**
If lyrics input is available, enter formatted lyrics:
```
[Verse 1]
Your lyrics here

[Chorus]
Hook goes here
```

### Generate
Click the "Create" or "Generate" button:
```
browser action=act request={"kind":"click","ref":"create button ref"} profile=openclaw
```

### Wait for Generation
Generation takes 30-60 seconds. Monitor progress:
1. Take periodic snapshots
2. Look for progress indicator
3. Wait for audio player to appear

```
# Check every 10 seconds
browser action=snapshot profile=openclaw
# Look for completed song or progress percentage
```

## Extending Songs

### From Song Page
1. Navigate to a generated song
2. Look for "Extend" or "Continue" button
3. Enter extension prompt
4. Click extend

### Extension Prompts
When extending, describe what to add:
- "add drums and build energy"
- "introduce strings, more emotional"
- "transition to chorus, powerful"

## Downloading Songs

### Find Download Button
After generation completes:
1. Look for download icon (usually arrow down)
2. Or right-click on audio player
3. Click download

### Save Location
Downloaded files typically go to browser's default download folder.
Move to `~/udio/songs/` for organization.

## Extracting Auth Token

For API wrapper usage, extract the auth token from browser:

### Via Browser Console
1. Open DevTools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Run:
```javascript
document.cookie.split('; ').find(c => c.startsWith('sb-api-auth-token=')).split('=')[1]
```

### Via Application Tab
1. DevTools > Application tab
2. Cookies > https://www.udio.com
3. Find `sb-api-auth-token`
4. Copy the Value

### Store Securely
```bash
# macOS Keychain
security add-generic-password -a udio -s udio_auth_token -w "paste-token-here" -U

# Retrieve later
security find-generic-password -a udio -s udio_auth_token -w
```

## Common UI Elements

| Element | Purpose | Typical Location |
|---------|---------|------------------|
| Create/Generate button | Start generation | Top nav or main page |
| Prompt input | Enter music description | Create page, center |
| Instrumental toggle | Disable vocals | Below prompt |
| Lyrics input | Custom lyrics | Below prompt (if enabled) |
| Extend button | Continue a song | Song page, below player |
| Download button | Save audio file | Song page, player controls |
| My Songs/Library | View past generations | User menu or nav |

## Handling Issues

### Page Not Loading
```
browser action=navigate targetUrl="https://www.udio.com" profile=openclaw
# Wait longer
browser action=snapshot profile=openclaw
```

### Session Expired
If actions fail or get redirected to login:
1. User needs to log in again
2. May need to re-extract auth token

### Generation Stuck
If generation takes >2 minutes:
1. Check for error messages in snapshot
2. May need to refresh and retry
3. Udio servers may be overloaded

### Rate Limited
Free tier has daily limits. If hitting limits:
1. Wait for daily reset
2. Consider paid plan
3. Use API wrapper for better error handling

## Workflow Example

Complete workflow for generating a song:

```python
# 1. Open Udio
browser.open("https://www.udio.com/create")
snapshot = browser.snapshot()

# 2. Check if logged in
if "Sign In" in snapshot:
    print("Please log in to Udio...")
    # Wait for user
    
# 3. Enter prompt
browser.type(prompt_ref, "indie rock upbeat guitar drums energetic")

# 4. Enable instrumental if needed
if instrumental:
    browser.click(instrumental_toggle_ref)

# 5. Generate
browser.click(create_button_ref)

# 6. Wait for completion
while True:
    snapshot = browser.snapshot()
    if "completed" in snapshot or audio_player_visible:
        break
    time.sleep(10)

# 7. Download
browser.click(download_button_ref)
print("Song downloaded!")
```

## Tips

- **Take frequent snapshots** — UI changes during generation
- **Be patient** — Generation takes 30-60+ seconds
- **Save working sessions** — Browser profile preserves login
- **Note successful prompts** — Track what works for future use
- **Watch for rate limits** — Free tier is limited
