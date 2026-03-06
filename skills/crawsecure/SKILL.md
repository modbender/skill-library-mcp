---
name: CrawSecure
description: CrawSecure is a documentation-first security skill for the ClawHub
  / OpenClaw ecosystem.
---

# CrawSecure

CrawSecure is a **documentation-first security skill** for the ClawHub / OpenClaw ecosystem.

This skill **does not include executable code or binaries**. Its purpose is to clearly document, explain, and guide the safe usage of the **CrawSecure CLI**, which is distributed and installed **separately** by the user.

The goal of this skill is to promote **security awareness, transparency, and best practices** when working with third‑party skills.

---

## 🔍 What this skill provides

- Clear documentation of what CrawSecure analyzes
- Explanation of risk signals and classifications
- Guidance on how to use the CrawSecure CLI safely
- Security philosophy and trust boundaries

> ℹ️ This skill itself performs **no scans** and **executes no code**.

---

## 🧰 About the CrawSecure CLI

The CrawSecure CLI is an **external, optional tool** that users may install independently.

It performs **local, offline static analysis** of ClawHub / OpenClaw skills **before installation or trust**.

### CLI distribution (external)

- Source & releases: https://github.com/diogopaesdev/crawsecure
- Official website: https://crawsecure.com

The CLI is **not bundled** with this skill.

---

## 🚨 Risk signals analyzed by the CLI

When used, the CrawSecure CLI may detect:

- Dangerous command patterns  
  (e.g. destructive or execution‑related behavior)
- References to sensitive files or credentials  
  (e.g. `.env`, `.ssh`, private keys)
- Indicators of unsafe or misleading practices

Risk levels are classified as:

- **SAFE**
- **MEDIUM**
- **HIGH**

---

## 🔒 Security & trust boundaries

This skill:
- Does **not** execute code
- Does **not** install software
- Does **not** access the network
- Does **not** modify files
- Requests **read‑only** permissions only

Any actual scanning happens **only if** the user installs and runs the CrawSecure CLI from a trusted source.

---

## ✅ When to use this skill

- To understand what CrawSecure checks and why
- Before deciding to install or run the CrawSecure CLI
- As a reference for safer skill development practices
- To promote transparency inside the ClawHub ecosystem

---

## 📦 Version

**v2.0.1** – Documentation‑only clarification release

This version clarifies scope and removes any ambiguity about bundled execution.
