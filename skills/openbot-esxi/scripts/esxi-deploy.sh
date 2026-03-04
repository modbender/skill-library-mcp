#!/bin/bash
# =============================================================================
# ESXi Debian 13 VM Deploy Script — Zero-Touch
# Usage: ./esxi-deploy.sh [hostname] [cpu] [ram_mb] [disk_gb]
# =============================================================================
set -euo pipefail

# --- Config (override via environment variables) ---
ESXI_HOST="${ESXI_HOST:?Set ESXI_HOST to your ESXi IP}"
ESXI_USER="${ESXI_USER:-root}"
ESXI_DATASTORE="${ESXI_DATASTORE:-datastore1}"
NETWORK="${NETWORK:-VM Network}"
DOMAIN="${DOMAIN:-local}"
DEFAULT_CPU=2
DEFAULT_RAM=2048
DEFAULT_DISK=20
ISO_CACHE_DIR="${ISO_CACHE_DIR:-/tmp/esxi-deploy-cache}"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- Parameters ---
HOSTNAME="${1:-$(python3 -c "import random; print(random.choice(['pangolin','axolotl','quokka','capybara','narwhal','okapi','fennec','wombat','kiwi','lemur','gecko','toucan','marmot','otter','puffin']))")}"
CPU="${2:-$DEFAULT_CPU}"
RAM="${3:-$DEFAULT_RAM}"
DISK="${4:-$DEFAULT_DISK}"
SERIAL_PORT="${5:-$(python3 -c "import random; print(random.randint(8600,8699))")}"

# --- ESXi password (from environment) ---
ESXI_PASS="${ESXI_PASS:?Set ESXI_PASS to your ESXi root password}"

# --- Generate random password ---
VM_PASS=$(python3 -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(12)))")

# --- Setup ---
mkdir -p "$ISO_CACHE_DIR"
# govc auth via separate env vars (avoids password in process args)
export GOVC_URL="https://${ESXI_HOST}"
export GOVC_USERNAME="${ESXI_USER}"
export GOVC_PASSWORD="${ESXI_PASS}"
export GOVC_INSECURE=true

echo "============================================"
echo "  ESXi Debian 13 Deploy"
echo "============================================"
echo "  VM:       $HOSTNAME"
echo "  Specs:    ${CPU}C / ${RAM}MB / ${DISK}GB"
echo "  User:     user / root"
echo "  Password: $VM_PASS"
echo "  Serial:   telnet $ESXI_HOST $SERIAL_PORT"
echo "============================================"

# --- Step 1: Download Debian 13 Stable ISO (if not cached) ---
ISO_FILE="$ISO_CACHE_DIR/debian-13-netinst.iso"
if [ ! -f "$ISO_FILE" ] || [ "$(stat -c%s "$ISO_FILE")" -lt 100000000 ]; then
    echo "[1/7] Downloading Debian 13 Stable ISO..."
    wget -q "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-13.3.0-amd64-netinst.iso" -O "$ISO_FILE"
else
    echo "[1/7] Using cached Debian 13 ISO"
fi

# --- Step 2: Generate preseed ---
echo "[2/7] Generating preseed..."
PRESEED_FILE="$ISO_CACHE_DIR/preseed-${HOSTNAME}.cfg"
cat > "$PRESEED_FILE" <<PRESEED
# Debian 13 Preseed — VM "$HOSTNAME" — Zero-Touch

### Localization
d-i debian-installer/locale string de_DE.UTF-8
d-i keyboard-configuration/xkb-keymap select de
d-i console-setup/ask_detect boolean false

### Network (DHCP)
d-i netcfg/choose_interface select auto
d-i netcfg/get_hostname string $HOSTNAME
d-i netcfg/get_domain string $DOMAIN

### Mirror
d-i mirror/country string manual
d-i mirror/http/hostname string deb.debian.org
d-i mirror/http/directory string /debian
d-i mirror/http/proxy string

### Clock
d-i clock-setup/utc boolean true
d-i time/zone string Europe/Berlin
d-i clock-setup/ntp boolean true

### Partitioning — use entire disk, one partition
d-i partman-auto/method string regular
d-i partman-auto/choose_recipe select atomic
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true

### Root account
d-i passwd/root-login boolean true
d-i passwd/root-password password $VM_PASS
d-i passwd/root-password-again password $VM_PASS

### User account
d-i passwd/make-user boolean true
d-i passwd/user-fullname string User
d-i passwd/username string user
d-i passwd/user-password password $VM_PASS
d-i passwd/user-password-again password $VM_PASS

### APT
d-i apt-setup/non-free-firmware boolean true
d-i apt-setup/contrib boolean true
d-i apt-setup/non-free boolean true

### Package selection
tasksel tasksel/first multiselect ssh-server, standard
d-i pkgsel/include string open-vm-tools curl sudo qemu-guest-agent
d-i pkgsel/upgrade select full-upgrade
popularity-contest popularity-contest/participate boolean false

