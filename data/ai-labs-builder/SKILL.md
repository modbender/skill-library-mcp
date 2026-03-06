---
name: ai-labs-builder
description: AI Labs Builder - Create modern websites, AI applications, dashboards, and automated workflows. Unified system for building production-ready projects with Next.js, TypeScript, Tailwind, shadcn/ui, and MCP integration. Use when creating new projects, building AI features, designing dashboards, or automating workflows. Triggers include "create website", "build ai app", "make dashboard", "setup workflow", or any project creation requests.
version: "1.0.0"
user-invocable: true
triggers:
  - ai labs
  - create website
  - build ai app
  - make dashboard
  - setup workflow
  - create project
  - build application
  - ai agent
  - chat interface
  - dashboard
  - automation
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Node
metadata:
  clawdbot:
    emoji: "🚀"
    config:
      stateDirs: [".ailabs"]
---

# AI Labs Builder

Unified system for creating modern websites, AI applications, dashboards, and workflows.

## Quick Start

```bash
# Create a website
ailabs create website my-portfolio --type portfolio

# Create an AI app
ailabs create ai-app my-chatbot --type chat

# Create a dashboard
ailabs create dashboard my-analytics --type analytics

# Create a workflow
ailabs create workflow my-automation --template automation

# Deploy
ailabs deploy my-project --platform vercel
```

## Commands

### Website Creation

```bash
ailabs create website <name> [options]

Options:
  --type <type>      portfolio | saas | blog | ecommerce
  --style <style>    modern | glassmorphism | brutalism | minimal
  --components       Include shadcn/ui components
  --animations       Include Framer Motion animations
  --seo              Include SEO optimization
```

### AI Application

```bash
ailabs create ai-app <name> [options]

Options:
  --type <type>      chat | agent | rag | multimodal
  --provider         openai | claude | gemini | local
  --streaming        Enable streaming responses
  --memory           Enable conversation memory
  --tools            Enable tool calling
```

### Dashboard

```bash
ailabs create dashboard <name> [options]

Options:
  --type <type>      analytics | admin | personal | monitoring
  --widgets          Include widget system
  --realtime         Enable real-time updates
  --charts           Include chart components
```

### Workflow

```bash
ailabs create workflow <name> [options]

Options:
  --template         automation | integration | pipeline
  --mcp              Include MCP server setup
  --schedule         Add cron scheduling
  --webhook          Add webhook triggers
```

## Project Types

### 1. Websites

**Portfolio**
- Hero section with animations
- Projects showcase
- Skills/Experience timeline
- Contact form
- Blog integration

**SaaS Landing**
- Feature highlights
- Pricing tables
- Testimonials
- CTA sections
- FAQ accordion

**Blog**
- MDX support
- Tag/categories
- Search functionality
- RSS feed
- Newsletter signup

### 2. AI Applications

**Chat Interface**
- Message history
- Streaming responses
- Code syntax highlighting
- File attachments
- Voice input/output

**AI Agent**
- Autonomous task execution
- Tool calling
- Memory management
- Multi-step reasoning
- Human-in-the-loop

**RAG System**
- Document ingestion
- Vector database
- Semantic search
- Source citations
- Context management

### 3. Dashboards

**Analytics**
- KPI cards
- Charts (line, bar, pie)
- Date range picker
- Export functionality
- Real-time updates

**Admin Panel**
- User management
- Role-based access
- CRUD operations
- Audit logs
- Settings panel

**Personal Dashboard**
- Weather widget
- Calendar integration
- Task management
- Notes/quick capture
- Bookmarks

### 4. Workflows

**Automation**
- Scheduled tasks
- Email notifications
- Data processing
- Report generation

**Integration**
- API connections
- Webhook handling
- Data sync
- Event triggers

**Pipeline**
- CI/CD automation
- Testing workflows
- Deployment pipelines
- Quality checks

## Design System

### Colors

```css
/* Modern */
--primary: #6366f1;
--secondary: #8b5cf6;
--accent: #ec4899;

/* Glassmorphism */
--glass-bg: rgba(255, 255, 255, 0.05);
--glass-border: rgba(255, 255, 255, 0.1);
--glass-blur: blur(20px);

/* Brutalism */
--brutal-black: #000;
--brutal-white: #fff;
--brutal-accent: #ff00ff;
```

### Typography

- **Headings**: Inter, Geist, or JetBrains Mono
- **Body**: Inter or system-ui
- **Code**: JetBrains Mono or Fira Code

### Components

All projects include:
- Button variants (primary, secondary, ghost, outline)
- Cards (default, hover, glass)
- Forms (input, textarea, select, checkbox, radio)
- Navigation (header, sidebar, breadcrumbs)
- Feedback (toast, alert, modal, tooltip)
- Data (table, pagination, tabs)

## AI Integration

### OpenAI

```typescript
import { OpenAI } from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Streaming chat
const stream = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: prompt }],
  stream: true,
});
```

### Claude

```typescript
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const message = await anthropic.messages.create({
  model: 'claude-3-opus-20240229',
  max_tokens: 1024,
  messages: [{ role: 'user', content: prompt }],
});
```

### Vector Database (Pinecone/Memory)

```typescript
import { Pinecone } from '@pinecone-database/pinecone';

const pc = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY,
});

// Store embeddings
await index.upsert([{
  id: '1',
  values: embedding,
  metadata: { text: content }
}]);
```

## Deployment

### Vercel (Recommended)

```bash
ailabs deploy my-project --platform vercel
```

Features:
- Automatic Git integration
- Preview deployments
- Edge functions
- Analytics

### Netlify

```bash
ailabs deploy my-project --platform netlify
```

Features:
- Git-based deployment
- Branch previews
- Form handling
- Edge functions

### GitHub Pages

```bash
ailabs deploy my-project --platform github
```

Features:
- Free hosting
- Custom domains
- Jekyll support
- Actions integration

## Best Practices

### Performance
- Use Next.js Image component
- Implement lazy loading
- Optimize fonts with next/font
- Use React Server Components

### SEO
- Meta tags with next/head
- Sitemap generation
- robots.txt
- Structured data

### Security
- Environment variables
- Input validation
- CSRF protection
- Content Security Policy

### Accessibility
- ARIA labels
- Keyboard navigation
- Color contrast
- Screen reader support

## Examples

### Create a Portfolio

```bash
ailabs create website portfolio \
  --type portfolio \
  --style glassmorphism \
  --components \
  --animations \
  --seo
```

### Create an AI Chatbot

```bash
ailabs create ai-app chatbot \
  --type chat \
  --provider openai \
  --streaming \
  --memory
```

### Create an Analytics Dashboard

```bash
ailabs create dashboard analytics \
  --type analytics \
  --widgets \
  --realtime \
  --charts
```

### Create an Automation Workflow

```bash
ailabs create workflow daily-report \
  --template automation \
  --mcp \
  --schedule "0 9 * * *"
```

## Integration with Other Skills

- **mcp-workflow**: For advanced workflow automation
- **gcc-context**: For version controlling project context
- **agent-reflect**: For continuous improvement

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [OpenAI API](https://platform.openai.com/docs)
- [MCP Specification](https://modelcontextprotocol.io/)
