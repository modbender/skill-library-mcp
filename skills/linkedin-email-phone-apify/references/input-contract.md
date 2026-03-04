# Input contract

Required:
- `linkedinUrls` (array of LinkedIn profile URLs)

Optional toggles:
- `includeEmails` (default `true`)
- `includePhones` (default `true`)

Email branch options:
- `includeWorkEmails` (default `true`)
- `includePersonalEmails` (default `true`)
- `onlyWithEmails` (default `true`)

Phone branch options:
- `onlyWithPhones` (default `true`)

Hardcoded actor IDs:
- Phone actor: `X95BXRaFOqZ7rzjxM`
- Email actor: `q3wko0Sbx6ZAAB2xf`

Example:

```json
{
  "linkedinUrls": [
    "https://www.linkedin.com/in/williamhgates",
    "https://www.linkedin.com/in/jeffweiner08"
  ],
  "includeEmails": true,
  "includePhones": true,
  "includeWorkEmails": true,
  "includePersonalEmails": true,
  "onlyWithEmails": true,
  "onlyWithPhones": true
}
```
