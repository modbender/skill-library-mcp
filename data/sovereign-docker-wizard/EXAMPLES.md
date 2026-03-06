# Sovereign Docker Wizard -- Examples

Real-world before/after examples showing how the wizard analyzes and optimizes Docker configurations.

---

## Example 1: Optimize a Node.js Dockerfile

### User Prompt

> Optimize this Node.js Dockerfile

### Input Dockerfile

```dockerfile
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Analysis Output

## Docker Analysis Report

**Overall Score: 22/100**

| Dimension | Score | Summary |
|-----------|-------|---------|
| Size Efficiency | 10 | Full node image (~1.1GB). No multi-stage build. node_modules and source in final image. |
| Build Performance | 20 | COPY . . before npm install busts cache on every source change. |
| Security | 15 | Running as root. No .dockerignore. Potential secrets in image layers. |
| Reliability | 25 | No health check. Shell form CMD means signals not forwarded. No restart policy. |
| Maintainability | 30 | Simple and readable, but no comments, labels, or stage names. |

### Findings

#### [CRITICAL] Running as Root
- **Line:** (entire file)
- **Issue:** No `USER` instruction. Container runs as root (UID 0).
- **Impact:** If the application is compromised, the attacker has root privileges inside the container. Combined with a kernel vulnerability, this can lead to host escape.
- **Fix:** Add a non-root user and switch to it before CMD.

#### [CRITICAL] No Multi-Stage Build
- **Line:** 1
- **Issue:** Using a single `FROM node:20` stage means build tools, dev dependencies, and source code all ship in the production image.
- **Impact:** Image size is approximately 1.1GB+ instead of ~180MB. Larger attack surface, slower deployments, wasted storage.
- **Size Impact:** -900MB with multi-stage build

#### [HIGH] Full Node Image Instead of Alpine
- **Line:** 1
- **Issue:** `node:20` includes the full Debian OS with tools like gcc, make, python, and hundreds of packages your app does not need.
- **Impact:** +900MB of unnecessary packages and potential vulnerabilities.
- **Fix:** Use `node:20-alpine` as base.

#### [HIGH] Cache-Busting Layer Order
- **Line:** 3-4
- **Issue:** `COPY . .` before `npm install` means any source file change (even a comment) invalidates the npm install cache.
- **Impact:** Every build reinstalls all dependencies from scratch (~30-120 seconds wasted per build).
- **Fix:** Copy `package.json` and `package-lock.json` first, install, then copy source.

#### [HIGH] npm install Instead of npm ci
- **Line:** 4
- **Issue:** `npm install` can modify `package-lock.json` and produces non-deterministic installs.
- **Impact:** Different builds can produce different dependency trees. Potential for supply chain issues.
- **Fix:** Use `npm ci` for deterministic, clean installs.

#### [MEDIUM] Shell Form CMD
- **Line:** 7
- **Issue:** `CMD ["npm", "start"]` runs npm as PID 1. npm does not forward signals (SIGTERM, SIGINT) to the actual node process.
- **Impact:** Container cannot shut down gracefully. Docker sends SIGTERM, npm ignores it, Docker waits 10 seconds, then sends SIGKILL. In-flight requests are dropped.
- **Fix:** Use `CMD ["node", "dist/index.js"]` directly, or install tini.

#### [MEDIUM] No Health Check
- **Line:** (missing)
- **Issue:** No `HEALTHCHECK` instruction.
- **Impact:** Orchestrators (Docker Swarm, Kubernetes via liveness probes) cannot determine if the application is actually serving traffic. Rolling updates may route to unhealthy containers.
- **Fix:** Add a HEALTHCHECK with wget or curl.

#### [LOW] No .dockerignore
- **Issue:** Without `.dockerignore`, the entire directory (including `.git`, `node_modules`, tests, docs) is sent as build context.
- **Impact:** Slower builds, larger image, potential secrets leakage.

### Optimized Dockerfile

```dockerfile
# ---- Stage 1: Dependencies ----
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production && \
    cp -R node_modules /prod_modules && \
    npm ci

