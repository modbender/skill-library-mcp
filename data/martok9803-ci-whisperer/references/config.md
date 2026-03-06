# CI Whisperer configuration

## GitHub auth

CI Whisperer relies on GitHub CLI (`gh`). Authenticate on the host:

```bash
/usr/bin/gh auth login
```

## PR fix mode toggle (on/off)

By default CI Whisperer is read-only.

To allow PR creation (still requires explicit user approval each time):

```bash
export CI_WHISPERER_WRITE=1
```

Recommended: set this only for sessions where you actually want auto-fix PRs.

## Security notes

- Never paste GitHub tokens into chat.
- Redact secrets from logs before quoting.
