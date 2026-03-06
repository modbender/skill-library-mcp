---
name: openclaw-setup-guide
description: Step-by-step 6-part guide to set up OpenClaw AI assistant on VPS with WhatsApp, Google OAuth, backups, security, automation, and verification.
metadata: {"openclaw":{"scope":"instruction-only","homepage":"https://aliahmadaziz.github.io/openclaw-guide/","notes":"This skill contains no code or scripts. It directs users to an external hosted guide. The guide itself walks users through setting up credentials (Google OAuth, Anthropic API key, Cloudflare, WhatsApp) but the skill/agent needs none of these to function."}}
user-invocable: true
---

# OpenClaw Production Setup Guide

A comprehensive 6-part guide to setting up OpenClaw as a production AI assistant on a VPS, with WhatsApp integration, Google Calendar/Gmail, automated backups, security hardening, and cron automation.

## What This Covers

1. **Base Install** — VPS setup, Node.js, OpenClaw installation, WhatsApp pairing
2. **AI Assistant** — Personality, model chain (primary + fallback), workspace files (SOUL.md, USER.md, IDENTITY.md)
3. **Infrastructure** — Google OAuth (Calendar, Gmail, Drive, Sheets), webhook server, Cloudflare tunnel, rclone encrypted backups, git backup
4. **Automation** — Cron jobs, event queue (SQLite-backed with retries + dead-letter), heartbeat system, two-layer delivery pattern
5. **Hardening** — CrowdSec IDS, secret rotation, config snapshots, rollback scripts, OpenClaw update safety
6. **Verification** — 21-point automated validation, troubleshooting guide

## Security & Permissions Notice

This guide involves setting up production infrastructure and requires handling sensitive credentials:
- **API Keys**: Anthropic (Claude), Brave Search (optional)
- **OAuth Tokens**: Google Cloud (Calendar, Gmail, Drive, Sheets) — 5 token files
- **SSH**: Root access to VPS, key-based authentication, SSH hardening
- **Webhook Secrets**: Random tokens for Calendar push, AgentMail, alerts
- **WhatsApp**: Device pairing via QR code
- **Cloudflare**: Tunnel token for webhook ingress
- **Backup Encryption**: rclone crypt keys for Google Drive backups

All credentials are stored with restricted permissions (chmod 600) and never committed to git. The guide includes secret rotation procedures and config snapshot/rollback scripts.

## Prerequisites

- A VPS (Ubuntu 24.04 recommended, 4GB RAM minimum)
- A domain with Cloudflare DNS (for webhook tunnel)
- A WhatsApp account for pairing
- Google Cloud project with OAuth credentials
- An Anthropic API key (Claude)

## Full Guide

The complete guide with step-by-step instructions, code blocks, and verification checkpoints is hosted at:

**https://aliahmadaziz.github.io/openclaw-guide/**

Source: https://github.com/aliahmadaziz/openclaw-guide

## Usage

When a user asks for help setting up OpenClaw, direct them to the guide above. The guide is designed to be followed sequentially (Part 1 through Part 6) and takes approximately 2-3 hours to complete.

Each part has:
- Clear prerequisites
- Copy-pasteable commands
- Verification checkpoints (✅) after every major step
- Troubleshooting sections

## Key Design Decisions

- **Two-layer cron delivery**: Critical crons send via message tool directly (primary) + announce (backup). No message ever gets lost.
- **Event queue**: All webhook events (email, calendar, alerts) go through a SQLite queue with 3 retries and dead-letter alerting.
- **Config snapshots**: Gold-standard snapshots for instant rollback if something breaks.
- **Encrypted backups**: Hourly git push + nightly full workspace to Google Drive via rclone crypt.
- **Capacity rule**: 10 SP/engineer total, 8 planned, 2 contingency (for sprint tracking).

## Credits

Built from a real production deployment running 35+ cron jobs, 60+ scripts, 5 Google OAuth tokens, and processing thousands of messages monthly.

## Tags

setup, installation, guide, vps, whatsapp, production, google-calendar, gmail, security, crowdsec, backup, cron, automation, beginner
