# Deployment — NextJS

## Build & Output

```bash
# Production build
npm run build

# Output modes in next.config.js
module.exports = {
  output: 'standalone',  // Self-contained Node.js server
  // output: 'export',   // Static HTML export (no server features)
}
```

## Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Production deploy
vercel --prod
```

**vercel.json:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "DATABASE_URL": "@database-url"
  }
}
```

## Standalone Output

```javascript
// next.config.js
module.exports = {
  output: 'standalone',
}
```

```bash
# Build
npm run build

# Copy static files (REQUIRED)
cp -r .next/static .next/standalone/.next/static
cp -r public .next/standalone/public

# Run
node .next/standalone/server.js
# Listens on port 3000
```

## Docker

**Dockerfile:**
```dockerfile
FROM node:20-alpine AS base

# Dependencies
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Build
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Production
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

**.dockerignore:**
```
node_modules
.next
.git
*.md
```

```bash
# Build
docker build -t nextjs-app .

# Run
docker run -p 3000:3000 nextjs-app
```

## Docker Compose

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb

volumes:
  postgres_data:
```

## Environment Variables

```bash
# .env.local (development, gitignored)
DATABASE_URL=postgresql://localhost:5432/mydb
NEXTAUTH_SECRET=your-secret

# .env.production (production defaults, committed)
NEXT_PUBLIC_SITE_URL=https://example.com

# Runtime env (override at deploy)
DATABASE_URL=postgresql://prod:5432/mydb
```

**Loading order:**
1. `.env.local` (not in test)
2. `.env.[environment].local`
3. `.env.[environment]`
4. `.env`

**Access:**
```typescript
// Server only (no prefix)
process.env.DATABASE_URL

// Client + Server (with prefix)
process.env.NEXT_PUBLIC_SITE_URL
```

## Static Export

```javascript
// next.config.js
module.exports = {
  output: 'export',
  // Optional: custom output directory
  distDir: 'dist',
  // Optional: trailing slashes
  trailingSlash: true,
}
```

**Limitations:**
- No Server Components (all become static)
- No API Routes
- No ISR/Revalidation
- No Middleware
- No Image Optimization (use external loader)

```bash
npm run build
# Output in /out folder
# Deploy to any static host (Netlify, GitHub Pages, S3)
```

## Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/nextjs
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## PM2 Process Manager

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'nextjs-app',
    script: '.next/standalone/server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000,
    },
  }],
}
```

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Health Checks

```typescript
// app/api/health/route.ts
export async function GET() {
  try {
    // Check database
    await db.$queryRaw`SELECT 1`
    
    return Response.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    return Response.json(
      { status: 'unhealthy', error: error.message },
      { status: 503 }
    )
  }
}
```

## Performance

```javascript
// next.config.js
module.exports = {
  // Compress responses
  compress: true,
  
  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60 * 60 * 24 * 365, // 1 year
  },
  
  // Bundle analyzer
  webpack: (config, { isServer }) => {
    if (process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          reportFilename: isServer ? 'server.html' : 'client.html',
        })
      )
    }
    return config
  },
}
```

## Monitoring

```typescript
// instrumentation.ts (Next.js 15)
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    // OpenTelemetry, Sentry, etc.
    await import('./sentry.server.config')
  }
}

// sentry.server.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
})
```

## CI/CD Example (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      
      - run: npm ci
      - run: npm run build
      - run: npm test
      
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```
