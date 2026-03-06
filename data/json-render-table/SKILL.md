---
name: json-render-table
description: Render compact generic data tables to PNG images with json-render-cli. Use when users ask to visualize arbitrary structured rows/columns (non-ticket-specific) as clean table screenshots with controllable layout.
user-invocable: false
---

# JSON Render Table

## Overview

Render generic structured data into compact table images using `json-render-cli` components (`Column`, `Row`, `Container`, `Text`, `Badge`).
Use this skill for non-ticket table use cases.

## Workflow

1. Ensure `json-render` is available. If missing, run `npm i -g json-render-cli`; if Chromium is missing, run `npx playwright install chromium`.
2. Define target columns and row schema for the current dataset.
3. Generate message JSON in memory from the table template.
4. Pass config via process substitution (`-c <(...)`) to avoid temporary config files.
5. Set `screenshot.fullPage=true` when row count or line wrapping is variable.
6. Tune viewport width/height to the current content footprint before final render, and avoid oversized fixed `--size`.
7. Render PNG and return output path (or Base64 only when explicitly requested).
8. Theme mode is configured with `theme.mode`; use `system` by default, or force `light` / `dark` when needed.

## Agent Coordination

- Prefer rendering in the current (main) agent when the image must be delivered in the same turn.
- Delegate rendering to a sub-agent only when output-path handoff is explicit and deterministic.
- Keep rendered PNG files intact in sub-agent execution; do not delete or move them there.
- Perform garbage collection only in the main agent, and only after delivery succeeds.

## Model Routing

- If the current assistant model is high-cost (for example, Opus-class), route simple deterministic rendering to a lower-cost fast model (for example, `gemini3flash`) only when Agent Coordination rules can be enforced; otherwise render in the current main agent.

## Use Case Selection

- Generic table: use `references/compact-table-template.md`.
- Ticket-focused table: use `json-render-ticket-table`.
- Information cards (KPI/compare/summary): use `json-render-info-cards`.
- Announcement/hero cards: use `json-render-announcement-cards`.
- Flow/timeline summaries: use `json-render-flow-summary`.

## Build And Render

Use `references/compact-table-template.md`.
Treat the included template as an executable starter and customize columns and widths per dataset.

Default style:
- No title area
- Compact header + body
- Edge-to-edge screenshot
- Stable column widths
- Bottom rows remain visible (`screenshot.fullPage=true`)

## Layout Rules

- Define columns with `Row + Container` and explicit widths.
- Keep spacing compact and deterministic.
- Use `Badge` only for categorical status-like fields.
- Resize the widest column first when content overflows.
- Keep viewport width close to the sum of column widths and avoid large horizontal slack.
- Start from a compact viewport height and expand only when clipping appears.

## Output Rules

- Prefer `-o /tmp/<name>.png` for image delivery.
- Use `-o stdout` only when caller explicitly asks for Base64.
- Avoid temporary JSON files unless explicitly requested.
- If a sub-agent renders the PNG, return path only and skip cleanup in that sub-agent.
- Run final PNG cleanup only in the main agent after image delivery.

## Troubleshooting

- If Chromium is missing, run: `npx playwright install chromium`.
- If rendering is too wide, reduce wide columns or font size.
- If left/right whitespace is too large, decrease viewport width or topic column width and rerender.
- If top/bottom whitespace is too large, decrease viewport height and rerender.
- If bottom rows are clipped, enable `screenshot.fullPage=true`.
