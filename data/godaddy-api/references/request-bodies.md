# Request Body Schemas

## Domain Purchase

```json
{
  "domain": "example.com",
  "privacy": true,
  "nameServers": ["ns01.domaincontrol.com", "ns02.domaincontrol.com"],
  "consent": {
    "agreedBy": "192.0.2.1",
    "agreedAt": "2024-01-01T00:00:00Z",
    "agreementKeys": ["DNRA"]
  },
  "period": 1,
  "contactAdmin": {
    "nameFirst": "John",
    "nameLast": "Doe",
    "email": "john@example.com",
    "phone": "+1.5555551234",
    "addressMailing": {
      "address1": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "postalCode": "12345",
      "country": "US"
    }
  },
  "contactRegistrant": { /* same as contactAdmin */ },
  "contactBilling": { /* same as contactAdmin */ },
  "contactTech": { /* same as contactAdmin */ }
}
```

## Domain Renewal

```json
{
  "period": 1
}
```

## DNS Record (single)

```json
{
  "type": "A",
  "name": "@",
  "data": "192.0.2.1",
  "ttl": 3600
}
```

## DNS Records (array for add/replace)

```json
[
  {
    "type": "A",
    "name": "@",
    "data": "192.0.2.1",
    "ttl": 3600
  },
  {
    "type": "CNAME",
    "name": "www",
    "data": "example.com",
    "ttl": 3600
  },
  {
    "type": "TXT",
    "name": "_acme-challenge",
    "data": "verification-token-here",
    "ttl": 600
  },
  {
    "type": "MX",
    "name": "@",
    "data": "mail.example.com",
    "priority": 10,
    "ttl": 3600
  }
]
```

## Bulk Availability Check

```json
["example.com", "example.net", "example.org"]
```

## Certificate Order

```json
{
  "type": "DV_SSL",
  "commonName": "example.com",
  "period": 1,
  "productId": "ssl123",
  "slotSize": "5"
}
```

## Notes

- Use templates in `assets/payload-templates/` as starting points
- Always validate JSON before sending
- Check required fields per endpoint in official docs
- TTL is in seconds (common values: 600, 1800, 3600, 86400)
- Priority field only for MX/SRV records
