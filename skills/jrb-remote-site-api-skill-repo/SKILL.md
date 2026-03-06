---
name: JRB Remote Site API Skill
description: Interface with WordPress sites running the jrb-remote-site-api
  plugin. This skill enables AI agents to perform administrative tasks, content
  management, and integration with the Fluent suite (CRM, ...
---

# JRB Remote Site API Skill

Interface with WordPress sites running the `jrb-remote-site-api` plugin. This skill enables AI agents to perform administrative tasks, content management, and integration with the Fluent suite (CRM, Forms, Support, etc.) via a secure REST API.

## Configuration

Required environment variables for targeting a site:
- `JRB_API_URL`: The base URL of the site (e.g., `https://jrbconsulting.au`)
- `JRB_API_TOKEN`: The secure API token configured in the plugin settings

## Core Capabilities

### 1. System & Auth
- **Ping**: Verify connection and token validity.
- **Site Info**: Get WordPress version, active theme, plugin version, and capabilities.

### 2. Content Management (CRUD)
- **Posts & Pages**: Create, read, update, delete, and list. Supports custom statuses (draft, publish, private).
- **Media**: Upload and manage files in the WordPress Media Library.

### 3. Plugin & Theme Management
- **Plugins**: List, install, activate, deactivate, update, and delete.
- **Themes**: List active/available themes, switch themes, install from URL.

### 4. Fluent Suite Integration (Modules)
- **FluentCRM**: Manage contacts, lists, tags, and campaigns.
- **FluentSupport**: Professional ticket management and customer support.
- **FluentProject**: Task and project management automation.
- **FluentBoards**: Advanced board and task management.

## Usage Patterns

### Verification
```bash
curl -H "X-JRB-Token: \$JRB_API_TOKEN" "\$JRB_API_URL/wp-json/jrb-remote/v1/site"
```

### Create a Page
```bash
curl -X POST -H "X-JRB-Token: \$JRB_API_TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{"title": "New Page", "content": "Hello World", "status": "publish"}' \\
     "\$JRB_API_URL/wp-json/jrb-remote/v1/pages"
```

## Installation
This skill is designed to work with the **JRB Remote Site API** WordPress plugin.
To install:
`clawhub install jrb-remote-site-api`
