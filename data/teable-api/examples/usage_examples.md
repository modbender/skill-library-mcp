# Teable Skill Usage Examples

## Environment Setup

```bash
# Set API Key (required)
export TEABLE_API_KEY="your_personal_access_token_here"

# For self-hosted Teable (optional)
export TEABLE_URL="https://your-teable-instance.com"
```

## Example 1: Manage Spaces

```bash
# List all spaces
python3 scripts/teable_space.py list

# Create a new space
python3 scripts/teable_space.py create --name "My Project" --icon "🚀"

# Get space details
python3 scripts/teable_space.py get --space-id "spcXXXXXX"

# Get all bases in a space
python3 scripts/teable_space.py bases --space-id "spcXXXXXX"
```

## Example 2: Manage Bases

```bash
# Create a base in a space
python3 scripts/teable_base.py create --space-id "spcXXXXXX" --name "CRM System" --icon "👥"

# Get base details
python3 scripts/teable_base.py get --base-id "bseXXXXXX"

# List all bases in a space
python3 scripts/teable_base.py list --space-id "spcXXXXXX"

# Update base name
python3 scripts/teable_base.py update --base-id "bseXXXXXX" --name "CRM System v2"

# Duplicate a base
python3 scripts/teable_base.py duplicate --base-id "bseXXXXXX" --name "CRM System - Backup"

# Export a base
python3 scripts/teable_base.py export --base-id "bseXXXXXX" --output backup.zip

# Get collaborators
python3 scripts/teable_base.py collaborators --base-id "bseXXXXXX"

# Delete a base (move to trash)
python3 scripts/teable_base.py delete --base-id "bseXXXXXX"
```

## Example 3: Manage Tables

```bash
# Create a table in a base
python3 scripts/teable_table.py create --base-id "bseXXXXXX" --name "Customers"

# List all tables in a base
python3 scripts/teable_table.py list --base-id "bseXXXXXX"

# Get table details
python3 scripts/teable_table.py get --table-id "tblXXXXXX"

# Get field list
python3 scripts/teable_table.py fields --table-id "tblXXXXXX"

# Get view list
python3 scripts/teable_table.py views --table-id "tblXXXXXX"

# Update a table
python3 scripts/teable_table.py update --table-id "tblXXXXXX" --name "Customers 2024" --description "All customer information"

# Delete a table
python3 scripts/teable_table.py delete --table-id "tblXXXXXX"
```

## Example 4: Manage Records

```bash
# List records
python3 scripts/teable_record.py list --table-id "tblXXXXXX" --take 50

# List records by view
python3 scripts/teable_record.py list --table-id "tblXXXXXX" --view-id "viwXXXXXX" --take 20

# Get a single record
python3 scripts/teable_record.py get --table-id "tblXXXXXX" --record-id "recXXXXXX"

# Create a record
python3 scripts/teable_record.py create --table-id "tblXXXXXX" --fields '{"Name":"John Doe","Phone":"13800138000","City":"Beijing"}'

# Batch create records
python3 scripts/teable_record.py create --table-id "tblXXXXXX" --fields '[{"Name":"Jane Smith"},{"Name":"Bob Johnson"}]'

# Update a record
python3 scripts/teable_record.py update --table-id "tblXXXXXX" --record-id "recXXXXXX" --fields '{"City":"Shanghai","Status":"Active"}'

# Duplicate a record
python3 scripts/teable_record.py duplicate --table-id "tblXXXXXX" --record-id "recXXXXXX"

# Get record history
python3 scripts/teable_record.py history --table-id "tblXXXXXX" --record-id "recXXXXXX" --take 10

# Delete records
python3 scripts/teable_record.py delete --table-id "tblXXXXXX" --record-ids '["rec1","rec2","rec3"]'
```

## Example 5: Manage Dashboards

