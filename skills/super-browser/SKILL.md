# Super Browser Automation

**The ultimate browser automation framework.** Combines the best of 8 top-rated browser skills.

---

## Why This Skill?

Unified browser automation that works locally or in the cloud. Handles any web task from scraping to testing.

---

## Core Features

### 1. Environment Selection (automatic)
- **Cloud** - Browserbase (remote, scalable)
- **Local** - Local Chrome/Chromium
- Auto-detect based on available keys

### 2. Session Management
- Create/destroy sessions
- Use profiles (persist logins)
- Connect to existing tabs

### 3. Core Actions
| Command | Description |
|---------|-------------|
| navigate | Go to URL |
| click | Click element |
| type | Input text |
| snapshot | Analyze page |
| screenshot | Capture screen |
| pdf | Export to PDF |

### 4. Interactions
- Use @refs from snapshot
- Wait for elements
- Mouse control
- Drag and drop

### 5. Best Practices
- Always observe before acting
- Use explicit waits
- Handle errors gracefully

---

## Usage

### Quick Automation
```
browser open url="https://example.com"
browser snapshot
browser click ref="login-btn"
```

### Cloud Session
```
browser session create --provider=browserbase
browser task run --goal="Find pricing page"
```

### Profile Management
```
browser profile create --name=shopping
browser profile connect --name=shopping
```

---

## Merged From

| Skill | Rating |
|-------|--------|
| agent-browser | 3.672 |
| browser-automation | 3.590 |
| browser-use | 3.538 |
| fast-browser-use | 3.534 |
| stagehand-browser-cli | 3.519 |
| agent-browser-stagehand | 3.531 |

---

## Version

v1.0.0 - Initial release
