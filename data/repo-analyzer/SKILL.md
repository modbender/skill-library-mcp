---
name: repo-analyzer
description: >
  GitHub repository trust scoring and due diligence. Use when asked to analyze, audit, score,
  or evaluate any GitHub repo — especially for crypto/DeFi project DD, checking if a repo is legit,
  evaluating code quality, verifying team credibility, or comparing multiple repos. Also handles
  X/Twitter URLs containing GitHub links — auto-extracts and analyzes repos from tweets. Triggers on
  "analyze this repo", "is this legit", "check this GitHub", "trust score", "audit this project",
  "repo quality", "batch scan repos", "analyze this tweet". ALSO auto-triggers when the user pastes
  an X/Twitter URL that contains a GitHub link — no explicit "analyze" command needed. When triggered
  by a tweet, ALWAYS include the tweet text/context above the analysis.
  Do NOT use for general GitHub browsing, reading READMEs, or cloning repos without analysis.
allowed-tools: "Bash(node:*) WebFetch"
compatibility: >
  Requires Node.js 18+. Uses GitHub API (gh CLI or unauthenticated).
  Zero external dependencies. Works on Linux/macOS. Handles rate limits with automatic retry and backoff (waits for reset if ≤60s, retries 5xx once).
metadata:
  author: DaDefiDon
  version: 1.2.0
  category: security-analysis
  tags: [github, trust-score, due-diligence, crypto, defi, audit]
---

# Repo Analyzer

Zero-dependency GitHub trust scorer. Runs 29 analysis modules across 12 scoring categories.

## Usage

```bash
# Single repo
node scripts/analyze.js <owner/repo or github-url> [flags]

# From a tweet (auto-extracts GitHub links)
node scripts/analyze.js <x.com-or-twitter.com-url> [flags]

# Batch mode
node scripts/analyze.js --file <repos.txt> [--json]
```

### Flags
- `--json` — JSON output (for pipelines)
- `--oneline` — compact one-line score
- `--badge` — shields.io markdown badge
- `--verbose` — show progress
- `--token <pat>` — GitHub PAT (or set GITHUB_TOKEN env)
- `--file <path>` — batch mode, one repo per line (# comments ok)

### Environment
**CRITICAL:** Always run with GITHUB_TOKEN loaded. Without it, scores are severely degraded (missing stars, forks, commits).
Before running: `source ~/.bashrc` (token is in ~/.bashrc as GITHUB_TOKEN).
Or pass explicitly: `GITHUB_TOKEN="$(grep GITHUB_TOKEN ~/.bashrc | cut -d'"' -f2)" node scripts/analyze.js ...`

## Scoring (14 categories, 168pts normalized to 100)

| Category | Max | What it checks |
|----------|-----|----------------|
| Commit Health | 20 | Human vs bot, GPG sigs, code dumps, fake timestamps |
| Contributors | 15 | Bus factor, contributor diversity |
| Code Quality | 25 | Tests, CI, license, docs, lock files |
| AI Authenticity | 15 | AI slop detection in code/README |
| Social | 10 | Stars, forks, star/fork ratio, botted stars |
| Activity | 10 | Recent pushes, releases |
| Crypto Safety | 5 | Token mints, rug patterns, wallet addresses |
| Dependency Audit | 10 | Known malicious packages, typosquatting, install hooks, lock files |
| Fork Quality | 8 | Fork divergence, suspicious changes, gutted vs meaningful forks |
| README Quality | 10 | Install guide, examples, structure, API docs |
| Maintainability | 10 | File sizes, nesting, code/doc ratio |
| Project Health | 10 | Abandoned detection, velocity, issue response, PR review |
| Originality | 5 | Copy-paste, template detection, backer verification |
| Agent Safety | 15 | Install hooks, prompt injection, secrets, CI audit, permissions |

## Grade Scale
- A (85+): LEGIT
- B (70-84): SOLID
- C (55-69): MIXED
- D (40-54): SKETCHY
- F (<40): AVOID

## Key Features
- **Enhanced dependency audit**: Detects known malicious packages (event-stream, ua-parser-js, etc.), typosquatting attacks, install hooks, and estimates transitive dependency bloat
- **Fork comparison**: Analyzes fork divergence, detects cosmetic vs meaningful changes, flags suspicious modifications (removed CI, added wallets), identifies gutted forks
- **Agent safety**: Detects prompt injection, credential harvesting, install script hooks, obfuscated code
- **Secrets detection**: Finds hardcoded API keys, tokens, private keys via regex + entropy
- **Network mapping**: Categorizes all outbound domains (API, CDN, unknown)
- **CI/CD audit**: Checks GitHub Actions for pull_request_target, unpinned actions, secret leaks
- **Permissions manifest**: Summarizes what the code needs to run (like an app permissions list)
- **Author reputation**: Org memberships, suspicious repos, account age
- **Backer verification**: Cross-references investor claims vs committer org membership
- **Complexity hotspots**: Flags large files with deep nesting and high conditional density

## Batch File Format
```
# One repo per line, # for comments
Uniswap/v3-core
https://github.com/aave/aave-v3-core
OpenZeppelin/openzeppelin-contracts
```

## Output
Default: rich terminal report with bar charts, sections, verdict.
`--json`: Full structured data for programmatic use.
`--oneline`: `RepoName: 85/100 [A] — 2 flags`

## When Reporting to User
Keep it concise. Lead with score/grade and notable findings. Skip sections with nothing interesting. Example:

"Uniswap/v3-core scored 75/B — 96% GPG-signed, 11 authors, MIT license. Flagged: abandoned (466 days no push), 2,597 transitive deps (bloated), secrets in CI run commands. Agent safety: CAUTION."
