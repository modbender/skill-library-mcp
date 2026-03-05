# openclaw-ops-elvatis

Local ops plugin.

## Commands

### Operations & Monitoring (Phase 1)
- `/health` - Quick system health check (gateway, resources, plugins, errors)
- `/services` - Show all OpenClaw profiles and service status
- `/logs [service] [lines]` - View gateway or plugin logs (defaults: gateway, 50 lines)
- `/plugins` - Detailed plugin dashboard with versions and workspace info

### Configuration (Phase 2)
- `/config` - Show configuration overview (environment, main config, plugin configs, env vars)
- `/config <plugin>` - Show detailed config for a specific plugin (values, schema validation, defaults comparison)

### Legacy Commands
- `/cron` - list cron jobs + scripts + recent reports
- `/privacy-scan` - run the GitHub privacy scan and show latest report path
- `/limits` - show provider auth expiry + observed cooldown windows
- `/release` - show staging gateway + human GO checklist (QA gate)
- `/staging-smoke` - install all `openclaw-*` plugins into the staging profile, restart gateway, and verify status (writes report)
- `/handoff` - show latest openclaw-ops-elvatis handoff log tail

## Usage Examples

### Quick Health Check
```bash
openclaw health
```
Shows gateway status, system resources (CPU, memory, disk), plugin count, and recent errors.

### View Logs
```bash
# View last 50 lines of gateway logs (default)
openclaw logs

# View last 100 lines of specific plugin
openclaw logs openclaw-ops-elvatis 100

# View audit logs
openclaw logs audit 200
```

### Service Management
```bash
# Check all profiles
openclaw services

# View detailed plugin info
openclaw plugins
```

### Operations Dashboard
```bash
# Full operational overview
openclaw cron          # Scheduled tasks
openclaw limits        # Rate limits and auth expiry
openclaw health        # System health
openclaw services      # All services
```

## GitHub Actions

### openclaw-triage-labels

Automated issue labeling across all `elvatis/openclaw-*` repositories. Runs daily at 06:00 UTC and can be triggered manually via `workflow_dispatch`.

Applies labels based on keyword analysis:
- `security` - security-related issues (CVE, vulnerability, XSS, etc.)
- `bug` - bug reports (crash, error, regression, etc.)
- `needs-triage` - everything else that has not been triaged yet

#### Cross-repo PAT setup (required for multi-repo triage)

The default `GITHUB_TOKEN` is scoped to `openclaw-ops-elvatis` only. To label issues in sibling repos (`openclaw-memory-core`, `openclaw-gpu-bridge`, etc.), you must configure a fine-grained Personal Access Token:

1. Go to [GitHub token settings](https://github.com/settings/tokens?type=beta)
2. Create a fine-grained PAT with:
   - **Repository access**: All repositories (or select all `elvatis/openclaw-*` repos)
   - **Permissions**: Issues (Read and write), Metadata (Read)
3. Go to this repo's **Settings > Secrets and variables > Actions**
4. Add a repository secret named `TRIAGE_GH_TOKEN` with the PAT value

Without `TRIAGE_GH_TOKEN`, the workflow gracefully skips repos where it lacks permissions (no 403 errors - just a warning in the logs).

## Install

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-ops-elvatis
openclaw gateway restart
```
