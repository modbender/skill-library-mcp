# Blueprint Workflow - render.yaml

Use this flow for multi-service or reproducible deployments.

## 1. Build a Complete render.yaml

Required baseline:

```yaml
services:
  - type: web
    name: app
    runtime: node
    plan: free
    buildCommand: npm ci
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: JWT_SECRET
        sync: false
```

Rules:
- Use `plan: free` unless user requests another plan.
- Declare all env vars explicitly.
- Mark user-supplied secrets with `sync: false`.
- Use `fromDatabase` references when provisioning managed datastores.

## 2. Validate Before Push

If CLI is available:

```bash
render whoami -o json
render blueprints validate
```

Do not continue when validation fails.

## 3. Commit and Push

```bash
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

Blueprint deeplinks only work when the file is already in the remote repository.

## 4. Generate Dashboard Deeplink

Convert remote to HTTPS if needed and use:

```text
https://dashboard.render.com/blueprint/new?repo=<REPOSITORY_URL>
```

## 5. Final Verification

After apply in dashboard:
- Confirm deploy status is live.
- Check health endpoint.
- Scan recent error logs.
