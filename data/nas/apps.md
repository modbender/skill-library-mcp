## Docker & Applications

### Architecture Awareness

| NAS CPU | Architecture | Docker Compatibility |
|---------|--------------|---------------------|
| Intel Celeron | x86_64 | Full |
| AMD Ryzen | x86_64 | Full |
| ARM Cortex-A (J-series) | arm64 | Limited |
| Realtek (budget models) | arm | Very limited |

**Before buying:** Check CPU architecture. Budget NAS often ARM = most images won't work.

### Docker on Synology

```yaml
# Use bridge network for isolation
networks:
  nas-apps:
    driver: bridge

# Bind to LAN IP, not 0.0.0.0
ports:
  - "192.168.1.10:8080:80"
```

### Common Traps

1. **Permission hell with volumes** — PUID/PGID must match NAS user. Not 1000:1000 always.

2. **Memory limits critical** — NAS has limited RAM. Set container memory limits or OOM kills everything.

3. **Don't run databases on NAS** — Postgres/MySQL on SMB/spinning disks = terrible performance. OK for sqlite.

4. **Path mapping confusion** — Host path `/volume1/docker/app` ≠ container path `/config`. Map explicitly.

5. **Updates break things** — Pin image versions. `:latest` surprise-breaks production setups.

### Resource-Friendly Apps

Low memory, NAS-appropriate:

- **Jellyfin/Plex** — Media server (transcode needs good CPU)
- **Paperless-ngx** — Document OCR and archive
- **Immich** — Photo backup (self-hosted Google Photos)
- **Home Assistant** — Smart home (consider dedicated Pi)
- **Pi-hole** — DNS-level ad blocking
- **Nginx Proxy Manager** — Reverse proxy with GUI

### Storage for Containers

```
/volume1/docker/
├── appdata/          ← config files (fast SSD if available)
├── media/            ← shared media library
└── downloads/        ← temp/scratch space
```

Don't put container configs on spinning array. If NAS has NVMe cache, use it for Docker.
