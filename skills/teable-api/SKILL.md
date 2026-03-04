# Teable API

Complete Teable API management skill for OpenClaw. Provides full CRUD operations for records, bases, spaces, tables, dashboards, and trash.

## Metadata

```yaml
name: teable-api
description: Complete Teable API management - manage records, bases, spaces, tables, dashboards, and trash
author: Cortana
version: 1.0.6
created: 2026-02-27
requires:
  env: [TEABLE_API_KEY]
```

**Note**: `TEABLE_URL` is optional for self-hosted instances (defaults to https://app.teable.ai)

## Installation

### Prerequisites

Install the required Python package:

```bash
pipx install requests
# or globally
pip3 install requests
```

### Environment Variables

**Required**: Set the `TEABLE_API_KEY` environment variable before using any scripts:

```bash
# Temporary (current shell session)
export TEABLE_API_KEY="your_personal_access_token_here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export TEABLE_API_KEY="your_personal_access_token_here"' >> ~/.bashrc
source ~/.bashrc
```

**Getting Your Teable API Token**:
1. Log in to your Teable instance
2. Go to Settings → Access Token
3. Create a new Personal Access Token
4. Copy and save the token (shown only once)

**Optional**: For self-hosted Teable instances, set `TEABLE_URL`:

```bash
export TEABLE_URL="https://your-teable-instance.com"
# Default: https://app.teable.ai
```

## Usage

### Command-Line Scripts

All scripts are located in the `scripts/` directory:

```bash
# Record operations
python3 scripts/teable_record.py list --table-id <tableId>
python3 scripts/teable_record.py create --table-id <tableId> --fields '{"Name":"Test","Age":30}'
python3 scripts/teable_record.py update --table-id <tableId> --record-id <recordId> --fields '{"Name":"Updated"}'
python3 scripts/teable_record.py delete --table-id <tableId> --record-ids '["rec1","rec2"]'

# Base operations
python3 scripts/teable_base.py list --space-id <spaceId>
python3 scripts/teable_base.py get --base-id <baseId>
python3 scripts/teable_base.py create --space-id <spaceId> --name "My Base"
python3 scripts/teable_base.py delete --base-id <baseId>

# Space operations
python3 scripts/teable_space.py list
python3 scripts/teable_space.py get --space-id <spaceId>
python3 scripts/teable_space.py create --name "My Space"
python3 scripts/teable_space.py delete --space-id <spaceId>

# Table operations
python3 scripts/teable_table.py list --base-id <baseId>
python3 scripts/teable_table.py get --table-id <tableId>
python3 scripts/teable_table.py create --base-id <baseId> --name "My Table"
python3 scripts/teable_table.py delete --table-id <tableId>

# Dashboard operations
python3 scripts/teable_dashboard.py list --base-id <baseId>
python3 scripts/teable_dashboard.py create --base-id <baseId> --name "My Dashboard"
python3 scripts/teable_dashboard.py delete --dashboard-id <dashboardId>

# Trash operations
python3 scripts/teable_trash.py list --base-id <baseId>
python3 scripts/teable_trash.py reset --resource-id <baseId> --resource-type base
```

### Python API

```python
from teable_record import TeableRecordClient

# Initialize client
client = TeableRecordClient()

# List records
records = client.list_records(table_id="tblXXXX", take=100)

# Create a record
new_record = client.create_record(
    table_id="tblXXXX",
    fields={"Name": "Test", "Age": 30}
)

# Update a record
updated = client.update_record(
    table_id="tblXXXX",
    record_id="recXXXX",
    fields={"Status": "Completed"}
)

# Delete records
client.delete_records(table_id="tblXXXX", record_ids=["rec1", "rec2"])
```

## Available Scripts

### teable_record.py - Record Management

| Command | Description | Required Parameters |
|---------|-------------|---------------------|
| `list` | List records | `--table-id` |
| `get` | Get single record | `--table-id`, `--record-id` |
| `create` | Create record | `--table-id`, `--fields` |
| `update` | Update record | `--table-id`, `--record-id`, `--fields` |
| `delete` | Delete records | `--table-id`, `--record-ids` |
| `duplicate` | Duplicate record | `--table-id`, `--record-id` |
| `history` | Get record history | `--table-id`, `--record-id` |

**Optional Parameters**:
- `--view-id`: Specify view
- `--take`: Number of records (max 1000)
- `--skip`: Skip count (pagination)
- `--field-key-type`: Field key type (name/id/dbFieldName)
- `--cell-format`: Cell format (json/text)
- `--projection`: Return only specified fields
- `--order-by`: Sorting
- `--filter`: Filter conditions
- `--typecast`: Enable automatic type conversion

### teable_base.py - Base Management

| Command | Description | Required Parameters |
|---------|-------------|---------------------|
| `list` | List bases | `--space-id` (optional) |
| `get` | Get base details | `--base-id` |
| `create` | Create base | `--space-id`, `--name` |
| `update` | Update base | `--base-id` |
| `delete` | Delete base | `--base-id` |
| `duplicate` | Duplicate base | `--base-id` |
| `export` | Export base | `--base-id`, `--output` |
| `collaborators` | List collaborators | `--base-id` |

### teable_space.py - Space Management

| Command | Description | Required Parameters |
|---------|-------------|---------------------|
| `list` | List spaces | None |
| `get` | Get space details | `--space-id` |
| `create` | Create space | `--name` |
| `update` | Update space | `--space-id` |
| `delete` | Delete space | `--space-id` |
| `bases` | List bases in space | `--space-id` |

### teable_table.py - Table Management

| Command | Description | Required Parameters |
|---------|-------------|---------------------|
| `list` | List tables | `--base-id` |
| `get` | Get table details | `--table-id` |
| `create` | Create table | `--base-id`, `--name` |
| `update` | Update table | `--table-id` |
| `delete` | Delete table | `--table-id` |
| `fields` | List fields | `--table-id` |
| `views` | List views | `--table-id` |

### teable_dashboard.py - Dashboard Management

| Command | Description | Required Parameters |
|---------|-------------|---------------------|
| `list` | List dashboards | `--base-id` |
| `get` | Get dashboard details | `--dashboard-id` |
| `create` | Create dashboard | `--base-id`, `--name` |
| `update` | Update dashboard | `--dashboard-id` |
| `delete` | Delete dashboard | `--dashboard-id` |
| `install-plugin` | Install plugin | `--dashboard-id`, `--plugin-id` |

### teable_trash.py - Trash Management

| Command | Description | Required Parameters |
|---------|-------------|---------------------|
| `list` | List trash items | `--base-id` |
| `reset` | Empty trash | `--resource-id`, `--resource-type` |
| `restore` | Restore item | `--item-id` |
| `delete` | Permanently delete | `--item-id` |

## Examples

### Create a Record with Typecast

```bash
# Enable typecast for automatic type conversion
python3 scripts/teable_record.py create \
  --table-id "tblABC123" \
  --fields '{"Name":"John","Age":"30","Completed":"yes","DueDate":"2024-01-15"}' \
  --typecast
```

### Batch Create Records

```bash
python3 scripts/teable_record.py create \
  --table-id "tblABC123" \
  --fields '[{"Name":"Alice"},{"Name":"Bob"},{"Name":"Charlie"}]'
```

### List Records with Pagination

```bash
# Get first 100 records
python3 scripts/teable_record.py list --table-id "tblABC123" --take 100

# Get next 100 (skip first 100)
python3 scripts/teable_record.py list --table-id "tblABC123" --take 100 --skip 100
```

### Filter and Sort Records

```bash
python3 scripts/teable_record.py list \
  --table-id "tblABC123" \
  --filter '{"operator":"and","filterSet":[{"fieldId":"fld1","operator":"is","value":"Active"}]}' \
  --order-by '[{"fieldId":"fld2","order":"asc"}]'
```

### Complete Workflow Example

```bash
# 1. Create a space
python3 scripts/teable_space.py create --name "Project Alpha" --icon "🚀"

# 2. Create a base in the space
python3 scripts/teable_base.py create --space-id "spcXXX" --name "Task Manager"

# 3. Create a table in the base
python3 scripts/teable_table.py create --base-id "bseXXX" --name "Tasks"

# 4. Add records
python3 scripts/teable_record.py create \
  --table-id "tblXXX" \
  --fields '{"Task":"Design","Status":"In Progress","Priority":"High"}'
```

## API Reference

### Base URL

- **Teable Cloud**: `https://app.teable.ai`
- **Self-hosted**: Your instance URL (set via `TEABLE_URL`)

All API endpoints are relative to the base URL and start with `/api`.

### Authentication

All requests require Bearer token authentication:

```bash
curl -H 'Authorization: Bearer YOUR_TOKEN' \
  'https://app.teable.ai/api/table/tblXXX/record'
```

### ID Formats

| Resource | ID Format | Example |
|----------|-----------|---------|
| Space | `spc...` | `spcABC123` |
| Base | `bse...` | `bseDEF456` |
| Table | `tbl...` | `tblGHI789` |
| Record | `rec...` | `recJKL012` |
| Field | `fld...` | `fldMNO345` |
| View | `viw...` | `viwPQR678` |
| Dashboard | `dbd...` | `dbdSTU901` |

## Troubleshooting

### 401 Unauthorized

Check that `TEABLE_API_KEY` is correctly set:

```bash
echo $TEABLE_API_KEY
```

### 403 Forbidden

Your token lacks the required permissions. Create a new token with appropriate scopes in Teable settings.

### 404 Not Found

Verify that IDs are correct (spaceId, baseId, tableId, recordId, etc.) and match the expected format.

### Connection Timeout

- Self-hosted users: Check that `TEABLE_URL` is accessible
- Users in mainland China accessing official API: Use `proxychains`
  ```bash
  proxychains python3 scripts/teable_record.py list --table-id "tblXXX"
  ```

### Typecast Not Working

Ensure the `--typecast` flag is included in your command:

```bash
python3 scripts/teable_record.py create \
  --table-id "tblXXX" \
  --fields '{"Age":"30"}' \
  --typecast  # Required for string-to-number conversion
```

## Data Types Reference

For detailed information about Teable field types and typecast functionality, see:

- **Data Types Guide**: `references/data-types-and-typecast.md`

This guide covers:
- All 20+ field types with examples
- Typecast automatic conversion rules
- Best practices for data import
- Common issues and solutions

## Additional Resources

- [Teable Official Documentation](https://help.teable.ai/en/api-doc/overview)
- [Getting IDs Guide](https://help.teable.ai/en/api-doc/get-id)
- [Record Field Interface](https://help.teable.ai/en/api-doc/record/interface)
- [API Error Codes](https://help.teable.ai/en/api-doc/error-code)

## License

MIT License

## Support

For issues or questions, please open an issue on the GitHub repository or contact the skill author.
