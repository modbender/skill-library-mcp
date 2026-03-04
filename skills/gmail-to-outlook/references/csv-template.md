# CSV Template — Bulk User Migration

## Microsoft Data Migration Service Format

```csv
source_email,destination_email
john@company.com,john@company.onmicrosoft.com
jane@company.com,jane@company.onmicrosoft.com
admin@company.com,admin@company.onmicrosoft.com
```

## Extended Format (with additional mapping)

```csv
source_email,destination_email,source_display_name,migration_start_date
john@company.com,john@company.onmicrosoft.com,"John Smith",2024-03-01
jane@company.com,jane@company.onmicrosoft.com,"Jane Doe",2024-03-01
admin@company.com,admin@company.onmicrosoft.com,"IT Admin",2024-03-02
```

## Notes

- **Headers required**: First row must contain column names exactly as shown
- **Email format**: Use primary email addresses, not aliases
- **Destination**: Can be existing Microsoft 365 users or will create new ones
- **Case sensitive**: Email addresses should match exactly as they appear in admin consoles
- **Special characters**: Avoid spaces in email addresses
- **Encoding**: Save as UTF-8 CSV to handle international characters

## Batch Migration Strategy

For large organizations (100+ users), split into batches:

### Batch 1: Test Group (Week 1)
```csv
source_email,destination_email,batch
testuser1@company.com,testuser1@company.onmicrosoft.com,pilot
testuser2@company.com,testuser2@company.onmicrosoft.com,pilot
```

### Batch 2: Early Adopters (Week 2)
```csv
source_email,destination_email,batch
manager1@company.com,manager1@company.onmicrosoft.com,early
manager2@company.com,manager2@company.onmicrosoft.com,early
```

### Batch 3: General Users (Week 3+)
```csv
source_email,destination_email,batch
user1@company.com,user1@company.onmicrosoft.com,general
user2@company.com,user2@company.onmicrosoft.com,general
```

## Pre-Migration User Preparation

Before adding users to migration CSV:

1. **Verify Google Workspace licenses** — Active users only
2. **Check Microsoft 365 licenses** — Assign Exchange Online license
3. **Validate email addresses** — No typos or inactive accounts
4. **Note special cases** — Shared mailboxes, service accounts, former employees
5. **Estimate data size** — Plan for large mailboxes (10GB+)

## Common Pitfalls

- **Mixed domains**: Don't mix @company.com and @company.onmicrosoft.com in same batch
- **Inactive users**: Remove terminated employees from CSV
- **Alias confusion**: Use primary email address, not aliases
- **Permission issues**: Ensure destination accounts exist with proper licenses
- **Time zones**: Consider business hours when scheduling migration batches