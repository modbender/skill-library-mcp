# Apple Mail SQLite Queries

## Database Location

```bash
# Find current version
ls ~/Library/Mail/V*/MailData/Envelope\ Index
# Usually V10 or V11
```

## Schema Essentials

| Table | Key Columns |
|-------|-------------|
| `messages` | subject, sender, date_received, attachment_count, message_id |
| `addresses` | address, comment (display name) |
| `mailboxes` | url (folder path), unread_count |

## Common Queries

### Recent emails (last 7 days)
```sql
SELECT m.subject, a.address, datetime(m.date_received, 'unixepoch')
FROM messages m
JOIN addresses a ON m.sender = a.ROWID
WHERE m.date_received > strftime('%s','now','-7 days')
ORDER BY m.date_received DESC
LIMIT 50;
```

### Unread count by folder
```sql
SELECT url, unread_count FROM mailboxes WHERE unread_count > 0;
```

### Search by sender domain
```sql
SELECT m.subject, a.address
FROM messages m
JOIN addresses a ON m.sender = a.ROWID
WHERE a.address LIKE '%@example.com';
```

## Traps

- **Stale data**: Force sync before query: `osascript -e 'tell app "Mail" to check for new mail'`
- **date_received is Unix timestamp**: Use `datetime(date_received, 'unixepoch')` to convert
- **attachment_count > 0**: Doesn't mean attachments are downloaded
- **Path escaping**: Use `Envelope\ Index` or quote the path
