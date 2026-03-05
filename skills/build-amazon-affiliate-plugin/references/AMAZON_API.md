# Amazon PA-API Integration Guide

## Overview

Product Advertising API (PA-API) 5.0 provides programmatic access to Amazon product catalog data.

## Requirements

- Amazon Associate account in good standing
- PA-API access (must have made 3 qualifying sales in 180 days)
- Access Key ID
- Secret Access Key
- Associate Tag

## Regional Endpoints

| Region | Endpoint |
|--------|----------|
| US | https://api.amazon.com |
| UK | https://api.amazon.co.uk |
| DE | https://api.amazon.de |
| FR | https://api.amazon.fr |
| ES | https://api.amazon.es |
| IT | https://api.amazon.it |
| JP | https://api.amazon.co.jp |
| CA | https://api.amazon.ca |

## API Operation

### GetItems

```
POST /paapi5/getitems
Host: api.amazon.com
Content-Type: application/json
X-Amz-Date: {timestamp}
X-Amz-Target: com.amazon.paapi.v1.ProductAdvertisingAPIv1.GetItems
Authorization: AWS4-HMAC-SHA256 Credential={access_key}/{region}/{service}/aws4_request

{
  "ItemIds": ["B08N5WRWNW"],
  "Resources": [
    "Images.Primary.Medium",
    "ItemInfo.Title",
    "Offers.Listings.Price"
  ],
  "PartnerTag": "{associate_tag}",
  "PartnerType": "Associates",
  "Marketplace": "www.amazon.com"
}
```

## Response Structure

```json
{
  "ItemsResult": {
    "Items": [{
      "ASIN": "B08N5WRWNW",
      "DetailPageURL": "https://...",
      "Images": {
        "Primary": {
          "Medium": {
            "URL": "https://...",
            "Height": 160,
            "Width": 120
          }
        }
      },
      "ItemInfo": {
        "Title": {
          "DisplayValue": "Product Title"
        }
      },
      "Offers": {
        "Listings": [{
          "Price": {
            "Amount": "29.99",
            "Currency": "USD",
            "DisplayAmount": "$29.99"
          }
        }]
      }
    }]
  }
}
```

## Request Signing (AWS Signature V4)

```
1. Create canonical request
2. Create string to sign
3. Calculate signing key
4. Calculate signature
5. Add to Authorization header
```

## PHP Implementation Notes

```php
// Generate signed request
$service = 'ProductAdvertisingAPI';
$host = 'api.amazon.com';
$region = 'us-east-1';
$endpoint = 'https://api.amazon.com';

// Request payload
$payload = json_encode([
    'ItemIds' => [$asin],
    'Resources' => [
        'Images.Primary.Medium',
        'ItemInfo.Title',
        'Offers.Listings.Price'
    ],
    'PartnerTag' => $this->associate_tag,
    'PartnerType' => 'Associates',
    'Marketplace' => 'www.amazon.com'
]);

// AWS Signature V4 signing
$date = gmdate('Ymd\THis\Z');
$dateStamp = gmdate('Ymd');
$canonicalUri = '/paapi5/getitems';
$canonicalQuerystring = '';
$canonicalHeaders = "content-type:application/json\nhost:$host\nx-amz-date:$date\nx-amz-target:com.amazon.paapi.v1.ProductAdvertisingAPIv1.GetItems\n";
$signedHeaders = 'content-type;host;x-amz-date;x-amz-target';
$canonicalRequest = "POST\n$canonicalUri\n$canonicalQuerystring\n$canonicalHeaders\n$signedHeaders\n" . hash('sha256', $payload);
```

## Rate Limits

- Default: 1 request per second
- Can request increase through Amazon support

## Fallback Strategy

If PA-API unavailable:
1. Check cache for previous response
2. Display fallback HTML with affiliate link
3. Show placeholder image

## Error Codes

| Code | Description |
|------|-------------|
| 429 | Rate limit exceeded |
| 503 | Service unavailable |
| 401 | Invalid credentials |
| NoSales | No qualifying sales |

## Alternatives to PA-API

If PA-API access is lost:
- Manual product lookup
- Amazon Associates SiteStripe
- Amazon OneLink (international)
- Manual affiliate link management
