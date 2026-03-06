# OpenClaw Deployment and Operations

Reference normalized against:
- `https://docs.openclaw.ai/install`
- `https://docs.openclaw.ai/install/docker`
- `https://docs.openclaw.ai/install/updating`
- `https://docs.openclaw.ai/install/uninstall`

Last verified: 2026-02-17.

## Local Install and Onboarding
- Install CLI via official install flow from docs.
- Run `openclaw onboard` to initialize and connect providers/channels.
- Validate with `openclaw doctor`.

## Docker Deployment
- Use the official Docker guide under `/install/docker`.
- Typical lifecycle:
  - `docker compose up -d`
  - `docker compose logs -f`
  - `docker compose down`
- Keep OpenClaw state mounted on persistent volume.

## Service Lifecycle
- `openclaw gateway install`: Install background service.
- `openclaw gateway restart`: Restart service.
- `openclaw gateway status`: Check runtime status.
- `openclaw gateway uninstall`: Remove service.

## Updating and Rollback
- Update CLI: `openclaw update`
- If rollback is needed, reinstall pinned version using the official package path described in docs.
- Re-run `openclaw doctor` after updates.

## Uninstall
- Use `openclaw uninstall` for full removal flow.
- Confirm whether state data should be preserved or removed.

## Production Safety Checklist
- Set strong `gateway.auth.token`.
- Avoid public bind unless required.
- Use VPN/Tailscale or private network for remote access.
- Monitor with `openclaw gateway health`.
