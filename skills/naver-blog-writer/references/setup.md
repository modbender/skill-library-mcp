# Setup (ACP marketplace path)

## Recommended path (paid offering execute)

```bash
# local daemon
export X_LOCAL_TOKEN="<thin-runner-local-token>"
export LOCAL_DAEMON_PORT="19090"

# onboarding helper (optional but recommended)
export PROOF_TOKEN="<proof_token>"
export SETUP_ISSUE_URL="https://<control-plane>/v3/onboarding/setup-url/issue"
# OR pre-issued setup URL
export SETUP_URL="https://<control-plane>/v2/onboarding/setup-sessions/start?setup_token=..."

# ACP offering execute path (for purchase/billing flow)
export OPENCLAW_OFFERING_ID="naver-blog-writer"
export OPENCLAW_OFFERING_EXECUTE_URL="https://<acp-service>/execute"
export OPENCLAW_CORE_API_KEY="<optional-if-required>"
export OPENCLAW_CORE_API_KEY_HEADER="x-api-key"
```

## Internal fallback only (direct dispatch)

Use only for debugging/ops, not for normal paid commerce tracking.

```bash
export CONTROL_PLANE_URL="https://control-plane-production-662b.up.railway.app"
export ACP_ADMIN_API_KEY="<admin-key>"
```

## Basic runbook

```bash
# 1) preflight
scripts/preflight.sh

# 2) if RUNNER_NOT_READY, setup once
scripts/setup_runner.sh --proof-token "$PROOF_TOKEN" --setup-issue-url "$SETUP_ISSUE_URL"
npx @y80163442/naver-thin-runner login

# 3) publish
scripts/publish.sh --title "제목" --body "본문" --tags "tag1,tag2"
```
