# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-18

### Added
- Initial release of Perplexity PRO integration for OpenClaw
- Anti-bot browser automation using Xvfb virtual display
- VNC-based manual authentication flow
- Persistent session storage in `~/.openclaw/browser-profile/`
- Support for macOS, Windows, and Linux VNC clients
- Cloudflare bypass via 7-level anti-detection strategy
- OpenClaw skill structure for ClawHub publishing
- Complete documentation (SKILL.md, README.md)

### Security
- VNC authentication with password protection
- Profile isolation per user
- OAuth token persistence (user responsibility to secure server)

### Notes
- Requires Google Chrome (not Snap version)
- Manual OAuth authentication required via VNC
- Tested on Ubuntu 22.04 LTS headless

## [Unreleased]

### Planned
- FlareSolverr integration for extreme bypass scenarios
- Automated VNC password rotation
- SSH tunnel support for secure remote access
- Multi-account support
- Docker containerization option
