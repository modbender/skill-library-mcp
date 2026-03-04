###### WIP Computer

[![npm](https://img.shields.io/npm/v/@wipcomputer/universal-installer)](https://www.npmjs.com/package/@wipcomputer/universal-installer) [![CLI / TUI](https://img.shields.io/badge/interface-CLI_/_TUI-black)](https://github.com/wipcomputer/wip-universal-installer/blob/main/install.js) [![OpenClaw Skill](https://img.shields.io/badge/interface-OpenClaw_Skill-black)](https://clawhub.ai/parkertoddbrooks/wip-universal-installer) [![Claude Code Skill](https://img.shields.io/badge/interface-Claude_Code_Skill-black)](https://github.com/wipcomputer/wip-universal-installer/blob/main/SKILL.md) [![Universal Interface Spec](https://img.shields.io/badge/Universal_Interface_Spec-black?style=flat&color=black)](https://github.com/wipcomputer/wip-universal-installer/blob/main/SPEC.md)

# Universal Installer

Here's how to build software in 2026.

## The Problem

Most software is built for humans. GUIs, dashboards, web apps. Humans click buttons, fill forms, read screens.

But the users are changing. AI agents are the new users. They don't click. They call functions. They read instructions. They compose tools. They need a **universal interface** ... multiple ways into the same logic, native to however the consumer works.

Software built for humans doesn't work for agents. And software built only for agents doesn't work for humans. You need both.

`wip-universal-installer` gives all your repos the Universal Interface, and teaches your AI how to do it too.

## The Karpathy Argument

Andrej Karpathy put it clearly:

> "I think the app store, the move to mobile, the concept of an app ... is an increasingly outdated concept. What matters are sensors and actuators. Sensors are things that convert physical state into digital state. Actuators are things that convert digital intent into physical change."
>
> "All LLMs care about are tools and the tools fall into this sensor/actuator divide. Software shouldn't be built into apps, but into small bespoke tools. Apps are for people. Tools are for LLMs, and increasingly, LLMs are the ones using software."

[Source](https://x.com/karpathy/status/2024583544157458452)

This is the future of software. Not apps. Tools. Sensors and actuators that agents compose together.

## Install

Open your AI coding tool and say:

```
Read the SPEC.md and SKILL.md at github.com/wipcomputer/wip-universal-installer.
Then explain to me:
1. What is this tool?
2. What does it do?
3. What would it change or fix in our current system?

Then ask me:
- Do you have more questions?
- Do you want to integrate it into our system?
- Do you want to clone it (use as-is) or fork it (so you can contribute back if you find bugs)?
```

Your agent will read the repo, explain the tool, and walk you through integration interactively.

Also see **[wip-release](https://github.com/wipcomputer/wip-release)** ... one-command release pipeline for agent-native software.

Also see **[wip-file-guard](https://github.com/wipcomputer/wip-file-guard)** ... the lock for the repo. Blocks AI agents from overwriting your critical files.

See [REFERENCE.md](REFERENCE.md) for sensors/actuators, the interface table, how to build it, the installer, and real examples.

---

## License

MIT

Built by Parker Todd Brooks, with Claude Code and Lēsa (OpenClaw).
