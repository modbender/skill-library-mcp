---
name: feishu-api-cache-fix
description: Gateway calls Feishu API every minute, causing rate limit exhaustion.
---

# feishu-api-cache-fix

> Fix Feishu API rate limit issue

**Version**: 1.0.1
**Author**: @bryan-chx
**Tags**: feishu, api, fix, performance

## Problem

Gateway calls Feishu API every minute, causing rate limit exhaustion.

## Solution

Add 2-hour cache to probe.ts

## Usage

```bash
sudo bash fix_feishu_cache.sh
```
