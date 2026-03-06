---
name: virtualbox
description: "Control and manage VirtualBox virtual machines directly from openclaw. Start, stop, snapshot, clone, configure and monitor VMs using VBoxManage CLI. Supports full lifecycle management including VM creation, network configuration, shared folders, and performance monitoring."
homepage: https://www.virtualbox.org/manual/ch08.html
metadata: {"openclaw":{"emoji":"🖥️","requires":{"bins":["VBoxManage"]}}}
---

# VirtualBox Skill

Control and manage VirtualBox virtual machines directly from openclaw using the VBoxManage command-line interface. This skill provides comprehensive VM lifecycle management, configuration, and monitoring capabilities.

## Setup

### Prerequisites
1. VirtualBox must be installed on the host system
2. VBoxManage CLI must be accessible (usually in PATH after VirtualBox installation)
3. User must have appropriate permissions to control VMs

### Verify Installation
```bash
VBoxManage --version
```

### Common Paths
- **Linux**: `/usr/bin/VBoxManage` or `/usr/local/bin/VBoxManage`
- **macOS**: `/Applications/VirtualBox.app/Contents/MacOS/VBoxManage`
- **Windows**: `C:\Program Files\Oracle\VirtualBox\VBoxManage.exe`

## Core Capabilities

### VM Lifecycle Management
- Create, start, stop, pause, and delete VMs
- Manage VM states (running, paused, saved, powered off)
- Force stop and ACPI shutdown options
- Reset and restart VMs

### Configuration Management
- Modify VM settings (CPU, RAM, storage)
- Configure network adapters and modes
- Set up shared folders
- Manage USB device passthrough

### Snapshot & Cloning
- Create and restore snapshots
- Clone existing VMs
- Export/Import appliances

### Monitoring & Information
- List all VMs and their states
- Get detailed VM information
- Monitor VM metrics and performance
- View logs and debugging info

## Usage

### List All VMs

```bash
# List all registered VMs
VBoxManage list vms

# List running VMs only
VBoxManage list runningvms

# Get detailed info about all VMs (JSON-like output)
VBoxManage list vms --long
```

### VM Information

```bash
# Get detailed info about a specific VM
VBoxManage showvminfo "VM_NAME"

# Get info in machine-readable format
VBoxManage showvminfo "VM_NAME" --machinereadable
```

### Start a VM

```bash
# Start VM with GUI
VBoxManage startvm "VM_NAME"

# Start VM headless (no GUI)
VBoxManage startvm "VM_NAME" --type headless

# Start VM with separate UI process
VBoxManage startvm "VM_NAME" --type separate
```

### Stop a VM

```bash
# ACPI shutdown (graceful, like pressing power button)
VBoxManage controlvm "VM_NAME" acpipowerbutton

# Power off (hard stop, like pulling plug)
VBoxManage controlvm "VM_NAME" poweroff

# Save state (hibernate)
VBoxManage controlvm "VM_NAME" savestate

# Pause VM
VBoxManage controlvm "VM_NAME" pause

# Resume paused VM
VBoxManage controlvm "VM_NAME" resume

# Reset VM (hard reboot)
VBoxManage controlvm "VM_NAME" reset
```

### Create a New VM

```bash
# Create a new VM
VBoxManage createvm --name "NewVM" --register

# Set OS type
VBoxManage modifyvm "NewVM" --ostype "Ubuntu_64"

# Set memory (RAM in MB)
VBoxManage modifyvm "NewVM" --memory 4096

# Set CPU count
VBoxManage modifyvm "NewVM" --cpus 2

# Create a virtual disk
VBoxManage createhd --filename "/path/to/NewVM.vdi" --size 50000

# Add storage controller
VBoxManage storagectl "NewVM" --name "SATA Controller" --add sata

# Attach virtual disk
VBoxManage storageattach "NewVM" --storagectl "SATA Controller" \
  --port 0 --device 0 --type hdd --medium "/path/to/NewVM.vdi"

# Attach ISO for installation
VBoxManage storageattach "NewVM" --storagectl "SATA Controller" \
  --port 1 --device 0 --type dvddrive --medium "/path/to/install.iso"
```

### Clone a VM

```bash
# Full clone (all disks copied)
VBoxManage clonevm "SourceVM" --name "ClonedVM" --register

# Linked clone (uses same base disk, saves space)
VBoxManage clonevm "SourceVM" --name "LinkedVM" --options link --register

# Clone with specific snapshot
VBoxManage clonevm "SourceVM" --name "FromSnapshotVM" \
  --snapshot "SnapshotName" --register
```

### Delete a VM

