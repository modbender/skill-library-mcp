---
name: aws-cloud-watch
description: Query AWS CloudWatch metrics for ECS/EC2/RDS and return charts.
---

# AWS CloudWatch Skill

Use this skill to fetch CloudWatch metrics for ECS / EC2 / RDS and return text summaries.

## Entry

Preferred entry script:

```
node {baseDir}/src/skill.mjs --service ecs --metric cpu --resource <cluster-name> --hours 1
```

## Environment

Required (AK/SK):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Optional:
- `AWS_REGION` (default: `us-west-2`)

## Usage (internal)

Run the CLI script in `{baseDir}`:

```
node {baseDir}/src/cli.js --service ecs --metric CPUUtilization --resource <cluster-name-or-arn> --hours 1
node {baseDir}/src/cli.js --service ecs --metric cpu --resource <cluster-name>
```

You can define metric aliases in `{baseDir}/config.json` (see `config.example.json`).

### Supported services
- `ecs` (cluster-level metrics)
- `ec2`
- `rds`

### Defaults
- Region: `us-west-2`
- Period: 300 seconds (5 minutes)
- Time window: 1 hour

## Notes

- ECS metrics are cluster-level unless Container Insights is enabled.
- If the metric is unavailable, return a clear message.
- Text-only output (no chart rendering).
- Uses SigV4 signing via native crypto (no AWS SDK, no external packages).
