# Security Policy — kube-medic

## Design Principles

1. **Read-only by default.** All diagnostic subcommands (`sweep`, `pod`, `deploy`, `resources`, `events`) execute only read operations: `kubectl get`, `kubectl describe`, `kubectl logs`, `kubectl top`, `kubectl rollout status`, `kubectl rollout history`. No cluster state is modified.

2. **Write operations require explicit confirmation.** The `--confirm-write` flag is the only path to cluster modifications. It requires:
   - The user to see the exact command being proposed
   - Explicit user approval before execution
   - The command to match the allowlist (see below)

3. **Strict write allowlist.** Only these `kubectl` commands are permitted through `--confirm-write`:
   - `kubectl rollout undo ...` — rollback a deployment
   - `kubectl rollout restart ...` — restart pods in a deployment
   - `kubectl scale ...` — scale a deployment
   - `kubectl delete pod ...` — delete a specific pod (force restart)
   - `kubectl cordon ...` — mark a node as unschedulable
   - `kubectl uncordon ...` — mark a node as schedulable

   Any command not matching these patterns is **rejected**.

4. **No `kubectl exec`. Ever.** `kubectl exec` is not in the allowlist and cannot be executed through kube-medic. This prevents arbitrary command execution inside containers, which is the highest-risk kubectl operation.

5. **No credential leakage.** kube-medic never includes the following in its output:
   - Kubeconfig file paths or contents
   - Service account tokens
   - Secret values (kube-medic never reads Kubernetes Secrets)
   - Cloud provider credentials
   - Certificate data

6. **No shell injection surface.**
   - `set -euo pipefail` enforced globally
   - All JSON construction uses `jq --arg` / `jq --argjson` — no string interpolation
   - Shell variables are double-quoted throughout
   - The `--confirm-write` command is parsed into an argv array and validated against an allowlist before execution
   - No `eval`, no backticks, and no `bash -c` execution paths on user-controlled input

## RBAC Recommendations

kube-medic works best with a **read-only ClusterRole**. Here's a minimal RBAC policy:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kube-medic-readonly
rules:
  # sweep, pod, deploy
  - apiGroups: [""]
    resources: ["pods", "pods/log", "events", "nodes", "componentstatuses", "services"]
    verbs: ["get", "list"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list"]
  # resources (requires metrics-server)
  - apiGroups: ["metrics.k8s.io"]
    resources: ["nodes", "pods"]
    verbs: ["get", "list"]
```

For write operations (optional — only if you want rollback/scale capabilities):

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kube-medic-write
rules:
  # rollout undo / restart
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "patch", "update"]
  - apiGroups: ["apps"]
    resources: ["deployments/rollback"]
    verbs: ["create"]
  # scale
  - apiGroups: ["apps"]
    resources: ["deployments/scale"]
    verbs: ["get", "update", "patch"]
  # delete pod (force restart)
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["delete"]
  # cordon/uncordon
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "patch"]
```

**Recommendation:** Start with `kube-medic-readonly`. Only bind the write role if you want the agent to perform remediation actions.

## What This Skill Can Access

- Pod status, logs (current + previous), and events
- Node status, conditions, and resource metrics
- Deployment specs, rollout status, and revision history
- ReplicaSet details
- Cluster events (all types)
- Component statuses
- Resource usage via metrics-server (`kubectl top`)

## What This Skill Cannot Access

- Kubernetes Secrets (never reads them)
- ConfigMap contents (never reads them)
- Container filesystems (no `kubectl exec` or `kubectl cp`)
- Admission webhooks or API server configuration
- etcd directly
- Cloud provider APIs

## Threat Model

| Threat | Mitigation |
|--------|------------|
| Agent executes destructive commands without approval | Write allowlist + user confirmation gate |
| Arbitrary command execution via `kubectl exec` | `exec` is not in the allowlist; blocked unconditionally |
| Credential leakage in output | No secrets, tokens, or kubeconfig in JSON output |
| Shell injection via pod/deployment names | All values passed through `jq --arg`; shell variables quoted |
| Excessive permissions in cluster | Minimal RBAC ClusterRole documented; read-only by default |
| Sensitive data in pod logs | Logs are passed to the LLM for analysis — use RBAC to restrict `pods/log` access if logs contain PII |

## Important Note on Log Data

Pod logs may contain sensitive information (PII, tokens, internal URLs). When kube-medic retrieves logs via `kubectl logs`, this data is passed to the LLM for analysis. If your logs contain regulated data:

- Restrict `pods/log` access in RBAC to specific namespaces
- Use the `--namespace` flag to limit scope
- Consider log redaction at the application level

## Reporting Vulnerabilities

If you discover a security issue, please email security@cacheforge.dev with details. We will respond within 48 hours.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ |

*Powered by Anvil AI 🏥*
