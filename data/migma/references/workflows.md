# Example Conversations

Real examples of what users ask and how to handle them.

## "Create a welcome email and send it to sarah@example.com"

```bash
# Generate the email
migma generate "Welcome email for new subscribers" --wait --json
# Send it
migma send --to sarah@example.com --subject "<subject from generate>" \
  --from-conversation <conversationId> \
  --from hello@company.migma.email --from-name "Company" --json
```

## "Design a Black Friday sale email with 40% off"

```bash
migma generate "Black Friday sale — 40% off everything, highlight our best sellers" --wait --json
```

Show the user the subject line and let them know the email is ready. If they want to preview, add `--save ./bf.html` and tell them where the file is.

## "Send that email to all our VIP customers"

```bash
# Find the VIP tag or segment
migma tags list --json
# Send to the tag
migma send --tag <tagId> --subject "Black Friday: 40% Off" \
  --from-conversation <conversationId> \
  --from hello@company.migma.email --from-name "Company" --json
```

## "Check if this email will land in spam"

```bash
migma validate deliverability --conversation <conversationId> --json
# Or for a full check:
migma validate all --conversation <conversationId> --json
```

## "Import our brand from our website"

```bash
migma projects import https://theirwebsite.com --wait --json
migma projects use <projectId>
```

## "Export this email to Klaviyo"

```bash
migma export klaviyo <conversationId> --json
```

## "Add these contacts to our list"

```bash
# Single contact
migma contacts add --email john@example.com --firstName John --lastName Doe --json

# Bulk from CSV
migma contacts import ./contacts.csv --json
```

## "Set up a sending domain for us"

```bash
# Instant (no DNS)
migma domains managed create companyname --json
# → hello@companyname.migma.email is ready immediately
```

## "Create a product launch email, validate it, then send to our launch list"

```bash
# Generate
migma generate "Product launch announcement — our new feature is live" --wait --save ./launch.html --json

# Validate
migma validate all --html ./launch.html --json

# Send test first
migma send --to test@company.com --subject "Product Launch" --html ./launch.html \
  --from hello@company.migma.email --from-name "Company" --json

# Send to segment
migma send --segment <segmentId> --subject "Product Launch" --html ./launch.html \
  --from hello@company.migma.email --from-name "Company" --json
```