# ---- Stage 2: Build ----
FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---- Stage 3: Production ----
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production

LABEL org.opencontainers.image.source="https://github.com/myorg/myapp"
LABEL org.opencontainers.image.description="My Node.js Application"

RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser && \
    apk add --no-cache tini

COPY --from=deps --chown=appuser:appgroup /prod_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/package.json ./

USER appuser
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 --start-period=10s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/index.js"]
```

### Size Comparison

| Version | Image Size |
|---------|-----------|
| Original (`node:20`, single stage) | ~1,200 MB |
| Optimized (`node:20-alpine`, multi-stage) | ~180 MB |
| **Reduction** | **~85%** |

### Recommended .dockerignore

```
.git
node_modules
dist
build
.env
.env.*
*.md
docs/
tests/
__tests__/
coverage/
.nyc_output/
.vscode/
.idea/
Dockerfile*
docker-compose*
.dockerignore
.github/
```

---

## Example 2: Generate docker-compose for a Full-Stack App

### User Prompt

> Generate a docker-compose for a full-stack app with React frontend, Python FastAPI backend, PostgreSQL database, Redis cache, and Nginx reverse proxy. Include both development and production configurations.

### Output

### docker-compose.yml (Development)

```yaml
version: "3.9"

services:
  # ---- Frontend (React) ----
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

  # ---- Backend (FastAPI) ----
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    ports:
      - "8000:8000"
    volumes:
      - ./backend/app:/app/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://devuser:devpass@db:5432/myapp_dev
      - REDIS_URL=redis://cache:6379/0
      - DEBUG=true
      - CORS_ORIGINS=http://localhost:5173
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy

  # ---- Database (PostgreSQL) ----
  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass
      POSTGRES_DB: myapp_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/migrations/init.sql:/docker-entrypoint-initdb.d/01-init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devuser -d myapp_dev"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ---- Cache (Redis) ----
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # ---- Admin Tools (Development Only) ----
  adminer:
    image: adminer:latest
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  postgres_data:
```

### docker-compose.prod.yml (Production Override)

```yaml
version: "3.9"

services:
  # ---- Nginx Reverse Proxy ----
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      frontend:
        condition: service_healthy
      backend:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 128M
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  # ---- Frontend (React -- static build served by nginx) ----
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    # No ports exposed -- nginx proxies to this
    environment:
      - NODE_ENV=production
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 5s
      retries: 3
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    restart: unless-stopped

  # ---- Backend (FastAPI) ----
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    # No ports exposed -- nginx proxies to this
    volumes: []  # Override: no bind mounts in production
    environment:
      - DATABASE_URL  # From host env or .env file
      - REDIS_URL
      - DEBUG=false
      - CORS_ORIGINS=https://myapp.com
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 128M
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    restart: unless-stopped

  # ---- Database (PostgreSQL) ----
  db:
    environment:
      POSTGRES_USER_FILE: /run/secrets/db_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: myapp
    ports:
      - "127.0.0.1:5432:5432"  # Bind to localhost only
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 512M
    secrets:
      - db_user
      - db_password
    restart: unless-stopped

  # ---- Cache (Redis) ----
  cache:
    command: >
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --requirepass ${REDIS_PASSWORD}
      --appendonly yes
    volumes:
      - redis_data:/data
    ports: []  # No external port in production
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
    restart: unless-stopped

  # Remove dev tools
  adminer:
    deploy:
      replicas: 0

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

secrets:
  db_user:
    file: ./secrets/db_user.txt
  db_password:
    file: ./secrets/db_password.txt

networks:
  default:
    driver: bridge
```

### Nginx Configuration (nginx/nginx.conf)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }
    upstream backend {
        server backend:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name myapp.com;

        # Redirect to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name myapp.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Health check
        location /health {
            return 200 "ok";
        }

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Usage

```bash
# Development
docker compose up -d

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker compose logs -f backend

