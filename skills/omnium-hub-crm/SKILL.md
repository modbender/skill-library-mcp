---
name: omnium-hub-crm
description: Manage Omnium Hub CRM (contacts, opportunities, appointments). Use for all CRM-related tasks.
---

# Omnium Hub Skill

This skill allows you to interact with the **Omnium Hub** CRM.

## Prerequisites

To use this skill, you need an **Omnium Hub API Key**.
- If you do not have an API key, ask the user for it: "Please provide your Omnium Hub API Key to proceed."
- Once provided, use it in the scripts below.

## Tools

### 1. Manage Contacts

Use `scripts/omnium_client.py` to manage contacts.

**Usage:**
```bash
python3 scripts/omnium_client.py --api-key "YOUR_KEY" contacts --action [lookup|create|update] --email "user@example.com" [other options]
```

**Actions:**
- `lookup`: Find a contact by email or phone.
- `create`: Create a new contact.
- `update`: Update an existing contact.

**Examples:**
*   "Find the contact for john@example.com in Omnium Hub."
    -> `python3 scripts/omnium_client.py --api-key "..." contacts --action lookup --email "john@example.com"`

*   "Add Jane Doe (jane@test.com) to Omnium Hub."
    -> `python3 scripts/omnium_client.py --api-key "..." contacts --action create --first-name "Jane" --last-name "Doe" --email "jane@test.com"`

### 2. Manage Opportunities

Use `scripts/omnium_client.py` with the `opportunities` command.

**Usage:**
```bash
python3 scripts/omnium_client.py --api-key "YOUR_KEY" opportunities --action list --pipeline-id "..."
```

## Troubleshooting

- **401 Unauthorized**: The API Key is invalid. Ask the user to check their Omnium Hub credentials.
- **404 Not Found**: The contact or resource does not exist.
