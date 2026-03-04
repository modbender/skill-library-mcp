# VS Platform Notes

## Architecture

VS (Virtual Switch) simulates a BCM56850 ASIC using TAP devices inside a KVM VM.

## Port Mapping

VS uses TAP devices with `SAI_VS_HOSTIF_USE_TAP_DEVICE=true`:

- eth1 → Ethernet0
- eth2 → Ethernet4
- eth3 → Ethernet8
- First 3 virtio NICs after eth0 (management)
- Remaining 29 ports: TAP devices exist but no backing NIC → oper=down

Port config: `/usr/share/sonic/device/x86_64-kvm_x86_64-r0/Force10-S6000/port_config.ini`

## SAI Profiles

**Master template:** `src/sonic-device-data/src/sai.vs_profile` — gets copied as `sai.profile` into ALL ~200 VS HwSKU dirs at build time.

Individual files under `src/device/x86_64-kvm_x86_64-r0/` are **gitignored and auto-generated** — edit only the templates.

`device/virtual/` profiles are used by `docker-sonic-vs` (single-container variant), NOT by full KVM image.

SAI profile inside running VM: `/etc/sai.d/sai.profile` (syncd container).

## Oper Speed

virtio NICs report `-1` for link speed via sysfs, causing VS SAI to report `0xFFFFFFFF` oper speed.

Fix: `SAI_VS_USE_CONFIGURED_SPEED_AS_OPER_SPEED=true` in sai.profile makes ports report configured speed instead.

## Testing on VS VM

```bash
# Deploy image
sudo virt-install --name sonic-vs --ram 4096 --vcpus 4 \
  --disk path=sonic-vs.img,format=raw --import --os-variant debian12

# SSH access
ssh admin@<vm-ip>  # default password: YourPaSsWoRd

# Verify
show version
show interfaces status
show ip bgp summary
```

## sonic-cfggen Template Testing

`sonic-cfggen -t template.j2` uses `os.path.basename()` + FileSystemLoader with `['/', '/usr/share/sonic/templates']`. System template is found before your file. Must copy patched template to `/usr/share/sonic/templates/` for VM testing.
