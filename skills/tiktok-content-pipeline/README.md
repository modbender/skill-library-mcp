# TikTok Content Pipeline

A complete, research-backed TikTok content automation skill for OpenClaw. Generate carousel content, publish via Postiz, schedule with account-age-aware timing, and optimize based on real analytics data — for any niche.

## Features

- **Carousel content generation** — AI-powered slide creation with hooks, CTAs, and SEO keyword overlays
- **Smart scheduling** — Research-backed optimal posting times (Tue-Thu 2-5pm) with automatic frequency adjustment based on account age
- **Multi-account management** — Run multiple TikTok accounts from one CLI
- **Viral content scoring** — Pre-post content analysis scores hook quality, structure, and engagement potential (0-100)
- **Performance diagnostics** — Automatic diagnosis matrix: high views + low engagement = fix CTA, low views + high saves = fix hook, etc.
- **Analytics engine** — Pull metrics from Postiz, generate reports, auto-implement optimizations
- **Template system** — Create reusable content templates for any niche (gaming, property, fitness, crypto, food, etc.)
- **Research-backed defaults** — All thresholds, timing, and strategies sourced from 2025-2026 TikTok algorithm research

## Quick Start

1. **Install**: `npm install` in the skill directory
2. **Configure**: Copy `config.example.json` → `accounts/your-brand/config.json`, add your Postiz API key and TikTok integration ID
3. **Create account**: `node cli.js create your-brand --template example-nostalgia`
4. **Generate & post**: `node cli.js generate your-brand --type showcase --post`

## Full Guide

See [SETUP.md](SETUP.md) for detailed setup, custom template creation, and automation via cron.

See [SKILL.md](SKILL.md) for the complete agent reference — viral mechanics, diagnostic matrix, threshold tables, and architecture.
