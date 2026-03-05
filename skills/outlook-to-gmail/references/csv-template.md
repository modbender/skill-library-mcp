# CSV Template — Bulk User Migration

## Format for Google Data Migration Service

```csv
source_email,destination_email
user1@company.onmicrosoft.com,user1@company.com
user2@company.onmicrosoft.com,user2@company.com
```

## Notes

- Source email = Microsoft 365 UPN (usually `user@tenant.onmicrosoft.com` or `user@domain.com`)
- Destination email = Google Workspace email
- No headers required but recommended for clarity
- Max 100 users per batch (Google recommendation for monitoring)
- Shared mailboxes: migrate to a Google Group or dedicated GW account

## Generating the CSV

From Microsoft 365 Admin Center:
1. Users → Active users → Export
2. Edit CSV to keep only `User principal name` column
3. Add `destination_email` column with Google Workspace addresses

From PowerShell:
```powershell
Get-Mailbox -ResultSize Unlimited | Select-Object UserPrincipalName | Export-Csv users.csv -NoTypeInformation
```

From Google Admin (to verify destination accounts exist):
```
Admin Console → Directory → Users → Download users
```
