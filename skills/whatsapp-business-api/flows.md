# Flows — WhatsApp Business API

WhatsApp Flows let you create multi-step interactive forms and experiences directly in WhatsApp.

## Overview

Flows are JSON-based interactive screens that can:
- Collect structured data (forms)
- Display information
- Navigate between screens
- Submit data to your endpoint

---

## Flow Structure

```json
{
  "version": "3.1",
  "screens": [
    {
      "id": "WELCOME",
      "title": "Welcome",
      "layout": {
        "type": "SingleColumnLayout",
        "children": [...]
      }
    }
  ]
}
```

---

## Component Types

### TextHeading

```json
{
  "type": "TextHeading",
  "text": "Welcome to Our Service"
}
```

### TextBody

```json
{
  "type": "TextBody",
  "text": "Please fill out the form below to get started."
}
```

### TextInput

```json
{
  "type": "TextInput",
  "name": "full_name",
  "label": "Full Name",
  "required": true,
  "input-type": "text"
}
```

Input types: `text`, `number`, `email`, `password`, `passcode`, `phone`

### TextArea

```json
{
  "type": "TextArea",
  "name": "comments",
  "label": "Additional Comments",
  "required": false
}
```

### Dropdown

```json
{
  "type": "Dropdown",
  "name": "country",
  "label": "Country",
  "required": true,
  "data-source": [
    {"id": "us", "title": "United States"},
    {"id": "uk", "title": "United Kingdom"},
    {"id": "ca", "title": "Canada"}
  ]
}
```

### RadioButtonsGroup

```json
{
  "type": "RadioButtonsGroup",
  "name": "plan",
  "label": "Select Plan",
  "required": true,
  "data-source": [
    {"id": "basic", "title": "Basic - $9/mo"},
    {"id": "pro", "title": "Pro - $29/mo"},
    {"id": "enterprise", "title": "Enterprise - Contact us"}
  ]
}
```

### CheckboxGroup

```json
{
  "type": "CheckboxGroup",
  "name": "features",
  "label": "Select Features",
  "required": true,
  "min-selected-items": 1,
  "max-selected-items": 3,
  "data-source": [
    {"id": "analytics", "title": "Analytics"},
    {"id": "support", "title": "Priority Support"},
    {"id": "api", "title": "API Access"}
  ]
}
```

### DatePicker

```json
{
  "type": "DatePicker",
  "name": "appointment_date",
  "label": "Select Date",
  "required": true,
  "min-date": "1704067200000",
  "max-date": "1735689600000"
}
```

### Footer (with navigation)

```json
{
  "type": "Footer",
  "label": "Continue",
  "on-click-action": {
    "name": "navigate",
    "next": {
      "type": "screen",
      "name": "NEXT_SCREEN"
    },
    "payload": {
      "full_name": "${form.full_name}"
    }
  }
}
```

---

## Complete Flow Example

