---
name: grepwrapper
description: Search exact code matches across public GitHub repos using grep.app via the grepwrapper CLI.
metadata: {"openclaw":{"emoji":"🔎","requires":{"bins":["grepwrapper"],"env":[]},"install":[{"id":"npm","kind":"node","package":"git+https://github.com/riprsa/grepwrapper.git","bins":["grepwrapper"],"label":"Install grepwrapper CLI"}]}}
---

# grepwrapper

Use this skill when the user asks to:
- find exact code matches on GitHub
- locate repo/file/path occurrences for a snippet
- run grep.app code search from CLI

## Install

```bash
npm i -g git+https://github.com/riprsa/grepwrapper.git
```

## Standard usage

```bash
grepwrapper search --q "PendingBalanceAt(ctx context.Context, account common.Address) (*big.Int, error)"
```

Options:
- `--q <query>` required
- `--case` case-sensitive
- `--words` whole-word (mutually exclusive with `--regexp`)
- `--regexp` regex mode (mutually exclusive with `--words`)
- `--page <n>` page number

Examples:

```bash
grepwrapper search --q "QMD" --case --regexp
grepwrapper search --q "QMD" --case --words --page 2
```

## Expected output

CLI returns summary lines:
- `time=<ms> total=<n> returned=<n>`
- one line per hit: `- <repo>:<path> (matches=<count>)`

## Agent behavior

- Return top matches with direct GitHub links when possible.
- If many matches exist, summarize and ask whether user wants next page / narrower filters.
- Prefer exact query first, then widen with `--regexp` only when needed.