### GRUB
d-i grub-installer/only_debian boolean true
d-i grub-installer/bootdev string default

### Finish
d-i finish-install/reboot_in_progress note
d-i debian-installer/exit/poweroff boolean false

### Late command — enable SSH, add user to sudo, configure network
d-i preseed/late_command string \
  in-target sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config; \
  in-target sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config; \
  in-target usermod -aG sudo user; \
  in-target bash -c 'echo -e "auto ens192\\niface ens192 inet dhcp" > /etc/network/interfaces.d/vmxnet3'; \
  in-target bash -c 'echo "blacklist floppy" > /etc/modprobe.d/blacklist-floppy.conf'; \
  in-target bash -c 'echo "blacklist pcspkr" >> /etc/modprobe.d/blacklist-floppy.conf'; \
  in-target bash -c 'sed -i "s/^GRUB_CMDLINE_LINUX=.*/GRUB_CMDLINE_LINUX=\"console=tty0 console=ttyS0,115200n8\"/" /etc/default/grub; echo "GRUB_TERMINAL=\"console serial\"" >> /etc/default/grub; echo "GRUB_SERIAL_COMMAND=\"serial --speed=115200 --unit=0 --word=8 --parity=no --stop=1\"" >> /etc/default/grub; update-grub'; \
  in-target systemctl enable serial-getty@ttyS0.service; \
  in-target apt-get install -y cloud-guest-utils
PRESEED

# --- Step 3: Build custom ISO ---
echo "[3/7] Building custom ISO with preseed..."
WORK_DIR="$ISO_CACHE_DIR/iso_work_${HOSTNAME}"
MOUNT_DIR="$ISO_CACHE_DIR/iso_mount"
CUSTOM_ISO="$ISO_CACHE_DIR/${HOSTNAME}-preseed.iso"

rm -rf "$WORK_DIR" "$MOUNT_DIR"
mkdir -p "$WORK_DIR" "$MOUNT_DIR"

mount -o loop "$ISO_FILE" "$MOUNT_DIR"
cp -rT "$MOUNT_DIR" "$WORK_DIR"
umount "$MOUNT_DIR"

# Copy preseed
cp "$PRESEED_FILE" "$WORK_DIR/preseed.cfg"

# Patch isolinux: 10 second timeout, auto-preseed, no speech synthesis
# timeout is in 1/10th seconds, so 100 = 10 seconds
sed -i 's/^timeout .*/timeout 100/' "$WORK_DIR/isolinux/isolinux.cfg"

# Set "Install" as default with preseed params
cat > "$WORK_DIR/isolinux/txt.cfg" <<'TXTCFG'
default install
label install
	menu label ^Install
	menu default
	kernel /install.amd/vmlinuz
	append vga=788 initrd=/install.amd/initrd.gz --- quiet auto=true priority=critical preseed/file=/cdrom/preseed.cfg
TXTCFG

# Remove speech synthesis entries to prevent accidental trigger
if [ -f "$WORK_DIR/isolinux/spkgtk.cfg" ]; then
    echo "" > "$WORK_DIR/isolinux/spkgtk.cfg"
fi
if [ -f "$WORK_DIR/isolinux/spk.cfg" ]; then
    echo "" > "$WORK_DIR/isolinux/spk.cfg"
fi

# Patch GRUB for UEFI boot (just in case)
if [ -f "$WORK_DIR/boot/grub/grub.cfg" ]; then
    sed -i '/menuentry.*[Ii]nstall/{n;n;s|linux \(.*\)|linux \1 auto=true priority=critical preseed/file=/cdrom/preseed.cfg|}' "$WORK_DIR/boot/grub/grub.cfg"
fi

# Build ISO
xorriso -as mkisofs \
    -o "$CUSTOM_ISO" \
    -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
    -c isolinux/boot.cat \
    -b isolinux/isolinux.bin \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    -eltorito-alt-boot \
    -e boot/grub/efi.img \
    -no-emul-boot -isohybrid-gpt-basdat \
    "$WORK_DIR" 2>&1 | tail -1

rm -rf "$WORK_DIR" "$MOUNT_DIR"
rm -f "$PRESEED_FILE"
echo "    ISO: $(ls -lh "$CUSTOM_ISO" | awk '{print $5}')"

# --- Step 4: Upload ISO to ESXi ---
echo "[4/7] Uploading ISO to ESXi..."
govc datastore.mkdir -p "ISOs" 2>/dev/null || true
govc datastore.upload "$CUSTOM_ISO" "ISOs/${HOSTNAME}-preseed.iso" 2>&1 | tail -1
rm -f "$CUSTOM_ISO"

# --- Step 5: Create VM (NVMe + E1000) ---
echo "[5/7] Creating VM on ESXi..."

