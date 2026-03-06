# VMX Configuration Reference

Key VMX settings used by the deploy script.

## NVMe Controller + Disk
```
nvme0.present = "TRUE"
nvme0.pciSlotNumber = "160"
nvme0:0.present = "TRUE"
nvme0:0.fileName = "vmname.vmdk"
nvme0:0.deviceType = "disk"
```

## Dual NIC (E1000 for installer + vmxnet3 for production)
```
# E1000 — removed post-install
ethernet0.present = "TRUE"
ethernet0.virtualDev = "e1000"
ethernet0.networkName = "VM Network"
ethernet0.addressType = "generated"

# vmxnet3 — production
ethernet1.present = "TRUE"
ethernet1.virtualDev = "vmxnet3"
ethernet1.networkName = "VM Network"
ethernet1.addressType = "generated"
```

## Serial Port (Telnet)
```
serial0.present = "TRUE"
serial0.fileType = "network"
serial0.fileName = "telnet://ESXI_IP:PORT"
serial0.yieldOnMsrRead = "TRUE"
serial0.startConnected = "TRUE"
```

**Important:** Use the ESXi host IP, not `0.0.0.0`. The `remoteSerialPort` firewall ruleset must be enabled:
```bash
esxcli network firewall ruleset set -e true -r remoteSerialPort
```

## SATA CD-ROM
```
sata0.present = "TRUE"
sata0:0.present = "TRUE"
sata0:0.fileName = "/vmfs/volumes/DATASTORE/ISOs/preseed.iso"
sata0:0.deviceType = "cdrom-image"
sata0:0.startConnected = "TRUE"
```

## Boot Order
```
# During install (CD first)
bios.bootOrder = "cdrom,hdd"

# After install (HDD first)
bios.bootOrder = "hdd"
```

## PCIe Bridges (required for NVMe + multiple devices)
```
pciBridge0.present = "TRUE"
pciBridge4.present = "TRUE"
pciBridge4.virtualDev = "pcieRootPort"
pciBridge4.functions = "8"
pciBridge5.present = "TRUE"
pciBridge5.virtualDev = "pcieRootPort"
pciBridge5.functions = "8"
pciBridge6.present = "TRUE"
pciBridge6.virtualDev = "pcieRootPort"
pciBridge6.functions = "8"
pciBridge7.present = "TRUE"
pciBridge7.virtualDev = "pcieRootPort"
pciBridge7.functions = "8"
```
