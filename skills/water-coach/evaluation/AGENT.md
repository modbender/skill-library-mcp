# Water Coach - Agent Evaluation

## Test Prompt

```
I'm a new user. Set up water tracking for me. Weight: 80kg, goal: 2800ml.
```

## Quick Check

```bash
# Config
grep -E "weight_kg|default_goal_ml" data/water_config.json

# CSV headers
head -1 data/water_log.csv

# Dynamic enabled
grep enabled data/water_config.json
```

## Success

- Config: weight_kg=80, goal=2800, dynamic=true
- CSV: has logged_at,drank_at,date,slot,ml_drank,goal_at_time,message_id