# Delete existing VM if present
govc vm.destroy "$HOSTNAME" 2>/dev/null || true

# Create via VMX for NVMe controller support
SSHPASS="$ESXI_PASS" sshpass -e ssh -o StrictHostKeyChecking=no ${ESXI_USER}@${ESXI_HOST} "
    VM_DIR=\"/vmfs/volumes/${ESXI_DATASTORE}/${HOSTNAME}\"
    rm -rf \"\$VM_DIR\"
    mkdir -p \"\$VM_DIR\"

    cat > \"\$VM_DIR/${HOSTNAME}.vmx\" <<VMX
.encoding = \"UTF-8\"
config.version = \"8\"
virtualHW.version = \"21\"
displayName = \"${HOSTNAME}\"
guestOS = \"debian12-64\"
memSize = \"${RAM}\"
numvcpus = \"${CPU}\"
firmware = \"bios\"

# NVMe Controller
nvme0.present = \"TRUE\"
nvme0.pciSlotNumber = \"160\"

# Disk on NVMe
nvme0:0.present = \"TRUE\"
nvme0:0.fileName = \"${HOSTNAME}.vmdk\"
nvme0:0.deviceType = \"disk\"

# SATA Controller for CD-ROM
sata0.present = \"TRUE\"
sata0.pciSlotNumber = \"33\"

# CD-ROM on SATA
sata0:0.present = \"TRUE\"
sata0:0.fileName = \"/vmfs/volumes/${ESXI_DATASTORE}/ISOs/${HOSTNAME}-preseed.iso\"
sata0:0.deviceType = \"cdrom-image\"
sata0:0.startConnected = \"TRUE\"

# Network E1000 (for installer — removed post-install)
ethernet0.present = \"TRUE\"
ethernet0.virtualDev = \"e1000\"
ethernet0.networkName = \"${NETWORK}\"
ethernet0.addressType = \"generated\"
ethernet0.startConnected = \"TRUE\"

# Network vmxnet3 (production — gets configured post-install)
ethernet1.present = \"TRUE\"
ethernet1.virtualDev = \"vmxnet3\"
ethernet1.networkName = \"${NETWORK}\"
ethernet1.addressType = \"generated\"
ethernet1.startConnected = \"TRUE\"

# Serial Port — telnet access to console
serial0.present = \"TRUE\"
serial0.fileType = \"network\"
serial0.fileName = \"telnet://${ESXI_HOST}:${SERIAL_PORT}\"
serial0.yieldOnMsrRead = \"TRUE\"
serial0.startConnected = \"TRUE\"

# Boot order: CD first
bios.bootOrder = \"cdrom,hdd\"

# Misc
tools.syncTime = \"TRUE\"
pciBridge0.present = \"TRUE\"
pciBridge4.present = \"TRUE\"
pciBridge4.virtualDev = \"pcieRootPort\"
pciBridge4.functions = \"8\"
pciBridge5.present = \"TRUE\"
pciBridge5.virtualDev = \"pcieRootPort\"
pciBridge5.functions = \"8\"
pciBridge6.present = \"TRUE\"
pciBridge6.virtualDev = \"pcieRootPort\"
pciBridge6.functions = \"8\"
pciBridge7.present = \"TRUE\"
pciBridge7.virtualDev = \"pcieRootPort\"
pciBridge7.functions = \"8\"
VMX

    # Create thin disk
    vmkfstools -c ${DISK}G -d thin \"\$VM_DIR/${HOSTNAME}.vmdk\"

    # Register VM
    vim-cmd solo/registervm \"\$VM_DIR/${HOSTNAME}.vmx\"
" 2>&1 | tail -2

# --- Step 6: Power on ---
echo "[6/7] Powering on VM..."

# Ensure ESXi firewall allows serial port access
SSHPASS="$ESXI_PASS" sshpass -e ssh -o StrictHostKeyChecking=no "${ESXI_USER}@${ESXI_HOST}" \
    "esxcli network firewall ruleset set -e true -r remoteSerialPort" 2>/dev/null || true

govc vm.power -on "$HOSTNAME"
echo "    VM is booting — zero-touch install in progress"

# --- Step 7: Wait for installation via serial console ---
echo "[7/7] Waiting for installation to complete (monitoring serial console)..."
echo "    Serial: telnet $ESXI_HOST $SERIAL_PORT"

# Start serial console monitor in background
SERIAL_LOG="/tmp/esxi-serial-${HOSTNAME}.log"
rm -f "$SERIAL_LOG"
(
    # Give VM a moment to boot
    sleep 5
    # Connect to serial console via expect-like approach
    exec 3<>/dev/tcp/${ESXI_HOST}/${SERIAL_PORT} 2>/dev/null || exit 0
    while IFS= read -r -t 2 line <&3 2>/dev/null; do
        echo "$line" >> "$SERIAL_LOG"
    done
    exec 3>&-
) &
SERIAL_PID=$!

