# 📘 Zoho Skill for OpenClaw

[![Zoho Integration](https://img.shields.io/badge/Zoho-CRM-blue)](https://www.zoho.com)
[![Version](https://img.shields.io/badge/Version-1.0.0-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

**Automate Zoho CRM, Books, Desk, Creator, and 50+ Zoho apps** - Complete OAuth2 authentication and API integration skill for OpenClaw.

## ✨ Features

- 🔐 **Secure OAuth2 Authentication** - Complete token management
- 📊 **Zoho CRM API** - Leads, Contacts, Deals, Accounts
- 💰 **Zoho Books API** - Invoicing, Expenses, Reports
- 🎫 **Zoho Desk API** - Ticketing and Support
- 📝 **Zoho Creator API** - Form submissions and data
- 📧 **Zoho Campaigns API** - Email marketing
- 🔄 **Auto Token Refresh** - Never worry about expired tokens
- 📡 **Webhook Support** - Real-time updates
- 🌐 **Multi-DC Support** - US, EU, AU, IN, CN, JP

## 🚀 Quick Start

### Prerequisites

1. Zoho Account (free or paid)
2. API Client credentials
3. OAuth2 knowledge

### Setup Steps

**Step 1:** Create Zoho API Client
🔗 https://api-console.zoho.com/

**Step 2:** Generate Refresh Token
```bash
# Get authorization code
https://accounts.zoho.com/oauth/v2/auth?
scope=ZohoCRM.modules.ALL&
client_id=YOUR_CLIENT_ID&
response_type=code&
access_type=offline&
redirect_uri=YOUR_URI
```

**Step 3:** Set Environment Variables
```bash
export ZOHO_CLIENT_ID="your-client-id"
export ZOHO_CLIENT_SECRET="your-client-secret"
export ZOHO_REFRESH_TOKEN="your-refresh-token"
```

**Step 4:** Start Using!
```markdown
[Zoho]
action: get_leads
filters:
  status: Not Contacted
```

---

## 📖 Documentation

- **[SKILL.md](SKILL.md)** - Complete technical documentation
- **[EXAMPLES.md](EXAMPLES.md)** - Use case examples
- **[SETUP.md](SETUP.md)** - Step-by-step setup guide

---

## 🎯 Use Cases

### 🍽️ Restaurant Business
- Table bookings → CRM contact → Invoice
- Customer support tickets
- Marketing campaigns

### 🛒 SaaS Company
- Lead management pipeline
- Subscription billing
- Customer support

### 🏢 Any Business
- Contact database management
- Invoice automation
- Help desk integration

---

## 📦 What's Included

```
zoho/
├── 📄 SKILL.md          ← Full documentation
├── 📄 README.md          ← This file
├── 📄 SETUP.md          ← Installation guide
├── 📄 EXAMPLES.md       ← Use cases
└── 📄 package.json      ← Package metadata
```

---

## 🔧 Commands

### CRM Operations
```markdown
[Zoho CRM]
action: create_lead
data:
  Company: My Company
  Last_Name: Customer Name
  Email: customer@example.com
```

### Books Operations
```markdown
[Zoho Books]
action: create_invoice
customer_id: "123456"
items:
  - name: Service Fee
    rate: 100
    quantity: 5
```

### Desk Operations
```markdown
[Zoho Desk]
action: create_ticket
subject: "Customer Issue"
priority: High
description: "Customer reported a problem..."
```

---

## 📊 Supported Zoho Products

| Product | Status | API |
|---------|--------|-----|
| Zoho CRM | ✅ Ready | Full Support |
| Zoho Books | ✅ Ready | Full Support |
| Zoho Desk | ✅ Ready | Full Support |
| Zoho Creator | ✅ Ready | Full Support |
| Zoho Campaigns | ✅ Ready | Full Support |
| Zoho Inventory | 🔜 Coming Soon | - |
| Zoho Projects | 🔜 Coming Soon | - |

---

## 🔐 Security

- ✅ OAuth2 authentication
- ✅ Token refresh automation
- ✅ HTTPS required
- ✅ Environment variable storage

---

## 📈 Performance

- Token caching
- Request rate limiting
- Retry logic
- Batch operations

---

## 🤝 Contributing

Contributions welcome! See [SKILL.md](SKILL.md) for details.

1. Fork the repository
2. Create feature branch
3. Submit Pull Request

---

## 📝 License

MIT License - See LICENSE file

---

## 🆘 Support

- **Documentation:** See [SKILL.md](SKILL.md)
- **Zoho Docs:** https://www.zoho.com/developer/
- **Issues:** Report on GitHub

---

**Happy Zoho Automation!** 🚀📊

Made with ❤️ for the OpenClaw Community
