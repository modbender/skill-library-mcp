# Yuboto Omni API (Swagger v1) - Quick Reference

- OpenAPI: `3.0.1`
- Title: `OmniAPI`
- Swagger UI: `https://api.yuboto.com/scalar/#description/introduction`
- JSON spec: `https://api.yuboto.com/swagger/v1/swagger.json`
- Auth scheme in spec: `ApiKey` (request header).

## Endpoint Groups

### Account
- `POST  ` `/v2/Account/Cost`
- `POST  ` `/v2/Account/CostDetails`
- `POST  ` `/v2/Account/CreateKey`
- `POST  ` `/v2/Account/SSO/GetAccessToken`
- `POST  ` `/v2/Account/SSO/GetAccessTokenFromRefreshToken`
- `GET   ` `/v2/Account/UserBalance`
- `GET   ` `/v2/Account/UserSubscriptions`

### Blacklisted
- `GET   ` `/v2/Blacklisted`
- `POST  ` `/v2/Blacklisted`
- `DELETE` `/v2/Blacklisted/{phonenumber}/{channel}`

### Contacts
- `POST  ` `/v2/Contacts`
- `GET   ` `/v2/Contacts/ContactFields`
- `GET   ` `/v2/Contacts/CustomFields`
- `POST  ` `/v2/Contacts/Search`
- `PUT   ` `/v2/Contacts/{id}`
- `DELETE` `/v2/Contacts/{id}`
- `GET   ` `/v2/Contacts/{id}/{PageNumber}/{PageSize}`

### Forms
- `GET   ` `/v2/Forms`
- `POST  ` `/v2/Forms/ShortUrl`
- `GET   ` `/v2/Forms/ShortUrl/{id}`

### LandingPages
- `GET   ` `/v2/LandingPages`

### Messages
- `GET   ` `/v2/Messages/Cancel/{id}`
- `GET   ` `/v2/Messages/Dlr/{id}`
- `GET   ` `/v2/Messages/DlrPhonenumber/{id}`
- `POST  ` `/v2/Messages/Send`
- `GET   ` `/v2/Messages/VerifyPin/{id}/{pin}`

### SubscriberLists
- `GET   ` `/v2/SubscriberLists`
- `POST  ` `/v2/SubscriberLists`
- `PUT   ` `/v2/SubscriberLists/{id}`
- `DELETE` `/v2/SubscriberLists/{id}`

### TrackableUrls
- `GET   ` `/v2/TrackableUrls`
- `POST  ` `/v2/TrackableUrls`
- `POST  ` `/v2/TrackableUrls/Decrypt`
- `POST  ` `/v2/TrackableUrls/ShortUrl`
- `GET   ` `/v2/TrackableUrls/ShortUrl/{id}`
- `DELETE` `/v2/TrackableUrls/{id}`
