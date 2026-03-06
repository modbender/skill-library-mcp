# Platform playbook: AWS EC2 (or similar cloud VM)

## Threat assumptions

- Public cloud instances are frequently scanned.
- Misconfigured security groups and public IPs are common.
- A compromise may expose cloud credentials and any attached data volumes.

## Preferred deployment pattern (strongly recommended)

- Place the instance in a **private subnet** with **no public IPv4**.
- Access it via:
  - AWS Systems Manager Session Manager (preferred), or
  - a bastion host + SSH, or
  - VPN/Tailscale.
- Keep the OpenClaw Gateway bound to **loopback** on the instance.
- If remote access is needed, use a secure tunnel or Tailscale Serve; do **not** open 18789 to the world.

## Audit checks (AWS)

1. **Security group inbound rules**
   - Ensure **no inbound** to `18789/tcp` from `0.0.0.0/0` or wide CIDRs.
   - If you need admin access, restrict SSH tightly (or use SSM and disable SSH).
2. **Public IP / exposure**
   - If the instance has a public IP, treat it as higher risk and re-check inbound/outbound rules.
3. **Instance metadata**
   - Prefer IMDSv2 and consider SSRF risks (especially if the agent can fetch URLs or run arbitrary HTTP clients).
4. **IAM role**
   - Least privilege only; avoid broad permissions.
5. **Storage**
   - Encrypt EBS volumes.
6. **Logging**
   - Centralise logs (CloudWatch) if appropriate; set retention.

## OpenClaw-specific cloud guidance

- Do not reverse-proxy the Control UI to the public internet.
- Disable Bonjour discovery (no benefit in most cloud setups).
- Keep DM pairing on; never run shared inbox + broad tools.
- If running in Docker on EC2, also apply the Docker playbook (`platform-docker.md`).

## Verification

- From an external network, confirm port 18789 is not reachable.
- Rerun `openclaw security audit --deep` and confirm no Critical issues.
