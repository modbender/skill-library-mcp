# Example: Rybbit Analytics (Scenario B — Proxy Conflict + Multi-Port)

## Original docker-compose.yml

```yaml
services:
  caddy:
    image: caddy:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"

  backend:
    image: rybbit/backend:latest
    ports:
      - "3001:3001"
    environment:
      - DATABASE_URL=${DATABASE_URL}

  frontend:
    image: rybbit/frontend:latest
    ports:
      - "3002:3002"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
```

## Issues Detected

- Caddy service (proxy conflict with xCloud nginx)
- Multiple exposed ports: 8123, 3001, 3002 (xCloud needs single port)
- External Caddyfile volume mount

## Fixed docker-compose.yml

```yaml
services:
  nginx-router:
    image: nginx:alpine
    ports:
      - "3080:80"
    configs:
      - source: nginx_config
        target: /etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend
    networks:
      - app-network

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    expose:
      - "8123"
    networks:
      - app-network

  backend:
    image: rybbit/backend:latest
    expose:
      - "3001"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    networks:
      - app-network

  frontend:
    image: rybbit/frontend:latest
    expose:
      - "3002"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    networks:
      - app-network

configs:
  nginx_config:
    content: |
      server {
        listen 80;

        location /api/ {
          proxy_pass http://backend:3001/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
          proxy_pass http://frontend:3002/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
        }
      }

networks:
  app-network:
    driver: bridge
```

## .env.example

```
DATABASE_URL=
NEXT_PUBLIC_API_URL=
```

## xCloud Deploy Steps

1. Push repo to GitHub
2. Server → New Site → Custom Docker → connect repo
3. Exposed port: **3080**
4. Env vars to add: `DATABASE_URL`, `NEXT_PUBLIC_API_URL`
5. Deploy
