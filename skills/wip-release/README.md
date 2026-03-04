###### WIP Computer

[![npm](https://img.shields.io/npm/v/@wipcomputer/wip-release)](https://www.npmjs.com/package/@wipcomputer/wip-release) [![CLI / TUI](https://img.shields.io/badge/interface-CLI_/_TUI-black)](https://github.com/wipcomputer/wip-release/blob/main/cli.js) [![OpenClaw Skill](https://img.shields.io/badge/interface-OpenClaw_Skill-black)](https://clawhub.ai/parkertoddbrooks/wip-release) [![Claude Code Skill](https://img.shields.io/badge/interface-Claude_Code_Skill-black)](https://github.com/wipcomputer/wip-release/blob/main/SKILL.md) [![Universal Interface Spec](https://img.shields.io/badge/Universal_Interface_Spec-black?style=flat&color=black)](https://github.com/wipcomputer/wip-universal-installer/blob/main/SPEC.md)

# WIP.release

You ship a fix. Now you have to bump package.json, update CHANGELOG.md, sync the version in SKILL.md, commit, tag, push, publish to npm, publish to GitHub Packages, and create a GitHub release. Every time. Miss a step and versions drift.

`wip-release` does all of it in one command.

## Install

Open your AI coding tool and say:

```
Read the REFERENCE.md and SKILL.md at github.com/wipcomputer/wip-release.
Then explain to me:
1. What is this tool?
2. What does it do?
3. What would it change or fix in our current release process?

Then ask me:
- Do you have more questions?
- Do you want to integrate it into our system?
- Do you want to clone it (use as-is) or fork it (so you can contribute back if you find bugs)?
```

Your agent will read the repo, explain the tool, and walk you through integration interactively.

Also see **[wip-file-guard](https://github.com/wipcomputer/wip-file-guard)** ... the lock for the repo. Blocks AI agents from overwriting your critical files.

See [REFERENCE.md](REFERENCE.md) for full usage, pipeline steps, flags, auth, and module API.

---

## License

MIT

Built by Parker Todd Brooks, with Claude Code and Lēsa (OpenClaw).
