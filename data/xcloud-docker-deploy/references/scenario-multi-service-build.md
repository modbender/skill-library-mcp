# Scenario C: Multi-Service Build

## Detection

This scenario applies when **two or more services** in `docker-compose.yml` have `build:` directives:

```yaml
services:
  frontend:
    build: ./frontend
  backend:
    build: ./backend
  worker:
    build: ./worker
```

## Solution Overview

Each service needs its own image in GHCR. Use a GitHub Actions **matrix strategy** to build all images in parallel, then reference each in the compose file.

## Step 1 — Assign GHCR Image Names

For each service with `build:`, assign a GHCR image path:

| Service | GHCR Image |
|---------|-----------|
| frontend | `ghcr.io/OWNER/REPO/frontend:latest` |
| backend | `ghcr.io/OWNER/REPO/backend:latest` |
| worker | `ghcr.io/OWNER/REPO/worker:latest` |

## Step 2 — Modified docker-compose.yml

```yaml
services:
  frontend:
    image: ghcr.io/OWNER/REPO/frontend:latest
    # build: removed
    ports:
      - "3080:3000"
    environment:
      - BACKEND_URL=${BACKEND_URL}

  backend:
    image: ghcr.io/OWNER/REPO/backend:latest
    # build: removed
    expose:
      - "8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}

  worker:
    image: ghcr.io/OWNER/REPO/worker:latest
    # build: removed
    environment:
      - REDIS_URL=${REDIS_URL}

  db:
    image: postgres:15-alpine     # ← unchanged, already public image
    expose:
      - "5432"
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

## Step 3 — GitHub Actions Matrix Workflow

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  OWNER: ${{ github.repository_owner }}
  REPO: ${{ github.event.repository.name }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    strategy:
      matrix:
        service: [frontend, backend, worker]
        include:
          - service: frontend
            context: ./frontend
            dockerfile: ./frontend/Dockerfile
          - service: backend
            context: ./backend
            dockerfile: ./backend/Dockerfile
          - service: worker
            context: ./worker
            dockerfile: ./worker/Dockerfile

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push ${{ matrix.service }}
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.context }}
          file: ${{ matrix.dockerfile }}
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.OWNER }}/${{ env.REPO }}/${{ matrix.service }}:latest
            ${{ env.REGISTRY }}/${{ env.OWNER }}/${{ env.REPO }}/${{ matrix.service }}:sha-${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Trigger xCloud deploy
        if: ${{ secrets.XCLOUD_DEPLOY_WEBHOOK != '' }}
        run: |
          curl -X POST "${{ secrets.XCLOUD_DEPLOY_WEBHOOK }}" \
            -H "Content-Type: application/json"
```

## Step 4 — Make GHCR Images Public

After first push, for each image:
1. Go to `github.com/OWNER/REPO` → Packages
2. Find each package → Settings → Change visibility to **Public**

## xCloud Configuration

- **Exposed port:** The single port the frontend/nginx-router exposes (e.g., `3080`)
- All env vars added via xCloud UI
- No special config needed — xCloud pulls all GHCR images on deploy
