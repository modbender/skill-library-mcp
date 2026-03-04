# Tools, Browser & Skills Configuration Reference

Configuration for tool permissions, browser automation, and skill loading.

---

## Table of Contents
1. [Tools Block](#tools-block)
2. [Browser Block](#browser-block)
3. [Skills Block](#skills-block)

---

## Tools Block

Controls what tools agents can access and how they execute.

```json5
tools: {
  profile: "messaging",              // messaging | full | minimal
  deny: ["gateway", "cron"],         // Globally denied tools
  allow: [],                         // Explicitly allowed tools

  elevated: {
    enabled: false                   // Allow elevated/sudo operations
  },

  exec: {
    security: "deny",               // deny | ask | allow
    ask: "always",                   // always | first | never
    backgroundMs: 30000,             // Background execution timeout
    timeoutSec: 120                  // Command timeout
  },

  loopDetection: {},                 // Detect agent loops

  web: {
    search: {},                      // Web search config
    fetch: {}                        // Web fetch config
  },

  media: {
    audio: {},                       // Audio processing config
    video: {}                        // Video processing config
  },

  agentToAgent: {},                  // Inter-agent tool calls
  sessions: {},                      // Session management tools
  subagents: {},                     // Sub-agent spawning

  fs: {
    workspaceOnly: true              // Restrict file access to workspace
  }
}
```

### Tool Profiles

| Profile | Includes | Use Case |
|---------|----------|----------|
| `messaging` | Communication, files, web search (no code exec) | Default, safe for most users |
| `full` | All tools including code execution | Power users, developers |
| `minimal` | Read-only web and file access only | Restricted environments |

### Tool Deny/Allow Lists

```json5
tools: {
  deny: [
    "gateway",              // Prevent config modification
    "cron",                 // Prevent job creation
    "sessions_spawn",       // Prevent sub-session spawning
    "sessions_send"         // Prevent arbitrary message sending
  ]
}
```

### Code Execution Security

```json5
tools: {
  exec: {
    security: "deny",       // deny = no code execution
                             // ask = prompt before execution
                             // allow = execute freely
    ask: "always"            // always = prompt every time
                             // first = prompt once per session
                             // never = never prompt
  }
}
```

### Elevated Operations

```json5
tools: {
  elevated: {
    enabled: false           // DANGER: true allows sudo/admin operations
  }
}
```

**WARNING:** `elevated.enabled: true` combined with `open` DM policy gives strangers admin access to your system.

### File System Restriction

```json5
tools: {
  fs: {
    workspaceOnly: true      // Only access workspace directory
  }
}
```

When `true`, agents cannot access `/etc/`, `/var/`, other users' directories, or any path outside the workspace.

---

## Browser Block

Playwright browser integration for web automation.

```json5
browser: {
  enabled: true,
  evaluateEnabled: false,            // Allow JS evaluation in pages
  defaultProfile: "openclaw",

  profiles: {
    openclaw: {
      cdpPort: 18800                 // Chrome DevTools Protocol port
    },
    chrome: {
      cdpUrl: "http://localhost:9222" // Connect to existing Chrome
    },
    remote: {
      cdpUrl: "http://10.0.0.42:9222" // Remote browser via CDP
    }
  },

  headless: true,                    // Run without visible window
  noSandbox: false,                  // Disable Chromium sandbox
  executablePath: null               // Custom Chromium path
}
```

### Browser Profiles

| Profile | Type | Description |
|---------|------|-------------|
| Managed (`cdpPort`) | Isolated | OpenClaw manages its own Chromium. Separate cookies/state. |
| Extension relay (`cdpUrl` to localhost) | Your browser | Connects to existing Chrome via CDP. Shares your sessions. |
| Remote (`cdpUrl` to IP) | Remote | Connects to a browser on another machine. |

### Configuration Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable browser tools |
| `evaluateEnabled` | boolean | `false` | Allow `page.evaluate()` JS execution |
| `defaultProfile` | string | `"openclaw"` | Default browser profile to use |
| `headless` | boolean | `true` | Run without visible UI |
| `noSandbox` | boolean | `false` | Disable Chromium sandbox (needed in some Docker setups) |
| `executablePath` | string | `null` | Path to custom Chromium binary |

---

## Skills Block

Skill loading and installation configuration.

```json5
skills: {
  allowBundled: true,                // Allow built-in skills

  entries: {                         // Per-skill enable/disable
    "my-skill": { enabled: true },
    "web-scraper": { enabled: false }
  },

  load: {
    watch: true,                     // Hot-reload skill files on change
    watchDebounceMs: 250,            // Debounce delay (ms)
    extraDirs: [                     // Extra directories to scan
      "/opt/shared-skills",
      "~/projects/my-skills"
    ]
  },

  install: {
    nodeManager: "npm"               // npm | yarn | pnpm
  }
}
```

### Entries

Enable or disable individual skills:

```json5
skills: {
  entries: {
    "gmail-manager": { enabled: true },
    "calendar-sync": { enabled: true },
    "web-scraper": { enabled: false }   // Temporarily disabled
  }
}
```

### Extra Directories

Scan additional directories for skills:

```json5
skills: {
  load: {
    extraDirs: ["/opt/team-skills", "~/custom-skills"]
  }
}
```

### File Watching

When `watch: true`, the Gateway monitors skill directories for file changes. Updated skills are available on the next session start (not mid-conversation).
