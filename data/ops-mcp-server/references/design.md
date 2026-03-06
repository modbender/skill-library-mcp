# Ops MCP Server Event Format Design

This document describes the event format design for the Ops MCP Server, specifically the NATS subject patterns used for event messaging.

## Overview

The Ops system uses NATS subject-based messaging to organize and route operational events. Events are categorized into three main types:

1. Namespace-level Events - Kubernetes resource events within namespaces
2. Node Events - Kubernetes node-level events
3. Notification Events - External system notifications

## Event Format Specifications

### 1. Namespace-Level Events

Namespace-level events track Kubernetes resources within specific namespaces.

#### Format

```
ops.clusters.{cluster}.namespaces.{namespace}.{resourceType}.{resourceName}.{observation}
```

#### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `{cluster}` | Cluster name (from `EVENT_CLUSTER` environment variable) | `production`, `staging` |
| `{namespace}` | Kubernetes namespace | `default`, `kube-system` |
| `{resourceType}` | Resource type | `deployments`, `pods`, `configmaps`, `services` |
| `{resourceName}` | Specific resource name | `api-gateway`, `nginx-abc123` |
| `{observation}` | Observation type (see below) | `status`, `events`, `alerts`, `findings` |

#### Observation Types

| Type | Description | Use Case |
|------|-------------|----------|
| `status` | Resource status information | Running state, health status, readiness |
| `events` | Kubernetes events | Pod started, image pulled, scheduling events |
| `alerts` | Alert information | Resource threshold alerts, health alerts |
| `findings` | Proactive reports | Auto-discovered issues, status updates |

#### Examples

```bash
# Pod events in production namespace
ops.clusters.cluster-1.namespaces.default.pods.api-gateway-abc123.events

# Deployment status in staging
ops.clusters.cluster-2.namespaces.app.deployments.web-service.status

# ConfigMap alerts
ops.clusters.cluster-1.namespaces.config.configmaps.app-config.alerts

# Service findings
ops.clusters.cluster-1.namespaces.default.services.api-gateway.findings
```

#### Wildcard Patterns

```bash
# All pod events in a namespace
ops.clusters.*.namespaces.production.pods.*.events

# All events for a specific pod
ops.clusters.*.namespaces.default.pods.api-gateway-abc123.*

# All resources in a namespace
ops.clusters.cluster-1.namespaces.default.*.*.events

# Multi-level match
ops.clusters.*.namespaces.production.>
```

### 2. Node Events

Node events track cluster node-level information.

#### Format

```
ops.clusters.{cluster}.nodes.{nodeName}.{observation}
```

#### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `{cluster}` | Cluster name (from `EVENT_CLUSTER` environment variable) | `production`, `staging` |
| `{nodeName}` | Kubernetes node name | `worker-01`, `master-03` |
| `{observation}` | Observation type (see below) | `events`, `alerts`, `findings` |

#### Observation Types

| Type | Description | Use Case |
|------|-------------|----------|
| `events` | Kubernetes node events | Node ready, disk pressure, memory pressure |
| `alerts` | Node-level alerts | Resource exhaustion, hardware issues |
| `findings` | Proactive node reports | Health checks, capacity warnings |

#### Examples

```bash
# Node events
ops.clusters.cluster-1.nodes.worker-01.events

# Node alerts
ops.clusters.cluster-1.nodes.master-03.alerts

# Node findings
ops.clusters.cluster-2.nodes.worker-02.findings
```

#### Wildcard Patterns

```bash
# All events from all nodes
ops.clusters.cluster-1.nodes.*.events

# All observations for a specific node
ops.clusters.cluster-1.nodes.worker-01.*

# Multi-level match for all node data
ops.clusters.*.nodes.>
```

### 3. Notification Events

Notification events are not collected from Kubernetes by the Ops project. Instead, they are used to collect notifications from external systems and transform them into processable operational events.

#### Format

```
ops.notifications.providers.{provider}.channels.{channel}.severities.{severity}
```

#### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `{provider}` | Notification provider or system name | `ksyun`, `ai`, `alertmanager`, `pagerduty` |
| `{channel}` | Notification channel type | `webhook`, `email`, `sms`, `slack` |
| `{severity}` | Severity level | `info`, `warning`, `error`, `critical` |

#### Severity Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `info` | Informational messages | Status updates, routine notifications |
| `warning` | Warning conditions | Potential issues, capacity warnings |
| `error` | Error conditions | Service errors, failed operations |
| `critical` | Critical alerts | Service down, security incidents |

#### Examples

```bash
# Critical webhook from KSyun
ops.notifications.providers.ksyun.channels.webhook.severities.critical

# Warning email notifications
ops.notifications.providers.alertmanager.channels.email.severities.warning

# Info-level Slack messages from AI system
ops.notifications.providers.ai.channels.slack.severities.info

# SMS alerts from PagerDuty
ops.notifications.providers.pagerduty.channels.sms.severities.error
```

#### Wildcard Patterns

```bash
# All critical notifications from all providers
ops.notifications.providers.*.channels.*.severities.critical

# All webhook notifications
ops.notifications.providers.*.channels.webhook.severities.*

# All notifications from a specific provider
ops.notifications.providers.ksyun.>

# All notifications across all channels and severities
ops.notifications.>
```

## Usage in MCP Tools

The `get-events-from-ops` tool accepts these NATS subject patterns as the `subject_pattern` parameter.

### Query Examples

```bash
# Get pod events from production namespace
subject_pattern: "ops.clusters.*.namespaces.production.pods.*.events"

# Get all critical notifications
subject_pattern: "ops.notifications.providers.*.channels.*.severities.critical"

# Get all events for a specific node
subject_pattern: "ops.clusters.cluster-1.nodes.worker-01.*"

# Get all events from a namespace (multi-level)
subject_pattern: "ops.clusters.*.namespaces.default.>"
```

## Best Practices

### 1. Use Specific Patterns When Possible

```bash
# Good - specific
ops.clusters.cluster-1.namespaces.default.pods.api-gateway.events

# Less efficient - too broad
ops.clusters.*.namespaces.*.pods.*.events
```

### 2. Leverage Wildcards Appropriately

- Use `*` for single-level wildcard (one segment)
- Use `>` for multi-level wildcard (remaining path)

### 3. Filter by Observation Type

```bash
# Only get alerts, not all observations
ops.clusters.cluster-1.namespaces.*.pods.*.alerts
```

### 4. Combine with Time Filters

Always use `start_time` parameter to limit result scope:

```bash
{
  "subject_pattern": "ops.clusters.cluster-1.namespaces.default.pods.*.events",
  "start_time": "1740672000000",  // Unix timestamp in milliseconds
  "page_size": "10"
}
```

## Environment Variables

### Required Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `EVENT_CLUSTER` | Cluster identifier used in subject patterns | `cluster-1`, `cluster-2`|

### Example Configuration

```bash
export EVENT_CLUSTER="cluster-1"
```

This ensures all events from this cluster will have the subject prefix:

```bash
ops.clusters.cluster-1.*
```

## Reference

- NATS Subject Documentation: <https://docs.nats.io/nats-concepts/subjects>
- Wildcard Patterns:
  - `*` matches one token at a specific level
  - `>` matches one or more tokens at the tail of the subject
- MCP Tool: `get-events-from-ops`, `list-events-from-ops`
