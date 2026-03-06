# upstream-recon

A [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) for investigating open-source projects before filing issues, PRs, or comments.

Prevents duplicate issues, wasted PR effort, and uninformed comments by checking existing threads, maintainer sentiment, and merge culture first.

## Install

```bash
npx skills add oss-skills/upstream-recon
```

Or copy manually:
```bash
cp -r . ~/.claude/skills/upstream-recon/
```

## What it does

Activates when you're about to interact with a repo you don't maintain. Uses `gh` CLI to analyze:

- Existing issues and PRs for your topic (duplicate detection)
- Maintainer response patterns and merge velocity
- Rejection patterns and governance style

Ends with a recommendation: `MERGE-LIKELY`, `MERGE-UNLIKELY`, `FILE-ISSUE-FIRST`, `COMMENT-ON-EXISTING`, or `DUPLICATE-EXISTS`.

## License

MIT