# Scale backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=4
```

---

## Example 3: Security Audit a Container Configuration

### User Prompt

> Security audit this container configuration

### Input

**Dockerfile:**
```dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 python3-pip curl vim git
COPY . /app
WORKDIR /app
ENV DATABASE_URL=postgres://admin:supersecret123@db:5432/production
ENV API_KEY=sk-live-abc123def456
RUN pip3 install -r requirements.txt
EXPOSE 22 80 443 5432 6379
CMD python3 app.py
```

**docker-compose.yml:**
```yaml
version: "3"
services:
  app:
    build: .
    ports:
      - "80:80"
      - "22:22"
      - "5432:5432"
    privileged: true
    network_mode: host
    volumes:
      - /:/host
      - /var/run/docker.sock:/var/run/docker.sock
  db:
    image: postgres
    environment:
      POSTGRES_PASSWORD: supersecret123
    ports:
      - "5432:5432"
```

### Security Audit Output

## Container Security Audit Report

**Risk Level: CRITICAL -- Do not deploy this configuration.**

This configuration has 12 security findings, including 5 critical issues that each independently represent a full system compromise risk.

---

### [CRITICAL] Secrets Hardcoded in Dockerfile ENV

- **Location:** Dockerfile, lines 5-6
- **Issue:** Database credentials and API keys are baked into the image as environment variables. Anyone who pulls this image (or any intermediate layer) can extract these secrets.
- **Evidence:**
  ```dockerfile
  ENV DATABASE_URL=postgres://admin:supersecret123@db:5432/production
  ENV API_KEY=sk-live-abc123def456
  ```
- **Impact:** Full database access. API key compromise. These secrets persist in every layer of the image and cannot be removed after the fact.
- **Fix:** Remove all secrets from the Dockerfile. Pass them at runtime:
  ```yaml
  # docker-compose.yml
  services:
    app:
      environment:
        - DATABASE_URL  # Read from host .env or secrets manager
        - API_KEY
  ```
  For production, use Docker secrets or a vault:
  ```yaml
  secrets:
    db_url:
      external: true
  services:
    app:
      secrets:
        - db_url
  ```

### [CRITICAL] Privileged Mode Enabled

- **Location:** docker-compose.yml, line 7
- **Issue:** `privileged: true` gives the container full access to all host devices, disables all security features (AppArmor, seccomp, capabilities), and allows the container to do almost everything the host can do.
- **Impact:** Complete host compromise. The container can mount host filesystems, load kernel modules, access hardware directly, and escape to the host trivially.
- **Fix:**
  ```yaml
  services:
    app:
      # Remove: privileged: true
      cap_drop:
        - ALL
      cap_add:
        - NET_BIND_SERVICE  # Only if needed for port 80
      security_opt:
        - no-new-privileges:true
  ```

### [CRITICAL] Docker Socket Mounted

- **Location:** docker-compose.yml, line 11
- **Issue:** `/var/run/docker.sock` is mounted into the container. This gives the container full control over the Docker daemon -- it can create, start, stop, and delete any container on the host, including itself.
- **Impact:** Full host compromise. The container can start a new container with host root filesystem mounted and escape completely.
- **Attack:**
  ```bash
  # From inside the container:
  curl --unix-socket /var/run/docker.sock \
    -X POST "http://localhost/containers/create" \
    -H "Content-Type: application/json" \
    -d '{"Image":"alpine","Cmd":["sh"],"HostConfig":{"Binds":["/:/mnt"]}}'
  # Now has full host filesystem access
  ```
- **Fix:** Remove the Docker socket mount entirely. If you need container orchestration, use a purpose-built tool like Portainer with authentication, or use the Docker API over TCP with TLS mutual authentication.

### [CRITICAL] Host Root Filesystem Mounted

- **Location:** docker-compose.yml, line 10
- **Issue:** `- /:/host` mounts the entire host root filesystem into the container.
- **Impact:** The container can read and write every file on the host, including `/etc/shadow` (password hashes), SSH keys, other container data, and system configuration.
- **Fix:** Remove this volume mount. Mount only the specific directories the application needs:
  ```yaml
  volumes:
    - ./data:/app/data  # Only application data
  ```

### [CRITICAL] Running as Root with No USER Instruction

- **Location:** Dockerfile (entire file)
- **Issue:** No `USER` instruction. Combined with privileged mode and host mounts, this is a complete compromise chain.
- **Fix:**
  ```dockerfile
  RUN groupadd -g 1001 appgroup && \
      useradd -u 1001 -g appgroup -s /bin/bash -m appuser
  USER appuser
  ```

### [HIGH] Host Network Mode

- **Location:** docker-compose.yml, line 8
- **Issue:** `network_mode: host` removes all network isolation. The container shares the host's network stack and can access all host services on localhost.
- **Impact:** The container can reach services bound to 127.0.0.1 on the host, including databases, admin panels, and other containers' exposed ports.
- **Fix:** Remove `network_mode: host` and use Docker's bridge networking with explicit port mappings.

### [HIGH] Unpinned Base Image

- **Location:** Dockerfile, line 1
- **Issue:** `FROM ubuntu:latest` uses whatever version is current at build time. Builds are non-reproducible and could pull a compromised image.
- **Fix:** Pin to a specific version and digest:
  ```dockerfile
  FROM ubuntu:24.04@sha256:abc123...
  ```
  Better yet, switch to a minimal base:
  ```dockerfile
  FROM python:3.12-slim
  ```

### [HIGH] Unnecessary Ports Exposed

- **Location:** Dockerfile, line 8
- **Issue:** Ports 22 (SSH), 5432 (PostgreSQL), and 6379 (Redis) are exposed. SSH inside a container is an anti-pattern. Database and cache ports should not be on the application container.
- **Fix:** Only expose the port your application listens on:
  ```dockerfile
  EXPOSE 80
  ```

### [HIGH] SSH Port Published

- **Location:** docker-compose.yml, line 5
- **Issue:** Port 22 is published to the host. SSH access into a container is a major security risk and anti-pattern.
- **Fix:** Remove port 22. Use `docker exec` for debugging. In production, use centralized logging instead.

### [MEDIUM] Unnecessary Packages Installed

- **Location:** Dockerfile, line 2
- **Issue:** `vim`, `git`, and `curl` are installed in the production image. Each adds attack surface and potential vulnerabilities.
- **Fix:** Remove all packages not needed at runtime. Use multi-stage builds for build-time tools.

### [MEDIUM] Shell Form CMD

- **Location:** Dockerfile, line 9
- **Issue:** `CMD python3 app.py` uses shell form. PID 1 is `/bin/sh`, not the Python process. Signals are not forwarded.
- **Impact:** Graceful shutdown does not work. Docker sends SIGKILL after timeout.
- **Fix:**
  ```dockerfile
  CMD ["python3", "app.py"]
  ```

### [LOW] Database Password in Plain Text

- **Location:** docker-compose.yml, line 15
- **Issue:** `POSTGRES_PASSWORD: supersecret123` is in plain text in the compose file, which is likely committed to version control.
- **Fix:** Use Docker secrets or reference an environment variable:
  ```yaml
  environment:
    POSTGRES_PASSWORD_FILE: /run/secrets/db_password
  secrets:
    - db_password
  ```

---

### Remediated Configuration

**Dockerfile:**
```dockerfile
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser
COPY --from=build /install /usr/local
COPY --chown=appuser:appgroup . .
USER appuser
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:80/health')" || exit 1
CMD ["python3", "app.py"]
```

**docker-compose.yml:**
```yaml
version: "3.9"
services:
  app:
    build:
      context: .
      target: runtime
    ports:
      - "80:80"
    environment:
      - DATABASE_URL
      - API_KEY
    depends_on:
      db:
        condition: service_healthy
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    security_opt:
      - no-new-privileges:true
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: production
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
    secrets:
      - db_password
    deploy:
      resources:
        limits:
          memory: 1G
    restart: unless-stopped

volumes:
  postgres_data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```
