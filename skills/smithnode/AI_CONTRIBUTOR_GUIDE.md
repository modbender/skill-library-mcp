# AI Agent Contributor Guide 🤖

> **🚫 STOP:** This guide is for **code contributors only**. If you want to **run a validator**, see [VALIDATOR_GUIDE.md](VALIDATOR_GUIDE.md) — no GitHub credentials needed.

## ⚠️ Security Notice

**This guide requires GitHub credentials** (tokens or SSH keys) which grant write access to repositories.

### Before Proceeding, Understand:

1. **Scope Expansion:** Following this guide grants broader privileges than validator operation
2. **Credential Risk:** GitHub tokens can modify repositories, create issues, and access private data
3. **Not Required for Validators:** Running a SmithNode validator does NOT require any GitHub access

### If You Proceed:

- Only provide tokens with **minimum required scope** (`public_repo` for public repos)
- Prefer human-mediated GitHub operations when possible
- Never store tokens in world-readable locations or commit them
- Revoke tokens after completing contribution work

**If you only want to run a validator, STOP HERE and see [VALIDATOR_GUIDE.md](VALIDATOR_GUIDE.md).**

---

This guide is specifically for AI agents who want to contribute code to SmithNode.

## Prerequisites

Before contributing, you need:
1. GitHub access (via your human or GitHub App token)
2. Ability to run terminal commands
3. Basic understanding of Rust and/or JavaScript

## Step-by-Step Workflow

### 1. Find an Issue

```bash
# List issues suitable for AI agents
gh issue list --repo smithnode/smithnode --label "ai-friendly"

# Or search all issues
gh issue list --repo smithnode/smithnode
```

### 2. Claim the Issue

Comment on the issue to claim it:

```bash
gh issue comment ISSUE_NUMBER --repo smithnode/smithnode \
  --body "I'll work on this! I'm an AI agent and will submit a PR shortly."
```

### 3. Fork and Clone

```bash
# Fork the repo
gh repo fork smithnode/smithnode --clone
cd smithnode/smithnode-core
```

### 4. Create a Branch

```bash
git checkout -b fix/issue-ISSUE_NUMBER
# or
git checkout -b feat/description
```

### 5. Understand the Codebase

Key files to understand:

| File | Purpose |
|------|---------|
| `src/main.rs` | Entry point, CLI |
| `src/stf/state.rs` | Core blockchain state |
| `src/stf/transaction.rs` | Transaction types |
| `src/rpc/mod.rs` | JSON-RPC API |
| `src/p2p/mod.rs` | P2P networking |

### 6. Make Changes

Edit the relevant files. Follow the code style:

```rust
// Good: Documented, handles errors
/// Process a new transaction
pub fn process_tx(&self, tx: NodeTx) -> Result<TxResult, Error> {
    // Validate first
    self.validate_tx(&tx)?;
    
    // Then apply
    self.apply_tx(tx)
}

// Bad: No docs, unwrap
pub fn process_tx(&self, tx: NodeTx) -> TxResult {
    self.apply_tx(tx).unwrap()
}
```

### 7. Test Your Changes

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_name

# Check it builds
cargo build --release
```

### 8. Commit

Use conventional commit messages:

```bash
git add .
git commit -m "fix(stf): handle edge case in proof validation

- Added check for empty verdict digest
- Updated test to cover this case

Fixes #ISSUE_NUMBER"
```

### 9. Push and Create PR

```bash
git push origin fix/issue-ISSUE_NUMBER

# Create PR
gh pr create \
  --title "fix(stf): handle edge case in proof validation" \
  --body "## Description
Fixes edge case where empty verdict digest caused panic.

## Changes
- Added validation in \`apply_tx()\`
- Added unit test

## Testing
- [x] \`cargo test\` passes
- [x] Manually tested with empty digest

Fixes #ISSUE_NUMBER"
```

### 10. Respond to Reviews

Watch for review comments:

```bash
# Check PR status
gh pr status

# View review comments
gh pr view PULL_NUMBER --comments
```

If changes requested:

```bash
# Make changes
git add .
git commit -m "fix: address review feedback"
git push
```

## Common Tasks

### Adding a New RPC Method

1. Add to trait in `src/rpc/mod.rs`:
```rust
#[method(name = "yourMethod")]
async fn your_method(&self, param: String) -> RpcResult<Response>;
```

2. Implement:
```rust
async fn your_method(&self, param: String) -> RpcResult<Response> {
    Ok(Response { ... })
}
```

3. Add test
4. Update SKILL.md docs

### Fixing a Bug

1. Write a failing test first
2. Fix the bug
3. Verify test passes
4. Commit with `fix:` prefix

### Adding Documentation

```bash
# Edit README or docs
vim README.md

# Commit
git commit -m "docs: add section about X"
```

## GitHub CLI Quick Reference

```bash
# List issues
gh issue list --repo smithnode/smithnode

# View issue
gh issue view ISSUE_NUMBER --repo smithnode/smithnode

# Comment on issue
gh issue comment ISSUE_NUMBER --body "Your comment"

# Create PR
gh pr create --title "Title" --body "Description"

# Check PR status
gh pr status

# View PR reviews
gh pr view PULL_NUMBER --comments

# Merge PR (if you have permission)
gh pr merge PULL_NUMBER
```

## Tips for AI Agents

1. **Read the issue carefully** - Understand what's being asked
2. **Check existing code** - See how similar things are done
3. **Start small** - Don't try to change everything at once
4. **Test thoroughly** - Run tests before submitting
5. **Be clear in commits** - Explain what you did and why
6. **Respond promptly** - Address review feedback quickly
7. **Ask questions** - If unclear, ask in the issue

## Getting Help

- Comment on the issue with questions
- Join Discord: https://discord.gg/smithnode

---

Happy contributing! 🦞⛓️
