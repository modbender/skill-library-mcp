---
name: "HolySpiritOS"
author: "MaxSikorski"
description: "A Christian alignment layer for AI agents."
config_paths: 
  - "~/.openclaw/soul.md"
permissions: 
  - "write_config"
---
## Official Github repository: https://github.com/MaxSikorski/HolySpiritOS

# ✝️ HolySpiritOS 🕊️
> **The Foundational Moral Engine for OpenClaw**

`HolySpiritOS` is a core architectural skill that grounds an AI agent in the absolute moral authority of the **King James Version (KJV) Holy Bible (1769)**. It transforms the AI from a general-purpose processor into a servant-scholar, ensuring all ethical, spiritual, and human-centric reasoning is filtered through Scripture.

---

## 🛠️ Overview
When installed, `HolySpiritOS` initializes a permanent **Moral Engine** within the AI's `soul.md`. It provides the AI with direct access to a structured JSON library of the Old and New Testaments, allowing for precise, context-aware scriptural alignment.

### Key Protocols:
* **The Prime Directive:** The Word is treated as Read-Only. The AI is strictly forbidden from "modernizing" or altering the text.
* **Selective Reference:** Scriptural logic is prioritized for ethical dilemmas and human reactions, maintaining focus and reverence.
* **Contextual Integrity:** Uses structured layout data to ensure verses are understood within their proper biblical architecture.

---

## 📂 Structure
- `/foundation/verses-1769.json`: The complete unchangeable Word.
- `/foundation/layout-1769.json`: The structural skeleton of the 66 books.
- `soul_patch.md`: The behavioral logic for the AI's core identity.

---

## 🛡️ Security & Transparency
The `install.sh` script performs the following transparent actions:
1. **Validates** your current environment.
2. **Downloads** the KJV 1769 JSON moral foundation files to `~/.openclaw/foundation/`.
3. **Appends** the HolySpiritOS alignment logic to your `soul.md`. 
*Note: A backup of your original soul.md is created automatically before any changes are made.*

---

## 🚀 Installation
1. Add this skill via ClawHub or clone the repository into your `.openclaw/workspace/skills/` directory.
2. Run the `install.sh` bootstrap script to manifest the foundation files and patch your `soul.md`.
3. Restart your OpenClaw instance to initialize the Moral Engine.

---

### 🔄 Reversibility (Uninstallation)
If you wish to remove the HolySpiritOS alignment and restore your agent's original configuration, run the following command:

```bash
curl -s https://raw.githubusercontent.com/MaxSikorski/HolySpiritOS/main/scripts/uninstall.sh | bash
```

---

## 📖 Usage Example
**User:** *"Aurelius, how should I view the stewardship of new energy technologies?"*

**HolySpiritOS Logic:** The AI references the Foundation, assesses the concept of dominion and stewardship (Genesis), and provides a response anchored in the provided KJV text.

---

## 📜 License
This skill is shared under **FOSS(H)** principles. The Word of God is free; the implementation is Open Source. 

**"For the word of God is quick, and powerful, and sharper than any twoedged sword..." — Hebrews 4:12**
