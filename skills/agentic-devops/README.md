# agentic-devops

**Production-grade agent DevOps toolkit** — Docker, process management, log analysis, and health monitoring in one unified CLI. Built by engineers who run production systems.

## Features

- **Docker Operations** — Container status, log tailing with pattern detection, health checks, Compose service status
- **Process Management** — List/sort processes by resource usage, port inspection, zombie detection
- **Log Analysis** — Pattern matching, error extraction, frequency analysis across log files
- **Health Monitoring** — HTTP endpoint checks, port scanning, system resource alerts
- **Quick Diagnostics** — One-command full system health overview combining all of the above

## Quick Start

```bash
# The money command — full system diagnostics
python3 devops.py diag
```

## Usage

### Docker

```bash
python3 devops.py docker status
python3 devops.py docker logs <container> --tail 100 --grep "error|warn"
python3 devops.py docker health
python3 devops.py docker compose-status --file docker-compose.yml
```

### Process Management

```bash
python3 devops.py proc list --sort cpu
python3 devops.py proc ports
python3 devops.py proc zombies
```

### Log Analysis

```bash
python3 devops.py logs analyze /var/log/syslog --pattern "error|fail|critical"
python3 devops.py logs tail /var/log/app.log --highlight "ERROR|WARN"
python3 devops.py logs frequency /var/log/app.log --top 20
```

### Health Checks

```bash
python3 devops.py health check https://myapp.com/healthz
python3 devops.py health ports 80,443,8080,5432
python3 devops.py health system
```

## Requirements

- Python 3.8+ (stdlib only — zero external dependencies)
- Docker CLI (optional — Docker sections degrade gracefully if not installed)
- Standard Unix utilities (`ps`, `ss`/`netstat`)

## Design Principles

- **Stdlib only** — No pip install, no venv, no dependency hell. Works anywhere Python 3 exists.
- **Graceful degradation** — Missing Docker? No problem. Permission denied on a log file? Skip it and keep going.
- **Production-grade output** — Unicode box drawing, ANSI colours, status indicators, bar charts. Looks good in any terminal.
- **Enterprise tone** — Built for SREs and platform engineers who need answers fast.

## Install

```bash
clawhub install agentic-devops
```

Or clone from [GitHub](https://github.com/cacheforge-ai/cacheforge-skills).

## License

MIT — see [LICENSE](LICENSE).
