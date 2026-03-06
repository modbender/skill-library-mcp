# Events Examples

Query Kubernetes and system events using NATS subject patterns.

## Available Tools

### 1. list-events-from-ops

List available event types with search and pagination.

**Parameters:**

- `search` (optional, string): Search term to filter event types
- `page` (optional, string): Page number (default: 1)
- `page_size` (optional, string): Results per page (default: 10)

### 2. get-events-from-ops

Get events using NATS subject patterns.

**Parameters:**

- `subject_pattern` (required, string): NATS subject pattern
- `start_time` (optional, string): Start timestamp in milliseconds (e.g., `1740672000000`)
- `page` (optional, string): Page number (default: 1)
- `page_size` (optional, string): Events per page (default: 10)

## Event Subject Patterns

Based on the [design document](../references/design.md), events follow these patterns:

### Namespace-Level Events

```
ops.clusters.{cluster}.namespaces.{namespace}.{resourceType}.{resourceName}.{observation}
```

**Resource Types:** `deployments`, `pods`, `configmaps`, `services`, etc.  
**Observations:** `status`, `events`, `alerts`, `findings`

### Node Events

```
ops.clusters.{cluster}.nodes.{nodeName}.{observation}
```

**Observations:** `events`, `alerts`, `findings`

### Notification Events

```
ops.notifications.providers.{provider}.channels.{channel}.severities.{severity}
```

**Providers:** `ksyun`, `ai`, `alertmanager`, `pagerduty`  
**Channels:** `webhook`, `email`, `sms`, `slack`  
**Severities:** `info`, `warning`, `error`, `critical`

## Example 1: List Available Event Types

```bash
# List all event types
npx mcporter call ops-mcp-server list-events-from-ops

# Search for specific events
npx mcporter call ops-mcp-server list-events-from-ops search=pod page_size=20
```

## Example 2: Get Pod Events

```bash
# Get pod events
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.*.events" start_time="1740672000000" page_size="10"

# Simplified (without optional params)
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.*.events"
```

### Subject Pattern Examples

```bash
# All pod events in kube-system
ops.clusters.*.namespaces.kube-system.pods.*.events

# Specific pod
ops.clusters.cluster-1.namespaces.kube-system.pods.calico-node-abc123.events

# All pod statuses
ops.clusters.*.namespaces.kube-system.pods.*.status

# Pod alerts only
ops.clusters.*.namespaces.*.pods.*.alerts
```

## Example 3: Get Deployment Events

```bash
# Get deployment events
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.deployments.*.events"
```

## Example 4: Get Node Events

```bash
# Get all node events
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.cluster-1.nodes.*.events" start_time="1740672000000"
```

### Subject Pattern Examples

```bash
# All node events
ops.clusters.cluster-1.nodes.*.events

# Specific node
ops.clusters.cluster-1.nodes.worker-01.events

# Node alerts
ops.clusters.*.nodes.*.alerts
```

## Example 5: Get Notification Events

```bash
# Get critical notifications
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.notifications.providers.*.channels.*.severities.critical" start_time="1740585600000"
```

### Subject Pattern Examples

```bash
# All critical notifications
ops.notifications.providers.*.channels.*.severities.critical

# Webhook notifications from ksyun
ops.notifications.providers.ksyun.channels.webhook.severities.*

# All error-level notifications
ops.notifications.providers.*.channels.*.severities.error
```

## Wildcard Patterns

### Single-Level Wildcard (`*`)

Matches exactly one token at that level:

```bash
# All pods in kube-system namespace (any cluster)
ops.clusters.*.namespaces.kube-system.pods.*.events

# All namespaces in cluster-1
ops.clusters.cluster-1.namespaces.*.pods.calico-node.events
```

### Multi-Level Wildcard (`>`)

Matches one or more tokens at the tail:

```bash
# Everything under kube-system namespace
ops.clusters.*.namespaces.kube-system.>

# All events for a specific pod (all observation types)
ops.clusters.*.namespaces.default.pods.api-gateway.>

# All notifications
ops.notifications.>
```

## Time-Based Queries

Convert time to Unix timestamp (milliseconds):

