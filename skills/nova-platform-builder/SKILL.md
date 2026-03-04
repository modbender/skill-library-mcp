---
name: nova-app-builder
description: "Build and deploy Nova Platform apps (TEE apps on Sparsity Nova / sparsity.cloud). Use when a user wants to create a Nova app, write enclave application code, build it into a Docker image, and deploy it to the Nova Platform to get a live running URL. Handles the full lifecycle: scaffold, code, build, push, deploy, verify running. Triggers on requests like 'build me a Nova app', 'deploy to Nova Platform', 'create a TEE app on sparsity.cloud', 'I want to run an enclave app on Nova'."
---

# Nova App Builder

End-to-end workflow: scaffold → code → push to Git → create app → build → deploy → (on-chain: create app on-chain → enroll version → generate ZK proof → register instance).

## Architecture Overview

Nova apps run inside AWS Nitro Enclaves, managed by **Enclaver** (Sparsity edition) and supervised by **Odyn** (PID 1 inside the enclave). Key concepts:

- **Enclaver**: packages your Docker image into an EIF (Enclave Image File) and manages the enclave lifecycle.
- **Odyn**: supervisor inside the enclave; provides Internal API for signing, attestation, encryption, KMS, S3, and manages networking.
- **Nova Platform**: cloud platform at [sparsity.cloud](https://sparsity.cloud) — builds EIFs from Git, runs enclaves, exposes app URLs.
- **Nova KMS**: distributed key management; enclave apps derive keys via `/v1/kms/derive`.

## Prerequisites (collect from user before starting)

- **App idea**: What does the app do?
- **Nova account + API key**: Sign up at [sparsity.cloud](https://sparsity.cloud) → Account → API Keys.
- **GitHub repo + GitHub API key (PAT)**: Used only to push your app code to GitHub. Nova Platform then builds from the repo URL via GitHub Actions. The PAT is not passed to Nova Platform.

> ⚠️ **Do NOT ask for Docker registry credentials or AWS S3 credentials.**
> Nova Platform handles the Docker build and image registry internally (Git-based build pipeline).
> S3 storage credentials are managed by the Enclaver/Odyn layer — the app only calls Internal API endpoints (`/v1/s3/*`). Users never touch AWS credentials.

## Full Workflow

### Step 1 — Scaffold the project

```bash
python3 scripts/scaffold.py \
  --name <app-name> \
  --desc "<one-line description>" \
  --port <port> \
  --out <output-dir>
```

> **Port choice**: Any port works. Set it via `advanced.app_listening_port` when creating the app. Must also match `EXPOSE` in your Dockerfile. No requirement to use 8080.

This copies the asset template into `<output-dir>/<app-name>/` and prints the file list.

Alternatively, fork [nova-app-template](https://github.com/sparsity-xyz/nova-app-template) — a production-ready starter with KMS, S3, App Wallet, E2E encryption, and a built-in React frontend.

### Step 2 — Write the app logic

Edit `enclave/main.py`. Key patterns:

**Minimal FastAPI app:**
```python
import os, httpx
from fastapi import FastAPI

app = FastAPI()
IN_ENCLAVE = os.getenv("IN_ENCLAVE", "false").lower() == "true"
ODYN_BASE = "http://127.0.0.1:18000" if IN_ENCLAVE else "http://odyn.sparsity.cloud:18000"

@app.get("/api/hello")
def hello():
    r = httpx.get(f"{ODYN_BASE}/v1/eth/address", timeout=10)
    return {"message": "Hello from TEE!", "enclave": r.json()["address"]}
```

**With App Wallet + KMS (from nova-app-template):**
```python
from kms_client import NovaKmsClient

kms = NovaKmsClient(endpoint=ODYN_BASE)

@app.get("/api/wallet")
def wallet():
    return kms.app_wallet_address()     # {"address": "0x...", "app_id": 0}

@app.post("/api/sign")
def sign(body: dict):
    return kms.app_wallet_sign(body["message"])   # {"signature": "0x..."}
```

**Dual-chain topology** (as in the template):
- **Auth/Registry chain**: Base Sepolia (84532) — KMS authorization & app registry
- **Business chain**: Ethereum Mainnet (1) — your business logic

Helios light-client RPC runs locally at `http://127.0.0.1:18545` (Base Sepolia) and `http://127.0.0.1:18546` (Mainnet).

> ⚠️ **Helios RPC ports must be decided before creating the app** — they are set in `advanced.helios_chains[].local_rpc_port` and locked at creation time. Choose values carefully up front.

Rules for enclave code:
- All outbound HTTP must use `httpx` (proxy-aware). Never use `requests` or `urllib` — they may bypass the egress proxy.
- Persistent state → use `/v1/s3/*` endpoints; the enclave filesystem is ephemeral.
- Secrets → derive via KMS (`/v1/kms/derive`); never from env vars or hardcoded.
- Test locally: `IN_ENCLAVE=false uvicorn main:app --port <port>` (Odyn calls hit the public mock).

### Step 3 — Commit & push to Git

Your repo only needs `Dockerfile` + app code. No local Docker build needed — Nova Platform builds from your Git repo directly.

KMS integration is fully handled by the platform — just set `enable_decentralized_kms: true` (and optionally `enable_app_wallet: true`) in `advanced` when creating the app. No contract addresses, app IDs, or manual KMS config needed in your code.

```bash
git add .
git commit -m "Initial Nova app"
git push origin main
```

### Step 4 — Deploy to Nova Platform

The deployment is a **3-step** process: **Create App → Trigger Build → Create Deployment**.

#### Via Portal (recommended for first-time)

1. Go to [sparsity.cloud](https://sparsity.cloud) → **Apps** → **Create App**
2. Fill in **Name**, **Description**, **Git Repo URL**, configure Advanced settings → Submit → copy the **App sqid**
3. In the App page → **Builds** → **Trigger Build**:
   - Git Ref: `main` (or tag / commit SHA)
   - Version: e.g. `v1.0.0`
5. Wait for build status → `success` (Nova builds Docker image → EIF → generates PCRs)
6. **Deployments** → **Create Deployment** → select the successful build → **Deploy**
7. Poll until state → `running` → copy the **App URL** (hostname from app detail)

#### Via API (scripted)

```bash
BASE="https://sparsity.cloud/api"
TOKEN="<your-api-key>"
REPO="https://github.com/you/my-app"

# 1. Create app — 'advanced' is the only config field needed
SQID=$(curl -sX POST "$BASE/apps" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"my-app",
    "repo_url":"'"$REPO"'",
    "advanced":{
      "directory":"/",
      "app_listening_port":8080,
      "egress_allow":["**"],
      "enable_decentralized_kms":false,
      "enable_persistent_storage":false,
      "enable_s3_storage":false,
      "enable_s3_kms_encryption":false,
      "enable_ipfs_storage":false,
      "enable_walrus_storage":false,
      "enable_app_wallet":false,
      "enable_helios_rpc":false,
      "helios_chains":[
        {"chain_id":"1","kind":"ethereum","network":"mainnet","execution_rpc":"","local_rpc_port":18545}
      ]
    }
  }' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['sqid'])")
echo "App sqid: $SQID"

# 2. Trigger build
BUILD_ID=$(curl -sX POST "$BASE/apps/$SQID/builds" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"git_ref":"main","version":"1.0.0"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Build ID: $BUILD_ID"

# 3. Poll build
while true; do
  STATUS=$(curl -s "$BASE/builds/$BUILD_ID/status" \
    -H "Authorization: Bearer $TOKEN" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))")
  echo "Build: $STATUS"
  [ "$STATUS" = "success" ] && break
  [ "$STATUS" = "failed" ] && echo "Build failed!" && exit 1
  sleep 15
done

# 4. Create deployment
DEPLOY_ID=$(curl -sX POST "$BASE/apps/$SQID/deployments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"build_id\":$BUILD_ID}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Deployment ID: $DEPLOY_ID"

# 5. Poll deployment
while true; do
  RESP=$(curl -s "$BASE/deployments/$DEPLOY_ID/status" -H "Authorization: Bearer $TOKEN")
  STATE=$(echo $RESP | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('deployment_state',''))")
  echo "Deployment state: $STATE"
  [ "$STATE" = "running" ] && break
  [ "$STATE" = "failed" ] && echo "Deploy failed!" && exit 1
  sleep 15
done

# 6. Get app URL (hostname from detail, or use unified status)
curl -s "$BASE/apps/$SQID/detail" -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['app'].get('hostname',''))"

# Tip: GET /api/apps/{sqid}/status gives the full lifecycle in one call:
# build_status, deployment_state, proof_status, onchain_instance_id, etc.
```

### Step 5 — Verify the live app

```bash
# Health check
curl https://<hostname>/

# Attestation (proves it's a real Nitro Enclave) — POST, returns binary CBOR
curl -sX POST https://<hostname>/.well-known/attestation --output attestation.bin

# App Wallet address
curl https://<hostname>/api/app-wallet
```

### Step 6 — On-Chain Registration (optional but important for trust)

After the app is running, register it on-chain to establish verifiable trust. This is a 4-step sequence:

```bash
# 7a. Create app on-chain
curl -sX POST "$BASE/apps/$SQID/create-onchain" \
  -H "Authorization: Bearer $TOKEN"
# Poll: GET /api/apps/{sqid}/status → onchain_app_id is set when done

# 7b. Enroll build version on-chain (PCR measurements → trusted code fingerprint)
curl -sX POST "$BASE/apps/$SQID/builds/$BUILD_ID/enroll" \
  -H "Authorization: Bearer $TOKEN"

# Poll enrollment via build status endpoint
while true; do
  ENROLLED=$(curl -s "$BASE/builds/$BUILD_ID/status" \
    -H "Authorization: Bearer $TOKEN" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('is_enrolled',''))")
  echo "Enrolled: $ENROLLED"
  [ "$ENROLLED" = "True" ] && break
  sleep 10
done

# 7c. Generate ZK proof
curl -sX POST "$BASE/zkproof/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"deployment_id\": $DEPLOY_ID}"

# Poll proof via deployment status endpoint (or /zkproof/status/{deployment_id})
while true; do
  PROOF=$(curl -s "$BASE/deployments/$DEPLOY_ID/status" \
    -H "Authorization: Bearer $TOKEN" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('proof_status',''))")
  echo "Proof status: $PROOF"
  [ "$PROOF" = "proved" ] && break
  [ "$PROOF" = "failed" ] && echo "Proof failed!" && exit 1
  sleep 30
done

# 7d. Register instance on-chain
curl -sX POST "$BASE/zkproof/onchain/register" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"deployment_id\": $DEPLOY_ID}"

# Poll: GET /api/deployments/{id}/status → onchain_instance_id is set when done
# Or use unified: GET /api/apps/{sqid}/status → latest_onchain_instance_id
```

**What each step does:**
- **Create app on-chain**: Registers your app in the Nova App Registry contract (Base Sepolia)
- **Enroll version**: Records the EIF's PCR measurements on-chain — the trusted code fingerprint
- **Generate ZK proof**: Platform generates a zero-knowledge proof from the enclave's attestation
- **Register instance**: Verifies the ZK proof on-chain and links the live instance to its enrolled version

After registration, anyone can verify on-chain that this running instance matches the audited build.

## Key Notes

1. **`advanced` is REQUIRED at app creation.** Omitting it will cause the build to fail. Only `advanced` exists — the old `enclaver` field has been removed from the API.
2. **Your repo only needs `Dockerfile` + app code.** The platform handles everything else at build time.
3. **App ID format**: `sqid` (string like `abc123`) — use in all URL paths, not the integer `id`.
4. **Port**: Set via `advanced.app_listening_port`. Must also match `EXPOSE` in Dockerfile.
5. **Helios RPC**: Use the canonical port mapping in `references/nova-api.md` — ports are fixed and locked at app creation.
6. **KMS dependency chain**: `enable_app_wallet` or `enable_s3_kms_encryption` implies KMS → implies Helios (with base-sepolia chain) → implies `kms_app_id` + `nova_app_registry`.
7. **KMS is handled by Enclaver** — no contract addresses or config.py changes needed in your app code.
8. **No Docker push**: Platform builds from Git.
9. **On-chain steps** (create-onchain → enroll → ZK proof → register) are required for public verifiability, but optional for a functional running app.

## Common Issues

| Symptom | Fix |
|---|---|
| Build stuck in `pending` | Check GitHub Actions in nova build repo; may be queued |
| Build `failed` | Check `error_message` in build response; usually Dockerfile issue |
| Deploy API returns 401 | Regenerate API key at sparsity.cloud |
| App stuck in `provisioning` >10 min | Check app logs via `GET /api/apps/{sqid}/detail` |
| `httpx` request fails inside enclave | Add domain to `advanced.egress_allow`. Note: `"**"` matches domains only — add `"0.0.0.0/0"` for direct IP connections |
| Direct IP connection blocked | `"**"` does NOT cover IPs. Add `"0.0.0.0/0"` (IPv4) and/or `"::/0"` (IPv6) to `egress_allow` |
| S3 fails | Ensure `169.254.169.254` and S3 endpoint are in egress allow list |
| `/v1/kms/*` returns 400 | Check `kms_integration` config; requires `helios_rpc.enabled=true` for registry mode |
| App Wallet unavailable | Nova KMS unreachable or `use_app_wallet: true` missing in `kms_integration` |
| Proxy not respected | Switch from `requests`/`urllib` to `httpx` |
| Health check returns 502 | App is starting; wait for enclave to fully boot |
| ZK proof stuck | Check `GET /api/zkproof/status/{deployment_id}` for details |

## Reference Files

- **`references/odyn-api.md`** — Full Odyn Internal API (signing, encryption, S3, KMS, App Wallet, attestation)
- **`references/nova-api.md`** — Nova Platform REST API (full endpoint reference)

## Key URLs

- Nova Platform: https://sparsity.cloud
- **Nova Platform API docs**: https://sparsity.cloud/api/docs
- **Create-App Full Parameter Guide**: https://sparsity.cloud/resources/nova-api/create-app-guide
- Nova Examples: https://github.com/sparsity-xyz/sparsity-nova-examples/
- Enclaver (Sparsity): https://github.com/sparsity-xyz/enclaver
- Nova App Template: https://github.com/sparsity-xyz/nova-app-template
- Enclaver Docs: [odyn.md](https://github.com/sparsity-xyz/enclaver/blob/sparsity/docs/odyn.md), [internal_api.md](https://github.com/sparsity-xyz/enclaver/blob/sparsity/docs/internal_api.md)
