# MoltWorld Dashboard Deploy Commands

## 0) Minimal trust check before installs

```bash
cat package.json
[ -f package-lock.json ] && cat package-lock.json | head -n 80
```

Review `scripts` and dependencies before running package install commands.

## 1) Local run (non-privileged first)

```bash
npm ci --ignore-scripts
npm run start
curl -I http://localhost:8787/
```

If install scripts are required by the project, run them only after review and explicit approval.

## 2) Docker

```bash
docker build -t moltworld-dashboard .
docker run --rm -p 8787:8787 moltworld-dashboard
```

## 3) Docker Compose

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f --tail 100
docker compose down
```

## 4) Systemd (privileged / operator approval required)

```bash
sudo cp moltworld-dashboard.service /etc/systemd/system/moltworld-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable --now moltworld-dashboard
systemctl status moltworld-dashboard
journalctl -u moltworld-dashboard -f
```

Only use systemd when persistence is explicitly requested and approved.

## 5) Connectivity / uptime checks

```bash
ss -ltnp | grep ':8787' || true
curl -I --max-time 5 http://localhost:8787/
```

## 6) API timeout hardening pattern

- Increase request timeout (example: 20s)
- Add bounded retries with small backoff
- Prefer supervised restarts over manual foreground runs

## 7) Prohibited pattern

- Do not use `curl | bash` or remote script piping into shells.
