# Hostinger VPS Notes

## Creating a VPS

1. Log in to Hostinger hPanel
2. Go to **VPS** section
3. Click **Create New VPS**
4. Choose plan (KVM 2+ recommended for GUI)
5. Select **Ubuntu 22.04** or **Ubuntu 24.04**
6. Choose datacenter (closest to users)
7. Set root password
8. Complete purchase

## Accessing VPS Info

In hPanel:
- **VPS** → Select your server
- **Overview** shows:
  - IP Address
  - Hostname
  - Resource usage
- **SSH Access** shows connection details

## SSH Access

```bash
ssh root@YOUR_VPS_IP
```

First time: Accept fingerprint, enter root password.

## Recommended Plans

| Plan | RAM | CPU | Use Case |
|------|-----|-----|----------|
| KVM 1 | 1 GB | 1 | Headless only |
| KVM 2 | 2 GB | 2 | GUI (light use) |
| KVM 4 | 4 GB | 2 | GUI (recommended) |
| KVM 8 | 8 GB | 4 | Multiple agents |

## Firewall (hPanel)

Hostinger has a built-in firewall in hPanel:
1. Go to **VPS** → **Firewall**
2. Ensure these ports are allowed:
   - 22 (SSH)
   - 3389 (RDP)
   - 18789 (Koda)

Or use the default "Allow All" if managing via UFW on server.

## Snapshots

Before major changes:
1. **VPS** → **Snapshots**
2. Click **Create Snapshot**

Allows rollback if something breaks.

## Reinstalling OS

To start fresh:
1. **VPS** → **Operating System**
2. Select Ubuntu 22.04/24.04
3. Click **Reinstall**
4. ⚠️ This erases everything!
