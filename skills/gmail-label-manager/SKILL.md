---
name: Gmail Label Manager Skill
description: This skill automates the organization of unread Gmail messages by
  applying labels, removing unnecessary labels, and archiving emails, based on
  predefined patterns from archived emails.
---

# Gmail Label Manager Skill

This skill automates the organization of unread Gmail messages by applying labels, removing unnecessary labels, and archiving emails, based on predefined patterns from **archived emails**.

## Features

1. **Automated Workflow Steps:**
    - Finds the first unread email.
    - Identifies the appropriate label using:
        - Dynamic analysis of labels on archived emails from the same sender.
        - Ignores labels from emails still in the inbox.
    - Adds the determined label(s) to the unread email.
    - Removes irrelevant label(s) from the email. Also remove irrelevant CATEGORY labels (`CATEGORY_PERSONAL`, `CATEGORY_PROMOTIONS`, `CATEGORY_UPDATES`, `UNREAD`, etc.).
    - Archives the email by removing the `INBOX` label.
    - Verifies the operation to ensure all changes are applied correctly.

2. **Customizable Patterns:**
    - Dynamically learns from archived emails—no static cache required.
    - Reduces dependency on external configurations.

---

## Installation

### Requirements:
   - Install the `gog` CLI and authenticate it for Gmail API access.

### Skill Setup:
   - Place the skill files inside your OpenClaw workspace.
   - Modify paths within the script for your local setup if required.

---

## Testing the Workflow

- Run the `script.sh` manually or as part of a larger pipeline to confirm functionality before deploying automatic runs.
- Test with a mix of labeled archived emails and unlabeled inbox emails to ensure accuracy.

---