```json
{
  "version": "3.1",
  "screens": [
    {
      "id": "CONTACT_INFO",
      "title": "Contact Information",
      "layout": {
        "type": "SingleColumnLayout",
        "children": [
          {
            "type": "TextHeading",
            "text": "Let's get your details"
          },
          {
            "type": "TextInput",
            "name": "full_name",
            "label": "Full Name",
            "required": true,
            "input-type": "text"
          },
          {
            "type": "TextInput",
            "name": "email",
            "label": "Email",
            "required": true,
            "input-type": "email"
          },
          {
            "type": "TextInput",
            "name": "phone",
            "label": "Phone Number",
            "required": true,
            "input-type": "phone"
          },
          {
            "type": "Footer",
            "label": "Next",
            "on-click-action": {
              "name": "navigate",
              "next": {
                "type": "screen",
                "name": "PREFERENCES"
              },
              "payload": {
                "full_name": "${form.full_name}",
                "email": "${form.email}",
                "phone": "${form.phone}"
              }
            }
          }
        ]
      }
    },
    {
      "id": "PREFERENCES",
      "title": "Your Preferences",
      "data": {
        "full_name": {"type": "string", "__example__": "John Doe"},
        "email": {"type": "string", "__example__": "john@example.com"},
        "phone": {"type": "string", "__example__": "+1234567890"}
      },
      "layout": {
        "type": "SingleColumnLayout",
        "children": [
          {
            "type": "TextHeading",
            "text": "Hello, ${data.full_name}!"
          },
          {
            "type": "Dropdown",
            "name": "plan",
            "label": "Select Plan",
            "required": true,
            "data-source": [
              {"id": "starter", "title": "Starter - Free"},
              {"id": "pro", "title": "Pro - $19/mo"},
              {"id": "business", "title": "Business - $49/mo"}
            ]
          },
          {
            "type": "CheckboxGroup",
            "name": "interests",
            "label": "Interests",
            "required": false,
            "data-source": [
              {"id": "updates", "title": "Product Updates"},
              {"id": "tips", "title": "Tips & Tricks"},
              {"id": "offers", "title": "Special Offers"}
            ]
          },
          {
            "type": "Footer",
            "label": "Submit",
            "on-click-action": {
              "name": "complete",
              "payload": {
                "full_name": "${data.full_name}",
                "email": "${data.email}",
                "phone": "${data.phone}",
                "plan": "${form.plan}",
                "interests": "${form.interests}"
              }
            }
          }
        ]
      }
    }
  ]
}
```

---

## Send Flow Message

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "interactive",
  "interactive": {
    "type": "flow",
    "header": {
      "type": "text",
      "text": "Sign Up"
    },
    "body": {
      "text": "Complete your registration in just 2 steps."
    },
    "footer": {
      "text": "Takes less than 1 minute"
    },
    "action": {
      "name": "flow",
      "parameters": {
        "flow_message_version": "3",
        "flow_token": "unique_flow_instance_token",
        "flow_id": "123456789",
        "flow_cta": "Sign Up Now",
        "flow_action": "navigate",
        "flow_action_payload": {
          "screen": "CONTACT_INFO"
        }
      }
    }
  }
}
```

---

## Receive Flow Response

When user completes a flow, you receive a webhook:

```json
{
  "messages": [
    {
      "from": "1234567890",
      "id": "wamid.xxxxx",
      "type": "interactive",
      "interactive": {
        "type": "nfm_reply",
        "nfm_reply": {
          "response_json": "{\"full_name\":\"John Doe\",\"email\":\"john@example.com\",\"plan\":\"pro\"}",
          "body": "Sent",
          "name": "flow"
        }
      }
    }
  ]
}
```

---

## Create Flow via API

```bash
curl -X POST "https://graph.facebook.com/v21.0/$WHATSAPP_BUSINESS_ACCOUNT_ID/flows" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "signup_flow",
    "categories": ["SIGN_UP"]
  }'
```

Then upload the flow JSON:

```bash
curl -X POST "https://graph.facebook.com/v21.0/{flow_id}/assets" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -F "name=flow.json" \
  -F "file=@flow.json"
```

---

## Flow Categories

| Category | Use Case |
|----------|----------|
| SIGN_UP | Registration, onboarding |
| SIGN_IN | Login, authentication |
| APPOINTMENT_BOOKING | Scheduling |
| LEAD_GENERATION | Sales inquiries |
| CONTACT_US | Support requests |
| CUSTOMER_SUPPORT | Help desk |
| SURVEY | Feedback collection |
| OTHER | General purpose |

---

## Best Practices

1. **Keep it short** — Max 3-5 screens per flow
2. **Use clear labels** — Avoid jargon
3. **Validate on server** — Don't trust client data
4. **Provide feedback** — Confirm submission success
5. **Handle errors** — Show user-friendly messages
6. **Test thoroughly** — Use preview before publishing
