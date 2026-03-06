# TrueNAS App Installation Guide

Install apps from the TrueNAS Apps catalog with proper dataset and ACL setup.

## Order of Operations

1. **Check app template** — evaluate config options before installing
2. **Create dataset(s)** — under the apps config pool
3. **Set ACL** — apps preset with correct ownership
4. **Install app** — with proper storage mapping and app-specific options

## Step 1: Check App Template

```bash
curl -sk "$TRUENAS_URL/api/v2.0/app/available?name=APP_NAME" \
  -H "Authorization: Bearer $TRUENAS_API_KEY" \
  | jq '.[0] | {name, train, version: .latest_version}'
```

**Look for:**
- Storage requirements (single folder vs multiple)
- Docker socket mount option
- Device passthrough needs (disks, GPUs)
- Privileged mode requirements
- Environment variables
- Network settings

**CRITICAL: Apps often have MULTIPLE storage mounts.**
Example: Scrutiny has `config` AND `influxdb`. Each storage key you don't explicitly
set to `host_path` defaults to `ixVolume` (auto-managed by TrueNAS).
Check existing installs or app schema to find ALL storage keys.

**Common app-specific options:**

| App | Key Options |
|-----|-------------|
| Uptime Kuma | `mount_docker_socket: true` for container monitoring |
| Scrutiny | Device passthrough for SMART disk access |
| Plex | GPU passthrough, transcode paths |
| *arr apps | Download client paths, media paths |

## Step 2: Create Dataset(s)

Create as child of the apps config pool (inherits NFSv4/passthrough).
Create one dataset per storage mount the app needs.

```bash
# Main app folder
curl -sk -X POST "$TRUENAS_URL/api/v2.0/pool/dataset" \
  -H "Authorization: Bearer $TRUENAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "apps/config/APP_NAME"}'

# Additional storage mounts as subdatasets
curl -sk -X POST "$TRUENAS_URL/api/v2.0/pool/dataset" \
  -H "Authorization: Bearer $TRUENAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "apps/config/APP_NAME/influxdb"}'
```

**Known multi-storage apps:**

| App | Storage Keys |
|-----|--------------|
| Scrutiny | `config`, `influxdb` |
| Plex | `config`, `transcode` |
| Jellyfin | `config`, `cache` |

## Step 3: Set ACL (Apps Preset)

**CRITICAL:** Use `user: "apps"` and `group: "apps"` as STRINGS, not numeric uid/gid.

```bash
curl -sk -X POST "$TRUENAS_URL/api/v2.0/filesystem/setacl" \
  -H "Authorization: Bearer $TRUENAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/mnt/apps/config/APP_NAME",
    "user": "apps",
    "group": "apps",
    "acltype": "NFS4",
    "dacl": [
      {"tag": "owner@", "type": "ALLOW", "perms": {"BASIC": "FULL_CONTROL"}, "flags": {"BASIC": "INHERIT"}},
      {"tag": "group@", "type": "ALLOW", "perms": {"BASIC": "FULL_CONTROL"}, "flags": {"BASIC": "INHERIT"}},
      {"tag": "everyone@", "type": "ALLOW", "perms": {"BASIC": "MODIFY"}, "flags": {"BASIC": "INHERIT"}},
      {"tag": "GROUP", "type": "ALLOW", "perms": {"BASIC": "MODIFY"}, "flags": {"BASIC": "INHERIT"}, "id": 545},
      {"tag": "GROUP", "type": "ALLOW", "perms": {"BASIC": "FULL_CONTROL"}, "flags": {"BASIC": "INHERIT"}, "id": 544}
    ],
    "options": {"recursive": true}
  }'
```

## Step 4: Install App

**Set ALL storage mounts to host_path — any you miss will default to ixVolume.**

```bash
curl -sk -X POST "$TRUENAS_URL/api/v2.0/app" \
  -H "Authorization: Bearer $TRUENAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_app": false,
    "catalog_app": "APP_NAME",
    "app_name": "APP_NAME",
    "train": "TRAIN",
    "version": "latest",
    "values": {
      "storage": {
        "config": {
          "type": "host_path",
          "host_path_config": {"path": "/mnt/apps/config/APP_NAME"}
        },
        "data": {
          "type": "host_path",
          "host_path_config": {"path": "/mnt/apps/config/APP_NAME/data"}
        }
      },
      "APP_SECTION": {
        "option": true
      }
    }
  }'
```

**Note:** Check `train` from Step 1 — many apps are in "community" not "stable".

## Verification

```bash
# Check app status
curl -sk "$TRUENAS_URL/api/v2.0/app?name=APP_NAME" \
  -H "Authorization: Bearer $TRUENAS_API_KEY" \
  | jq '.[0] | {name, state, portals, volumes: .active_workloads.volumes}'

# Verify ACL
curl -sk -X POST "$TRUENAS_URL/api/v2.0/filesystem/getacl" \
  -H "Authorization: Bearer $TRUENAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "/mnt/apps/config/APP_NAME"}' \
  | jq '{uid, gid, acl_count: (.acl | length)}'
```

## Update Existing App

```bash
curl -sk -X PUT "$TRUENAS_URL/api/v2.0/app/id/APP_NAME" \
  -H "Authorization: Bearer $TRUENAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"values": {"section": {"option": "value"}}}'
```

## Important Notes

- **TrueNAS is an appliance** — use API only, no SSH/custom scripts
- **API key auth** — use Bearer token with API key from TrueNAS UI
- **Check train** — apps may be in "stable", "community", or "enterprise"
- **ACL strings** — always use `user: "apps"` not `uid: 568`
- **Evaluate templates** — don't install with empty `values: {}`
- **ALL storage mounts** — each storage key you don't set to `host_path` defaults to `ixVolume`
