# Troubleshooting

## Updating the VS Image

**Symptom**: After `add-topo`, DUT still runs old image despite downloading a new one.
**Cause**: The playbook copies from the **source image** at `<sonic_vm_storage>/images/sonic-vs.img`, NOT from `<root_path>/sonic-vs.img` (download landing zone). If you only replaced the download copy, the playbook still uses the old source.

**Image path chain:**
1. Download landing zone: `~/veos-vm/sonic-vs.img`
2. Source image (what add-topo copies FROM): `~/sonic-vm/images/sonic-vs.img` ← **MUST update this**
3. DUT disk (what VM boots): `~/sonic-vm/disks/sonic_<dut>.img` (playbook copies here if missing)

**Correct procedure:**
```bash
# 1. Copy new image to the SOURCE location
cp ~/veos-vm/sonic-vs.img ~/sonic-vm/images/sonic-vs.img

# 2. Set skip_vsonic_image_downloading: true in group_vars/vm_host/vsonic.yml

# 3. Update sonic_login in group_vars/all/creds.yml to match the image
#    CI image → "admin", local build → your username

# 4. remove-topo (deletes DUT disk) → add-topo (re-copies from source)
./testbed-cli.sh -t vtestbed.yaml -m veos_vtb remove-topo <testbed> password.txt
./testbed-cli.sh -t vtestbed.yaml -m veos_vtb add-topo <testbed> password.txt

# 5. VERIFY the image after deploy
ssh <user>@<DUT_IP> "cat /etc/sonic/sonic_version.yml"
```

**Common mistakes:**
- Copying to `disks/` only — `remove-topo` deletes it, `add-topo` re-copies from `images/`
- Forgetting to update `sonic_login` when switching between CI and local images
- Not setting `skip_vsonic_image_downloading: true` — playbook may overwrite your image

## Kickstart Fails Silently

**Symptom**: `add-topo` reports "Start sonic vm weren't succesfull"; DUT has no management IP; SSH shows "No route to host".
**Cause**: `sonic_login` in `creds.yml` doesn't match the image's default user. Kickstart can't log in via serial console to configure management IP.
**Fix**: Update `sonic_login` to match the image (see [credentials.md](credentials.md)), then redo remove-topo + add-topo.

## Non-admin User Build

**Symptom**: SSH as `admin` to DUT fails; `sonic_kickstart.py` fails.
**Cause**: sonic-vs built by non-`admin` user has that username instead of `admin`.
**Fix**: See [credentials.md](credentials.md) — create `admin` user on DUT and set `sonic_login` in creds.yml.

## Docker Registry :443 Hang

**Symptom**: `add-topo` hangs during PTF container pull, no error output.
**Cause**: `docker_registry_host: sonicdev-microsoft.azurecr.io:443` in `vars/docker_registry.yml`.
**Fix**: Remove `:443`. Pre-pull the PTF image: `docker pull sonicdev-microsoft.azurecr.io/docker-ptf:latest`

## max_fp_num Too Low

**Symptom**: Only first few data port interfaces work; BGP neighbors on higher-indexed ports stay down.
**Cause**: Default `max_fp_num: 4` limits veth pair creation.
**Fix**: Set `max_fp_num: 127` in `group_vars/vm_host/main.yml`.

## Converger KeyError on add-topo

**Symptom**: `testbed-cli.sh add-topo` fails with `KeyError: 'ARISTA02T1'` (or similar).
**Cause**: Stale `vars/topo_<TOPO>.yml.bak` from a previous converged run.
**Fix**: `rm -f vars/topo_*.yml.bak` before running `add-topo`.

## Config Files Revert

**Symptom**: Settings you changed are back to defaults after a testbed operation.
**Cause**: Some ansible tasks or git operations overwrite tracked config files.
**Fix**: Run your fix-configs.sh script before EVERY `testbed-cli.sh` command.

## Docker Permission Denied on DUT

**Symptom**: `deploy-mg` fails at "docker status" with "permission denied".
**Cause**: `admin` user on DUT isn't in docker group, or group hasn't taken effect.
**Fix**: `sudo chmod 666 /var/run/docker.sock` on DUT (quickest), or `sudo usermod -aG docker admin` + re-login.

## BGP Sessions Active (Not Established) with Converged Peers

**Symptom**: Only ARISTA01T1 (or first peer per role) Established; others show Active.
**Cause**: Normal with converged peers — only the prime device per role gets physical port-channels. VRF peers without wired interfaces show Active on the DUT side.
**Impact**: Expected behavior. ExaBGP sessions in PTF handle route injection for all peers.

## Dual-Host Conflict

**Symptom**: `add-topo` fails with "Please use -l server_X" or runs on wrong host.
**Cause**: Both `STR-ACS-SERV-01` (in `veos`) and `STR-ACS-VSERV-01` (in `veos_vtb`) define the same server.
**Fix**: Comment out `STR-ACS-SERV-01` in the `veos` inventory file.

## Ansible Connects as Wrong User

**Symptom**: SSH debug shows wrong user despite `ansible_user` setting.
**Cause**: Stale SSH control socket (ControlPersist) caching old connection.
**Fix**: `rm -f ~/.ansible/cp/*`

## Management Bridge Not Persistent

**Symptom**: `br1` disappears after reboot; DUT unreachable.
**Cause**: `setup-management-network.sh` creates a transient bridge.
**Fix**: Add netplan config:
```yaml
# /etc/netplan/99-br1.yaml
network:
  version: 2
  bridges:
    br1:
      addresses: [10.250.0.1/24]
      mtu: 9100
```

## Docker Daemon Crash After apt upgrade

**Symptom**: Docker commands fail after system package upgrade.
**Fix**:
```bash
sudo systemctl reset-failed docker.service
sudo systemctl restart docker.socket
sudo systemctl restart docker.service
```

## debian:jessie Missing

**Symptom**: Topology setup fails looking for `debian:jessie` image.
**Fix**:
```bash
docker pull publicmirror.azurecr.io/debian:jessie
docker tag publicmirror.azurecr.io/debian:jessie debian:jessie
```

## NTP/Chrony Sync Failure

**Symptom**: `deploy-mg` shows chrony "No suitable source" error.
**Impact**: Non-fatal. Safe to ignore — DUT has no NTP server in isolated testbed.