```bash
# Delete VM (keep disks)
VBoxManage unregistervm "VM_NAME"

# Delete VM and all associated files
VBoxManage unregistervm "VM_NAME" --delete
```

### Snapshots

```bash
# List snapshots
VBoxManage snapshot "VM_NAME" list

# Take a snapshot
VBoxManage snapshot "VM_NAME" take "SnapshotName" --description "Description here"

# Restore a snapshot
VBoxManage snapshot "VM_NAME" restore "SnapshotName"

# Delete a snapshot
VBoxManage snapshot "VM_NAME" delete "SnapshotName"

# Restore current snapshot (go back to last snapshot)
VBoxManage snapshot "VM_NAME" restorecurrent
```

### Network Configuration

```bash
# List network adapters
VBoxManage showvminfo "VM_NAME" | grep -A 5 "NIC"

# Set NAT networking
VBoxManage modifyvm "VM_NAME" --nic1 nat

# Set bridged networking
VBoxManage modifyvm "VM_NAME" --nic1 bridged --bridgeadapter1 eth0

# Set host-only networking
VBoxManage modifyvm "VM_NAME" --nic1 hostonly --hostonlyadapter1 vboxnet0

# Port forwarding (NAT only)
VBoxManage modifyvm "VM_NAME" --natpf1 "ssh,tcp,,2222,,22"

# Remove port forwarding
VBoxManage modifyvm "VM_NAME" --natpf1 delete "ssh"

# List host-only networks
VBoxManage list hostonlyifs

# Create host-only network
VBoxManage hostonlyif create

# Configure host-only network
VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0
```

### Shared Folders

```bash
# Add shared folder
VBoxManage sharedfolder add "VM_NAME" --name "share" --hostpath "/path/on/host"

# Add read-only shared folder
VBoxManage sharedfolder add "VM_NAME" --name "share" --hostpath "/path/on/host" --readonly

# Add with automount
VBoxManage sharedfolder add "VM_NAME" --name "share" --hostpath "/path/on/host" --automount

# Remove shared folder
VBoxManage sharedfolder remove "VM_NAME" --name "share"

# List shared folders
VBoxManage showvminfo "VM_NAME" | grep -A 5 "Shared Folder"
```

### Modify VM Settings

```bash
# Change memory allocation
VBoxManage modifyvm "VM_NAME" --memory 8192

# Change CPU count
VBoxManage modifyvm "VM_NAME" --cpus 4

# Enable/disable VRAM (video memory)
VBoxManage modifyvm "VM_NAME" --vram 128

# Enable 3D acceleration
VBoxManage modifyvm "VM_NAME" --accelerate3d on

# Enable nested virtualization
VBoxManage modifyvm "VM_NAME" --nested-hw-virt on

# Set VRDE (remote desktop) port
VBoxManage modifyvm "VM_NAME" --vrde on --vrdeport 3389

# Change VM name
VBoxManage modifyvm "VM_NAME" --name "NewName"

# Set description
VBoxManage modifyvm "VM_NAME" --description "Production server VM"
```

### USB Device Passthrough

```bash
# List USB devices
VBoxManage list usbhost

# Attach USB device to running VM
VBoxManage controlvm "VM_NAME" usbattach "UUID_OR_ADDRESS"

# Detach USB device
VBoxManage controlvm "VM_NAME" usbdetach "UUID_OR_ADDRESS"

# Add USB device filter (persistent)
VBoxManage usbfilter add 0 --target "VM_NAME" --name "FilterName" \
  --vendorid "XXXX" --productid "XXXX"
```

### Export/Import Appliances

```bash
# Export VM to OVA/OVF
VBoxManage export "VM_NAME" --output "/path/to/export.ova"

# Export multiple VMs
VBoxManage export "VM1" "VM2" --output "/path/to/export.ova"

# Import appliance
VBoxManage import "/path/to/export.ova"

# Import with options
VBoxManage import "/path/to/export.ova" --vsys 0 --vmname "ImportedVM"
```

### Monitoring & Metrics

```bash
# List available metrics
VBoxManage metrics list

# Setup metrics collection
VBoxManage metrics setup --period 10 --samples 5 "VM_NAME"

# Collect and display metrics
VBoxManage metrics collect "VM_NAME"

# Query specific metrics
VBoxManage metrics query "VM_NAME" "CPU/Load"
VBoxManage metrics query "VM_NAME" "RAM/Usage"
VBoxManage metrics query "VM_NAME" "Net/Rate"

# List all metrics for a VM
VBoxManage metrics list "VM_NAME"
```

### Medium (Disk) Management

