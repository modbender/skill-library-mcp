# Deployment Pipeline Skills

## Overview

You are building a skill graph for a cloud deployment pipeline. Each skill represents a discrete capability that an automation agent can perform. Skills depend on other skills — they cannot execute until their dependencies have completed successfully.

Create individual skill files and a graph manifest that captures these relationships.

---

## Skills

### 1. Provision Infrastructure
- **ID**: `provision-infrastructure`
- **Purpose**: Spin up cloud resources (VMs, load balancers, networking) using infrastructure-as-code templates.
- **Dependencies**: None (this is the root skill)
- **Outputs**: Resource IDs, IP addresses, connection strings

### 2. Configure Services
- **ID**: `configure-services`
- **Purpose**: Install and configure required services (database, cache, message queue) on the provisioned infrastructure.
- **Dependencies**: `provision-infrastructure`
- **Outputs**: Service endpoints, health check URLs

### 3. Deploy Application
- **ID**: `deploy-application`
- **Purpose**: Build application artifacts, push container images, and deploy to the configured infrastructure.
- **Dependencies**: `configure-services`
- **Outputs**: Deployment ID, application URL, deployed version

### 4. Run Tests
- **ID**: `run-tests`
- **Purpose**: Execute smoke tests, integration tests, and end-to-end tests against the deployed application.
- **Dependencies**: `deploy-application`
- **Outputs**: Test results, pass/fail status, coverage report URL

### 5. Monitor Health
- **ID**: `monitor-health`
- **Purpose**: Watch application metrics (latency, error rate, CPU/memory) for a stabilization period after deployment.
- **Dependencies**: `deploy-application`
- **Outputs**: Health status, metric snapshots, alert triggers

### 6. Rollback
- **ID**: `rollback`
- **Purpose**: Revert to the previous deployment version if tests fail or health monitoring detects issues.
- **Dependencies**: `monitor-health`, `run-tests`
- **Outputs**: Rollback confirmation, restored version ID

---

## Graph Requirements

The `graph.json` file must represent these relationships as a directed acyclic graph:

- **Nodes**: One entry per skill with `id`, `name`, and `file_path` fields
- **Edges**: One entry per dependency with `from` (dependency) and `to` (dependent) fields, plus a `type` field set to `"depends_on"`
- The graph must have exactly 6 nodes and at least 5 edges
- Every node must be connected (no orphans)
- The graph must be acyclic

## Skill File Requirements

Each skill file should be a markdown document with YAML front matter:

```yaml
---
name: "Human Readable Name"
id: "skill-id"
depends_on:
  - "dependency-id-1"
  - "dependency-id-2"
---
```

Followed by markdown content with:
- A description of what the skill does
- A "Related Skills" section listing upstream dependencies and downstream dependents
- A "Steps" section with 3-5 key steps for executing the skill
