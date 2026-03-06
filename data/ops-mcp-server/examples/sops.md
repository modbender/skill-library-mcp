# SOPS Operations Examples

Execute standardized operational procedures (SOPS) safely and consistently.

## Available Tools

### 1. list-sops-from-ops

List all available SOPS procedures.

**Parameters:** None

### 2. list-sops-parameters-from-ops

Get required parameters for a specific SOPS procedure.

**Parameters:**

- `sops_id` (required, string): ID of the SOPS procedure

### 3. execute-sops-from-ops

Execute a SOPS procedure.

**Parameters:**

- `sops_id` (required, string): ID of the SOPS procedure to execute
- `parameters` (optional, string): JSON string of parameters

## What are SOPS?

SOPS (Standard Operating Procedures) are predefined operational tasks that:

- Ensure consistent execution across teams
- Reduce human error
- Provide audit trails
- Enable safe automation

## Example 1: List Available SOPS

```bash
# List all SOPS procedures
npx mcporter call ops-mcp-server list-sops-from-ops
```

### Expected Response

```json
{
  "available_sops": [
    {
      "description": "",
      "id": "clear-mount",
      "variables": {
        "cluster": {
          "desc": "cluster"
        },
        "host": {
          "desc": "host",
          "required": true
        }
      }
    },
    {
      "description": "",
      "id": "restart-kubelet-bypod",
      "variables": {
        "cluster": {
          "desc": "cluster"
        },
        "host": {
          "value": "anymaster",
          "desc": "host",
          "required": true
        },
        "namespace": {
          "display": "namespace",
          "required": true
        },
        "pod": {
          "display": "pod name",
          "required": true
        },
        "white": {
          "display": "white",
          "required": true
        },
        "whitelist": {
          "display": "whitelist",
          "required": true,
          "examples": [
            "white1,white2,white3"
          ]
        }
      }
    },
    {
      "description": "restart node or host",
      "id": "restart-node",
      "variables": {
        "cluster": {
          "desc": "cluster"
        },
        "host": {
          "desc": "host",
          "required": true
        },
        "white": {
          "required": true
        }
      }
    },
    {
      "description": "",
      "id": "list-clusters",
      "variables": {
        "cluster": {
          "desc": "cluster"
        },
        "host": {
          "value": "anymaster",
          "desc": "host",
          "required": true
        },
        "namespace": {
          "default": "ops-system",
          "display": "namespace",
          "required": true
        }
      }
    }
  ],
  "count": 18
}
```

## Example 2: Get SOPS Parameters

```bash
# Get parameters for list-clusters
npx mcporter call ops-mcp-server list-sops-parameters-from-ops sops_id="list-clusters"

# Get parameters for restart-kubelet-bypod
npx mcporter call ops-mcp-server list-sops-parameters-from-ops sops_id="restart-kubelet-bypod"
```

### Expected Response

```json
{
  "count": 3,
  "parameters": [
    {
      "description": "host",
      "display": "",
      "name": "host",
      "required": true
    },
    {
      "default": "ops-system",
      "description": "",
      "display": "namespace",
      "name": "namespace",
      "required": true
    },
    {
      "description": "cluster",
      "display": "",
      "name": "cluster",
      "required": false
    }
  ],
  "sops_id": "list-clusters"
}
```

## Example 3: Execute SOPS

```bash
# Execute list-clusters
npx mcporter call ops-mcp-server execute-sops-from-ops \
  sops_id="list-clusters" parameters='{"namespace":"ops-system","host":""}'
```
## Expected Response

### Execution Success

```
### Run Details
#### list-clusters
- Step: list-clusters
- Output:
NAME                            DESCRIPTION
cluster1                        cluster1
cluster2                        cluster2
cluster3                        cluster3
```

## Troubleshooting

### SOPS Not Found

**Problem:** SOPS ID not found

**Solutions:**

1. List all SOPS: `list-sops-from-ops`
2. Check SOPS ID spelling
3. Verify SOPS module is enabled

## Real-World Scenarios

### Scenario 1: Incident Response

```bash
# Step 1: List available procedures
npx mcporter call ops-mcp-server list-sops-from-ops

# Step 2: Get parameters
npx mcporter call ops-mcp-server list-sops-parameters-from-ops sops_id="pod-restart"

# Step 3: Execute
npx mcporter call ops-mcp-server execute-sops-from-ops \
  sops_id="pod-restart" parameters='{"namespace":"kube-system","pod_name":"calico-node-abc123"}'
```

### Scenario 2: Scheduled Maintenance

```bash
# Backup database
npx mcporter call ops-mcp-server execute-sops-from-ops \
  sops_id="db-backup" parameters='{"database":"kube-system"}'

# Scale down
npx mcporter call ops-mcp-server execute-sops-from-ops \
  sops_id="scale-deployment" parameters='{"namespace":"kube-system","deployment":"coredns","replicas":0}'

# Migrate database
npx mcporter call ops-mcp-server execute-sops-from-ops \
  sops_id="db-migrate" parameters='{"database":"kube-system"}'

# Scale up
npx mcporter call ops-mcp-server execute-sops-from-ops \
  sops_id="scale-deployment" parameters='{"namespace":"kube-system","deployment":"coredns","replicas":3}'
```

### Scenario 3: Load Testing Preparation

```bash
# Scale up deployment
npx mcporter call ops-mcp-server execute-sops-from-ops \
  sops_id="scale-deployment" parameters='{"namespace":"kube-system","deployment":"coredns","replicas":20}'

# Increase resources
npx mcporter call ops-mcp-server execute-sops-from-ops \
  sops_id="increase-resources" parameters='{"namespace":"kube-system","deployment":"coredns","cpu":"2000m","memory":"4Gi"}'
```

## SOPS Naming Conventions

Common SOPS naming patterns:

- **Action-Resource**: `restart-pod`, `scale-deployment`, `delete-job`
- **Category**: `k8s-pod-restart`, `db-backup-mysql`, `cache-clear-redis`
- **Emergency**: `emergency-stop`, `rollback-deployment`, `failover-database`

## Parameter Types

Common parameter types:

- **string**: `"kube-system"`, `"calico-node-abc123"`
- **number**: `5`, `1024`, `3.14`
- **boolean**: `true`, `false`
- **array**: `["pod-1", "pod-2"]`
- **object**: `{"cpu": "1000m", "memory": "2Gi"}`

## Reference

- **Tools**: `list-sops-from-ops`, `list-sops-parameters-from-ops`, `execute-sops-from-ops`
- **JSON Format**: <https://www.json.org/>
- **Parameter Types**: string, number, boolean, array, object
- **Best Practice**: Always verify, document, and have rollback plan

## Important Notes

- ⚠️ **Production Safety**: Always verify before executing SOPS in production
- 🔐 **Access Control**: SOPS execution may require special permissions
- 📝 **Audit Trail**: All executions are logged for compliance
- 🔁 **Idempotency**: Most SOPS are designed to be safely re-executed
- 📋 **Documentation**: Keep reason and context for each execution
