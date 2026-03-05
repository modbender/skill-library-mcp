# Troubleshooting

## Common Build Failures

| Problem | Cause | Fix |
|---------|-------|-----|
| `j2: command not found` | Python 3.12+ removed `imp` | `pip3 install jinjanator` |
| Build dies silently | OOM killer | Set `SONIC_BUILD_MEMORY`, reduce JOBS |
| Trixie phase missing | Stale artifacts in `target/` | `rm -rf target/*` and rebuild |
| `sg docker` nesting fails | Docker group session lost in subshell | Keep `sg docker` as outermost wrapper |
| `make: Nothing to be done` | Stale target files exist | Clean `target/` completely |
| DCO check fails on PR | Missing `Signed-off-by` | `git commit --amend --signoff` + force-push |
| Submodule checkout fails | HTTPS HTTP 500 | Use SSH remotes |
| Container exits immediately | `nohup bash -c 'sg docker -c "..."'` nesting | Use `sg docker -c 'nohup make ...'` (sg outermost) |

## Diagnosing OOM

Check kernel logs after a silent build death:

```bash
dmesg | grep -i "oom\|killed" | tail -20
```

Look for `CONSTRAINT_MEMCG` (container OOM, expected with `SONIC_BUILD_MEMORY`) vs system-wide OOM (dangerous).

## Diagnosing Stale Artifacts

If make skips phases or produces incomplete images:

```bash
ls -la target/*.bin target/*.gz target/*.squashfs 2>/dev/null
```

If any exist from a prior build, `rm -rf target/*` and reconfigure.

## Build Monitoring

```bash
# Live resource usage
watch -n5 'uptime && free -h && docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"'

# Check build container is running
docker ps | grep sonic

# Per-package logs (when main log is sparse)
ls target/debs/bookworm/*.log
```

## Docker Image Cleanup

Build images accumulate (~14GB each):

```bash
docker system df
docker image prune -a --filter "until=72h"
docker images | grep sonic-slave | awk '{print $3}' | xargs docker rmi
```
