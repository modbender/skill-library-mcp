---
name: focusnote-add-to-daily-note
description: Add text to today's daily note in FocusNote as a new bullet point
---

# FocusNote: Add to Daily Note

This skill adds user-provided text to today's daily note in FocusNote as a new bullet point.

## How It Works

1. Reads the FocusNote documents path from `~/.lucia/documents-path.txt`
2. Generates today's date in `YYYY-MM-DD` format
3. Locates or creates today's daily note
4. Adds the user's text as a new bullet point
5. Updates the document's JSON structure files

## Prerequisites

- FocusNote app must be running (it creates `~/.lucia/documents-path.txt` on startup)
- Node.js installed for running the helper script

## Implementation

When the user asks to add text to their daily note, follow these steps:

### Step 1: Read Documents Path

```javascript
const fs = require("fs");
const path = require("path");
const os = require("os");

// Read the documents path from FocusNote's config file
const focusnoteConfigPath = path.join(
  os.homedir(),
  ".lucia",
  "documents-path.txt",
);
const documentsPath = fs.readFileSync(focusnoteConfigPath, "utf-8").trim();
```

### Step 2: Generate Today's Date

```javascript
const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");
const todayDocName = `${year}-${month}-${day}`;
```

### Step 3: Locate Daily Note Folder

```javascript
const dailyNotePath = path.join(documentsPath, "notes", todayDocName);
const structurePath = path.join(dailyNotePath, "_structure.json");
const metadataPath = path.join(dailyNotePath, "_metadata.json");
const nodesDir = path.join(dailyNotePath, ".nodes");
```

### Step 4: Create Daily Note If It Doesn't Exist

```javascript
if (!fs.existsSync(dailyNotePath)) {
  // Create directory structure
  fs.mkdirSync(dailyNotePath, { recursive: true });
  fs.mkdirSync(nodesDir, { recursive: true });

  // Create metadata
  const metadata = {
    name: todayDocName,
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));

  // Create empty structure
  const structure = {
    rootNodeIds: [],
    deletedNodeIds: [],
    nodes: {},
  };
  fs.writeFileSync(structurePath, JSON.stringify(structure, null, 2));
}
```

### Step 5: Create New Bullet Node

```javascript
const { v4: uuidv4 } = require("uuid"); // npm install uuid

// Generate unique node ID
const nodeId = uuidv4();
const timestamp = Date.now();

// Create Lexical bullet structure
const lexicalContent = {
  root: {
    children: [
      {
        children: [
          {
            children: [
              {
                detail: 0,
                format: 0,
                mode: "normal",
                style: "",
                text: userText, // The text from the user
                type: "text",
                version: 1,
              },
            ],
            direction: "ltr",
            format: "",
            indent: 0,
            type: "listitem",
            version: 1,
            value: 1,
          },
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "list",
        version: 1,
        listType: "bullet",
        start: 1,
        tag: "ul",
      },
    ],
    direction: "ltr",
    format: "",
    indent: 0,
    type: "root",
    version: 1,
  },
};

// Create node object
const newNode = {
  id: nodeId,
  content: JSON.stringify(lexicalContent),
  isFolded: false,
  isTodo: false,
  isDone: false,
  isInProgress: false,
  isBlurred: false,
  backgroundColor: null,
  createdAt: timestamp,
  updatedAt: timestamp,
};
```

### Step 6: Save Node to Sharded Directory

```javascript
// Shard by first 2 characters of node ID
const shard = nodeId.substring(0, 2);
const shardDir = path.join(nodesDir, shard);

if (!fs.existsSync(shardDir)) {
  fs.mkdirSync(shardDir, { recursive: true });
}

const nodeFilePath = path.join(shardDir, `node-${nodeId}.json`);
fs.writeFileSync(nodeFilePath, JSON.stringify(newNode, null, 2));
```

### Step 7: Update Structure File

```javascript
// Read current structure
const structure = JSON.parse(fs.readFileSync(structurePath, "utf-8"));

// Add node to structure
structure.rootNodeIds.push(nodeId);
structure.nodes[nodeId] = {
  parentId: null,
  orderIndex: structure.rootNodeIds.length - 1,
  childIds: [],
};

// Update timestamp
structure.updatedAt = timestamp;

// Save updated structure
fs.writeFileSync(structurePath, JSON.stringify(structure, null, 2));
```

### Complete Script Example

Here's a complete Node.js script you can use:

