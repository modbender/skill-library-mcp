# Credentials Configuration

## The Build User Problem

The default user in a sonic-vs image depends on who built it:
- **CI-built images** (from Azure Pipelines): default user is `admin`
- **Locally built images**: default user matches the build machine's username (e.g. `yxieca`)

The `sonic_login` in `group_vars/all/creds.yml` **must match** the image's default user, otherwise kickstart fails silently (no management IP, SSH unreachable).

**After every fresh deploy**, create the missing user on the DUT:

```bash
# For CI image (has admin, needs your local user):
ssh admin@<DUT_IP>
sudo useradd -m -s /bin/bash -G sudo,docker <your_user>
echo '<your_user>:password' | sudo chpasswd
sudo bash -c "echo '<your_user> ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/<your_user>"

# For local build (has your user, needs admin):
ssh <your_user>@<DUT_IP>
sudo useradd -m -s /bin/bash -G sudo,docker admin
echo 'admin:password' | sudo chpasswd
sudo bash -c "echo 'admin ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/admin"

# Always fix docker socket:
sudo chmod 666 /var/run/docker.sock
```

### Identifying the Build User

Mount the QCOW2 image to check:
```bash
sudo modprobe nbd max_part=8
sudo qemu-nbd --connect=/dev/nbd0 sonic-vs.img
sudo mount /dev/nbd0p3 /mnt
sudo mount -t squashfs /mnt/image-*/fs.squashfs /mnt2
grep -v nologin /mnt2/etc/passwd  # Look for UID 1000
sudo umount /mnt2 && sudo umount /mnt && sudo qemu-nbd -d /dev/nbd0
```

## Files to Configure

All paths relative to `sonic-mgmt/ansible/`.

### group_vars/all/creds.yml

```yaml
sonic_login: "<build_user>"  # "admin" for CI images, your username for local builds
sonic_password: "password"
ansible_altpassword: "YourPaSsWoRd"
```

### group_vars/vm_host/creds.yml

```yaml
ansible_user: <host_user>
ansible_password: ''
ansible_become_password: ''
vm_host_user: <host_user>
vm_host_password: ''
vm_host_become_password: ''
```

### group_vars/lab/secrets.yml

```yaml
sonicadmin_user: "admin"
sonicadmin_password: "password"
sonicadmin_initial_password: "password"
```

### group_vars/all/ceos.yml

```yaml
skip_ceos_image_downloading: true
```

### group_vars/vm_host/main.yml

```yaml
max_fp_num: 127  # Default 4 is too low for T0/T1
```

### veos_vtb (inventory)

Set `ansible_user` for your vm_host entry:
```ini
STR-ACS-VSERV-01 ansible_host=10.250.0.1 ansible_user=<host_user>
```

### veos (inventory)

Comment out `STR-ACS-SERV-01` to avoid dual-host conflict:
```ini
#STR-ACS-SERV-01 ansible_host=...
```

### vars/docker_registry.yml

Remove `:443` — it causes docker pull to hang silently:
```yaml
docker_registry_host: sonicdev-microsoft.azurecr.io
```

### vtestbed.yaml

Add `use_converged_peers: true` under the testbed entry:
```yaml
- conf-name: vms-kvm-t0
  ...
  use_converged_peers: true
```

### password.txt

```bash
echo "abc" > ansible/password.txt
```

### EOS credentials

Default EOS creds are `admin` / `123456` (in `group_vars/eos/creds.yml`).

## Fix Script Template

Create a script to re-apply all settings (they revert on git/testbed operations):

```bash
#!/bin/bash
# fix-configs.sh — Run before EVERY testbed-cli.sh command
ANSIBLE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ANSIBLE_DIR"

HOST_USER="$(whoami)"

# vm_host creds
cat > group_vars/vm_host/creds.yml <<EOF
---
ansible_user: $HOST_USER
ansible_password: ''
ansible_become_password: ''
vm_host_user: $HOST_USER
vm_host_password: ''
vm_host_become_password: ''
EOF

# sonic login (set to your build user or admin)
sed -i "s/^sonic_login:.*/sonic_login: \"$HOST_USER\"/" group_vars/all/creds.yml

# skip ceos download
cat > group_vars/all/ceos.yml <<EOF
skip_ceos_image_downloading: true
EOF

# max_fp_num
sed -i 's/^max_fp_num:.*/max_fp_num: 127/' group_vars/vm_host/main.yml

# docker registry — remove :443
sed -i 's/:443//' vars/docker_registry.yml

# veos_vtb inventory — fix ansible_user
sed -i "s/ansible_user=.*/ansible_user=$HOST_USER/" veos_vtb

# veos — comment out STR-ACS-SERV-01
sed -i '/^STR-ACS-SERV-01/s/^/#/' veos

echo "Config fixes applied."
```