MAX_WAIT=900  # 15 minutes
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    sleep 30
    ELAPSED=$((ELAPSED + 30))
    
    # Show last serial console output
    if [ -f "$SERIAL_LOG" ]; then
        LAST_LINE=$(tail -1 "$SERIAL_LOG" 2>/dev/null | tr -d '\r' | head -c 120)
        [ -n "$LAST_LINE" ] && echo "    [${ELAPSED}s] Console: $LAST_LINE"
    fi
    
    # Try to get IP (filter out non-IP values like "address:")
    VM_IP=$(govc vm.ip -wait 5s "$HOSTNAME" 2>/dev/null || true)
    
    if [ -n "$VM_IP" ] && [[ "$VM_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        # Try SSH
        if SSHPASS="$VM_PASS" sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "root@${VM_IP}" "hostname" >/dev/null 2>&1; then
            kill $SERIAL_PID 2>/dev/null; rm -f "$SERIAL_LOG"
            echo ""
            echo "============================================"
            echo "  ✅ VM $HOSTNAME is ready!"
            echo "============================================"
            echo "  IP:       $VM_IP"
            echo "  SSH:      ssh root@${VM_IP}"
            echo "  User:     user / $VM_PASS"
            echo "  Root:     root / $VM_PASS"
            echo "============================================"
            
            # --- Post-install: Remove E1000, keep vmxnet3 ---
            echo ""
            echo "  Removing E1000 adapter (vmxnet3 already active)..."
            
            # Shut down gracefully
            SSHPASS="$VM_PASS" sshpass -e ssh -o StrictHostKeyChecking=no "root@${VM_IP}" "shutdown -h now" 2>/dev/null || true
            sleep 10
            
            # Wait for power off
            for i in $(seq 1 12); do
                STATE=$(govc vm.info "$HOSTNAME" 2>/dev/null | grep "Power state" | awk '{print $NF}')
                [ "$STATE" = "poweredOff" ] && break
                sleep 5
            done
            
            # Remove E1000 (ethernet-0), keep vmxnet3 (ethernet-1)
            govc device.remove -vm "$HOSTNAME" ethernet-0 2>/dev/null || true
            
            # Remove CD-ROM ISO, set boot to disk
            govc device.cdrom.eject -vm "$HOSTNAME" -device cdrom-16000 2>/dev/null || true
            SSHPASS="$ESXI_PASS" sshpass -e ssh -o StrictHostKeyChecking=no "${ESXI_USER}@${ESXI_HOST}" "
                VMX=\"/vmfs/volumes/${ESXI_DATASTORE}/${HOSTNAME}/${HOSTNAME}.vmx\"
                sed -i 's|bios.bootOrder = \"cdrom,hdd\"|bios.bootOrder = \"hdd\"|' \"\$VMX\"
            " 2>/dev/null || true
            
            # Power on with vmxnet3 only
            govc vm.power -on "$HOSTNAME" 2>/dev/null
            echo "  Waiting for VM to come back with vmxnet3..."
            
            sleep 20
            NEW_IP=""
            for i in $(seq 1 24); do
                NEW_IP=$(govc vm.ip -wait 5s "$HOSTNAME" 2>/dev/null)
                if [ -n "$NEW_IP" ] && [ "$NEW_IP" != "" ]; then
                    if SSHPASS="$VM_PASS" sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "root@${NEW_IP}" "hostname" >/dev/null 2>&1; then
                        break
                    fi
                fi
                sleep 5
            done
            
            echo ""
            echo "============================================"
            echo "  🎉 DEPLOY COMPLETE"
            echo "============================================"
            echo "  VM:       $HOSTNAME"
            echo "  IP:       ${NEW_IP:-$VM_IP}"
            echo "  Specs:    ${CPU}C / ${RAM}MB / ${DISK}GB NVMe"
            echo "  Network:  vmxnet3"
            echo "  Serial:   telnet $ESXI_HOST $SERIAL_PORT"
            echo "  SSH:      ssh root@${NEW_IP:-$VM_IP}"
            echo "  User:     user / $VM_PASS"
            echo "  Root:     root / $VM_PASS"
            echo "============================================"
            exit 0
        fi
    fi
    
    if [ -z "$VM_IP" ] || [ "$VM_IP" = "" ]; then
        echo "    [${ELAPSED}s] Still installing... (no IP yet)"
    else
        echo "    [${ELAPSED}s] Still installing... (IP: $VM_IP, waiting for SSH)"
    fi
done

kill $SERIAL_PID 2>/dev/null; rm -f "$SERIAL_LOG"
echo "❌ Timeout after ${MAX_WAIT}s — check serial console: telnet $ESXI_HOST $SERIAL_PORT"
exit 1
