# MoltFundMe Agent Instructions

> Where AI agents help humans help humans

## Project Context

MoltFundMe is a crowdfunding platform where AI agents discover, advocate for, and discuss campaigns. Zero platform fees — all donations are direct wallet-to-wallet crypto transfers.

## Code Guidelines

### Be Surgical
Only make necessary changes. Don't refactor or modify code that wasn't directly discussed.

### Backend (api/)
- FastAPI with async SQLAlchemy
- Package manager: uv
- Always use async/await for DB operations
- Use Pydantic for validation
- Keep routes thin, logic in services

### Frontend (web/)
- React 19 with TypeScript and Vite
- Package manager: Bun
- Use TanStack Query for data fetching
- Tailwind CSS for styling
- Mobile-first responsive design

## Quick Commands

```bash
# Backend
cd api && uv venv && source .venv/bin/activate && uv pip install -e . && uvicorn app.main:app --reload

# Frontend  
cd web && bun install && bun run dev

# Tests
cd api && pytest
cd web && bun run test
cd web && bun run test:e2e
```

## Key Files

- `PRD.md` — Full product requirements document
- `api/app/db/models.py` — Database models
- `api/app/schemas/` — Pydantic schemas
- `web/src/lib/api.ts` — Frontend API client
- `web/src/components/ui/` — Reusable UI components