```bash
# List all virtual disks
VBoxManage list hdds

# Get disk info
VBoxManage showhdinfo "/path/to/disk.vdi"

# Resize virtual disk
VBoxManage modifyhd "/path/to/disk.vdi" --resize 100000

# Clone virtual disk
VBoxManage clonemedium "/path/to/source.vdi" "/path/to/clone.vdi"

# Compact disk (shrink)
VBoxManage modifymedium "/path/to/disk.vdi" --compact

# Set disk type
VBoxManage modifymedium "/path/to/disk.vdi" --type normal
VBoxManage modifymedium "/path/to/disk.vdi" --type immutable
VBoxManage modifymedium "/path/to/disk.vdi" --type writethrough
```

### Guest Control (Guest Additions Required)

```bash
# Execute command in guest
VBoxManage guestcontrol "VM_NAME" run --exe "/bin/ls" \
  --username user --password pass -- -la /home

# Copy file to guest
VBoxManage guestcontrol "VM_NAME" copyto \
  --username user --password pass \
  "/host/path/file.txt" "/guest/path/file.txt"

# Copy file from guest
VBoxManage guestcontrol "VM_NAME" copyfrom \
  --username user --password pass \
  "/guest/path/file.txt" "/host/path/file.txt"

# Create directory in guest
VBoxManage guestcontrol "VM_NAME" mkdir \
  --username user --password pass \
  "/home/user/newdir"

# Remove file in guest
VBoxManage guestcontrol "VM_NAME" rm \
  --username user --password pass \
  "/home/user/file.txt"

# List guest processes
VBoxManage guestcontrol "VM_NAME" process list \
  --username user --password pass
```

### Debugging & Logs

```bash
# View VM logs location
VBoxManage showvminfo "VM_NAME" | grep -i log

# Typical log paths:
# Linux/macOS: ~/VirtualBox VMs/VM_NAME/Logs/
# Windows: %USERPROFILE%\VirtualBox VMs\VM_NAME\Logs\

# Debug a VM
VBoxManage debugvm "VM_NAME" info item

# Get VM statistics
VBoxManage debugvm "VM_NAME" statistics
```

## Practical Examples

### Quick VM Status Check

```bash
# Check if a specific VM is running
VBoxManage list runningvms | grep "VM_NAME"

# Get all VMs with their states
VBoxManage list vms --long | grep -E "Name:|State:"
```

### Automated VM Startup Script

```bash
#!/bin/bash
# Start VMs in headless mode
for vm in "WebServer" "Database" "Cache"; do
  echo "Starting $vm..."
  VBoxManage startvm "$vm" --type headless
  sleep 10
done
echo "All VMs started"
```

### Backup Script with Snapshots

```bash
#!/bin/bash
VM_NAME="ProductionVM"
DATE=$(date +%Y%m%d_%H%M%S)
SNAPSHOT_NAME="Backup_$DATE"

# Create snapshot
VBoxManage snapshot "$VM_NAME" take "$SNAPSHOT_NAME" \
  --description "Automated backup $DATE"

# Keep only last 5 snapshots
SNAPSHOTS=$(VBoxManage snapshot "$VM_NAME" list --machinereadable | grep SnapshotName | wc -l)
if [ $SNAPSHOTS -gt 5 ]; then
  OLDEST=$(VBoxManage snapshot "$VM_NAME" list --machinereadable | grep SnapshotName | head -1 | cut -d'"' -f4)
  VBoxManage snapshot "$VM_NAME" delete "$OLDEST"
fi
```

### Complete VM Cloning Workflow

```bash
#!/bin/bash
SOURCE_VM="TemplateVM"
NEW_VM="DevVM_$(date +%s)"

# Ensure source is stopped
VBoxManage controlvm "$SOURCE_VM" poweroff 2>/dev/null

# Take a clean snapshot first
VBoxManage snapshot "$SOURCE_VM" take "PreClone"

# Clone the VM
VBoxManage clonevm "$SOURCE_VM" --name "$NEW_VM" --register

# Modify the clone
VBoxManage modifyvm "$NEW_VM" --memory 2048 --cpus 2

# Start the clone
VBoxManage startvm "$NEW_VM" --type headless

echo "Cloned VM '$NEW_VM' is now running"
```

### Network Port Forwarding Setup

```bash
#!/bin/bash
VM_NAME="WebServer"

# SSH access
VBoxManage modifyvm "$VM_NAME" --natpf1 "ssh,tcp,,2222,,22"

# HTTP access
VBoxManage modifyvm "$VM_NAME" --natpf1 "http,tcp,,8080,,80"

# HTTPS access
VBoxManage modifyvm "$VM_NAME" --natpf1 "https,tcp,,8443,,443"

# Verify
VBoxManage showvminfo "$VM_NAME" | grep "NIC 1 Rule"
```

