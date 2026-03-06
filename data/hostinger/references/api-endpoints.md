# Hostinger API Reference

Full API documentation: https://developers.hostinger.com

## Base URL
`https://developers.hostinger.com`

## Authentication
Bearer token in Authorization header:
```
Authorization: Bearer YOUR_API_TOKEN
```

## API Endpoints by Category

### Billing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/billing/v1/catalog | Get catalog items |
| GET | /api/billing/v1/subscriptions | List subscriptions |
| DELETE | /api/billing/v1/subscriptions/{id} | Cancel subscription |
| DELETE | /api/billing/v1/subscriptions/{id}/auto-renewal/disable | Disable auto-renewal |
| PATCH | /api/billing/v1/subscriptions/{id}/auto-renewal/enable | Enable auto-renewal |
| GET | /api/billing/v1/payment-methods | List payment methods |
| POST | /api/billing/v1/payment-methods/{id} | Set default payment |
| DELETE | /api/billing/v1/payment-methods/{id} | Delete payment method |

### VPS
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vps/v1/virtual-machines | List VMs |
| POST | /api/vps/v1/virtual-machines | Create VM |
| GET | /api/vps/v1/virtual-machines/{id} | Get VM details |
| POST | /api/vps/v1/virtual-machines/{id}/start | Start VM |
| POST | /api/vps/v1/virtual-machines/{id}/stop | Stop VM |
| POST | /api/vps/v1/virtual-machines/{id}/restart | Restart VM |
| POST | /api/vps/v1/virtual-machines/{id}/recreate | Recreate VM |
| GET | /api/vps/v1/virtual-machines/{id}/metrics | Get metrics |
| PUT | /api/vps/v1/virtual-machines/{id}/hostname | Set hostname |
| DELETE | /api/vps/v1/virtual-machines/{id}/hostname | Clear hostname |
| PUT | /api/vps/v1/virtual-machines/{id}/nameservers | Set nameservers |
| PUT | /api/vps/v1/virtual-machines/{id}/root-password | Set password |
| PUT | /api/vps/v1/virtual-machines/{id}/panel-password | Set panel password |
| GET | /api/vps/v1/data-centers | List datacenters |
| GET | /api/vps/v1/templates | List OS templates |
| GET | /api/vps/v1/templates/{id} | Get template |

### VPS Snapshots
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vps/v1/virtual-machines/{id}/snapshot | Get snapshot |
| POST | /api/vps/v1/virtual-machines/{id}/snapshot | Create snapshot |
| DELETE | /api/vps/v1/virtual-machines/{id}/snapshot | Delete snapshot |
| POST | /api/vps/v1/virtual-machines/{id}/snapshot/restore | Restore snapshot |

### VPS Backups
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vps/v1/virtual-machines/{id}/backups | List backups |
| POST | /api/vps/v1/virtual-machines/{id}/backups/{backupId}/restore | Restore backup |

### VPS Recovery
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/vps/v1/virtual-machines/{id}/recovery | Start recovery mode |
| DELETE | /api/vps/v1/virtual-machines/{id}/recovery | Stop recovery mode |

### VPS Docker Manager
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vps/v1/virtual-machines/{id}/docker | List projects |
| POST | /api/vps/v1/virtual-machines/{id}/docker | Create project |
| GET | /api/vps/v1/virtual-machines/{id}/docker/{project} | Get project |
| GET | /api/vps/v1/virtual-machines/{id}/docker/{project}/containers | List containers |
| GET | /api/vps/v1/virtual-machines/{id}/docker/{project}/logs | Get logs |
| POST | /api/vps/v1/virtual-machines/{id}/docker/{project}/start | Start project |
| POST | /api/vps/v1/virtual-machines/{id}/docker/{project}/stop | Stop project |
| POST | /api/vps/v1/virtual-machines/{id}/docker/{project}/restart | Restart project |
| POST | /api/vps/v1/virtual-machines/{id}/docker/{project}/update | Update project |
| DELETE | /api/vps/v1/virtual-machines/{id}/docker/{project}/down | Delete project |

### VPS Firewall
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vps/v1/firewall | List firewalls |
| POST | /api/vps/v1/firewall | Create firewall |
| GET | /api/vps/v1/firewall/{id} | Get firewall |
| DELETE | /api/vps/v1/firewall/{id} | Delete firewall |
| POST | /api/vps/v1/firewall/{id}/activate/{vmId} | Activate on VM |
| POST | /api/vps/v1/firewall/{id}/deactivate/{vmId} | Deactivate on VM |
| POST | /api/vps/v1/firewall/{id}/sync/{vmId} | Sync rules |
| POST | /api/vps/v1/firewall/{id}/rules | Add rule |
| PUT | /api/vps/v1/firewall/{id}/rules/{ruleId} | Update rule |
| DELETE | /api/vps/v1/firewall/{id}/rules/{ruleId} | Delete rule |

