---
name: happy-hues
description: Get curated color palettes from Happy Hues for design projects. Use when the user asks for color schemes, palette recommendations, design colors, UI colors, or mentions "配色", "color palette", "happy hues", "颜色方案". Supports filtering by mood (warm, dark, bold, minimal, etc.) and provides role-based colors (background, headline, button, highlight, etc.).
---

# Happy Hues — Curated Color Palettes

17 curated color palettes from [happyhues.co](https://www.happyhues.co), each with role-based colors for real design use.

## Data

Load `references/palettes.json` — array of 17 palettes, each with:

| Field | Description |
|-------|-------------|
| `id` | Palette number (1-17) |
| `name` | Short name (e.g. "Dark Mode", "Clean Blue") |
| `mood` | Comma-separated mood tags for filtering |
| `background` | Page/section background |
| `headline` | Heading text color |
| `paragraph` | Body text color |
| `button` | Primary button/CTA background |
| `buttonText` | Button text color |
| `stroke` | Border/stroke color |
| `main` | Card/container background |
| `highlight` | Accent/highlight color |
| `secondary` | Secondary accent |
| `tertiary` | Tertiary accent |

## Usage

1. Read `references/palettes.json`
2. Match user's mood/vibe to palette `mood` tags
3. Return palette with colors and their design roles
4. Link to `https://www.happyhues.co/palettes/{id}` for live preview

## Mood Quick Reference

- **Light/clean**: 3 (Clean Blue), 6 (Minimal Purple), 8 (Teal Minimal), 14 (Sunny Blue)
- **Dark**: 4 (Dark Mode), 10 (Forest Green), 12 (Deep Purple), 13 (Fire Dark), 16 (Dark Peach)
- **Warm/cozy**: 1 (Default), 5 (Earthy Green), 9 (Orange Pop), 15 (Warm Rose), 17 (Vintage Pink)
- **Bold/vibrant**: 2 (Bold Pop), 9 (Orange Pop), 13 (Fire Dark)
- **Soft/feminine**: 7 (Soft Pink), 15 (Warm Rose), 12 (Deep Purple)
- **Professional**: 3 (Clean Blue), 8 (Teal Minimal), 11 (Luxury Dark)
