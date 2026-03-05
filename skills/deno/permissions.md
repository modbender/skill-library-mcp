# Permission System Traps

## Overly Broad Permissions

- `--allow-all` — disables security model, only for trusted scripts
- `--allow-read` without path — reads entire filesystem
- `--allow-write` without path — writes anywhere
- `--allow-net` without hosts — connects to any server
- `--allow-run` without list — executes any binary
- `--allow-env` without list — accesses all environment variables

## Correct Permission Scoping

```bash
# BAD: Too broad
deno run --allow-all server.ts

# GOOD: Minimal permissions
deno run \
  --allow-net=0.0.0.0:8000,api.stripe.com \
  --allow-read=./public,./templates \
  --allow-env=STRIPE_KEY,DATABASE_URL \
  server.ts
```

## Permission Combinations

- `--allow-read=/etc/passwd` + `--allow-net` — can exfiltrate sensitive files
- `--allow-run=bash` — bash can do anything, same as allow-all
- `--allow-write=.` + `--allow-run` — can write malicious script and execute
- `--allow-ffi` — foreign function interface, can bypass all security

## Runtime Permission Requests

```typescript
// Request permission at runtime
const status = await Deno.permissions.request({ name: "read", path: "./data" });
if (status.state !== "granted") {
  console.error("Permission denied");
  Deno.exit(1);
}
```

- User must approve in terminal — CI/CD hangs without `--no-prompt`
- `query` before `request` — check without prompting
- Denied permission — can't be re-requested in same run

## CI/CD Traps

- Permission prompt hangs — always use `--no-prompt` in CI
- Missing permission = exit code 1 — check logs for "PermissionDenied"
- `Deno.permissions.query` — returns `{ state: "prompt" }` in CI without flags
- Test with production permissions — `deno test --allow-read=./testdata`

## Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `PermissionDenied` | Missing flag | Add specific permission |
| `NotCapable` | Running with `--deny-*` | Remove deny flag |
| Hangs forever | Waiting for prompt | Add permission or `--no-prompt` |

## Permission Discovery

```bash
# Run and see what fails
deno run --no-prompt script.ts 2>&1 | grep PermissionDenied

# Document in deno.json
{
  "tasks": {
    "start": "deno run --allow-net=:8000 --allow-read=./data server.ts"
  }
}
```

## Checklist

- [ ] No `--allow-all` in production
- [ ] All permissions scoped to specific paths/hosts/vars
- [ ] CI uses `--no-prompt`
- [ ] Permissions documented in deno.json tasks
- [ ] Tested with exact production permissions locally
