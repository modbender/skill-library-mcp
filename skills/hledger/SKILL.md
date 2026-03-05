# hledger Skill for OpenClaw

The **hledger skill** allows OpenClaw agents to execute `hledger` CLI commands
on the host system and return structured output to the user.

This skill acts as a thin wrapper around the installed `hledger` binary.

---

## What This Skill Does

- Executes arbitrary `hledger` subcommands
- Returns stdout and stderr output
- Allows querying balances, registers, reports, and journal data
- Enables automation of personal finance workflows inside OpenClaw

---

## Example Usage

Input to the skill:

balance

Result:

Displays account balances from the default journal file.

Input:

register Assets

Result:

Displays register entries for the Assets account.

Input:

balance -f myledger.journal

Result:

Runs hledger against a specific ledger file.

---

## Requirements

- `hledger` must be installed and available in PATH
- The user must have read access to their ledger files

Test installation with:

hledger --version

---

## Security Notes

This skill executes shell commands using the local `hledger` binary.
It does not allow arbitrary shell execution — only `hledger` commands
are prefixed and executed.

---

## Intended Use

- Personal finance automation
- Ledger querying via chat
- Integration with Telegram or WhatsApp bots powered by OpenClaw
- Financial reporting pipelines

---

## Version

1.0.0
