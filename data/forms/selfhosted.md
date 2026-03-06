# Self-Hosted Form Solutions

## When to Self-Host

| Scenario | Self-Host? | Reason |
|----------|------------|--------|
| Internal surveys | Maybe | Depends on data sensitivity |
| Customer-facing forms | No | SaaS is easier, faster |
| Research/academic | Yes | Data control, ethics requirements |
| Healthcare/finance | Yes | Compliance (HIPAA, PCI) |
| High volume (10K+/month) | Yes | Cost savings |
| Full customization | Yes | No platform limits |

## Recommended Solutions

### HeyForm
- **Best for**: Conversational forms, simple deploy
- **Deploy**: Docker Compose
- **Requirements**: Postgres, SMTP

```yaml
# docker-compose.yml
services:
  heyform:
    image: heyform/heyform:latest
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://...
      SESSION_SECRET: your-secret
      SMTP_HOST: smtp.example.com
```

### OpnForm
- **Best for**: Typeform alternative, full featured
- **Deploy**: Docker or Laravel native
- **Requirements**: MySQL/Postgres, Redis

```yaml
services:
  opnform-api:
    image: jhumanj/opnform-api:latest
  opnform-client:
    image: jhumanj/opnform-client:latest
```

### SurveyJS (Library)
- **Best for**: Embedding in your own app
- **Deploy**: npm package in your app
- **Requirements**: None (frontend only) or your backend

```bash
npm install survey-core survey-react-ui
```

### Formbricks
- **Best for**: In-app surveys, product feedback
- **Deploy**: Docker
- **Requirements**: Postgres

```bash
docker run -d -p 3000:3000 \
  -e DATABASE_URL=postgres://... \
  formbricks/formbricks:latest
```

## Build Your Own (Code)

### Minimal Stack
- Frontend: React Hook Form or plain HTML
- Backend: API route (Next.js, Express, etc.)
- Storage: Supabase, Postgres, MongoDB
- Files: S3/R2/Supabase Storage

### Example: Next.js API Route
```ts
// pages/api/submit.ts
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  
  const { email, name, message } = req.body;
  
  // Validate
  if (!email || !name) {
    return res.status(400).json({ error: 'Missing fields' });
  }
  
  // Store
  await db.submissions.create({ email, name, message });
  
  // Notify
  await sendEmail({ to: 'admin@co.com', subject: 'New form', body: `...` });
  
  return res.status(200).json({ success: true });
}
```

## Data Storage Patterns

### Structured (Relational)
```sql
CREATE TABLE submissions (
  id SERIAL PRIMARY KEY,
  form_id VARCHAR(50),
  data JSONB,
  submitted_at TIMESTAMP DEFAULT NOW(),
  ip_address INET,
  user_agent TEXT
);
```

### Document (MongoDB)
```js
{
  formId: "contact-form",
  fields: {
    email: "user@example.com",
    name: "John",
    message: "Hello..."
  },
  metadata: {
    submittedAt: ISODate("..."),
    ip: "1.2.3.4",
    source: "homepage"
  }
}
```

## Security Checklist

- [ ] HTTPS only
- [ ] Rate limiting (100/hour/IP typical)
- [ ] CSRF protection (token or SameSite cookies)
- [ ] Input sanitization
- [ ] File upload scanning
- [ ] Admin auth for viewing submissions
- [ ] Encrypted at rest
- [ ] Regular backups
- [ ] Audit logging

## Compliance

### GDPR
- Consent checkbox required
- Right to deletion (API or admin UI)
- Data export capability
- Privacy policy link
- Cookie consent if tracking

### HIPAA (Healthcare)
- Business Associate Agreement with hosting
- Encryption in transit and at rest
- Access logging
- No PHI in URLs or logs

### SOC 2
- Access controls documented
- Incident response plan
- Regular security reviews
