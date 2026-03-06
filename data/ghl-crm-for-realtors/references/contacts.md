# Contacts API Reference

Base: `https://services.leadconnectorhq.com/contacts/`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/contacts/?locationId={id}&query={q}&limit={n}` | Search contacts |
| GET | `/contacts/{contactId}` | Get contact by ID |
| POST | `/contacts/` | Create contact (requires `locationId` in body) |
| PUT | `/contacts/{contactId}` | Update contact fields |
| DELETE | `/contacts/{contactId}` | Delete contact |
| POST | `/contacts/upsert` | Create or update by email/phone match |
| GET | `/contacts/business/{businessId}` | Get contacts by business |
| POST | `/contacts/{contactId}/tags` | Add tags (`{"tags": ["tag1","tag2"]}`) |
| DELETE | `/contacts/{contactId}/tags` | Remove tags |
| GET | `/contacts/{contactId}/notes` | List notes |
| POST | `/contacts/{contactId}/notes` | Create note (`{"body": "..."}`) |
| PUT | `/contacts/{contactId}/notes/{noteId}` | Update note |
| DELETE | `/contacts/{contactId}/notes/{noteId}` | Delete note |
| GET | `/contacts/{contactId}/tasks` | List tasks |
| POST | `/contacts/{contactId}/tasks` | Create task |
| PUT | `/contacts/{contactId}/tasks/{taskId}` | Update task |
| DELETE | `/contacts/{contactId}/tasks/{taskId}` | Delete task |
| GET | `/contacts/{contactId}/appointments` | Get appointments |
| POST | `/contacts/{contactId}/campaigns/{campaignId}` | Add to campaign |
| DELETE | `/contacts/{contactId}/campaigns/{campaignId}` | Remove from campaign |
| POST | `/contacts/{contactId}/workflow/{workflowId}` | Add to workflow |
| DELETE | `/contacts/{contactId}/workflow/{workflowId}` | Remove from workflow |

## Create/Update Contact Fields

```json
{
  "locationId": "required",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "+15551234567",
  "companyName": "Acme Inc",
  "address1": "123 Main St",
  "city": "Austin",
  "state": "TX",
  "postalCode": "73301",
  "country": "US",
  "source": "API",
  "tags": ["customer", "vip"],
  "customFields": [{"id": "field_id", "value": "field_value"}]
}
```

## Search Parameters
- `query` — Search by name, email, phone, company
- `limit` — 1-100, default 20
- `startAfter` / `startAfterId` — Cursor pagination
- `sortBy` — Field to sort by
- `sortOrder` — `asc` or `desc`

## Scopes Required
`contacts.readonly`, `contacts.write`
