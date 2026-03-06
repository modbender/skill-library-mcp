# Form Integrations

## Webhooks

### Basic Webhook Setup
```json
{
  "url": "https://your-api.com/webhook/form",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "X-Webhook-Secret": "your-secret"
  },
  "payload": {
    "form_id": "{{form_id}}",
    "timestamp": "{{submitted_at}}",
    "data": "{{fields}}"
  }
}
```

### Webhook Security
- Verify signature (HMAC-SHA256 of payload)
- Check timestamp (reject old requests)
- Whitelist source IPs if possible
- Use HTTPS only

### Webhook Receivers
| Service | URL Format |
|---------|------------|
| Zapier | zapier.com/hooks/catch/xxx/yyy |
| Make | hook.eu1.make.com/xxx |
| n8n | your-n8n.com/webhook/xxx |
| Pipedream | *.m.pipedream.net |

## Email Marketing

### Mailchimp
```bash
# Add to list
curl -X POST "https://usX.api.mailchimp.com/3.0/lists/{list_id}/members" \
  -H "Authorization: Bearer ${MAILCHIMP_API_KEY}" \
  -d '{"email_address":"user@example.com","status":"subscribed"}'
```

### ConvertKit
```bash
# Add subscriber + tag
curl -X POST "https://api.convertkit.com/v3/tags/{tag_id}/subscribe" \
  -d "api_secret=${CONVERTKIT_SECRET}&email=user@example.com"
```

### Brevo (Sendinblue)
```bash
curl -X POST "https://api.brevo.com/v3/contacts" \
  -H "api-key: ${BREVO_API_KEY}" \
  -d '{"email":"user@example.com","listIds":[5]}'
```

## CRM

### HubSpot
```bash
# Create contact
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts" \
  -H "Authorization: Bearer ${HUBSPOT_TOKEN}" \
  -d '{"properties":{"email":"user@example.com","firstname":"John"}}'
```

### Pipedrive
```bash
# Create person
curl -X POST "https://api.pipedrive.com/v1/persons?api_token=${PIPEDRIVE_TOKEN}" \
  -d '{"name":"John Doe","email":"user@example.com"}'
```

### Salesforce
```bash
# Create lead
curl -X POST "https://your-instance.salesforce.com/services/data/v56.0/sobjects/Lead" \
  -H "Authorization: Bearer ${SF_TOKEN}" \
  -d '{"LastName":"Doe","Email":"user@example.com","Company":"Acme"}'
```

## Databases

### Google Sheets
- Native integration in most form tools
- Webhook → Google Apps Script → Append row
- Zapier/Make as middleware

### Airtable
```bash
curl -X POST "https://api.airtable.com/v0/${BASE_ID}/${TABLE}" \
  -H "Authorization: Bearer ${AIRTABLE_TOKEN}" \
  -d '{"fields":{"Email":"user@example.com","Name":"John"}}'
```

### Notion
```bash
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer ${NOTION_TOKEN}" \
  -H "Notion-Version: 2022-06-28" \
  -d '{"parent":{"database_id":"xxx"},"properties":{...}}'
```

### Supabase
```ts
const { data, error } = await supabase
  .from('submissions')
  .insert({ email, name, message });
```

## Notifications

### Slack
```bash
curl -X POST "https://hooks.slack.com/services/T.../B.../xxx" \
  -d '{"text":"New form submission from user@example.com"}'
```

### Discord
```bash
curl -X POST "${DISCORD_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{"content":"New submission","embeds":[{"title":"Form","fields":[...]}]}'
```

### Telegram
```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}&text=New form: user@example.com"
```

### Email Notification
```ts
// SendGrid
const msg = {
  to: 'admin@company.com',
  from: 'forms@company.com',
  subject: 'New form submission',
  text: `Name: ${name}\nEmail: ${email}\nMessage: ${message}`,
};
await sgMail.send(msg);
```

## Payment in Forms

### Stripe Checkout
1. Create Checkout Session on form submit
2. Redirect to Stripe hosted page
3. Webhook for confirmation

### Stripe Elements (Embedded)
```tsx
<Elements stripe={stripePromise}>
  <CardElement />
  <button onClick={handlePayment}>Pay</button>
</Elements>
```

### PayPal Buttons
```tsx
<PayPalButtons
  createOrder={(data, actions) => {
    return actions.order.create({
      purchase_units: [{ amount: { value: '10.00' } }],
    });
  }}
  onApprove={(data, actions) => {
    return actions.order.capture().then(submitForm);
  }}
/>
```
