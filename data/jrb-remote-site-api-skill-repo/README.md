# JRB Remote Site API Agent Skill 🛡️

This repository houses the OpenClaw Agent Skill for interacting with the **JRB Remote Site API** (v6.4.0+). This skill allows a digital daemon  to securely manage WordPress sites, FluentCRM databases, and FluentSupport tickets.

## 🔗 Official Plugin Links
The agent requires the **JRB Remote Site API** plugin to be installed on the target WordPress site.
- **WordPress Plugin Directory:** [jrb-remote-site-api-for-openclaw](https://wordpress.org/plugins/jrb-remote-site-api-for-openclaw/)
- **GitHub Repository:** [JRBConsulting/jrb-remote-site-api-openclaw](https://github.com/JRBConsulting/jrb-remote-site-api-openclaw)

---

## 🚀 Installation & Setup

### 1. Install the Skill in OpenClaw
To add this skill to your local OpenClaw instance:
```bash
clawhub install jrb-remote-site-api
```
*(Alternatively, clone this repository into your `/workspace/skills/` directory.)*

### 2. Configure Your Agent
Ensure your agent's `TOOLS.md` or `.credentials/` contains the endpoint and token for the site(s) you wish to manage.

---

## 🌐 Managing Multiple Sites

This skill is designed to handle multi-site environments. To manage multiple properties, structure your agent's configuration using a site-mapping approach:

### Example Configuration (`.credentials/jrb-sites.json`)
```json
{
  "site_1": {
    "url": "https://example-site.com",
    "namespace": "jrbremoteapi/v1",
    "token": "YOUR_SECURE_X_JRB_TOKEN"
  },
  "site_2": {
    "url": "https://another-jrb-property.au",
    "namespace": "jrbremoteapi/v1",
    "token": "YOUR_SECURE_X_JRB_TOKEN"
  }
}
```

### Agent Instruction
When asking the agent to perform an action, specify the target:
> *"list the recent FluentCRM subscribers on **site_1**."*

The agent will then look up the corresponding credentials and route the request to the correct `jrbremoteapi/v1` endpoint using the `X-JRB-Token` header.

---

## 🛠️ Capabilities
- **System Info:** Read site version, URL, and plugin status.
- **FluentCRM:** Manage subscribers, lists, and campaigns.
- **FluentSupport:** Read tickets and customer data.
- **Media:** Library management and uploads.

See [SKILL.md](./SKILL.md) for full tool definitions and implementation details.