```bash
# List dashboards
python3 scripts/teable_dashboard.py list --base-id "bseXXXXXX"

# Create a dashboard
python3 scripts/teable_dashboard.py create --base-id "bseXXXXXX" --name "Sales Dashboard"

# Get dashboard details
python3 scripts/teable_dashboard.py get --dashboard-id "dbdXXXXXX"

# Update dashboard layout
python3 scripts/teable_dashboard.py update --dashboard-id "dbdXXXXXX" --layout '[{"x":0,"y":0,"w":6,"h":4}]'

# Install a plugin
python3 scripts/teable_dashboard.py install-plugin --dashboard-id "dbdXXXXXX" --plugin-id "plugin_chart" --name "Sales Chart"

# List installed plugins
python3 scripts/teable_dashboard.py list-plugins --dashboard-id "dbdXXXXXX"

# Delete a dashboard
python3 scripts/teable_dashboard.py delete --dashboard-id "dbdXXXXXX"
```

## Example 6: Manage Trash

```bash
# List trash items
python3 scripts/teable_trash.py list --base-id "bseXXXXXX"

# Empty trash
python3 scripts/teable_trash.py reset --resource-id "bseXXXXXX" --resource-type base

# Get trash item details
python3 scripts/teable_trash.py get --item-id "trashXXXXXX"

# Restore a trash item
python3 scripts/teable_trash.py restore --item-id "trashXXXXXX"

# Batch restore
python3 scripts/teable_trash.py restore --item-ids '["trash1","trash2"]'

# Permanently delete
python3 scripts/teable_trash.py delete --item-id "trashXXXXXX"
```

## Python Code Examples

```python
from teable_record import TeableRecordClient
from teable_base import TeableBaseClient

# Create clients
record_client = TeableRecordClient()
base_client = TeableBaseClient()

# Get records
records = record_client.list_records(
    table_id="tblXXXXXX",
    take=100,
    filter_cond={
        "operator": "and",
        "filterSet": [
            {"fieldId": "fld1", "operator": "is", "value": "Beijing"}
        ]
    }
)

# Create a record
new_record = record_client.create_record(
    table_id="tblXXXXXX",
    fields={"Name": "Jane Doe", "Phone": "13900139000"}
)

# Update a record
updated = record_client.update_record(
    table_id="tblXXXXXX",
    record_id="recXXXXXX",
    fields={"Status": "Completed"}
)

# Get base information
base_info = base_client.get_base("bseXXXXXX")
print(f"Base name: {base_info['name']}")
```

## Advanced Usage

### Paginate Large Datasets

```bash
# Get 1000 records at a time (max limit)
python3 scripts/teable_record.py list --table-id "tblXXXXXX" --take 1000 --skip 0
python3 scripts/teable_record.py list --table-id "tblXXXXXX" --take 1000 --skip 1000
python3 scripts/teable_record.py list --table-id "tblXXXXXX" --take 1000 --skip 2000
```

### Use Field IDs Instead of Names

```bash
python3 scripts/teable_record.py list --table-id "tblXXXXXX" --field-key-type id
python3 scripts/teable_record.py create --table-id "tblXXXXXX" --fields '{"fldABC123":"value"}' --field-key-type id
```

### Return Specific Fields Only

```bash
python3 scripts/teable_record.py list --table-id "tblXXXXXX" --projection "Name,Phone,Email"
```

### Sort Records

```bash
python3 scripts/teable_record.py list --table-id "tblXXXXXX" --order-by '[{"fieldId":"fld1","order":"asc"}]'
```

## Troubleshooting

### 401 Unauthorized
```bash
# Check if API Key is correctly set
echo $TEABLE_API_KEY
```

### 403 Forbidden
Your token lacks the required permissions. Create a new token with appropriate scopes in Teable settings.

### 404 Not Found
Check if IDs are correct and match the expected format (spcXXX, bseXXX, tblXXX, recXXX, etc.).

### Using proxychains (for users in mainland China)
```bash
proxychains python3 scripts/teable_record.py list --table-id "tblXXXXXX"
```