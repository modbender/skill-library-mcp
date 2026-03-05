---
name: shopping-list
version: 1.0.1
description: >
  Conversational shopping list with categories, family sharing, and purchase
  history. Add items, check them off, organize by category — all through
  natural language. Use for any shopping list, grocery list, "add to list",
  "what do we need", or "we need to buy" requests.
---

# Shopping List

Manage the household shopping list. Add items with quantities, check them off,
organize by category. Data lives in `skills/shopping-list/data/`.

For full command reference and output formats, read `skills/shopping-list/references/commands.md`.

## Before Every Command

Run these checks before every shopping list operation, in order:

1. If `skills/shopping-list/data/` directory does not exist, create it.
2. If `data/active.json` does not exist, create it with:
   ```json
   {
     "items": [],
     "categories": ["Produce", "Dairy", "Meat", "Pantry", "Frozen", "Beverages", "Household", "Personal"],
     "lastModified": "<current ISO timestamp>"
   }
   ```
3. If `data/active.json` exists but fails to parse as valid JSON, rename it to `data/active.json.corrupt` and create a fresh default file. Tell the user: "Shopping list data was corrupted. Saved backup as active.json.corrupt and started a fresh list."
4. If `data/config.json` does not exist, create it with: `{ "user": null, "snoozes": {} }`
5. If `config.json` has `"user": null`, ask the user: "What's your name? I'll use it to track who added each item." Store their answer (lowercased) in `config.json` before proceeding with the original command.
6. Run the archive process (see Archive section below).

All file paths in this document are relative to `skills/shopping-list/` unless stated otherwise.

## Data Files

### data/active.json

The live shopping list. Contains all items that have not yet been archived.

```json
{
  "items": [
    {
      "id": "F47AC10B-58CC-4372-A567-0E02B2C3D479",
      "name": "Whole Milk",
      "normalizedName": "whole milk",
      "quantity": 2,
      "unit": "gallons",
      "category": "Dairy",
      "checkedOff": false,
      "checkedOffDate": null,
      "addedBy": "aj",
      "addedDate": "2026-02-24T10:00:00Z",
      "notes": null
    }
  ],
  "categories": ["Produce", "Dairy", "Meat", "Pantry", "Frozen", "Beverages", "Household", "Personal"],
  "lastModified": "2026-02-24T10:00:00Z"
}
```

Field rules:

- `id` -- Generate via `uuidgen` in bash. If that command is unavailable, construct an ID from the current ISO timestamp concatenated with 4 random hex characters (e.g. `2026-02-24T10:00:00Z-a3f1`).
- `name` -- The item name as the user provided it, with leading/trailing whitespace trimmed. Preserve original casing for display purposes.
- `normalizedName` -- Always computed as `name.toLowerCase().trim()`. Recompute on every add or edit. This field is used for all matching and deduplication logic.
- `quantity` -- Optional. Defaults to `null` when the user does not specify a quantity. When present, must be a number greater than 0. Fractional values are fine (e.g. 0.5 for half a pound).
- `unit` -- Optional free text (e.g. "gallons", "lbs", "bunch", "bag"). Defaults to `null` when not specified.
- `category` -- One of the values from the `categories` array, or "Uncategorized".
- `checkedOff` -- Boolean. Starts as `false`. Set to `true` when the user checks off the item.
- `checkedOffDate` -- ISO timestamp when the item was checked off. `null` when not checked off.
- `addedBy` -- Lowercase string from `config.json` user field (e.g. "aj" or "shal").
- `addedDate` -- ISO timestamp when the item was first added.
- `notes` -- Optional free text for special instructions ("the organic one", "Costco size"). Defaults to `null`.
- `categories` (top-level array) -- The master list of known categories. Starts with 8 presets. Custom categories are appended when created.
- `lastModified` -- ISO timestamp. Updated on every write to this file.

### data/config.json

Stores session-persistent user configuration.

```json
{ "user": "aj", "snoozes": {} }
```

- `user` -- Set on first interaction, persists across sessions. Lowercase string.
- `snoozes` -- Reserved for Phase 2 restock suggestions. Ignore for now; preserve the field when writing.

### data/history-YYYY-MM.json

Monthly archive of purchased items. One file per calendar month, created on demand.

```json
{
  "month": "2026-02",
  "archivedItems": [
    { "...same fields as active item...", "archivedDate": "2026-02-25T08:00:00Z" }
  ]
}
```

The `archivedDate` field is added to each item when it moves from active to history. All original fields from the active item are preserved. A new file is created automatically when the first item is archived in a month that does not yet have a history file.

## Core Operations

