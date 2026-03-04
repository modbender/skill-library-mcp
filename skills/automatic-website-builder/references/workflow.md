# Website Builder Reference Workflow

## Goal
Ship small useful websites quickly with good defaults and minimal friction.

## Decision Rules

- Use `static` when:
  - single landing page,
  - waitlist page,
  - simple utility with no backend.

- Use `nextjs` when:
  - multiple routes,
  - likely follow-up feature work,
  - potential API routes / server components.

## Output Checklist

Always return:

1. Live URL
2. Folder path
3. One-liner on what was built
4. Next edit command (example):
   - `cd <folder> && code .`

## Safety

- Never embed tokens in HTML/JS.
- Confirm before destructive file cleanup.
- Keep dependencies minimal for faster deploys.
