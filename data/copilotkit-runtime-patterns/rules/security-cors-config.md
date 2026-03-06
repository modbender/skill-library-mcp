---
title: Configure CORS for Specific Origins
impact: HIGH
impactDescription: wildcard CORS exposes your LLM endpoint to any website
tags: security, CORS, origins, production
---

## Configure CORS for Specific Origins

Never use wildcard (`*`) CORS in production. Specify the exact frontend origin(s) that should be allowed to access your CopilotKit runtime. Wildcard CORS lets any website send requests to your endpoint, potentially abusing your LLM quota.

**Incorrect (wildcard CORS, open to abuse):**

```typescript
app.use(cors({ origin: "*" }))
```

**Correct (specific origin in production):**

```typescript
const allowedOrigins = process.env.NODE_ENV === "production"
  ? [process.env.FRONTEND_URL!]
  : ["http://localhost:3000", "http://localhost:5173"]

app.use(cors({ origin: allowedOrigins }))
```

Reference: [Security](https://docs.copilotkit.ai/guides/security)
