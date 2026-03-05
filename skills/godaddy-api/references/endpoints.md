# GoDaddy API Endpoints Reference

Base URLs:
- Production: `https://api.godaddy.com`
- OTE (test): `https://api.ote-godaddy.com`

## Domains

| Method | Endpoint | Description |
|---|---|---|
| GET | `/v1/domains` | List domains |
| GET | `/v1/domains/{domain}` | Get domain details |
| GET | `/v1/domains/available?domain={domain}&checkType={FAST\|FULL}&forTransfer={bool}` | Check single availability/transfer |
| POST | `/v1/domains/available?checkType={FAST\|FULL}` | Bulk availability (body: `string[]`) |
| POST | `/v1/domains/purchase/validate` | Validate purchase payload |
| POST | `/v1/domains/purchase` | Purchase domain |
| POST | `/v1/domains/{domain}/renew` | Renew domain |
| POST | `/v1/domains/{domain}/transfer` | Transfer domain in |
| PATCH | `/v1/domains/{domain}` | Update domain settings |
| PATCH | `/v1/domains/{domain}/contacts` | Update domain contacts |
| DELETE | `/v1/domains/{domain}` | Cancel/delete domain |
| PUT | `/v1/domains/{domain}/privacy` | Enable privacy |
| DELETE | `/v1/domains/{domain}/privacy` | Disable privacy |
| GET | `/v1/domains/agreements` | Get domain purchase/transfer agreements |
| POST | `/v1/domains/agreements` | Accept domain agreements |

## DNS

| Method | Endpoint | Description |
|---|---|---|
| GET | `/v1/domains/{domain}/records` | Get all DNS records |
| GET | `/v1/domains/{domain}/records/{type}` | Get records by type |
| GET | `/v1/domains/{domain}/records/{type}/{name}` | Get records by type+name |
| PATCH | `/v1/domains/{domain}/records` | Add/update DNS records |
| PUT | `/v1/domains/{domain}/records` | Replace all DNS records |
| PUT | `/v1/domains/{domain}/records/{type}` | Replace records for type |
| PUT | `/v1/domains/{domain}/records/{type}/{name}` | Replace records for type+name |
| DELETE | `/v1/domains/{domain}/records/{type}/{name}` | Delete records for type+name |

## Certificates

| Method | Endpoint | Description |
|---|---|---|
| POST | `/v1/certificates` | Create certificate order |
| POST | `/v1/certificates/validate` | Validate certificate order payload |
| GET | `/v1/certificates/{certificateId}` | Get certificate details |
| GET | `/v1/certificates/{certificateId}/actions` | Get certificate actions |
| GET | `/v1/certificates/{certificateId}/download` | Download certificate |
| POST | `/v1/certificates/{certificateId}/renew` | Renew certificate |
| POST | `/v1/certificates/{certificateId}/reissue` | Reissue certificate |
| POST | `/v1/certificates/{certificateId}/revoke` | Revoke certificate |
| POST | `/v1/certificates/{certificateId}/verifyDomainControl` | Verify domain control |

## Shoppers

| Method | Endpoint | Description |
|---|---|---|
| GET | `/v1/shoppers/{shopperId}` | Get shopper details |
| PATCH | `/v1/shoppers/{shopperId}` | Update shopper |
| DELETE | `/v1/shoppers/{shopperId}` | Delete shopper |

## Subscriptions

| Method | Endpoint | Description |
|---|---|---|
| GET | `/v1/subscriptions` | List subscriptions |
| GET | `/v1/subscriptions/{subscriptionId}` | Get subscription details |
| POST | `/v1/subscriptions/{subscriptionId}/cancel` | Cancel subscription |

## Agreements / metadata

| Method | Endpoint | Description |
|---|---|---|
| GET | `/v1/agreements` | List legal agreements |
| GET | `/v1/countries` | List countries |

## Aftermarket

| Method | Endpoint | Description |
|---|---|---|
| GET | `/v1/aftermarket/listings` | List aftermarket listings |
| GET | `/v1/aftermarket/listings/{listingId}` | Get listing details |

## Notes

- DNS types include `A`, `AAAA`, `CNAME`, `TXT`, `MX`, `SRV`, `NS`, `CAA`, etc.
- GoDaddy typically enforces ~60 requests/minute per endpoint.
- OTE is recommended for testing and is less restricted than production.
