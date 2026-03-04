# Form Platforms Comparison

## No-Code Platforms

### Google Forms
- **Best for**: Quick surveys, internal use, free
- **Limitations**: Limited styling, no conditional logic branching, basic embeds
- **Integrations**: Google Sheets native, Zapier for rest
- **API**: Yes, for reading responses

### Typeform
- **Best for**: Beautiful conversational forms, high engagement
- **Limitations**: Expensive at scale, slow load times
- **Integrations**: Native to many tools, webhooks, Zapier
- **Hidden gem**: Logic jumps + calculator for quiz funnels

### Tally
- **Best for**: Notion-like experience, generous free tier
- **Limitations**: Less enterprise features
- **Integrations**: Webhooks, Notion, Slack, email

### Jotform
- **Best for**: Complex forms, PDF generation, payments
- **Limitations**: UI feels dated
- **Integrations**: 100+ native, payments built-in

### Formbricks
- **Best for**: In-app surveys, open-source option
- **Limitations**: Newer, smaller community
- **Self-host**: Yes, Docker available

## Open Source (Self-Hosted)

### HeyForm
- **Stack**: React + Node
- **Features**: Conversational forms, analytics, embeds
- **Deploy**: Docker, Railway, Zeabur
- **License**: AGPL

### OpnForm
- **Stack**: Vue + Laravel
- **Features**: No-code builder, embeds, integrations
- **Deploy**: Docker, cloud option available
- **License**: AGPL

### SurveyJS
- **Stack**: JS library (React, Vue, Angular, Knockout)
- **Features**: Embeddable builder, JSON-based, theming
- **License**: MIT for core, commercial for creator
- **Best for**: Embedding in your own app

### OhMyForm
- **Stack**: Node + Angular
- **Features**: Typeform-style, drag-drop
- **Deploy**: Docker
- **License**: MIT

## Code Libraries

### React

| Library | Use Case |
|---------|----------|
| React Hook Form + Zod | Best performance, TypeScript |
| Formik | Legacy, large forms |
| SurveyJS React | Complex surveys in-app |

### Flutter

| Library | Use Case |
|---------|----------|
| flutter_form_builder | Quick scaffolding |
| Native Form widget | Full control |
| reactive_forms | Reactive patterns |

### Vue
- VeeValidate + Yup — validation
- FormKit — full framework

### Plain HTML
- Native validation attrs (required, pattern, min, max)
- JavaScript for conditional logic

## Platform Selection Guide

| Requirement | Recommendation |
|-------------|----------------|
| Free, quick, internal | Google Forms |
| High conversion, looks good | Typeform or Tally |
| Complex logic, calculations | Typeform, Jotform, code |
| Full control, own data | HeyForm, OpnForm (self-host) |
| Embed in own app | SurveyJS |
| Research/academic | Google Forms or code |
| Payments in form | Jotform, Tally |
| Mobile app | Code (RHF, Flutter) |
