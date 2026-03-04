# Sandbox Errors

Guide to diagnosing and fixing Docker sandbox and code execution issues.

## Error Types

### DOCKER_NOT_RUNNING

**Symptoms:**
- "Cannot connect to Docker daemon" error
- "Is Docker running?" messages
- Sandbox initialization fails
- Code execution requests fail

**Common Causes:**
- Docker daemon not started
- User not in docker group
- Docker socket permission denied
- Docker Desktop not running (macOS/Windows)

**Diagnostic Commands:**
```bash
# Check Docker status
docker info
systemctl status docker  # Linux
docker version

# Check Docker socket
ls -la /var/run/docker.sock

# Test Docker access
docker ps
```

**Fix:**
```bash
# Start Docker daemon (Linux)
sudo systemctl start docker
sudo systemctl enable docker

# Start Docker Desktop (macOS/Windows)
# Launch Docker Desktop application

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Fix socket permissions
sudo chmod 666 /var/run/docker.sock

# Verify
docker run hello-world
```

**Auto-Fix Available:** No (requires system-level action)

---

### CONTAINER_OOM

**Symptoms:**
- "Container killed - out of memory" error
- Sandbox container exits with code 137
- Memory limit exceeded messages
- Code execution fails on large datasets

**Common Causes:**
- Memory limit too low (default: 512MB)
- Memory leak in user code
- Large file processing
- Inefficient algorithms

**Diagnostic Commands:**
```bash
# Check container memory usage
openclaw sandbox stats

# View killed containers
docker ps -a --filter "exited=137"

# Monitor memory usage
docker stats --no-stream

# Check logs
openclaw logs --sandbox --filter="OOM"
```

**Fix:**
```bash
# Increase memory limit
openclaw config set sandbox.memory.limit "2GB"

# Set swap limit
openclaw config set sandbox.memory.swap "4GB"

# Enable memory monitoring
openclaw config set sandbox.monitoring.memory.enabled true
openclaw config set sandbox.monitoring.memory.alertThreshold 80

# Restart with new limits
openclaw sandbox restart

# For specific execution
openclaw sandbox exec --memory 4GB -- python script.py
```

**Prevention:**
```yaml
sandbox:
  memory:
    limit: "2GB"
    swap: "4GB"
    reservation: "512MB"
  monitoring:
    enabled: true
    alertThreshold: 85
```

**Auto-Fix Available:** Partial (can increase limits)

---

### SANDBOX_TIMEOUT

**Symptoms:**
- "Execution timeout" error
- Code execution killed after time limit
- Long-running scripts terminated
- Timeout after 30s (default)

**Common Causes:**
- Timeout setting too low
- Infinite loops in code
- Slow external API calls
- Large data processing

**Diagnostic Commands:**
```bash
# Check current timeout
openclaw config get sandbox.timeout.execution

# View timed-out executions
openclaw sandbox history --filter timeout

# Monitor execution time
openclaw sandbox exec --verbose -- python script.py
```

**Fix:**
```bash
# Increase timeout
openclaw config set sandbox.timeout.execution 300000  # 5 minutes in ms

# Set per-execution timeout
openclaw sandbox exec --timeout 600 -- python long_script.py

# Disable timeout (dangerous, use with care)
openclaw config set sandbox.timeout.execution 0

# Enable execution streaming
openclaw config set sandbox.streaming.enabled true
```

**Configuration:**
```yaml
sandbox:
  timeout:
    execution: 300000    # 5 minutes
    startup: 30000       # 30 seconds
    shutdown: 10000      # 10 seconds
```

**Auto-Fix Available:** Yes (increases timeout)

---

### WORKSPACE_MOUNT_FAIL

**Symptoms:**
- "Failed to mount workspace" error
- Files not accessible in sandbox
- Volume mount permission denied
- Bind mount failed

**Common Causes:**
- Workspace directory doesn't exist
- Permission denied on workspace path
- SELinux blocking volume mounts
- Docker volume driver issue

**Diagnostic Commands:**
```bash
# Check workspace path
openclaw config get sandbox.workspace.path
ls -la $(openclaw config get sandbox.workspace.path)

# Test volume mount
docker run -v /path/to/workspace:/workspace alpine ls /workspace

# Check SELinux status
getenforce
```

**Fix:**
```bash
# Create workspace directory
mkdir -p ~/.openclaw/workspace
chmod 755 ~/.openclaw/workspace

# Set correct ownership
sudo chown -R $USER:$USER ~/.openclaw/workspace

# Update workspace path
openclaw config set sandbox.workspace.path "$HOME/.openclaw/workspace"

# SELinux: add context (Linux)
chcon -Rt svirt_sandbox_file_t ~/.openclaw/workspace

# Or disable SELinux temporarily (testing only)
sudo setenforce 0

# Use named volume instead
openclaw config set sandbox.workspace.type "volume"
openclaw config set sandbox.workspace.name "openclaw-workspace"
```

**Auto-Fix Available:** No (requires file system access)

---

### PERMISSION_DENIED

**Symptoms:**
- "Permission denied" in sandbox
- Cannot execute files
- Cannot write to workspace
- File operation fails

