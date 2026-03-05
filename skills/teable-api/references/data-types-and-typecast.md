# Teable Data Types and Typecast Guide

This document provides a comprehensive guide to all Teable field types, data formats, and the typecast automatic conversion feature.

## Table of Contents

1. [Teable Field Types Overview](#teable-field-types-overview)
2. [Detailed Type Specifications](#detailed-type-specifications)
3. [Typecast Automatic Conversion](#typecast-automatic-conversion)
4. [Best Practices](#best-practices)
5. [FAQ](#faq)

---

## Teable Field Types Overview

| Type ID | Type Name | Description | Typecast Support |
|---------|-----------|-------------|------------------|
| `singleLineText` | Single Line Text | Short text strings | ✅ |
| `longText` | Long Text | Multi-line text content | ✅ |
| `number` | Number | Integer or decimal | ✅ |
| `singleSelect` | Single Select | Choose one from predefined options | ✅ |
| `multipleSelects` | Multiple Selects | Choose multiple from options | ✅ |
| `date` | Date | Date values | ✅ |
| `dateTime` | Date Time | Date + Time | ✅ |
| `checkbox` | Checkbox | Boolean (true/false) | ✅ |
| `attachment` | Attachment | File uploads | ⚠️ Partial |
| `link` | Link | Link to records in other tables | ✅ |
| `user` | User | Select users | ✅ |
| `rating` | Rating | 1-5 star rating | ✅ |
| `formula` | Formula | Auto-calculated (read-only) | ❌ |
| `rollup` | Rollup | Aggregation from linked records (read-only) | ❌ |
| `count` | Count | Count of linked records (read-only) | ❌ |
| `createdTime` | Created Time | Auto-recorded (read-only) | ❌ |
| `lastModifiedTime` | Last Modified Time | Auto-recorded (read-only) | ❌ |
| `createdBy` | Created By | Auto-recorded (read-only) | ❌ |
| `lastModifiedBy` | Last Modified By | Auto-recorded (read-only) | ❌ |
| `autoNumber` | Auto Number | Auto-incrementing (read-only) | ❌ |
| `button` | Button | Trigger actions | ❌ |

**Legend**: 
- ✅ = Full typecast support
- ⚠️ = Partial support
- ❌ = Not supported (read-only or special types)

---

## Detailed Type Specifications

### 1. Single Line Text (singleLineText)

```json
{
  "fieldName": "Text value"
}
```

**Example**:
```json
{
  "Name": "John Doe",
  "Email": "john@example.com"
}
```

### 2. Long Text (longText)

```json
{
  "fieldName": "Multi-line text\nwith line breaks"
}
```

**Example**:
```json
{
  "Description": "First line\nSecond line\nThird line"
}
```

### 3. Number (number)

```json
{
  "fieldName": 123.45
}
```

**Example**:
```json
{
  "Age": 30,
  "Price": 99.99,
  "Quantity": 100
}
```

**Typecast Example**:
```json
// Strings are automatically converted to numbers
{
  "Price": "99.99",  // Auto-converted when typecast enabled
  "Quantity": "50"
}
```

### 4. Single Select (singleSelect)

```json
{
  "fieldName": "Option Name"
}
```

**Example**:
```json
{
  "Status": "In Progress",
  "Priority": "High"
}
```

**Typecast Advantage**: If the option doesn't exist, typecast will create it automatically (requires permissions).

### 5. Multiple Selects (multipleSelects)

```json
{
  "fieldName": ["Option 1", "Option 2", "Option 3"]
}
```

**Example**:
```json
{
  "Skills": ["Python", "JavaScript", "SQL"],
  "Tags": ["Important", "Urgent", "Pending"]
}
```

**Typecast Example**:
```json
// Strings are also accepted and converted to arrays
{
  "Tags": "Important, Urgent"  // Split when typecast enabled
}
```

### 6. Date (date)

```json
{
  "fieldName": "YYYY-MM-DD"
}
```

**Example**:
```json
{
  "BirthDate": "1990-01-15",
  "StartDate": "2024-01-01",
  "EndDate": "2024-12-31"
}
```

**Typecast Supported Formats**:
```json
{
  "Date": "2024/01/15",      // ✅ Slash separator
  "Date": "01/15/2024",      // ✅ MM/DD/YYYY
  "Date": "Jan 15, 2024",    // ✅ English format
  "Date": "2024-01-15"       // ✅ ISO format
}
```

### 7. Date Time (dateTime)

```json
{
  "fieldName": "YYYY-MM-DDTHH:mm:ss.sssZ"
}
```

**Example**:
```json
{
  "MeetingTime": "2024-01-15T14:30:00.000Z",
  "Deadline": "2024-12-31T23:59:59.999+08:00"
}
```

**Typecast Supported Formats**:
```json
{
  "Time": "2024-01-15 14:30:00",  // ✅ Space separator
  "Time": "2024/01/15 2:30 PM",   // ✅ 12-hour format
  "Time": "2024-01-15T14:30:00Z"  // ✅ ISO 8601
}
```

### 8. Checkbox (checkbox)

```json
{
  "fieldName": true
}
```

**Example**:
```json
{
  "Completed": true,
  "Approved": false
}
```

**Typecast Example**:
```json
{
  "Completed": "yes",        // ✅ Converted to true
  "Completed": "true",       // ✅ Converted to true
  "Completed": 1,            // ✅ Converted to true
  "NotDone": "no",           // ✅ Converted to false
  "NotDone": "false"         // ✅ Converted to false
}
```

### 9. Attachment (attachment)

```json
{
  "fieldName": [
    {
      "name": "filename.pdf",
      "url": "https://example.com/file.pdf"
    }
  ]
}
```

**Example**:
```json
{
  "Resume": [
    {
      "name": "John_Resume.pdf",
      "url": "https://example.com/resume.pdf"
    }
  ],
  "Photos": [
    {
      "name": "avatar.jpg",
      "url": "https://example.com/avatar.jpg"
    },
    {
      "name": "work_photo.png",
      "url": "https://example.com/work.png"
    }
  ]
}
```

**Upload via Script**:
```bash
# Use upload-attachment API
python3 scripts/teable_record.py update \
  --table-id "tblXXX" \
  --record-id "recXXX" \
  --fields '{"Attachments": [{"name": "file.pdf", "url": "https://..."}]}'
```

### 10. Link (link)

```json
{
  "fieldName": ["recId1", "recId2"]
}
```

**Example**:
```json
{
  "LinkedCustomers": ["recABC123", "recDEF456"],
  "ProjectLead": ["rec789XYZ"]
}
```

**Typecast Example** (using primary key text):
```json
{
  // With typecast enabled, you can use primary key values directly
  "LinkedCustomers": ["Customer A", "Customer B"],  // ✅ Auto-lookup and link
  "ProjectLead": "John Doe"              // ✅ Single value converted to array
}
```

### 11. User (user)

```json
{
  "fieldName": [
    {
      "userId": "usrXXX",
      "name": "Username"
    }
  ]
}
```

**Example**:
```json
{
  "Owner": [
    {
      "userId": "usr123",
      "name": "John Doe"
    }
  ],
  "Participants": [
    {"userId": "usr123", "name": "John Doe"},
    {"userId": "usr456", "name": "Jane Smith"}
  ]
}
```

**Typecast Example**:
```json
{
  // With typecast enabled, you can use email or username
  "Owner": "john@example.com",  // ✅ Auto-lookup user
  "Participants": "John, Jane"  // ✅ Auto-split and lookup
}
```

### 12. Rating (rating)

```json
{
  "fieldName": 4
}
```

**Example**:
```json
{
  "Satisfaction": 5,
  "Recommendation": 4,
  "Quality": 3
}
```

**Typecast Example**:
```json
{
  "Satisfaction": "5",    // ✅ String to number
  "Satisfaction": 5       // ✅ Direct number
}
```

---

## Typecast Automatic Conversion

### What is Typecast?

Typecast is a smart Teable feature that allows you to input data in formats that don't exactly match the field type. The system automatically attempts to convert the data to the correct format.

### When to Use Typecast?

✅ **Recommended**:
- Importing data from CSV/Excel (all data is strings)
- Quick data entry without strict formatting
- Link fields using text instead of IDs
- User fields using email/username instead of userId

❌ **Not Recommended**:
- Scenarios requiring strict data validation
- High-performance batch processing
- Data that might be ambiguous

### Enable Typecast

#### Method 1: Command Line

```bash
# Create record with typecast
python3 scripts/teable_record.py create \
  --table-id "tblXXX" \
  --fields '{"Age": "30", "Date": "2024-01-15"}' \
  --typecast

# Update record with typecast
python3 scripts/teable_record.py update \
  --table-id "tblXXX" \
  --record-id "recXXX" \
  --fields '{"Done": "yes"}' \
  --typecast
```

#### Method 2: Python API

```python
from teable_record import TeableRecordClient

client = TeableRecordClient()

# Create record with typecast enabled
record = client.create_record(
    table_id="tblXXX",
    fields={
        "Age": "30",           # String → Number
        "Date": "2024/01/15",  # Non-standard → Date
        "Done": "yes"          # Text → Boolean
    },
    typecast=True  # Enable automatic conversion
)

# Batch create
records = client.create_records(
    table_id="tblXXX",
    records=[
        {"fields": {"Name": "John", "Age": "25"}},
        {"fields": {"Name": "Jane", "Age": "30"}}
    ],
    typecast=True
)

# Update record
updated = client.update_record(
    table_id="tblXXX",
    record_id="recXXX",
    fields={"Status": "In Progress"},  # Text → Select option
    typecast=True
)
```

#### Method 3: Direct API Call

```bash
curl -X POST 'https://app.teable.ai/api/table/tblXXX/record' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "records": [
      {
        "fields": {
          "Name": "John",
          "Age": "30",
          "JoinDate": "2024/01/15"
        }
      }
    ],
    "typecast": true
  }'
```

### Typecast Conversion Rules

| Target Type | Accepted Input | Conversion Result | Example |
|------------|---------------|-------------------|---------|
| **number** | Numeric string | Number | `"123"` → `123` |
| | Comma-separated | Number | `"1,234.56"` → `1234.56` |
| | Invalid string | ❌ Error | `"abc"` → Error |
| **checkbox** | "yes"/"true"/1 | `true` | `"yes"` → `true` |
| | "no"/"false"/0 | `false` | `"no"` → `false` |
| **date** | ISO format | Date | `"2024-01-15"` → Date |
| | Slash separator | Date | `"2024/01/15"` → Date |
| | Various formats | Date | `"Jan 15, 2024"` → Date |
| **dateTime** | ISO 8601 | DateTime | `"2024-01-15T14:30:00Z"` |
| | Space separator | DateTime | `"2024-01-15 14:30:00"` |
| **singleSelect** | Text | Option | `"In Progress"` → Option |
| | Non-existent option | Create new* | `"New Status"` → New Option |
| **multipleSelects** | Array | Multi-select | `["A", "B"]` |
| | Comma-separated | Split array | `"A, B, C"` → `["A","B","C"]` |
| **link** | Record ID array | Link | `["rec1", "rec2"]` |
| | Primary key values | Lookup & link* | `["Customer A", "Customer B"]` |
| **user** | userId array | User | `[{"userId":"usr1"}]` |
| | Email/username | Lookup user* | `"john@example.com"` |

\* Requires appropriate permissions

### Typecast Considerations

⚠️ **Important Notes**:

1. **Performance Impact**: Typecast increases server processing time; large batch operations may be slower
2. **Permission Requirements**: Auto-creating options requires edit permissions on the table
3. **Data Quality**: May hide data formatting issues; recommended to enable during development, use strict validation in production
4. **Error Handling**: Conversion failures return HTTP 400 errors; implement proper error handling

### Typecast Error Handling Example

```python
from teable_record import TeableRecordClient
import requests

client = TeableRecordClient()

try:
    record = client.create_record(
        table_id="tblXXX",
        fields={"Age": "not-a-number"},  # Cannot convert
        typecast=True
    )
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        error_detail = e.response.json()
        print(f"Type conversion failed: {error_detail}")
        # Handle error: log, notify user, etc.
```

---

## Best Practices

### 1. Data Import Scenarios

```python
import csv
from teable_record import TeableRecordClient

client = TeableRecordClient()

# Import from CSV (all CSV fields are strings)
with open('customers.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        client.create_record(
            table_id="tblXXX",
            fields={
                "Name": row["name"],
                "Age": row["age"],        # String → Number
                "Email": row["email"],
                "JoinDate": row["date"],  # String → Date
                "Level": row["level"],    # String → Single select
                "Verified": row["verified"]  # String → Boolean
            },
            typecast=True  # Key: enable automatic conversion
        )
```

### 2. Rapid Prototyping

```python
# Development: use typecast for quick testing
client.create_record(
    table_id="tblXXX",
    fields={
        "Done": "yes",
        "Date": "next week",
        "Owner": "John"
    },
    typecast=True
)

# Production: strict validation
client.create_record(
    table_id="tblXXX",
    fields={
        "Done": True,
        "Date": "2024-01-15",
        "Owner": [{"userId": "usr123", "name": "John Doe"}]
    },
    typecast=False
)
```

### 3. Batch Operations with Linked Records

```python
# Simplify linking with typecast
client.update_record(
    table_id="tblOrders",
    record_id="rec123",
    fields={
        # Traditional: need to query customer table for recId
        # "Customer": ["recCustomer1", "recCustomer2"]
        
        # Typecast: use customer names directly
        "Customer": ["Customer A", "Customer B"]
    },
    typecast=True
)
```

### 4. Mixed Type Handling

```python
# Handle data from different sources
records = [
    {"Name": "John", "Age": 30, "Birthday": "1990-01-15"},    # Correct format
    {"Name": "Jane", "Age": "25", "Birthday": "1995/05/20"},  # Strings
    {"Name": "Bob", "Age": "twenty", "Birthday": "unknown"},  # Invalid
]

for data in records:
    try:
        client.create_record(
            table_id="tblXXX",
            fields=data,
            typecast=True
        )
        print(f"✓ {data['Name']} imported successfully")
    except Exception as e:
        print(f"✗ {data['Name']} import failed: {e}")
        # Log failed data for manual processing
```

---

## FAQ

### Q1: Does Typecast Affect Performance?

**A**: Yes, there is a slight performance impact. Recommendations:
- Small batches (<100 records): Use freely
- Large imports (>1000 records): Pre-format data, disable typecast
- Real-time API calls:权衡 based on your scenario

### Q2: Why Isn't Typecast Working?

**Checklist**:
- [ ] Is `typecast: true` set in your request?
- [ ] Does the field type support typecast?
- [ ] Is the data format within convertible range?
- [ ] Do you have sufficient permissions (e.g., to create new options)?

### Q3: What Happens When Typecast Conversion Fails?

**A**: Returns HTTP 400 error with detailed information:
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Cannot convert 'abc' to number type",
    "fieldId": "fldXXX",
    "fieldName": "Age"
  }
}
```

### Q4: Can I Use Typecast for Only Some Fields?

**A**: No. Typecast is a global setting for the entire request. Recommendations:
- Pre-process fields that need conversion
- Or use typecast for everything and accept the performance overhead

### Q5: How Do I Check the Exact Field Type?

**A**: Use the table script to get field information:
```bash
python3 scripts/teable_table.py fields --table-id "tblXXX"
```

Or via API:
```python
from teable_table import TeableTableClient
client = TeableTableClient()
fields = client.get_fields(table_id="tblXXX")
for field in fields:
    print(f"{field['name']}: {field['type']}")
```

---

## Resources

- [Teable Official API Documentation](https://help.teable.ai/en/api-doc/overview)
- [Record Field Interface](https://help.teable.ai/en/api-doc/record/interface)
- [Create Records API](https://help.teable.ai/en/api-doc/record/create)
- [Update Record API](https://help.teable.ai/en/api-doc/record/update)

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-02-27  
**Maintainer**: Cortana
