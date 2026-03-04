# Product Requirements Document (MVP)
**Project**: Lightweight Observability Skill (OpenClaw)
**Status**: Implemented (v1.0)
**Owner**: erain
**Date**: 2026-02-08

#### 1. Problem & Goal
*   **Problem**: Currently, we lack visibility into token costs and system errors without SSH-ing into the server.
*   **Goal**: Create a low-cost, zero-maintenance tool to track daily costs and recent errors directly within Telegram.

#### 2. User Stories
*   As a **Bot Owner**, I want to send a command (e.g., `/stats` or natural language), so that I can instantly see how much money I spent today and yesterday.
*   As a **Developer**, I want to see a summary of recent error logs, so that I can spot system issues without opening a terminal.

#### 3. Functional Requirements
This feature is implemented as a **Local Skill** (`openclaw-skill-observability`).

**Feature A: Cost Reporting**
*   **Trigger**: User asks "How much did I spend today?" or similar.
*   **Tool**: `get_cost_report`
*   **Logic**: 
    1. Call `openclaw sessions list` to get recent history.
    2. Filter sessions updated in the last 24h.
    3. Aggregate token usage by model (Gemini Pro, Flash, GPT, etc.).
    4. Calculate estimated cost based on hardcoded pricing table.
*   **Output**: A text/markdown table summary.

**Feature B: Error Summary**
*   **Trigger**: User asks "Show me recent errors".
*   **Tool**: `get_recent_errors`
*   **Logic**: 
    1. Scan recent sessions from `openclaw sessions list`.
    2. Filter for sessions where `lastStatus != 'ok'` or `abortedLastRun == true`.
*   **Output**: A list of failed sessions with IDs and status codes.

#### 4. Non-Functional Requirements (Technical Constraints)
*   **Zero Infrastructure**: Do not install Prometheus/Grafana/InfluxDB.
*   **API-based**: Use OpenClaw's built-in CLI tools (`openclaw sessions list`) instead of parsing raw logs, ensuring compatibility with future versions.
*   **Native UI**: Text-only output for Telegram.
