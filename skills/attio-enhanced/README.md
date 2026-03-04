# Enhanced Attio Skill

An advanced Attio integration skill with enhanced functionality for bulk operations, error handling, data validation, enrichment, and task management.

## Features

### Batch Operations
- Bulk import/export capabilities with configurable chunk sizes
- Automatic splitting of large datasets into manageable batches
- Progress tracking during batch operations

### Enhanced Error Handling
- Automatic retry logic with exponential backoff for rate limits
- Comprehensive error classification and handling
- Detailed error reporting with context

### Data Validation
- Built-in validation for common CRM data types (persons, organizations, deals)
- Email format validation
- Required field checking
- Type validation for numeric fields

### Data Enrichment
- Contact data enrichment from external sources
- Company data lookup and enhancement
- Social media profile integration
- Industry and size data augmentation

### Task Management
- Comprehensive task tracking with lifecycle management
- Start, complete, fail, and track operations
- Timestamped task execution
- Result persistence

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   ```bash
   export ATTIO_API_KEY="your_api_key_here"
   export ATTIO_WORKSPACE_ID="your_workspace_id_here"
   ```

## Usage

### Basic Client Initialization

```python
from lib.attio_enhanced import AttioEnhancedClient

client = AttioEnhancedClient(
    api_key="your_api_key",
    workspace_id="your_workspace_id"
)
```

### Batch Record Creation

```python
import asyncio
from lib.attio_enhanced import AttioEnhancedClient

async def create_multiple_records():
    async with AttioEnhancedClient() as client:
        records = [
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'}
        ]
        
        results = await client.batch_create_records(
            record_type='person',
            records=records,
            chunk_size=50
        )
        
        print(f"Created {results['successful']} records successfully")
        print(f"Failed to create {results['failed']} records")
        
        return results

# Run the async function
asyncio.run(create_multiple_records())
```

### Data Validation

```python
from lib.attio_enhanced import AttioEnhancedClient

client = AttioEnhancedClient()

# Validate a single record
validation_errors = client.validate_crm_data('person', {
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'invalid-email-format'
})

if validation_errors:
    print("Validation failed:")
    for field, errors in validation_errors.items():
        print(f"  {field}: {', '.join(errors)}")
else:
    print("Validation passed!")
```

### Data Enrichment

```python
from lib.attio_enhanced import AttioEnhancedClient

client = AttioEnhancedClient()

contact_data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
    'company': 'Example Corp'
}

enriched_data = client.enrich_contact_data(contact_data)
print(enriched_data)
```

### Task Management

```python
from lib.attio_enhanced import AttioEnhancedClient

client = AttioEnhancedClient()

# Start a task
task_start = client.manage_attio_tasks(
    task_type='contact_import',
    operation='start',
    params={'contact_count': 100}
)

print(f"Started task: {task_start['task_id']}")

# Complete a task
task_complete = client.manage_attio_tasks(
    task_type='contact_import',
    operation='complete',
    params={
        'task_id': task_start['task_id'],
        'result': {'success': 95, 'failed': 5}
    }
)

print(f"Completed task: {task_complete['task_id']}")
```

## Advanced Features

### Batch Import Contacts (All-in-One)

```python
import asyncio
from lib.attio_enhanced import batch_import_contacts

async def import_contacts():
    contacts = [
        {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
        {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'}
    ]
    
    results = await batch_import_contacts(
        contacts=contacts
    )
    
    print(results)
    return results

asyncio.run(import_contacts())
```

### Validate and Clean Data

```python
from lib.attio_enhanced import validate_and_clean_crm_data

records = [
    {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
    {'first_name': '', 'last_name': 'Smith', 'email': 'invalid'}  # Invalid record
]

validation_results = validate_and_clean_crm_data(records, 'person')

print(f"Valid records: {validation_results['valid_count']}")
print(f"Invalid records: {validation_results['invalid_count']}")
```

## Configuration

The skill can be configured via environment variables:

- `ATTIO_API_KEY`: Your Attio API key
- `ATTIO_WORKSPACE_ID`: Your Attio workspace ID

## Error Handling

The enhanced Attio skill implements comprehensive error handling:

- **Rate Limiting**: Automatic retries with exponential backoff when encountering rate limits
- **Connection Errors**: Automatic retry on network failures
- **Server Errors**: Retry on 5xx responses
- **Validation Errors**: Detailed error messages for invalid data

## Testing

Run the examples in the `examples/` directory to test functionality:

```bash
python examples/batch_import_example.py
python examples/validation_example.py
```

## Security

- API keys are handled securely via environment variables
- All requests use HTTPS
- Sensitive data is not logged

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This skill is provided under the MIT License.