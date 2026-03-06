# openclaw-memory

Memory system for OpenClaw agents. Three components:

- **ALMA** — meta-learning optimizer that evolves memory designs
- **Observer** — extracts structured facts from conversations via LLM (OpenAI/Anthropic/Gemini)
- **Indexer** — full-text search over workspace Markdown files

## Install

```bash
npm install @artale/openclaw-memory
```

## Usage

```typescript
import { ALMAAgent, ObserverAgent, MemoryIndexer } from '@artale/openclaw-memory';

// ALMA: evolve memory designs
const alma = new ALMAAgent({
  constraints: { chunkSize: { min: 100, max: 1000, type: 'number' } }
});
const design = alma.propose();
alma.evaluate(design.id, { accuracy: 0.9, speed: 0.8 });
console.log(alma.best());

// Observer: extract facts (requires LLM API key)
const observer = new ObserverAgent({
  provider: 'anthropic',  // or 'openai' or 'gemini'
  apiKey: process.env.ANTHROPIC_API_KEY,
});
const facts = await observer.extract([
  { role: 'user', content: 'Alice prefers TypeScript over Python' }
]);

// Indexer: search workspace files
const indexer = new MemoryIndexer({ workspace: './my-workspace' });
indexer.index();
const results = indexer.search('TypeScript');
```

## Environment Variables

Observer requires an LLM API key (one of):
- `OPENAI_API_KEY` — for OpenAI provider
- `ANTHROPIC_API_KEY` — for Anthropic provider

ALMA and Indexer work fully offline with zero dependencies.

## OpenClaw Skill

Drop into your workspace to use as a skill:
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/arosstale/openclaw-memory
```

## Architecture

- **5 source files, 578 lines, 0 runtime dependencies**
- In-memory database (no native modules, works everywhere)
- Observer calls remote LLM APIs when configured — not offline
- ALMA and Indexer are fully offline

## License

MIT
