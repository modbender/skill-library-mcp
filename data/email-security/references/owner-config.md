# Owner Configuration

Store authorized email addresses here. Update via runtime commands or direct editing.

## Owner (Primary Authority)

Full control over agent email operations. Can add/remove admins and trusted senders.

```
owner@example.com
```

## Admins (Delegated Authority)

Can issue all commands. Cannot modify owner list or security policies.

```
# admin1@example.com
# admin2@example.com
```

## Trusted Senders

Commands require confirmation prompt before execution.

```
# colleague@company.com
# partner@vendor.com
```

## Blocked Senders

Always reject, even if other checks pass.

```
# spam@malicious.com
# phishing@attacker.com
```

## Custom Policies

Override default security settings:

```yaml
# Attachment policy
allowed_extensions: [pdf, txt, csv, png, jpg, jpeg, docx, xlsx]
max_attachment_size_mb: 25

# Rate limiting
max_commands_per_hour_owner: unlimited
max_commands_per_hour_admin: 50
max_commands_per_hour_trusted: 10

# Confirmation requirements
require_confirmation_for:
  - delete_email
  - send_email
  - forward_email
  - modify_rules

# Logging level
log_level: flagged  # Options: all, flagged, blocked, none
```
