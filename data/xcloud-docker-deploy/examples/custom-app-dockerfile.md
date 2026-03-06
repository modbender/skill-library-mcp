# Example: Custom App with Dockerfile (Scenario A — Build-from-Source)

## Original docker-compose.yml

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: my-app:latest
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=myapp
```

## Issues Detected

- `build: context: .` — xCloud cannot build images
- Database port `5432` exposed to host (security risk)

## Fixed docker-compose.yml

```yaml
services:
  app:
    image: ghcr.io/OWNER/my-app:latest
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:15
    expose:
      - "5432"     # internal only — removed host port binding
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=myapp
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

## .github/workflows/docker-build.yml

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: my-app

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/my-app:latest
            ghcr.io/${{ github.repository_owner }}/my-app:sha-${{ github.sha }}

      - name: Trigger xCloud deploy
        if: ${{ secrets.XCLOUD_DEPLOY_WEBHOOK != '' }}
        run: curl -X POST "${{ secrets.XCLOUD_DEPLOY_WEBHOOK }}"
```

## .env.example

```
SECRET_KEY=
POSTGRES_PASSWORD=
```

## xCloud Deploy Steps

1. Push repo to GitHub — GitHub Actions builds and pushes image automatically
2. Go to GitHub → Packages → make `my-app` package **Public**
3. Add `XCLOUD_DEPLOY_WEBHOOK` secret in GitHub repo settings (from xCloud site → Deploy settings)
4. Server → New Site → Custom Docker → connect repo
5. Exposed port: **8080**
6. Env vars: `SECRET_KEY`, `POSTGRES_PASSWORD`
7. Deploy