```bash
# Current time
date +%s000

# 1 hour ago
echo $(($(date +%s) - 3600))000

# Specific date (macOS)
date -j -f "%Y-%m-%d %H:%M:%S" "2024-01-15 10:00:00" +%s000
```

### Example with Timestamp

```bash
# Get pod events with pagination
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.*.events" start_time="1740672000000" page="1" page_size="20"
```

## Expected Output

```json
{
  "events": [
    {
      "subject": "ops.clusters.cluster-1.namespaces.kube-system.pods.calico-node-abc123.events",
      "timestamp": 1740672000000,
      "data": {
        "type": "Normal",
        "reason": "Started",
        "message": "Started container calico-node",
        "metadata": {
          "cluster": "cluster-1",
          "namespace": "kube-system",
          "resourceType": "pods",
          "resourceName": "calico-node-abc123"
        }
      }
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 10
}
```

## Troubleshooting

### No Events Found

**Problem:** Query returns no events

**Solutions:**

1. Check subject pattern syntax (use `*` and `>` correctly)
2. Verify time range includes events
3. List event types first: `list-events-from-ops`
4. Try broader pattern (use `>` instead of `*`)

### Invalid Subject Pattern

**Problem:** Error about invalid pattern

**Solutions:**

1. Ensure pattern matches one of the three formats (namespace, node, notification)
2. Use correct wildcard syntax (`*` for single level, `>` for multi-level)
3. Check for typos in pattern segments

### Too Many Results

**Problem:** Response is too large

**Solutions:**

1. Add `start_time` to limit time range
2. Reduce `page_size`
3. Use more specific pattern (fewer wildcards)

## Best Practices

### 1. Start Broad, Then Narrow

```bash
# Step 1: List event types
npx mcporter call ops-mcp-server list-events-from-ops search=pod

# Step 2: Get all pod events
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.*.events"

# Step 3: Filter to specific pod
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.cluster-1.namespaces.kube-system.pods.calico-node-abc123.events"
```

### 2. Always Use Time Filters

```bash
# Good - limited time range
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.*.events" start_time="1740672000000"

# Avoid - no time limit
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.*.events"
```

### 3. Use Appropriate Wildcards

```bash
# Good - specific with single wildcard
ops.clusters.*.namespaces.kube-system.pods.*.events

# Good - multi-level for exploration
ops.clusters.*.namespaces.kube-system.>

# Avoid - too broad
ops.>
```

### 4. Leverage Observation Types

```bash
# Get only alerts
ops.clusters.*.namespaces.kube-system.pods.*.alerts

# Get only status updates
ops.clusters.*.namespaces.kube-system.pods.*.status

# Get all observations
ops.clusters.*.namespaces.kube-system.pods.*.>
```

## Real-World Scenarios

### Scenario 1: Pod Restart Investigation

```bash
# Step 1: Find pod events
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.*.events" start_time="1740668400000"

# Step 2: Get specific pod alerts
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.calico-node-abc123.alerts"

# Step 3: Get all observations
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.calico-node-abc123.>"
```

### Scenario 2: Deployment Rollout Monitoring

```bash
# Monitor deployment events
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.cluster-1.namespaces.kube-system.deployments.coredns.events"

# Check pod events during rollout
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.coredns-*.events" start_time="1740671400000"

# Verify no alerts
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.namespaces.kube-system.pods.coredns-*.alerts"
```

### Scenario 3: Node Health Check

```bash
# Get node events
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.cluster-1.nodes.*.events" start_time="1740668400000"

# Check for node alerts
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.*.nodes.*.alerts"

# Specific node investigation
npx mcporter call ops-mcp-server get-events-from-ops \
  subject_pattern="ops.clusters.cluster-1.nodes.worker-01.>"
```

## Reference

- **Tools**: `list-events-from-ops`, `get-events-from-ops`
- **Design Document**: [design.md](../references/design.md)
- **NATS Documentation**: <https://docs.nats.io/nats-concepts/subjects>
- **Wildcard Reference**:
  - `*` - Matches one token
  - `>` - Matches one or more tokens (tail only)
