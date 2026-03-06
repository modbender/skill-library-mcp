# Edge Cases & Hardening

| # | Edge Case | Risk | Mitigation |
|---|-----------|------|------------|
| 🔴 1 | Current messages not on disk | High | OpenClaw writes JSONL in real-time — verified |
| 🔴 2 | Observer lookback too short during flush | High | Flush mode uses 2-hour lookback |
| 🔴 3 | Not enough token room for flush turn | High | softThresholdTokens bumped to 8000 |
| 🟡 4 | Observer-vs-observer race condition | Medium | Lock file with PID + 120s stale timeout |
| 🟡 5 | API failure during critical flush | Medium | Model fallback + manual notes as backup |
| 🟡 6 | memoryFlush fires only once per cycle | Medium | Retry logic + model fallback + manual notes |
| 🟢 7 | Group sessions don't get flush | Low | Groups reset frequently, rarely hit compaction |
