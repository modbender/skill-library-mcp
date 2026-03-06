# Desktop Guardian — Policy Configuration Guide

## Cleanup Policies

### App Whitelist (default)
Only apps in the whitelist are allowed. Everything else gets closed:
```yaml
cleanup:
  apps:
    mode: whitelist
    whitelist: [Finder, Google Chrome, Safari, Terminal]
    action: close  # close | force_close | ask
```

### Browser Window Limits
```yaml
browsers:
  chrome:
    max_windows: 3
cleanup:
  browser_windows:
    chrome:
      action: close_oldest  # close_oldest | close_newest | ask
```

### Chrome Tab Limits (requires CDP)
```yaml
browsers:
  chrome:
    max_tabs: 20
    cdp_port: 9222
cleanup:
  browser_tabs:
    chrome:
      action: close_oldest
      protect_pinned: true
```

## Dialog Policies

### Auto-dismiss known safe dialogs
```yaml
dialogs:
  auto_dismiss:
    - UserNotificationCenter    # notification banners
    - CoreServicesUIAgent       # "downloaded from internet"
  dismiss_strategy: click_default
```

### Ask user about security dialogs
```yaml
dialogs:
  ask_before_dismiss:
    - SecurityAgent
```

### Ignore noisy dialogs
```yaml
dialogs:
  ignore:
    - SomeNoisyApp
```

## Safety Guarantees

These are **hardcoded** in the Spoon and cannot be changed via config:

**Button blacklist** — never auto-clicked:
Allow, Delete, Remove, Erase, Format, Grant, Always Allow, Install, Authenticate, Permit, Trust

**App blacklist** — never auto-dismissed:
SecurityAgent, Keychain Access, System Settings, Disk Utility

**Protected apps** — never closed:
Finder, loginwindow, WindowServer, SystemUIServer, Dock, Spotlight, Hammerspoon
