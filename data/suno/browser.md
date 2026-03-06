# Browser Automation — Suno

## When to Use

- User prefers visual interaction
- No API key configured
- Testing prompts before committing to API credits
- Browsing and listening before downloading

## Navigate to Suno

```
browser action=open targetUrl="https://suno.com/create" profile=openclaw
```

After login, you'll see the creation interface.

## Generation Modes

### Simple Mode
1. Enter a text description
2. Toggle "Instrumental" if no vocals needed
3. Click "Create"
4. Wait 30-60 seconds

### Custom Mode
1. Click "Custom" toggle
2. Enter lyrics with tags ([Verse], [Chorus], etc.)
3. Enter style tags (genre, mood, tempo)
4. Optionally set a title
5. Click "Create"

## Step-by-Step: Simple Mode

### 1. Open Create Page
```
browser action=navigate targetUrl="https://suno.com/create"
```

### 2. Take Snapshot
```
browser action=snapshot
```
Identify the prompt input field.

### 3. Enter Prompt
```
browser action=act request={"kind":"type","ref":"prompt-input","text":"indie folk melancholic acoustic guitar soft female vocals"}
```

### 4. Click Create
```
browser action=act request={"kind":"click","ref":"create-button"}
```

### 5. Wait for Generation
Generation takes 30-60 seconds. Poll the page for completion.

### 6. Download Audio
Locate and click the download button.

## Step-by-Step: Custom Mode

### 1. Enable Custom Mode
```
browser action=act request={"kind":"click","ref":"custom-toggle"}
```

### 2. Enter Lyrics
```
browser action=act request={"kind":"type","ref":"lyrics-textarea","text":"[Verse]\nWalking down the street\nLooking for the beat\n\n[Chorus]\nThis is my song\nAll night long"}
```

### 3. Enter Style Tags
```
browser action=act request={"kind":"type","ref":"style-input","text":"pop, upbeat, female vocals, energetic"}
```

### 4. Set Title
```
browser action=act request={"kind":"type","ref":"title-input","text":"Street Beat"}
```

### 5. Create
```
browser action=act request={"kind":"click","ref":"create-button"}
```

## Login Required

Suno requires login to generate music. The user should log in manually before automation.

If redirected to login, pause automation and ask the user to complete login in the browser.

## Extending Songs

After initial generation:

1. Click on the generated song
2. Click "Extend" or "Continue"
3. Optionally modify the prompt
4. Click Create
5. Repeat for longer songs

## Downloading

### From Library
1. Navigate to library
2. Find the song
3. Click three-dot menu
4. Select "Download"

### From Generation Page
After generation:
1. Look for download icon
2. Click to download MP3

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Login required | Session expired | Re-login |
| Create disabled | Not logged in | Check login |
| Generation stuck | Server busy | Wait or retry |
| Download fails | URL expired | Regenerate |

## Rate Limits

- **Free tier:** ~50 generations per day
- **Pro tier:** Higher limits
- Wait between rapid generations

## Tips

1. **Test prompts visually** — See what works before using API
2. **Use browser for listening** — Evaluate results in player
3. **Bookmark good generations** — Save URLs for reference