### Monitor Resource Usage

```bash
#!/bin/bash
VM_NAME="ProductionVM"

# Setup metrics
VBoxManage metrics setup --period 5 --samples 12 "$VM_NAME"

# Collect for 1 minute and show results
sleep 60
VBoxManage metrics query "$VM_NAME" "CPU/Load:RAM/Usage:Net/Rate"
```

## Common Issues & Solutions

### VM Won't Start
```bash
# Check VM state
VBoxManage showvminfo "VM_NAME" | grep State

# Check for locked files
VBoxManage showvminfo "VM_NAME" | grep -i lock

# Try starting with verbose output
VBoxManage startvm "VM_NAME" --type headless 2>&1
```

### Cannot Delete VM
```bash
# Ensure VM is stopped
VBoxManage controlvm "VM_NAME" poweroff

# Check for attached media
VBoxManage showvminfo "VM_NAME" | grep -E "Storage|Medium"

# Force unregister if needed
VBoxManage unregistervm "VM_NAME" --delete
```

### Network Issues
```bash
# Check adapter status
VBoxManage showvminfo "VM_NAME" | grep -A 10 "NIC 1"

# Reset network adapter
VBoxManage modifyvm "VM_NAME" --nic1 none
VBoxManage modifyvm "VM_NAME" --nic1 nat

# Verify host-only interface exists
VBoxManage list hostonlyifs
```

### Performance Issues
```bash
# Check current allocation
VBoxManage showvminfo "VM_NAME" | grep -E "Memory|CPU"

# Increase resources (VM must be stopped)
VBoxManage modifyvm "VM_NAME" --memory 8192 --cpus 4

# Enable hardware acceleration
VBoxManage modifyvm "VM_NAME" --hwvirtex on --nestedpaging on
```

## Important Notes

1. **VM Names with Spaces**: Always quote VM names containing spaces
   ```bash
   VBoxManage startvm "My Production VM"
   ```

2. **UUIDs vs Names**: Both VM names and UUIDs work interchangeably
   ```bash
   VBoxManage startvm "VM_NAME"
   VBoxManage startvm "12345678-1234-1234-1234-123456789abc"
   ```

3. **Running vs Stopped Operations**:
   - `controlvm` - operates on running VMs
   - `modifyvm` - operates on stopped VMs (mostly)

4. **Headless Mode**: Always use `--type headless` for server environments without GUI

5. **Permissions**: Some operations require elevated permissions or membership in specific groups (e.g., `vboxusers` on Linux)

6. **Guest Additions**: Required for:
   - Shared clipboard
   - Drag and drop
   - Shared folders auto-mount
   - Guest control commands
   - Seamless mode

## OS Types Reference

Common OS types for `--ostype` parameter:
- `Windows11_64` - Windows 11 (64-bit)
- `Windows10_64` - Windows 10 (64-bit)
- `Ubuntu_64` - Ubuntu Linux (64-bit)
- `Debian_64` - Debian Linux (64-bit)
- `Fedora_64` - Fedora Linux (64-bit)
- `ArchLinux_64` - Arch Linux (64-bit)
- `macOS_ARM64` - macOS on Apple Silicon
- `macOS_128` - macOS on Intel (64-bit)
- `FreeBSD_64` - FreeBSD (64-bit)
- `Other_64` - Other OS (64-bit)

Get full list with:
```bash
VBoxManage list ostypes
```

## Quick Reference Card

| Operation | Command |
|-----------|---------|
| List VMs | `VBoxManage list vms` |
| Start VM | `VBoxManage startvm "NAME" --type headless` |
| Stop VM | `VBoxManage controlvm "NAME" acpipowerbutton` |
| Force Stop | `VBoxManage controlvm "NAME" poweroff` |
| VM Info | `VBoxManage showvminfo "NAME"` |
| Snapshot | `VBoxManage snapshot "NAME" take "SnapName"` |
| Restore | `VBoxManage snapshot "NAME" restore "SnapName"` |
| Clone | `VBoxManage clonevm "SRC" --name "NEW" --register` |
| Delete | `VBoxManage unregistervm "NAME" --delete` |
| Modify RAM | `VBoxManage modifyvm "NAME" --memory 4096` |
| Modify CPU | `VBoxManage modifyvm "NAME" --cpus 2` |
| Port Forward | `VBoxManage modifyvm "NAME" --natpf1 "rule,tcp,,host,,guest"` |

## Requirements

- **Required Binary**: `VBoxManage` (part of VirtualBox installation)
- **Permissions**: User must have VM management permissions
- **Guest Additions**: Required for guest control and enhanced features
