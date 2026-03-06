# Example: Patch → Build → Test → Commit → Push (manual commands)

This example is for users who prefer explicit steps (no Codex).

```bash
./skills/persistent-code-terminal/bin/persistent-code-terminal-start.sh
./skills/persistent-code-terminal/bin/persistent-code-terminal-send.sh "npm run build"
./skills/persistent-code-terminal/bin/persistent-code-terminal-read.sh
./skills/persistent-code-terminal/bin/persistent-code-terminal-send.sh "npm test"
./skills/persistent-code-terminal/bin/persistent-code-terminal-read.sh
./skills/persistent-code-terminal/bin/persistent-code-terminal-send.sh "git status"
./skills/persistent-code-terminal/bin/persistent-code-terminal-read.sh
./skills/persistent-code-terminal/bin/persistent-code-terminal-send.sh "git add -A"
./skills/persistent-code-terminal/bin/persistent-code-terminal-send.sh "git commit -m \"fix: make tests pass\""
./skills/persistent-code-terminal/bin/persistent-code-terminal-send.sh "git push"
./skills/persistent-code-terminal/bin/persistent-code-terminal-read.sh
```

Attach to watch:
```bash
./skills/persistent-code-terminal/bin/persistent-code-terminal-attach.sh
```
