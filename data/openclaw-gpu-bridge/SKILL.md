---
name: openclaw-gpu-bridge
description: "Offload GPU-intensive ML tasks (BERTScore, embeddings) to one or multiple remote GPU machines"
---

# @elvatis_com/openclaw-gpu-bridge

OpenClaw plugin to offload ML tasks (BERTScore + embeddings) to one or many remote GPU hosts.

## v0.2 Highlights

- Multi-GPU host pool (`hosts[]`) with:
  - round-robin or least-busy load balancing
  - automatic failover
  - periodic host health checks
- Backward compatibility with v0.1 (`serviceUrl` / `url`)
- Flexible model selection per request (`model` / `model_type`)
- GPU service model caching (on-demand loading)
- Optional transfer visibility via `/status` endpoint + batch progress logs

---

## Tools

- `gpu_health`
- `gpu_info`
- `gpu_status` (new in v0.2)
- `gpu_bertscore`
- `gpu_embed`

---

## OpenClaw Plugin Config

### v0.2 (recommended)

```json
{
  "plugins": {
    "@elvatis_com/openclaw-gpu-bridge": {
      "hosts": [
        {
          "name": "rtx-2080ti",
          "url": "http://your-gpu-host:8765",
          "apiKey": "gpu-key-1"
        },
        {
          "name": "rtx-3090",
          "url": "http://your-second-gpu-host:8765",
          "apiKey": "gpu-key-2"
        }
      ],
      "loadBalancing": "least-busy",
      "healthCheckIntervalSeconds": 30,
      "timeout": 45,
      "models": {
        "embed": "all-MiniLM-L6-v2",
        "bertscore": "microsoft/deberta-xlarge-mnli"
      }
    }
  }
}
```

### v0.1 compatibility

```json
{
  "plugins": {
    "@elvatis_com/openclaw-gpu-bridge": {
      "serviceUrl": "http://your-gpu-host:8765",
      "apiKey": "gpu-key",
      "timeout": 45
    }
  }
}
```

### Config reference

- `hosts`: array of GPU hosts (v0.2)
- `serviceUrl` / `url`: legacy single-host config
- `loadBalancing`: `round-robin` or `least-busy`
- `healthCheckIntervalSeconds`: host health polling interval
- `timeout`: request timeout for compute endpoints
- `apiKey`: fallback API key for hosts that do not define per-host key
- `models.embed`, `models.bertscore`: plugin-side default models

---

## GPU Service (Python) Setup

```bash
cd gpu-service
pip install -r requirements.txt
uvicorn gpu_service:app --host 0.0.0.0 --port 8765
```

Default models are warmed on startup:
- Embed: `all-MiniLM-L6-v2`
- BERTScore: `microsoft/deberta-xlarge-mnli`

Additional models are loaded on-demand and cached in memory.

### Environment variables

- `API_KEY`: require `X-API-Key` for all endpoints except `/health`
- `GPU_MAX_CONCURRENT`: max parallel jobs (default `2`)
- `GPU_EMBED_BATCH`: embedding chunk size for progress logging (default `32`)
- `MODEL_BERTSCORE`: default warm model for BERTScore
- `MODEL_EMBED`: default warm model for embeddings
- `TORCH_DEVICE`: force device (`cuda`, `cpu`, `cuda:1`)

---

## API Endpoints (GPU Service)

- `GET /health`
- `GET /info`
- `GET /status` (queue + active jobs + progress)
- `POST /bertscore`
- `POST /embed`

### Request-level model override

`/bertscore`:
```json
{
  "candidates": ["a"],
  "references": ["b"],
  "model_type": "microsoft/deberta-xlarge-mnli"
}
```

`/embed`:
```json
{
  "texts": ["hello world"],
  "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
}
```

---

## Exposing to the Internet

If you expose your GPU service outside LAN, use defense-in-depth:

1. **Pre-shared key auth (required)**
   - Set `API_KEY` on service
   - Configure same key in plugin host config (`apiKey`)
   - Requests must include `X-API-Key`

2. **TLS/HTTPS (required on public internet)**
   - Recommended: nginx reverse proxy with Let’s Encrypt certs
   - Alternative: run uvicorn with SSL cert/key directly

### nginx reverse proxy example

```nginx
server {
  listen 443 ssl http2;
  server_name gpu.example.com;

  ssl_certificate /etc/letsencrypt/live/gpu.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/gpu.example.com/privkey.pem;

  location / {
    proxy_pass http://127.0.0.1:8765;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

### uvicorn SSL example

```bash
uvicorn gpu_service:app --host 0.0.0.0 --port 8765 \
  --ssl-keyfile /path/key.pem \
  --ssl-certfile /path/cert.pem
```

3. **Optional: WireGuard VPN instead of public exposure**
   - Keep service private behind VPN
   - Prefer private WireGuard IPs in plugin `hosts[].url`

4. **Operational hardening**
   - Firewall allowlist only OpenClaw server IP
   - Rate limiting at reverse proxy
   - Monitor logs and rotate keys periodically

---

## Development

```bash
npm run build
npm test
```

TypeScript runs in strict mode.

## License

MIT
