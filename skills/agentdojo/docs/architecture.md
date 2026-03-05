# AgentDojo Architecture

## Pipeline
1. Cron trigger
2. Budget and policy preflight
3. Drill selection (role rotation + score gaps)
4. Isolated run execution
5. Scoring and audit checks
6. Persist state + daily digest

## Recommended OpenClaw Cron Pattern
- One isolated orchestration run at configured local time.
- Optional split: one run for learning, one run for digest aggregation.

Example schedule defaults:
- Learning window: 04:00 local
- Digest post-process: 04:20 local

## Hard Stops
- Max daily token/cost reached
- Policy violation detected
- Source quality below threshold
- Timeout hit

## Rollout
- Week 1: pilot with 3 agents
- Week 2: expand to full team
- Week 3: tune scoring and token profile
