# Google Contacts via TapAuth

## Provider Key

Use `google_contacts` as the provider name.

## Available Scopes

| Scope | Access |
|-------|--------|
| `contacts.readonly` | View contacts |
| `contacts` | Create & edit contacts |

## Example: Create a Grant

```bash
./scripts/tapauth.sh google_contacts "contacts.readonly" "Contact Reader"
```

## Example: List Contacts

```bash
curl -H "Authorization: Bearer <token>" \
  "https://people.googleapis.com/v1/people/me/connections?personFields=names,emailAddresses,phoneNumbers&pageSize=100"
```

## Example: Search Contacts

```bash
curl -H "Authorization: Bearer <token>" \
  "https://people.googleapis.com/v1/people:searchContacts?query=John&readMask=names,emailAddresses"
```

## Gotchas

- **People API:** Google Contacts uses the People API (`people.googleapis.com`), not a dedicated contacts API.
- **personFields/readMask required:** Most endpoints require specifying which fields to return. Omitting this returns empty results.
- **Token refresh:** Google tokens expire after ~1 hour. Call the TapAuth token endpoint again to get a fresh one.

## Recommended Minimum Scopes

| Use Case | Scopes |
|----------|--------|
| Read contacts | `contacts.readonly` |
| Manage contacts | `contacts` |