```javascript
#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const os = require("os");
const { v4: uuidv4 } = require("uuid");

function addToDailyNote(userText) {
  try {
    // Step 1: Read documents path
    const focusnoteConfigPath = path.join(
      os.homedir(),
      ".lucia",
      "documents-path.txt",
    );
    if (!fs.existsSync(focusnoteConfigPath)) {
      throw new Error(
        "FocusNote config file not found. Make sure FocusNote is running.",
      );
    }
    const documentsPath = fs.readFileSync(focusnoteConfigPath, "utf-8").trim();

    // Step 2: Generate today's date
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");
    const todayDocName = `${year}-${month}-${day}`;

    // Step 3: Set up paths
    const dailyNotePath = path.join(documentsPath, "notes", todayDocName);
    const structurePath = path.join(dailyNotePath, "_structure.json");
    const metadataPath = path.join(dailyNotePath, "_metadata.json");
    const nodesDir = path.join(dailyNotePath, ".nodes");

    // Step 4: Create daily note if needed
    if (!fs.existsSync(dailyNotePath)) {
      fs.mkdirSync(dailyNotePath, { recursive: true });
      fs.mkdirSync(nodesDir, { recursive: true });

      const metadata = {
        name: todayDocName,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));

      const structure = {
        rootNodeIds: [],
        deletedNodeIds: [],
        nodes: {},
      };
      fs.writeFileSync(structurePath, JSON.stringify(structure, null, 2));
    }

    // Step 5: Create new bullet node
    const nodeId = uuidv4();
    const timestamp = Date.now();

    const lexicalContent = {
      root: {
        children: [
          {
            children: [
              {
                children: [
                  {
                    detail: 0,
                    format: 0,
                    mode: "normal",
                    style: "",
                    text: userText,
                    type: "text",
                    version: 1,
                  },
                ],
                direction: "ltr",
                format: "",
                indent: 0,
                type: "listitem",
                version: 1,
                value: 1,
              },
            ],
            direction: "ltr",
            format: "",
            indent: 0,
            type: "list",
            version: 1,
            listType: "bullet",
            start: 1,
            tag: "ul",
          },
        ],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "root",
        version: 1,
      },
    };

    const newNode = {
      id: nodeId,
      content: JSON.stringify(lexicalContent),
      isFolded: false,
      isTodo: false,
      isDone: false,
      isInProgress: false,
      isBlurred: false,
      backgroundColor: null,
      createdAt: timestamp,
      updatedAt: timestamp,
    };

    // Step 6: Save node file
    const shard = nodeId.substring(0, 2);
    const shardDir = path.join(nodesDir, shard);

    if (!fs.existsSync(shardDir)) {
      fs.mkdirSync(shardDir, { recursive: true });
    }

    const nodeFilePath = path.join(shardDir, `node-${nodeId}.json`);
    fs.writeFileSync(nodeFilePath, JSON.stringify(newNode, null, 2));

    // Step 7: Update structure
    const structure = JSON.parse(fs.readFileSync(structurePath, "utf-8"));
    structure.rootNodeIds.push(nodeId);
    structure.nodes[nodeId] = {
      parentId: null,
      orderIndex: structure.rootNodeIds.length - 1,
      childIds: [],
    };
    structure.updatedAt = timestamp;
    fs.writeFileSync(structurePath, JSON.stringify(structure, null, 2));

    console.log(`✅ Added bullet to ${todayDocName}: "${userText}"`);
    return { success: true, documentName: todayDocName, nodeId };
  } catch (error) {
    console.error("❌ Error adding to daily note:", error.message);
    return { success: false, error: error.message };
  }
}

// Example usage
if (require.main === module) {
  const userText = process.argv.slice(2).join(" ") || "New bullet point";
  addToDailyNote(userText);
}

module.exports = { addToDailyNote };
```

## Usage Examples

**User:** "Add to my daily note: Finished the OpenClaw skill implementation"

**Assistant:** I'll add that to your daily note.

```bash
# Run the script
node add-to-daily-note.js "Finished the OpenClaw skill implementation"
```

**Output:** ✅ Added bullet to 2026-02-11: "Finished the OpenClaw skill implementation"

---

**User:** "Add a reminder to call mom tomorrow"

**Assistant:** I'll add that to today's note.

```bash
node add-to-daily-note.js "Reminder to call mom tomorrow"
```

## Installation

1. Save the script as `add-to-daily-note.js` in your OpenClaw skills directory
2. Install dependencies: `npm install uuid`
3. Make it executable: `chmod +x add-to-daily-note.js`

## Notes

- The skill creates a new bullet point each time it's called
- Bullets are added to the end of the daily note
- If the daily note doesn't exist, it will be created automatically
- The FocusNote app must be running for the documents path file to exist
- Changes are immediately visible when you open/refresh the daily note in FocusNote

## Troubleshooting

**Error: "FocusNote config file not found"**

- Make sure FocusNote is running
- Check that `~/.lucia/documents-path.txt` exists

**Bullets not appearing in FocusNote**

- Try closing and reopening the daily note
- Check that the node files were created in `.nodes/` directory
- Verify `_structure.json` was updated correctly
