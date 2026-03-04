# Bun + TypeScript Backend Architecture

## Bun Project Structure

```
my-bun-app/
├── src/
│   ├── routes/        # API routes
│   ├── services/      # Business logic
│   ├── middleware/    # Express-style middleware
│   ├── db/           # Database clients
│   └── index.ts      # Entry point
├── tests/
├── package.json
└── tsconfig.json
```

## TypeScript Config

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "skipLibCheck": true,
    "esModuleInterop": true
  }
}
```

## Bun HTTP Server

```typescript
// src/index.ts
const server = Bun.serve({
  port: 3000,
  fetch(req) {
    const url = new URL(req.url)
    
    if (url.pathname === '/users' && req.method === 'GET') {
      return Response.json({ users: [] })
    }
    
    return new Response('Not Found', { status: 404 })
  },
})

console.log(`Server running on port ${server.port}`)
```

## Database with Bun

```typescript
// Using Bun's built-in SQL client
const db = new Database('sqlite.db')

const users = db.query('SELECT * FROM users WHERE id = ?').get(userId)
```

## Checklist

- [ ] Install Bun
- [ ] Set up TypeScript
- [ ] Configure strict mode
- [ ] Set up routing
- [ ] Add database client
- [ ] Configure build output
- [ ] Set up testing