**Common Causes:**
- File ownership mismatch (host vs container user)
- Files not executable
- Read-only volume mount
- AppArmor/SELinux restrictions

**Diagnostic Commands:**
```bash
# Check file permissions
ls -la ~/.openclaw/workspace/

# Check container user
docker exec sandbox-container whoami
docker exec sandbox-container id

# Test permissions in container
openclaw sandbox exec -- ls -la /workspace
```

**Fix:**
```bash
# Match container UID (usually 1000)
openclaw config set sandbox.user.uid 1000
openclaw config set sandbox.user.gid 1000

# Make files executable
chmod +x ~/.openclaw/workspace/script.sh

# Fix ownership
sudo chown -R 1000:1000 ~/.openclaw/workspace/

# Use read-write mount
openclaw config set sandbox.workspace.readOnly false

# Run as root (not recommended, use with care)
openclaw config set sandbox.user.runAsRoot true
```

**Auto-Fix Available:** Partial

---

### IMAGE_PULL_FAILED

**Symptoms:**
- "Failed to pull Docker image" error
- Sandbox container won't start
- Network timeout during pull
- Authentication required for image

**Common Causes:**
- No internet connection
- Docker Hub rate limit
- Private image requires auth
- Image doesn't exist

**Diagnostic Commands:**
```bash
# Check current image
openclaw config get sandbox.image

# Try pulling manually
docker pull $(openclaw config get sandbox.image)

# Check Docker Hub rate limit
docker pull ratelimitpreview/test

# List available images
docker images
```

**Fix:**
```bash
# Use pre-pulled image
docker pull python:3.11-slim
openclaw config set sandbox.image "python:3.11-slim"

# Login to Docker Hub (for private images)
docker login

# Use local image
openclaw config set sandbox.image.pullPolicy "IfNotPresent"

# Set registry mirror (China/restricted networks)
openclaw config set sandbox.image.registry "mirror.gcr.io"

# Build custom image
cd ~/.openclaw/sandbox/
docker build -t openclaw-sandbox:latest .
openclaw config set sandbox.image "openclaw-sandbox:latest"
```

**Auto-Fix Available:** No (requires network/auth)

---

### CONTAINER_NETWORK_ERROR

**Symptoms:**
- Sandbox cannot access network
- DNS resolution fails in container
- Cannot download packages
- API calls timeout

**Fix:**
```bash
# Enable network access
openclaw config set sandbox.network.enabled true

# Set DNS servers
openclaw config set sandbox.network.dns '["8.8.8.8", "1.1.1.1"]'

# Use host network (bypass isolation)
openclaw config set sandbox.network.mode "host"

# Or bridge with custom network
docker network create openclaw-net
openclaw config set sandbox.network.name "openclaw-net"
```

---

## Sandbox Configuration

### Recommended Settings
```yaml
sandbox:
  enabled: true
  image: "python:3.11-slim"

  memory:
    limit: "2GB"
    swap: "4GB"

  cpu:
    limit: 2.0
    shares: 1024

  timeout:
    execution: 300000
    startup: 30000

  workspace:
    path: "$HOME/.openclaw/workspace"
    readOnly: false

  user:
    uid: 1000
    gid: 1000
    runAsRoot: false

  network:
    enabled: true
    mode: "bridge"
    dns: ["8.8.8.8", "1.1.1.1"]

  security:
    privileged: false
    capAdd: []
    capDrop: ["ALL"]
```

### Security Best Practices

1. **Never run as root** unless absolutely necessary
2. **Limit memory/CPU** to prevent resource exhaustion
3. **Drop capabilities** - remove unnecessary Linux capabilities
4. **Use read-only mounts** when possible
5. **Enable timeout** to prevent runaway processes
6. **Disable network** for untrusted code
7. **Use specific image tags** instead of :latest

### Resource Limits

```bash
# Set CPU limit (1.5 cores)
openclaw config set sandbox.cpu.limit 1.5

# Set memory limit
openclaw config set sandbox.memory.limit "1GB"

# Set disk I/O limit
openclaw config set sandbox.disk.readBps "100MB"
openclaw config set sandbox.disk.writeBps "50MB"

# Set max processes
openclaw config set sandbox.pids.limit 100
```

### Monitoring

```bash
# Real-time stats
openclaw sandbox stats --watch

# Resource usage history
openclaw sandbox metrics --last 1h

# Alert on high usage
openclaw alerts add --metric sandbox_memory --threshold 90 --action notify
```

## Docker Troubleshooting

### Docker Won't Start
```bash
# Check systemd service
sudo systemctl status docker
sudo journalctl -u docker -n 50

# Check disk space
df -h

# Check Docker root
docker info | grep "Docker Root Dir"

# Clean up space
docker system prune -a
```

### Container Keeps Crashing
```bash
# View container logs
docker logs <container_id>

# Inspect container
docker inspect <container_id>

# Check exit code
docker ps -a --filter "exited=1"

# Run interactively for debugging
docker run -it --rm python:3.11-slim /bin/bash
```

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Installation Errors](installation-errors.md) - Docker setup
- [Configuration Errors](configuration-errors.md) - Config issues
- [Diagnostic Commands](diagnostic-commands.md) - CLI reference
