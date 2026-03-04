# Composable Pattern Examples

Illustrations of how OpenClaw primitives combine. Use these as inspiration, not templates.

## 1. Visual Monitoring Pipeline
**nodes** `camera_snap` → **image** analysis → state comparison → **message** alert + **canvas** dashboard · **cron** schedules checks

## 2. Parallel Research Aggregator
Parse query into facets → **sessions_spawn** parallel subagents (each using **web_search** / **web_fetch** / **browser**) → parent monitors via **sessions_list** → aggregate → **canvas** presentation

## 3. Location-Aware Context Switcher
**nodes** `location_get` → compare to known locations → trigger context-appropriate behaviours (email summary, calendar brief, automation) · **cron** polls, **memory** tracks history

## 4. Cross-Channel Thread Tracker
**memory_search** finds prior discussions across channels → bridge context ("continuing from your Telegram chat...") → **sessions_send** notifies related sessions

## 5. Scheduled Report Generator
**cron** triggers → **exec** local commands + **browser** authenticated dashboards + **web_fetch** APIs → synthesise → **canvas** render + **message** distribute

## 6. Interactive Approval Workflow
User request → pre-checks → **message** with inline buttons (✅/❌/⏸️) → on defer: **cron** reminder · on approve: execute + log to **memory**

## 7. Adaptive Learning Loop
Perform analysis → present with feedback mechanism → corrections stored in **memory** → adapt prompting from error history → **cron** reviews patterns, proposes skill updates
