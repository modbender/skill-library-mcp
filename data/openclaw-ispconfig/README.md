# @elvatis_com/openclaw-ispconfig

OpenClaw plugin to manage ISPConfig via the Remote JSON API.

## Features

- Session-based API client with auto-reconnect
- 31 tools for read, write, and one-command provisioning
- Safety guards via `readOnly` and `allowedOperations`
- Live integration tests against a real ISPConfig host (read-only)

## ISPConfig API format

This plugin uses the JSON endpoint format:

- URL: `https://server:8080/remote/json.php?method_name`
- Method is passed as query string, not in JSON body
- Body format:
  - login: `{ "username": "...", "password": "..." }`
  - normal calls: `{ "session_id": "...", ...params }`
  - logout: `{ "session_id": "..." }`

## Installation

### ClawHub

```bash
clawhub install openclaw-ispconfig
```

### npm

```bash
npm install @elvatis_com/openclaw-ispconfig
```

## ISPConfig setup

1. In ISPConfig, create a Remote User.
2. Grant required API permissions.
3. Copy endpoint URL and credentials.
4. Configure plugin in OpenClaw.

## Configuration

`openclaw.plugin.json` config keys:

- `apiUrl` (required): ISPConfig JSON API URL
- `username` (required): remote user
- `password` (required, secret): remote password
- `serverId` (default `1`): default server id
- `defaultServerIp` (optional): fallback IP for provisioning DNS A record
- `readOnly` (default `false`): block write tools
- `allowedOperations` (default `[]`): whitelist of tool names
- `verifySsl` (default `true`): TLS certificate verification

## Tools

### Read tools

- `isp_methods_list` params: none
- `isp_system_info` params: none
- `isp_client_list` params: optional filter fields
- `isp_client_get` params: `client_id`
- `isp_sites_list` params: optional filters accepted by `sites_web_domain_get`
- `isp_site_get` params: `primary_id` (or `site_id`, `domain_id`)
- `isp_domains_list` params: none
- `isp_dns_zone_list` params: user-related filter params
- `isp_dns_record_list` params: `zone_id`
- `isp_mail_domain_list` params: optional filters
- `isp_mail_user_list` params: optional filters
- `isp_db_list` params: user-related filters
- `isp_ssl_status` params: none
- `isp_quota_check` params: `client_id`
- `isp_backup_list` params: none (returns skipped if API method unavailable)
- `isp_cron_list` params: optional filters

### Write tools

- `isp_client_add` params: ISPConfig `client_add` payload
- `isp_site_add` params: ISPConfig `sites_web_domain_add` payload
- `isp_domain_add` params: alias for `isp_site_add`
- `isp_dns_zone_add` params: ISPConfig `dns_zone_add` payload
- `isp_dns_record_add` params: include `type` (`A`, `AAAA`, `MX`, `TXT`, `CNAME`) and matching payload
- `isp_dns_record_delete` params: include `type` and matching delete payload
- `isp_mail_domain_add` params: ISPConfig `mail_domain_add` payload
- `isp_mail_user_add` params: ISPConfig `mail_user_add` payload
- `isp_mail_user_delete` params: ISPConfig `mail_user_delete` payload
- `isp_db_add` params: ISPConfig `sites_database_add` payload
- `isp_db_user_add` params: ISPConfig `sites_database_user_add` payload
- `isp_shell_user_add` params: ISPConfig `sites_shell_user_add` payload
- `isp_ftp_user_add` params: ISPConfig `sites_ftp_user_add` payload
- `isp_cron_add` params: ISPConfig `sites_cron_add` payload

### Provisioning tool

- `isp_provision_site`
- Required params:
  - `domain`
  - `clientName`
  - `clientEmail`
- Optional params:
  - `serverIp`
  - `createMail` (default `true`)
  - `createDb` (default `true`)
  - `serverId` (default from config)

Workflow:

1. Create client
2. Create site with SSL and Let's Encrypt enabled
3. Create DNS zone
4. Add DNS records (`A`, `CNAME`, SPF TXT, DMARC TXT)
5. Optionally create mail domain and `info@` + `admin@` mailboxes
6. Optionally create DB user and database
7. Ensure SSL flags are enabled on the site

## Safety

- `readOnly=true` blocks all write and provisioning tools
- `allowedOperations=[...]` allows only named tools

## Development

```bash
npm run build
npm test
```

For live tests, provide environment variables:

- `ISPCONFIG_API_URL`
- `ISPCONFIG_USER`
- `ISPCONFIG_PASS`

## License

MIT