### Adding Items

Parse the user's natural language into name, quantity, and unit for each item.

**Category inference:** Silently infer the category from the item name. Common mappings: milk/cheese/yogurt/butter go to Dairy, chicken/beef/fish to Meat, bananas/lettuce/onions to Produce, rice/pasta/flour to Pantry, dish soap/paper towels to Household, shampoo/toothpaste to Personal, beer/wine/juice to Beverages, frozen pizza/ice cream to Frozen. If the mapping is not obvious, assign "Uncategorized". Never prompt the user for a category. If the user wants to change it, they can say "move X to Y category".

**Multi-item input:** The user may add several items at once: "add eggs, bread, and 2 gallons milk" should produce 3 separate items. Parse commas and "and" as item separators. When the parsing is ambiguous (compound item names like "hot dog buns" near separators), ask the user rather than guessing wrong.

**Duplicate handling:** Before creating a new item, check if an item with the same `normalizedName` already exists in the active list.
- If it exists and is not checked off, update the existing item's quantity (add to it if the user gives a new quantity, or leave unchanged if not). Do not create a duplicate.
- If it exists and is checked off, uncheck it (set `checkedOff: false`, `checkedOffDate: null`) and update the quantity if specified.

**New categories:** If the user explicitly specifies a category that is not in the `categories` array, add it to the array and assign the item to it.

Set `addedBy` from `config.json` user value. Set `addedDate` to the current ISO timestamp. Set `checkedOff` to `false` and `checkedOffDate` to `null`. Update `lastModified` after writing.

### Checking Off Items

Match items by `normalizedName` -- case-insensitive, partial match is acceptable (e.g. "milk" matches "whole milk" if it is the only milk item).

- **One match:** Set `checkedOff` to `true` and `checkedOffDate` to the current ISO timestamp. Confirm to the user.
- **Multiple matches:** List the matching items and ask the user which one to check off.
- **No match:** Show the current list so the user can identify the correct item.

Checked-off items remain in `active.json` and display with strikethrough styling until the archive process moves them to history (after 24 hours).

### Removing Items

Permanently delete an item from the active list. No archive record, no history entry. This exists for "I added this by mistake" corrections.

Match by `normalizedName` using the same matching rules as checking off. Confirm removal to the user.

### Editing Items

Match the target item by `normalizedName`, then update the specified fields. Supported editable fields: name, quantity, unit, category, notes.

If the name changes, recompute `normalizedName`. If the category changes to one not in the `categories` array, add it. Update `lastModified` after writing.

### Changing User

When the user says "switch to Shal", "I'm AJ", or similar, update the `user` field in `config.json`. All subsequent item additions will use the new user value for `addedBy`.

## Archive Process

This process runs automatically at the start of every shopping list command, before handling the user's request.

1. Read `data/active.json`.
2. Find all items where `checkedOff` is `true` AND `checkedOffDate` is more than 24 hours ago.
3. If no items qualify, skip the rest of this process.
4. Determine the current month string (e.g. "2026-02"). Read `data/history-2026-02.json`. If it does not exist, create it with `{ "month": "2026-02", "archivedItems": [] }`.
5. Append each qualifying item to the history file's `archivedItems` array, adding an `archivedDate` field set to the current ISO timestamp.
6. Write the history file.
7. Remove the archived items from the `items` array in `data/active.json`.
8. Write the active file.

**Write order matters:** Always write the history file before the active file. If the process is interrupted between the two writes, the worst case is a harmless duplicate in history. Reversing the order risks data loss -- items removed from active but never written to history.

The `shopping clear` command triggers this same process immediately for all checked items, bypassing the 24-hour wait.

## Displaying the List

When showing the shopping list, sort categories in this fixed order:

1. Preset categories in their defined order: Produce, Dairy, Meat, Pantry, Frozen, Beverages, Household, Personal
2. Custom categories alphabetically after all presets
3. "Uncategorized" always appears last

Skip any category that has zero items (considering only unchecked items for this purpose). Within each category, sort items alphabetically by `normalizedName`. Do not rely on the stored array order in JSON.

Checked-off items appear with strikethrough styling within their category, visually distinct from unchecked items. They remain visible until archived.

## History Queries

When the user asks about past purchases ("what did we buy last month", "purchase history", "what did we get in January"), read the relevant `data/history-YYYY-MM.json` file(s). Present results grouped by date (most recent first) with item names and quantities. If no history file exists for the requested period, tell the user no purchase history was found for that month.

Note: history reflects the archive date, not the purchase date. An item checked off on Feb 28 but archived on March 1 appears in March's history.
