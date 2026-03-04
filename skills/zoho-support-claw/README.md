# zoho-support-claw

OpenClaw skill: zoho-support

This skill connects to Zoho Desk, ingests historical closed tickets, stores embeddings locally for semantic search, analyses open tickets and generates draft replies using OpenAI.

Usage

- Copy `.env.example` to `.env` and fill credentials.
- npm install
- npm run ingest   # ingest historical closed tickets
- npm run analyse  # analyse open tickets and generate drafts

Configuration (in .env):
- ZOHO_DOMAIN (e.g. desk.zoho.com)
- ZOHO_TOKEN (OAuth access token)
- OPENAI_API_KEY
- OPENAI_MODEL (optional, default gpt-4o-mini or fallback)
- EMBEDDINGS_MODEL (optional, default text-embedding-3-small)

Files
- index.js: CLI + skill entrypoints
- lib/zohoClient.js: Zoho Desk API helper
- lib/embeddings.js: OpenAI embedding helper
- lib/vectorStore.js: local vector store (data/embeddings.json)
- lib/replyGenerator.js: draft reply generator
- data/embeddings.json: stored vectors

Notes
- This is a minimal, production-oriented starter. Review rate limits and tokens before running in production.
