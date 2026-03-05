# Testing — kube-medic

## Quick Validation

### Syntax Check

```bash
bash -n scripts/kube-medic.sh && echo "✅ Syntax OK"
```

### Help & Version

```bash
bash scripts/kube-medic.sh --help
bash scripts/kube-medic.sh --version
# Expected: kube-medic 1.0.1
```

## Testing with kind (Local Cluster)

[kind](https://kind.sigs.k8s.io/) is the fastest way to get a throwaway Kubernetes cluster for testing.

### Setup

```bash
# Install kind (if needed)
go install sigs.k8s.io/kind@latest
# or: brew install kind

# Create a test cluster
kind create cluster --name kube-medic-test

# Verify
kubectl cluster-info --context kind-kube-medic-test
```

### Deploy Test Workloads

Create some pods in known states for testing:

```bash
# Healthy deployment
kubectl create deployment nginx-healthy --image=nginx:latest --replicas=2

# CrashLoopBackOff pod (bad command)
kubectl run crasher --image=busybox --restart=Always -- /bin/sh -c "exit 1"

# ImagePullBackOff pod (nonexistent image)
kubectl run bad-image --image=this-image-does-not-exist:v999

# OOMKilled pod (tiny memory limit)
kubectl run oom-test --image=nginx --restart=Always \
  --overrides='{"spec":{"containers":[{"name":"oom-test","image":"nginx","resources":{"limits":{"memory":"4Mi"}}}]}}'

# Pending pod (excessive resource request)
kubectl run pending-test --image=nginx \
  --overrides='{"spec":{"containers":[{"name":"pending-test","image":"nginx","resources":{"requests":{"cpu":"100","memory":"1Ti"}}}]}}'
```

Wait ~30 seconds for pods to reach their expected states.

### Test Each Subcommand

```bash
# 1. Sweep — should detect crasher, bad-image, oom-test, pending-test
bash scripts/kube-medic.sh sweep --context kind-kube-medic-test
# Expected: JSON with problem_pods listing the failing pods

# 2. Pod autopsy — investigate the crashing pod
bash scripts/kube-medic.sh pod crasher --context kind-kube-medic-test
# Expected: JSON with container state=waiting/CrashLoopBackOff, logs, events

# 3. Deploy — check the healthy deployment
bash scripts/kube-medic.sh deploy nginx-healthy --context kind-kube-medic-test
# Expected: JSON with replicas ready=2, rollout status = successfully rolled out

# 4. Events — should show BackOff, Failed, FailedScheduling events
bash scripts/kube-medic.sh events --context kind-kube-medic-test
# Expected: JSON with warning events for the broken pods

# 5. Resources — requires metrics-server (see below)
bash scripts/kube-medic.sh resources --context kind-kube-medic-test
# Expected: node info + pods missing limits
```

### Install metrics-server for `resources` Subcommand

kind doesn't ship with metrics-server. To test the `resources` subcommand:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch for kind (insecure TLS — test only)
kubectl patch deployment metrics-server -n kube-system --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# Wait for metrics to be available (~60 seconds)
kubectl top nodes
```

### Cleanup

```bash
kind delete cluster --name kube-medic-test
```

## Testing with minikube

```bash
# Create cluster
minikube start --profile kube-medic-test

# Enable metrics
minikube addons enable metrics-server --profile kube-medic-test

# Deploy test workloads (same as kind section above)
# Run tests (same as kind section, use --context minikube or kube-medic-test)

# Cleanup
minikube delete --profile kube-medic-test
```

## Testing with a Real Cluster

If you're testing against a real cluster, **use a safe namespace**:

```bash
# Create an isolated test namespace
kubectl create namespace kube-medic-test

# Deploy test workloads into it
kubectl -n kube-medic-test create deployment nginx-healthy --image=nginx --replicas=2
kubectl -n kube-medic-test run crasher --image=busybox --restart=Always -- /bin/sh -c "exit 1"

# Scope all tests to the safe namespace
bash scripts/kube-medic.sh sweep --namespace kube-medic-test
bash scripts/kube-medic.sh pod crasher --namespace kube-medic-test
bash scripts/kube-medic.sh events --namespace kube-medic-test

# Cleanup
kubectl delete namespace kube-medic-test
```

**⚠️ Never run unscoped `sweep` against a production cluster** during testing — it scans all namespaces and may generate noise in audit logs.

## Expected Results

| Subcommand | Test Scenario | Expected Output |
|------------|---------------|-----------------|
| `sweep` | Cluster with broken pods | `problem_pods` array lists crasher, bad-image, oom-test, pending-test |
| `sweep` | Healthy cluster | `problem_pods` is empty, all nodes Ready |
| `pod crasher` | CrashLoopBackOff pod | Container state `waiting`, reason `CrashLoopBackOff`, restart count > 0 |
| `pod bad-image` | ImagePullBackOff pod | Container state `waiting`, reason `ImagePullBackOff` or `ErrImagePull` |
| `deploy nginx-healthy` | Healthy deployment | `ready` = `desired`, rollout status = "successfully rolled out" |
| `resources` | With metrics-server | `node_usage` array with CPU/memory percentages |
| `resources` | Without metrics-server | `node_usage` empty, node conditions still reported |
| `events` | After deploying broken pods | Warning events for BackOff, Failed, FailedScheduling |

## Error Handling Tests

```bash
# Missing kubectl
PATH="" bash scripts/kube-medic.sh sweep 2>&1 | grep -q "kubectl not found" && echo "✅ Missing kubectl handled"

# Missing jq
# (harder to test without actually removing jq — check the preflight code path)

# No subcommand → shows help
bash scripts/kube-medic.sh 2>&1 | grep -q "Subcommands" && echo "✅ No-args shows help"

# Unknown subcommand
bash scripts/kube-medic.sh foobar 2>&1 | grep -q "Unknown subcommand" && echo "✅ Unknown subcommand handled"

# Pod not found
bash scripts/kube-medic.sh pod nonexistent-pod-name --namespace default 2>&1 | grep -qi "not found\|error" && echo "✅ Missing pod handled"

# Missing pod argument
bash scripts/kube-medic.sh pod 2>&1 | grep -q "Usage" && echo "✅ Missing pod arg handled"

# Missing deploy argument
bash scripts/kube-medic.sh deploy 2>&1 | grep -q "Usage" && echo "✅ Missing deploy arg handled"
```

## Write Operation Tests

**⚠️ Only test writes in disposable clusters (kind/minikube).**

```bash
# Deploy something to roll back
kubectl create deployment rollback-test --image=nginx:1.24
kubectl set image deployment/rollback-test nginx=nginx:1.25
sleep 5

# Test allowlisted write — rollback
bash scripts/kube-medic.sh --confirm-write "kubectl rollout undo deployment/rollback-test"
# Expected: JSON with command_executed + output

# Test blocked write — kubectl exec (must be rejected)
bash scripts/kube-medic.sh --confirm-write "kubectl exec -it nginx-healthy -- /bin/bash" 2>&1 | grep -q "not in allowlist" && echo "✅ kubectl exec blocked"

# Test blocked write — kubectl delete deployment (must be rejected)
bash scripts/kube-medic.sh --confirm-write "kubectl delete deployment nginx-healthy" 2>&1 | grep -q "not in allowlist" && echo "✅ delete deployment blocked"
```

## Full Test Suite Script

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT="scripts/kube-medic.sh"
PASS=0
FAIL=0

check() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "✅ ${name}"; ((PASS++))
  else
    echo "❌ ${name}"; ((FAIL++))
  fi
}

# Offline tests (no cluster needed)
check "bash -n syntax" bash -n "$SCRIPT"
check "help output" bash "$SCRIPT" --help
check "version output" bash "$SCRIPT" --version

# Live tests (requires kubectl + cluster)
if kubectl cluster-info &>/dev/null; then
  check "sweep" bash "$SCRIPT" sweep
  check "events" bash "$SCRIPT" events
  check "resources" bash "$SCRIPT" resources

  # Deploy a test pod for pod/deploy tests
  kubectl create deployment kube-medic-test --image=nginx --replicas=1 2>/dev/null || true
  sleep 5
  POD=$(kubectl get pods -l app=kube-medic-test -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
  if [[ -n "$POD" ]]; then
    check "pod autopsy" bash "$SCRIPT" pod "$POD"
  fi
  check "deploy status" bash "$SCRIPT" deploy kube-medic-test
  kubectl delete deployment kube-medic-test 2>/dev/null || true
else
  echo "⚠️  No cluster connection — skipping live tests"
fi

echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
```

*Powered by Anvil AI 🏥*
