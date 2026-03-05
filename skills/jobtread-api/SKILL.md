# Skill: JobTread via Pave Query API

## Summary
This skill lets you operate JobTread entirely through openclaw using the Pave-based API at `https://api.jobtread.com/pave`. Every request is a single POST with a `query` object that mirrors GraphQL-style expressions, and you decide which fields you want back. With the right grant key, you can create and manage accounts (customers/vendors), jobs, documents, tasks, locations, custom fields, documents, and even subscribe to webhooks for live updates.

## Setup & Credentials
1. **Create a grant:** Login to https://app.jobtread.com/grants and create a new grant for automation. Copy the one-time `grantKey` (it begins with `grant_` and will only show once).
2. **Store the key locally:** Use a secure file such as `~/.config/jobtread/grant_key`. Example:
   ```bash
   mkdir -p ~/.config/jobtread
   echo "grant_xxx" > ~/.config/jobtread/grant_key
   chmod 600 ~/.config/jobtread/grant_key
   ```
3. **Keep it fresh:** JobTread expires keys after 3 months of inactivity, so schedule a reminder (cron/heartbeat) to rotate or re-use the grant before expiration.
4. **Optional webhook secret:** If you plan to receive webhooks, note your endpoint URL and save the webhook ID in the same folder so you can disable or inspect it later.

## Authentication
- Every POST to `/pave` must include the grant key under `query.$.grantKey`. Example payload:
  ```json
  {
    "query": {
      "$": { "grantKey": "grant_xxx" },
      "currentGrant": { "id": {}, "user": { "name": {} } }
    }
  }
  ```
- You can also set `notify`, `timeZone`, or `viaUserId` inside `$` when you need to suppress notifications or scope results.
- For signed queries (PDF tokens, pre-signed data), call `pdfToken: { _: signQuery, $: { query: {...} } }` and append the token to `https://api.jobtread.com/t/`.

## API Basics & Request Flow
- All requests go to `POST https://api.jobtread.com/pave` with `Content-Type: application/json`.
- Structure:
  ```json
  {
    "query": {
      "$": { "grantKey": "grant_xxx" },  
      "operation": {
        "$": { ...inputs... },
        "field": { ...fields... }
      }
    }
  }
  ```
- Fields you request (`id`, `name`, etc.) determine what JobTread returns. Always include `id` when you plan to reference the object later.
- `_type` in responses tells you the schema for that node.

## Common Patterns & Examples
### 1. Discover your organization ID
```yaml
currentGrant:
  user:
    memberships:
      nodes:
        organization:
          id: {}
          name: {}
```
Use the returned `organization.id` in any following query.

### 2. Create customers/vendors
- **Customer**
```yaml
createAccount:
  $:
    name: "Test Customer"
    type: customer
    organizationId: "ORG_ID"
  createdAccount:
    id: {}
    name: {}
    type: {}
```
- **Vendor** (same as above but `type: vendor`).

### 3. Read or update accounts
- **Read account** by supplying `id` and requesting fields:
```yaml
account:
  $:
    id: "ACCOUNT_ID"
  id: {}
  name: {}
  isTaxable: {}
```
- **Update** and include `customFieldValues` if needed:
```yaml
updateAccount:
  $:
    id: "ACCOUNT_ID"
    isTaxable: false
  account:
    id: {}
    isTaxable: {}
```

### 4. Query accounts list with pagination, sorting, and filters
```yaml
organization:
  $: {}
  id: {}
  accounts:
    $:
      size: 5
      page: "1"
      sortBy:
        - field: type
          order: desc
      where:
        and:
          - - type
            - =
            - customer
          - - name
            - =
            - "Sebas Clients"
    nextPage: {}
    nodes:
      id: {}
      name: {}
      type: {}
```

