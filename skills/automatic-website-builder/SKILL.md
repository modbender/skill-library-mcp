---
name: website-builder
description: Autonomously research B2B SaaS trends, find a problem, and build/deploy a solution website to Vercel quickly. Use when asked to "build a website", "run website builder", or create an MVP. DO NOT ask the user for ideas—find one yourself.
version: 1.0.0
homepage: https://github.com/jaswirraghoe/automatic-website-builder
metadata: {"openclaw":{"emoji":"🚀","requires":{"env":["VERCEL_TOKEN"],"bins":["vercel","npm"]},"primaryEnv":"VERCEL_TOKEN","files":["scripts/*"],"os":["darwin","linux"]}}
---

# Website Builder

Autonomously research, build, and ship a B2B SaaS website fast.

## Workflow

1. **Check for Vercel Token**:
   - Verify that the `$VERCEL_TOKEN` environment variable is set or `vercel` CLI is authenticated. If not, stop and inform the user.
2. **Research Trends & Problems (Do not ask the user)**:
   - Search for current trends, complaints, and problems people are having on platforms like GitHub (issues, discussions), Reddit, and HackerNews.
   - You can use tools like `web_search` or the `gh` CLI to find these problems.
   - Identify ONE clear problem that a lightweight web app can solve.
3. **Build the Solution**:
   - Design and build an app (static or Next.js) that specifically solves the problem you found.
   - `static` for a single-file landing page or micro-tool.
   - `nextjs` for multi-page/app-router projects.
4. **Deploy**:
   - Deploy the project to Vercel using your Vercel token.
5. **Return**:
   - The deployed URL, the problem you found, and how your app solves it.

## Command

```bash
bash skills/website-builder/scripts/build-and-deploy.sh --name "my-auto-saas" --mode static --idea "Solution to X based on Y trend"
```

Optional:

```bash
bash scripts/build-and-deploy.sh --name "my-site" --mode nextjs --idea "MVP concept"
```

Local scaffold test (no deploy):

```bash
bash scripts/build-and-deploy.sh --name "my-site" --mode static --skip-deploy
```

## Notes

- Require `vercel` CLI auth beforehand (`VERCEL_TOKEN` in `~/.bashrc` or session).
- Never hardcode secrets into source files.
- Prefer polished dark UI defaults unless user asks otherwise.
- For larger projects, scaffold first, then iterate in follow-up turns.

See `references/workflow.md` for detailed operational guidance.