# Lark Suite Wiki

📚 Export and sync Lark Suite (Feishu) Wiki/Knowledge Base documents to local Markdown files.

## Features

- ✅ **Batch Export** - Export entire knowledge base with one command
- ✅ **Recursive Export** - Automatically follows and exports all linked subdocuments  
- ✅ **Preserves Structure** - Creates nested folders matching your wiki structure
- ✅ **Incremental Sync** - Only exports changed documents (tracks revision IDs)

## Quick Start

```bash
# Install skill
clawhub install larksuite-wiki

# Configure credentials (get from https://open.larksuite.com/console)
export LARK_APP_ID="cli_xxxxxxxx"
export LARK_APP_SECRET="xxxxxxxx"

# Sync entire wiki
python3 larksuite-wiki.py sync YOUR_DOC_ID --output ./my-wiki/
```

## Prerequisites

1. Create a Lark app at https://open.larksuite.com/console
2. Enable permissions: `docs:doc:read`, `drive:drive:read`, `wiki:wiki:read`
3. Publish app and authorize it to access your wiki
4. Add your app to each document (Share → Add App)

## Usage

### Read Document
```bash
python3 larksuite-wiki.py read DOC_ID
```

### Export Single Document
```bash
python3 larksuite-wiki.py export DOC_ID --output ./docs/
```

### Sync Entire Wiki
```bash
# First sync - exports all documents
python3 larksuite-wiki.py sync ROOT_DOC_ID --output ./lark-wiki/

# Incremental sync - only exports changed documents  
python3 larksuite-wiki.py sync ROOT_DOC_ID --output ./lark-wiki/

# Force re-export
python3 larksuite-wiki.py sync ROOT_DOC_ID --output ./lark-wiki/ --force
```

### Show Document Tree
```bash
python3 larksuite-wiki.py tree ROOT_DOC_ID
```

## Output Structure

```
lark-wiki/
├── .lark-sync-state.json      # Sync state for incremental updates
└── 01_Home/
    ├── 01_Home.md
    ├── 01_Subdoc/
    │   ├── 01_Subdoc.md
    │   └── 02_Child/
    │       └── 02_Child.md
    └── 02_Another/
        └── 02_Another.md
```

## License

MIT