### 5. Use `where` with `or`, nested fields, or custom fields
- Find account by custom field name:
```yaml
organization:
  $: {}
  id: {}
  contacts:
    $:
      with:
        cf:
          _: customFieldValues
          $:
            where:
              - - customField
                - name
              - "VIP"
            values:
              $:
                field: value
      where:
        - - cf
          - values
        - =
        - "Yes"
    nodes:
      id: {}
      name: {}
```

### 6. Locations and nested filters
Create location and find others tied to the same account:
```yaml
createLocation:
  $:
    accountId: "ACCOUNT_ID"
    name: Test Location
    address: "123 Main St"
  createdLocation:
    id: {}
    name: {}

organization:
  $: {}
  id: {}
  locations:
    $:
      where:
        - - account
          - name
        - Test Name
    nodes:
      id: {}
      name: {}
      account:
        id: {}
        name: {}
```

### 7. Documents, jobs, and aggregates
- Get a job's documents grouped by type/status and sums:
```yaml
job:
  $:
    id: "JOB_ID"
  documents:
    $:
      where:
        - - type
          - in
          - - customerInvoice
            - customerOrder
      group:
        by:
          - type
          - status
        aggs:
          amountPaid:
            sum: amountPaid
          priceWithTax:
            sum: priceWithTax
    withValues: {}
```
- Get document PDF token (append to `https://api.jobtread.com/t/{{token}}`):
```yaml
pdfToken:
  _: signQuery
  $:
    query:
      pdf:
        $:
          id: "DOCUMENT_ID"
```

### 8. Custom fields
- Read a record's custom field values (limit 25 per request):
```yaml
account:
  $:
    id: "ACCOUNT_ID"
  customFieldValues:
    $:
      size: 25
    nodes:
      id: {}
      value: {}
      customField:
        id: {}
```
- Update a custom field via `customFieldValues` map:
```yaml
updateAccount:
  $:
    id: "ACCOUNT_ID"
    customFieldValues:
      "CUSTOM_FIELD_ID": "New value"
  account:
    id: {}
```

### 9. Webhooks
- Use the JobTread UI to create a webhook (Webhooks page) and copy its ID.
- Manage them via the API: list `webhook(id: "ID")` or `deleteWebhook` to cancel.
- Example create query:
```yaml
createWebhook:
  $:
    organizationId: "ORG_ID"
    url: "https://your-endpoint/hooks/jobtread"
    eventTypes:
      - jobCreated
      - documentUploaded
  createdWebhook:
    id: {}
    url: {}
```

## Using This Skill with OpenClaw
- Use `curl` or your preferred HTTP client from OpenClaw's `exec` tool.
- Build the JSON payload as shown (always include the grant key inside `$`).
- You can also wrap the payload in shell variables or helper scripts for portability.
- Save reusable queries in the skill file or separate scripts so Claude or you can call them by name ("run job summary", "create customer", etc.).
- Document each automation in the JobTread vault so you can copy/paste from future sessions without digging through logs.

## Automation Ideas
1. **Nightly job summary:** Query each open job, sum approved customer orders, and store results in Obsidian (or send via WhatsApp).
2. **Webhook monitor:** Automatically spin up a webhook for file uploads and forward notifications to your Slack/WhatsApp via a small server.
3. **Batch account creation:** Feed a CSV of customers/vendors and run `createAccount` for each with the same grant key.
4. **Document check-ins:** Query documents with `status: pending` and send you a summary each morning.

## Troubleshooting & Tips
- **Rate limits:** Grant keys have a throughput cap. If you hit rate limits, add `time.sleep` between requests or batch fewer objects.
- **Missing IDs:** The API complains `id field required` when you forget to request `id`. Always include it when you plan to mutate the record later.
- **Grant expiration:** If a request returns `invalid key`, rotate the grant and update `~/.config/jobtread/grant_key`.
- **Webhooks:** Keep a log of webhook IDs so you can disable or reconfigure them later.
- **Signed tokens:** Use `signQuery` when you need temporary access to document PDFs without storing raw document IDs.

