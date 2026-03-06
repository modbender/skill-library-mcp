---
name: vibe-ship
description: Ship a complete web app from idea to public deployment in one session. Use when user says "build me an app", "ship this idea", "vibe code", "quick ship", "deploy this", or describes any consumer app, tool, or website they want built and deployed. Handles validation, tech stack selection, building, testing, and deployment to Vercel or GitHub Pages.
---

# Vibe Ship

Ship a working, deployed web app from a single idea in one session. No planning paralysis. No localhost. Public URL or it didn't happen.

## Workflow

### Step 1: Validate (2 minutes max)

Before writing any code, answer these four questions:

1. **Can you explain the value in one sentence?** If not, the idea isn't clear enough — ask user to clarify.
2. **Does the core mechanism work?** Is this technically feasible with available tools (no paid APIs unless user has keys)?
3. **Who would use this?** Be specific. "Everyone" is not an answer.
4. **What's the fatal flaw?** Actively try to kill the idea. If you can't, proceed.

If any answer is weak, tell the user and suggest a pivot. Don't build on broken concepts.

### Step 2: Choose Stack

**Default stack (90% of apps):**
- Next.js 14+ (App Router)
- Tailwind CSS
- TypeScript
- Deploy to Vercel

**When to deviate:**
- Static site / no backend needed → plain HTML/CSS/JS → GitHub Pages
- Needs database → add Supabase (free tier)
- Needs auth → add NextAuth or Clerk
- Needs AI → use local inference or user-provided API keys (never hardcode keys)

**Never use:**
- Create React App (dead)
- Webpack configs from scratch
- Complex state management for simple apps (no Redux for a landing page)

### Step 3: Build (iterative)

**Iteration 1 — Core functionality:**
```
1. Initialize project: npx create-next-app@latest [name] --typescript --tailwind --app --src-dir
2. Build the ONE core feature that makes this app valuable
3. Test it locally: npm run dev
4. Verify it actually works in the browser
```

**Iteration 2 — Make it look good:**
```
1. Dark mode by default (users expect it)
2. Mobile responsive (test at 375px width)
3. Loading states, empty states, error states
4. Micro-interactions (hover effects, transitions)
5. No default Tailwind look — intentional design choices
```

**Iteration 3 — Harden:**
```
1. Error handling on all external calls
2. Input validation
3. Environment variables for any secrets (never hardcode)
4. Meta tags: title, description, og:image
5. Favicon
```

### Step 4: Deploy

**Vercel (preferred):**
```bash
# If Vercel CLI available:
cd [project-dir]
vercel --yes --prod

# If not, push to GitHub and connect:
git init && git add . && git commit -m "Ship it"
gh repo create [name] --public --push
# Then deploy via Vercel dashboard or CLI
```

**GitHub Pages (static sites only):**
```bash
git init && git add . && git commit -m "Ship it"
gh repo create [name] --public --push
# Enable Pages in repo settings → deploy from main branch
```

**After deployment:**
1. Verify the public URL loads correctly
2. Test on mobile (responsive check)
3. Test core functionality end-to-end
4. Share the URL with user

### Step 5: Post-ship

1. Commit all code with meaningful message
2. Add README.md with: what it is, how it works, tech stack, live URL
3. Report to user: live URL + what was built + any known limitations

## Quality Checklist

Before declaring "shipped," verify ALL of these:

- [ ] Public URL accessible (not localhost)
- [ ] Core feature works end-to-end
- [ ] Looks intentional on desktop AND mobile
- [ ] No console errors
- [ ] No hardcoded secrets
- [ ] Has proper page title and description
- [ ] Error states handled (what happens when things break?)
- [ ] Loading states present (no blank screens while fetching)

## Anti-Patterns (Don't Do These)

- **Over-engineering**: Don't add auth, database, analytics for an MVP. Ship the core value.
- **Default Tailwind**: If it looks like every other Tailwind site, redesign it. Add personality.
- **Localhost shipping**: "It works on my machine" is not shipped. Deploy it.
- **Feature creep**: The user asked for one thing. Build that. Suggest extras AFTER it's live.
- **Asking permission at every step**: Make decisions. Ship. Get feedback on the live thing.

## Speed Targets

| App Complexity | Target Time | Example |
|----------------|-------------|---------|
| Landing page | 30 min | Product waitlist page |
| Single-feature tool | 1-2 hours | Color palette generator, calculator |
| Multi-page app | 2-4 hours | Dashboard, content tool |
| Full product | 4-8 hours | SaaS MVP with auth + database |

## Common Patterns

**API route pattern (Next.js):**
```typescript
// src/app/api/[endpoint]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    // ... logic
    return NextResponse.json({ success: true, data: result });
  } catch (error) {
    return NextResponse.json({ error: 'Something went wrong' }, { status: 500 });
  }
}
```

**Dark mode base (globals.css):**
```css
:root {
  --background: #0a0a0a;
  --foreground: #ededed;
}
body {
  background: var(--background);
  color: var(--foreground);
}
```

**Responsive grid:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>
```
