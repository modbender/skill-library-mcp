# Feishu Sheets API Reference

## Base URLs

- Sheets API v2: `https://open.feishu.cn/open-apis/sheets/v2/spreadsheets`
- Sheets API v3: `https://open.feishu.cn/open-apis/sheets/v3/spreadsheets`
- Auth API: `https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`

## Authentication

All API calls require a tenant access token in the Authorization header:
```
Authorization: Bearer {tenant_access_token}
```

Get token by calling auth API with app_id and app_secret.

## Core APIs

### 1. Create Spreadsheet

**Endpoint:** `POST /sheets/v3/spreadsheets`

**Request Body:**
```json
{
  "title": "Spreadsheet Name",
  "folder_token": "fldcnXXX"  // optional
}
```

**Response:**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "spreadsheet": {
      "title": "Spreadsheet Name",
      "spreadsheet_token": "shtcnXXX",
      "url": "https://xxx.feishu.cn/sheets/shtcnXXX"
    }
  }
}
```

### 2. Get Spreadsheet Info

**Endpoint:** `GET /sheets/v2/spreadsheets/{spreadsheet_token}/metainfo`

**Response:**
```json
{
  "code": 0,
  "data": {
    "properties": {
      "title": "Spreadsheet Name"
    },
    "sheets": [
      {
        "sheet_id": "0bxxxx",
        "title": "Sheet1",
        "grid_properties": {
          "row_count": 1000,
          "column_count": 20
        }
      }
    ]
  }
}
```

### 3. Read Values

**Endpoint:** `GET /sheets/v2/spreadsheets/{spreadsheet_token}/values/{range}`

**Range Formats:**
- `A1:C10` - Cell range
- `0bxxxx!A1:C10` - With sheet_id
- `Sheet1!A1:C10` - With sheet title

**Response:**
```json
{
  "code": 0,
  "data": {
    "range": "0bxxxx!A1:C3",
    "values": [
      ["Name", "Age", "City"],
      ["Alice", 25, "Beijing"],
      ["Bob", 30, "Shanghai"]
    ]
  }
}
```

### 4. Write Values

**Endpoint:** `PUT /sheets/v2/spreadsheets/{spreadsheet_token}/values`

**Request Body:**
```json
{
  "valueRange": {
    "range": "0bxxxx!A1:C3",
    "values": [
      ["Name", "Age", "City"],
      ["Alice", 25, "Beijing"],
      ["Bob", 30, "Shanghai"]
    ]
  }
}
```

### 5. Append Values

**Endpoint:** `POST /sheets/v2/spreadsheets/{spreadsheet_token}/values_append`

**Request Body:**
```json
{
  "valueRange": {
    "range": "0bxxxx",
    "values": [
      ["Charlie", 28, "Shenzhen"]
    ]
  }
}
```

### 6. Insert Rows/Columns

**Endpoint:** `POST /sheets/v2/spreadsheets/{spreadsheet_token}/insert_dimension_range`

**Request Body:**
```json
{
  "dimension": {
    "sheetId": "0bxxxx",
    "majorDimension": "ROWS",  // or "COLUMNS"
    "startIndex": 5,
    "endIndex": 7
  }
}
```

### 7. Delete Rows/Columns

**Endpoint:** `DELETE /sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range`

**Request Body:** Same as insert

### 8. Add Worksheet

**Endpoint:** `POST /sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update`

**Request Body:**
```json
{
  "requests": [{
    "addSheet": {
      "properties": {
        "title": "New Sheet"
      }
    }
  }]
}
```

### 9. Delete Worksheet

**Endpoint:** `POST /sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update`

**Request Body:**
```json
{
  "requests": [{
    "deleteSheet": {
      "sheetId": "0bxxxx"
    }
  }]
}
```

## Data Types

### Cell Values

**String:**
```json
"Hello World"
```

**Number:**
```json
123
45.67
```

**Formula:**
```json
{
  "type": "formula",
  "text": "=SUM(A1:A10)"
}
```

**Hyperlink:**
```json
{
  "type": "url",
  "text": "Click here",
  "link": "https://example.com"
}
```

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 0 | success | Request successful |
| 10001 | bad request | Invalid parameters |
| 10002 | unauthorized | Invalid or expired token |
| 10003 | forbidden | Insufficient permissions |
| 10004 | not found | Spreadsheet or sheet not found |
| 10005 | internal error | Server error |

## Rate Limits

- Default: 100 requests per minute per app
- Bulk operations (batch_update): 20 requests per minute

## Best Practices

1. **Reuse token:** Cache tenant_access_token for up to 2 hours
2. **Batch operations:** Use batch_update for multiple changes
3. **Range selection:** Be specific with ranges to reduce data transfer
4. **Error handling:** Always check response code before processing data
5. **Sheet ID:** Use sheet_id (not title) for reliable operations
