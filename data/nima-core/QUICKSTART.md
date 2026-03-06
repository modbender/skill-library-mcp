# NIMA Core Quickstart

```bash
./install.sh
```

Add to `~/.openclaw/openclaw.json`:
```json
{"plugins":{"entries":{"nima-memory":{"enabled":true,"identity_name":"your_bot"},"nima-recall-live":{"enabled":true},"nima-affect":{"enabled":true,"identity_name":"your_bot","baseline":"guardian"}}}}
```

```bash
openclaw gateway restart
```

Done. Your bot now has persistent memory.
