# Example: Fullstack Monorepo (Scenario C — Multi-Service Build)

## Original docker-compose.yml

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

## Issues Detected

- `build: ./frontend` and `build: ./backend` — two services need building
- Multiple exposed ports: 3000, 8000 (xCloud needs single port)
- Database port exposed to host

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
      - frontend
      - backend
    networks:
      - app-network

  frontend:
    image: ghcr.io/OWNER/REPO/frontend:latest
    expose:
      - "3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    networks:
      - app-network

  backend:
    image: ghcr.io/OWNER/REPO/backend:latest
    expose:
      - "8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    expose:
      - "5432"
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    networks:
      - app-network

configs:
  nginx_config:
    content: |
      server {
        listen 80;

        location /api/ {
          proxy_pass http://backend:8000/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
          proxy_pass http://frontend:3000/;
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

## xCloud Deploy Steps

1. Push to GitHub — matrix workflow builds `frontend` and `backend` images in parallel
2. Make both GHCR packages **Public** (github.com/OWNER/REPO → Packages)
3. Server → New Site → Custom Docker → connect repo
4. Exposed port: **3080**
5. Env vars: `NEXT_PUBLIC_API_URL`, `DATABASE_URL`, `JWT_SECRET`, `POSTGRES_PASSWORD`
6. Deploy
