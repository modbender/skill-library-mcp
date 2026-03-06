#!/bin/bash
#
# Check environment before Hummingbot installation
# Returns: TTY status, Docker, Git, container detection
#
set -eu

echo "Environment Check"
echo "================="
echo ""

# Check if running in container
if [ -f /.dockerenv ]; then
    echo "Container: Yes (Docker)"
    CONTAINER=true
elif grep -q docker /proc/1/cgroup 2>/dev/null || grep -q containerd /proc/1/cgroup 2>/dev/null; then
    echo "Container: Yes"
    CONTAINER=true
else
    echo "Container: No"
    CONTAINER=false
fi

# Check TTY
if [ -t 0 ]; then
    echo "Interactive TTY: Yes"
    TTY=true
else
    echo "Interactive TTY: No (will use defaults)"
    TTY=false
fi

# Check Docker
if command -v docker &>/dev/null; then
    echo "Docker: $(docker --version 2>/dev/null | head -1)"
    if docker info &>/dev/null; then
        echo "Docker daemon: Running"
    else
        echo "Docker daemon: Not running"
        exit 1
    fi
else
    echo "Docker: Not installed"
    exit 1
fi

# Check docker compose
if docker compose version &>/dev/null; then
    echo "Docker Compose: $(docker compose version --short 2>/dev/null)"
elif command -v docker-compose &>/dev/null; then
    echo "Docker Compose: $(docker-compose --version 2>/dev/null)"
else
    echo "Docker Compose: Not installed"
    exit 1
fi

# Check Git
if command -v git &>/dev/null; then
    echo "Git: $(git --version 2>/dev/null)"
else
    echo "Git: Not installed"
    exit 1
fi

# Check Make
if command -v make &>/dev/null; then
    echo "Make: Available"
else
    echo "Make: Not installed (required for setup)"
    exit 1
fi

echo ""
echo "Ready to install Hummingbot!"