### VPS SSH Keys
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vps/v1/public-keys | List keys |
| POST | /api/vps/v1/public-keys | Add key |
| DELETE | /api/vps/v1/public-keys/{id} | Delete key |
| POST | /api/vps/v1/public-keys/attach/{vmId} | Attach to VM |
| GET | /api/vps/v1/virtual-machines/{id}/public-keys | List VM keys |

### VPS PTR Records
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/vps/v1/virtual-machines/{id}/ptr/{ipId} | Set PTR record |
| DELETE | /api/vps/v1/virtual-machines/{id}/ptr/{ipId} | Delete PTR |

### VPS Post-Install Scripts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vps/v1/post-install-scripts | List scripts |
| POST | /api/vps/v1/post-install-scripts | Create script |
| GET | /api/vps/v1/post-install-scripts/{id} | Get script |
| PUT | /api/vps/v1/post-install-scripts/{id} | Update script |
| DELETE | /api/vps/v1/post-install-scripts/{id} | Delete script |

### VPS Malware Scanner (Monarx)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/vps/v1/virtual-machines/{id}/monarx | Get scan metrics |
| POST | /api/vps/v1/virtual-machines/{id}/monarx | Install scanner |
| DELETE | /api/vps/v1/virtual-machines/{id}/monarx | Uninstall scanner |

### DNS Zone
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dns/v1/zones/{domain} | Get records |
| PUT | /api/dns/v1/zones/{domain} | Update records |
| DELETE | /api/dns/v1/zones/{domain} | Delete records |
| POST | /api/dns/v1/zones/{domain}/reset | Reset to defaults |
| POST | /api/dns/v1/zones/{domain}/validate | Validate records |

### DNS Snapshots
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dns/v1/snapshots/{domain} | List snapshots |
| GET | /api/dns/v1/snapshots/{domain}/{id} | Get snapshot |
| POST | /api/dns/v1/snapshots/{domain}/{id}/restore | Restore snapshot |

### Domains Portfolio
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/domains/v1/portfolio | List domains |
| POST | /api/domains/v1/portfolio | Purchase domain |
| GET | /api/domains/v1/portfolio/{domain} | Get domain |
| PUT | /api/domains/v1/portfolio/{domain}/nameservers | Update NS |
| PUT | /api/domains/v1/portfolio/{domain}/domain-lock | Enable lock |
| DELETE | /api/domains/v1/portfolio/{domain}/domain-lock | Disable lock |
| PUT | /api/domains/v1/portfolio/{domain}/privacy-protection | Enable privacy |
| DELETE | /api/domains/v1/portfolio/{domain}/privacy-protection | Disable privacy |

### Domains Availability
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/domains/v1/availability | Check availability |

### Domains Forwarding
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/domains/v1/forwarding/{domain} | Get forwarding |
| POST | /api/domains/v1/forwarding | Create forwarding |
| DELETE | /api/domains/v1/forwarding/{domain} | Delete forwarding |

### Domains WHOIS
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/domains/v1/whois | List profiles |
| POST | /api/domains/v1/whois | Create profile |
| GET | /api/domains/v1/whois/{id} | Get profile |
| DELETE | /api/domains/v1/whois/{id} | Delete profile |
| GET | /api/domains/v1/whois/{id}/usage | Get usage |

### Hosting Websites
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/hosting/v1/websites | List websites |
| POST | /api/hosting/v1/websites | Create website |
| GET | /api/hosting/v1/datacenters | List datacenters |
| GET | /api/hosting/v1/orders | List orders |
| POST | /api/hosting/v1/domains/free-subdomains | Create subdomain |
| POST | /api/hosting/v1/domains/verify-ownership | Verify domain |

### Domain Verifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v2/direct/verifications/active | Get verifications |

## Rate Limits

API enforces rate limits. If exceeded:
- Returns 429 Too Many Requests
- IP may be temporarily blocked if exceeded repeatedly

Rate limit headers are included in responses.

## Error Responses

Errors return JSON with:
- `error`: Human-readable message
- `correlation_id`: For support requests

## SDKs & Tools

- Python: `pip install hostinger_api`
- Node/TS: `npm install hostinger-api-sdk`
- PHP: `composer require hostinger/api-php-sdk`
- CLI: https://github.com/hostinger/api-cli
- MCP Server: https://github.com/hostinger/api-mcp-server
- Ansible: https://github.com/hostinger/ansible-collection-hostinger
- Terraform: https://github.com/hostinger/terraform-provider-hostinger
