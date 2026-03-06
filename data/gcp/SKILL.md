---
name: Google Cloud
description: Deploy, monitor, and manage GCP services with battle-tested patterns.
metadata: {"clawdbot":{"emoji":"🌐","requires":{"anyBins":["gcloud"]},"os":["linux","darwin","win32"]}}
---

# Google Cloud Production Rules

## Cost Traps
- Stopped Compute Engine VMs still pay for persistent disks and static IPs — delete disks or use snapshots for long-term storage
- Cloud NAT charges per VM and per GB processed — use Private Google Access for GCP API traffic instead
- BigQuery on-demand pricing charges for bytes scanned, not rows returned — partition tables and use `LIMIT` in dev, but `LIMIT` doesn't reduce scan cost in prod
- Preemptible VMs save 80% but can be terminated anytime — only for fault-tolerant batch workloads
- Egress to internet costs, egress to same region is free — keep resources in same region, use Cloud CDN for global distribution

## Security Rules
- Service accounts are both identity and resource — one service account can impersonate another with `roles/iam.serviceAccountTokenCreator`
- IAM policy inheritance: Organization → Folder → Project → Resource — deny policies at org level override allows below
- VPC Service Controls protect against data exfiltration — but break Cloud Console access if not configured with access levels
- Default Compute Engine service account has Editor role — create dedicated service accounts with least privilege
- Workload Identity Federation eliminates service account keys — use for GitHub Actions, GitLab CI, external workloads

## Networking
- VPC is global, subnets are regional — unlike AWS, single VPC can span all regions
- Firewall rules are allow-only by default — implicit deny all ingress, allow all egress. Add explicit deny rules for egress control
- Private Google Access is per-subnet setting — enable on every subnet that needs to reach GCP APIs without public IP
- Cloud Load Balancer global vs regional — global for multi-region, but regional is simpler and cheaper for single region
- Shared VPC separates network admin from project admin — host project owns network, service projects consume it

## Performance
- Cloud Functions gen1 has 9-minute timeout — gen2 (Cloud Run based) allows 60 minutes
- Cloud SQL connection limits vary by instance size — use connection pooling or Cloud SQL Auth Proxy
- Firestore/Datastore hotspotting on sequential IDs — use UUIDs or reverse timestamps for document IDs
- GKE Autopilot simplifies but limits — no DaemonSets, no privileged containers, no host network
- Cloud Storage single object limit is 5TB — use compose for larger, parallel uploads for faster

## Monitoring
- Cloud Logging retention: 30 days default, \_Required bucket is 400 days — create custom bucket with longer retention for compliance
- Cloud Monitoring alert policies have 24-hour auto-close — incident disappears even if issue persists, configure notification channels for re-alert
- Error Reporting groups by stack trace — same error with different messages creates duplicates
- Cloud Trace sampling is automatic — may miss rare errors, increase sampling rate for debugging
- Audit logs: Admin Activity always on, Data Access off by default — enable Data Access logs for security compliance

## Infrastructure as Code
- Terraform google provider requires project ID everywhere — use `google_project` data source or variables, never hardcode
- `gcloud` commands are imperative — use Deployment Manager or Terraform for reproducible infra
- Cloud Build triggers on push but IAM permissions on first run confusing — grant Cloud Build service account necessary roles before first deploy
- Project deletion has 30-day recovery period — but project ID is globally unique forever, can't reuse
- Labels propagate to billing — use consistent labeling for cost allocation: `env`, `team`, `service`

## IAM Best Practices
- Primitive roles (Owner/Editor/Viewer) are too broad — use predefined roles, create custom for least privilege
- Service account keys are security liability — use Workload Identity, impersonation, or attached service accounts instead
- `roles/iam.serviceAccountUser` lets you run as that SA — equivalent to having its permissions, grant carefully
- Organization policies restrict what projects can do — `constraints/compute.vmExternalIpAccess` blocks public VMs org-wide
