# Lark Suite Wiki Skill Reference

## Environment Variables

```bash
export LARK_APP_ID="cli_a90f6c8bf8f8ded4"
export LARK_APP_SECRET="xtSodRRMmiU1R4oikynlFbBoEu3T2Wgo"
```

## Usage Examples

### List Wiki Spaces
```bash
larksuite-wiki spaces
```

### Read Document
```bash
larksuite-wiki read TDCZweBJ2iMFO4kI1LAlSE62gnd
```

### Export to Markdown
```bash
larksuite-wiki export TDCZweBJ2iMFO4kI1LAlSE62gnd --output ./docs/
```

## API Endpoints Used

- `POST /auth/v3/tenant_access_token/internal` - Authentication
- `GET /wiki/v2/spaces` - List spaces
- `GET /docx/v1/documents/{id}` - Get document info
- `GET /docx/v1/documents/{id}/raw_content` - Get document content

## Limitations

- App must be authorized to access each document
- Some block types may not convert perfectly
- Rate limits apply
