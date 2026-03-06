# OpenClaw AWS CloudWatch Skill (Node.js)

This skill queries CloudWatch metrics for ECS/EC2/RDS and returns text summaries.

## Setup

No npm install required (zero external dependencies).

## Environment

```bash
set AWS_ACCESS_KEY_ID=xxx
set AWS_SECRET_ACCESS_KEY=yyy
set AWS_REGION=us-west-2
```

## Config (optional)

Copy `config.example.json` to `config.json` and adjust aliases/defaults.

## Run

```bash
node src/skill.mjs --service ecs --metric cpu --resource my-ecs-cluster --hours 1
node src/cli.mjs --service ecs --metric CPUUtilization --resource my-ecs-cluster --hours 1
node src/cli.mjs --service ecs --metric MemoryUtilization --resource my-ecs-cluster --serviceName my-ecs-service --hours 1
node src/cli.mjs --service ec2 --metric CPUUtilization --resource i-1234567890abcdef0 --hours 3
node src/cli.mjs --service rds --metric connections --resource mydbinstance --hours 6
```


## Output

- Text summary to stdout (min/max/avg).

## Notes

- ECS without Container Insights supports cluster-level `CPUUtilization` / `MemoryReservation`.
- Default period: 300s (5 minutes). Default region: `us-west-2`.
- You can use metric aliases (see `config.example.json`).
- Text-only output (no chart rendering).
