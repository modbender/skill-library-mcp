# Teable API Skill

Complete Teable API management skill for OpenClaw. Provides full CRUD operations for records, bases, spaces, tables, dashboards, and trash.

## Quick Start

### 1. Install Dependencies

```bash
pipx install requests
# or
pip3 install requests
```

### 2. Configure Environment Variables

```bash
# Required: API Token
export TEABLE_API_KEY="your_personal_access_token_here"

# Optional: Self-hosted Teable URL (defaults to https://app.teable.ai)
export TEABLE_URL="https://your-teable-instance.com"
```

### 3. Usage Examples

```bash
# List spaces
python3 scripts/teable_space.py list

# Create a base
python3 scripts/teable_base.py create --space-id "spcXXX" --name "My Base"

# List records
python3 scripts/teable_record.py list --table-id "tblXXX" --take 50

# Create a record
python3 scripts/teable_record.py create --table-id "tblXXX" --fields '{"Name":"Test"}'
```

## Available Scripts

| Script | Functionality |
|--------|---------------|
| `teable_space.py` | Space management (create/read/update/delete) |
| `teable_base.py` | Base management + collaborators + invitation links |
| `teable_table.py` | Table management + fields + views |
| `teable_record.py` | Full CRUD + history + duplicate |
| `teable_dashboard.py` | Dashboard management + plugins |
| `teable_trash.py` | Trash management + restore + permanent delete |

## Documentation

- [SKILL.md](SKILL.md) - Complete API documentation
- [examples/usage_examples.md](examples/usage_examples.md) - Usage examples
- [references/data-types-and-typecast.md](references/data-types-and-typecast.md) - Data types guide

## Security Features

- **URL Validation**: Only HTTP/HTTPS schemes allowed, warns on HTTP
- **Path Traversal Protection**: Output files restricted to current directory
- **Credential Protection**: API key only sent to validated Teable endpoints

## Notes

- Users in mainland China accessing the official API may need `proxychains`
- Self-hosted users should set `TEABLE_URL` to point to their instance
- API Tokens can be generated in Teable Settings → Access Token
- Resource ID formats: spcXXX (Space), bseXXX (Base), tblXXX (Table), recXXX (Record)