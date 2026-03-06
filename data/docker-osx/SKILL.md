---
name: docker_osx
description: "Run macOS in Docker on Linux with KVM. Use when: user wants to build iOS apps/IPAs, needs macOS environment, wants to compile Apple apps without Mac, or wants to run macOS-only software. NOT for: servers without KVM, low-resource systems (needs 4+ CPU, 8GB RAM), or production macOS deployments. Requires Docker + KVM."
homepage: https://github.com/sickcodes/Docker-OSX
metadata:
  openclaw:
    emoji: 🍎
    requires:
      bins: [docker]
      kvm: true
---

# Docker-OSX

Run macOS in Docker - build iOS apps on Linux!

## Quick Start

```bash
start macos        # Boot VM (2-5 min)
status macos       # Check if ready
ssh macos          # Connect
stop macos         # Shutdown
```

## Commands

| Command | Description |
|---------|-------------|
| `start macos` | Boot macOS VM |
| `stop macos` | Shutdown VM |
| `status macos` | Check running |
| `ssh macos` | Get SSH command |
| `vnc macos` | Get VNC address |
| `logs macos` | View logs |

## Connection

- **SSH**: port 50922, password: `alpine`
- **VNC**: port 5900

## Building iOS

```bash
# In macOS terminal:
xcode-select --install
git clone <repo>
cd repo
xcodegen generate
xcodebuild -project App.xcodeproj -scheme App -configuration Release -destination 'generic/platform=iOS' CODE_SIGN_IDENTITY="" CODE_SIGNING_REQUIRED=NO CODE_SIGNING_ALLOWED=NO build
```

## Errors

| Error | Fix |
|-------|-----|
| KVM not available | Server needs hardware virtualization |
| Docker not installed | `curl -sSL get.docker.com | sh` |

## Resources

- 4+ CPU cores
- 8GB+ RAM
- 100GB disk
