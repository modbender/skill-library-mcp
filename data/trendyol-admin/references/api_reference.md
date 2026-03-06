# Trendyol Marketplace API Reference (v2.0)
> Source: https://developers.trendyol.com/v2.0/docs/getting-started
> Last updated: February 2026

---

## Table of Contents
1. [Overview](#1-overview)
2. [Authorization](#2-authorization)
3. [Environments (Prod & Stage)](#3-environments)
4. [Service Limitations](#4-service-limitations)
5. [Product Integration](#5-product-integration)
   - [API Endpoints](#51-api-endpoints)
   - [Shipment Providers List](#52-shipment-providers)
   - [Brand List (getBrands)](#53-brand-list)
   - [Category List (getCategoryTree)](#54-category-list)
   - [Category-Attribute List (getCategoryAttributes)](#55-category-attributes)
   - [Product Create (createProducts)](#56-product-create)
   - [Product Update (updateProducts)](#57-product-update)
   - [Stock and Price Update (updatePriceAndInventory)](#58-stock-and-price-update)
   - [Product Delete](#59-product-delete)
   - [Check Batchrequest Result (getBatchRequestResult)](#510-batch-request-result)
   - [Product Filter (filterProducts)](#511-product-filter)
   - [Product Archive](#512-product-archive)
   - [Product Buybox Check Service](#513-product-buybox)
   - [Product Unlock](#514-product-unlock)
6. [Order Integration](#6-order-integration)
   - [Get Order Packages (getShipmentPackages)](#61-get-order-packages)
   - [Get Awaiting Confirmation Packages](#62-awaiting-confirmation)
   - [Update Shipping Code (updateTrackingNumber)](#63-update-tracking)
   - [Notify Packages (updatePackage)](#64-notify-packages)
   - [Cancel Order Package Item](#65-cancel-order)
   - [Split Order Package Item](#66-split-order)
   - [Notify Deci and Box Info (updateBoxInfo)](#67-box-info)
   - [Shipping Alternative Delivery](#68-alternative-delivery)
   - [Change Cargo Provider](#69-change-cargo)
   - [Update Warehouse Information](#610-update-warehouse)
   - [Additional Supply Time Definition](#611-supply-time)
   - [Address Information](#612-address-info)
   - [Update Labor Cost](#613-labor-cost)
7. [Delivery Integration](#7-delivery-integration)
   - [Common Label Barcode Request (createCommonLabel)](#71-create-label)
   - [Getting Created Common Label (getCommonLabel)](#72-get-label)
   - [Compensation Integration](#73-compensation)
8. [Returned Orders Integration](#8-returns)
   - [Getting Returned Orders (getClaims)](#81-get-claims)
   - [Return Reasons](#82-return-reasons)
   - [Approve Returned Orders (approveClaimLineItems)](#83-approve-returns)
   - [Create Rejection Request (createClaimIssue)](#84-reject-returns)
   - [Claim Issue Reasons (getClaimsIssueReasons)](#85-claim-reasons)
   - [Get Claim Audit Information](#86-claim-audit)
   - [Create a Return Request (createClaim)](#87-create-claim)
9. [Question & Answer Integration](#9-qa)
   - [Getting Customer Questions](#91-get-questions)
   - [Answering Customer Questions](#92-answer-questions)
10. [Webhook Integration](#10-webhook)
    - [Webhook Model](#101-webhook-model)
    - [Webhook Create](#102-webhook-create)
    - [Webhook Filter](#103-webhook-filter)
    - [Webhook Update](#104-webhook-update)
    - [Webhook Delete](#105-webhook-delete)
    - [Webhook Active/Passive Status](#106-webhook-status)
11. [Seller Information Integration](#11-seller-info)
    - [Return and Shipping Address Info (getSuppliersAddresses)](#111-supplier-addresses)
12. [Invoice Integration](#12-invoice)
    - [Send Customer Invoice Link (sendInvoiceLink)](#121-send-invoice)
    - [Delete Customer Invoice Link](#122-delete-invoice)
    - [Send Customer Invoice File](#123-send-invoice-file)
13. [Product Integration V2](#13-product-v2)
14. [Accounting and Finance Integration](#14-finance)
15. [Postman Collections](#15-postman)

---

## 1. Overview
Trendyol API Integration allows companies participating in the Trendyol Partner Program (Marketplace) to connect Trendyol stores to their e-commerce systems through Trendyol API services. This enables:
- Product transfer (create, update, delete)
- Stock and price updates
- Order management (get, update status, cancel, split)
- Invoice delivery
- Customer question handling
- Webhook event notifications
- Returns management
- Delivery label creation

---

## 2. Authorization
### Regions and Store Front Codes
> ⚠️ **CRITICAL: The `storeFrontCode` header is the mandatory parameter used to switch between different country markets.**

| Region | Country | Store Front Code | Currency |
|---|---|---|---|
| Gulf | United Arab Emirates | `AE` | AED |
| Gulf | Saudi Arabia | `SA` | SAR |
| Gulf | Qatar | `QA` | QAR |
| Gulf | Kuwait | `KW` | KWD |
| Gulf | Bahrain | `BH` | BHD |
| Gulf | Oman | `OM` | OMR |
| Europe | Germany | `DE` | EUR |
| Europe | Azerbaijan | `AZ` | AZN |
| Europe | Romania | `RO` | RON |
| Europe | Czech Republic | `CZ` | CZK |
| Europe | Hungary | `HU` | HUF |
| Europe | Slovakia | `SK` | EUR |
| Europe | Bulgaria | `BG` | BGN |
| Europe | Greece | `GR` | EUR |

### Basic Authentication
All requests to the integration services must be authorized using **Basic Authentication**.

**Required credentials (obtained from Seller Panel > "Hesap Bilgilerim" > "Entegrasyon Bilgileri"):**
| Credential | Description |
|---|---|
| `supplierId` | Your seller/supplier ID |
| `API KEY` | Your API key (username for Basic Auth) |
| `API SECRET KEY` | Your API secret (password for Basic Auth) |

> ⚠️ **IMPORTANT:** Never share API keys on public platforms (GitHub, GitLab, etc.)

### Required Headers
All requests MUST include both `Authorization` and `User-Agent` headers.

**Authorization Header:**
```
Authorization: Basic base64(API_KEY:API_SECRET_KEY)
```

**User-Agent Header:**
- With integration partner: `{SellerId} - {IntegrationCompanyName}`
- Self-integration: `{SellerId} - SelfIntegration`
- Integration company name: alphanumeric, max 30 characters

**Examples:**
```
User-Agent: 1234 - TrendyolSoft
User-Agent: 4321 - SelfIntegration
```

**Error Responses:**
- Missing/wrong auth → `401` with `"exception": "ClientApiAuthenticationException"`
- Missing User-Agent → `403` Forbidden

### Rate Limits
- Max **50 requests per 10 seconds** to the same endpoint
- Exceeding → `429 Too Many Requests`

---

## 3. Environments
| Environment | Base URL | Notes |
|---|---|---|
| **PROD** | `https://apigw.trendyol.com/integration/` | No IP authorization needed |
| **STAGE** | `https://stageapigw.trendyol.com/integration/` | IP authorization required |

- Stage and Prod have **different** account/API credentials
- Stage requires IP whitelist (notify Trendyol of your server IPs)
- Multiple IPs can be defined and updated later
- If blocked in prod, contact Trendyol support

---

## 4. Service Limitations
- Rate limit: 50 requests per 10 seconds per endpoint
- Batch operations: max 1000 items per request
- Image requirements: 1200x1800 pixels, 96dpi, HTTPS URLs
- Max 8 images per barcode
- Product description: max 30,000 characters (HTML allowed)
- Barcode: max 40 characters (special chars: `.`, `-`, `_` allowed)
- Title: max 100 characters
- Stock code: max 100 characters

---

## 5. Product Integration

### 5.1 API Endpoints
| Operation | Method | PROD URL | STAGE URL |
|---|---|---|---|
| Create Products | POST | `https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products` | `https://stageapigw.trendyol.com/integration/product/sellers/{sellerId}/products` |
| Update Products | PUT | Same as above | Same as above |
| Delete Products | DELETE | Same as above | Same as above |
| Stock & Price Update | PUT | `https://apigw.trendyol.com/integration/inventory/sellers/{sellerId}/products/price-and-inventory` | Same pattern with stage |
| Filter Products | GET | `https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products` | Same pattern |
| Batch Request Result | GET | `https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products/batch-requests/{batchRequestId}` | Same pattern |

### 5.2 Shipment Providers
```
GET https://apigw.trendyol.com/integration/product/sellers/{sellerId}/addresses
```
Returns list of available cargo/shipment companies with their IDs.

### 5.3 Brand List
```
GET https://apigw.trendyol.com/integration/product/brands
```
Query params: `name` (filter by brand name), `page`, `size`

### 5.4 Category List
```
GET https://apigw.trendyol.com/integration/product/product-categories
```
Returns the full category tree with IDs.

### 5.5 Category Attributes
```
GET https://apigw.trendyol.com/integration/product/product-categories/{categoryId}/attributes
```
Returns required/optional attributes for a given category, including:
- `attributeId`, `attributeName`
- `required` (boolean)
- `allowCustom` (boolean)
- `slicer` (boolean) - opens product in separate contents (e.g., color)
- `varianter` (boolean) - variant within same content (e.g., size)
- `attributeValues` list with `id` and `name`

### 5.6 Product Create (createProducts)
```
POST https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products
```
**Request Body:**
```json
{
  "items": [
    {
      "barcode": "barkod-1234",
      "title": "Product Title",
      "productMainId": "MAIN-001",
      "brandId": 1791,
      "categoryId": 411,
      "quantity": 100,
      "stockCode": "STK-123",
      "dimensionalWeight": 2,
      "description": "Product description in HTML",
      "currencyType": "TRY",
      "listPrice": 150.00,
      "salePrice": 120.00,
      "vatRate": 10,
      "cargoCompanyId": 10,
      "shipmentAddressId": 0,
      "returningAddressId": 0,
      "deliveryOption": {
        "deliveryDuration": 1,
        "fastDeliveryType": "SAME_DAY_SHIPPING"
      },
      "images": [
        {
          "url": "https://example.com/image1.jpg"
        }
      ],
      "attributes": [
        {
          "attributeId": 338,
          "attributeValueId": 6980
        },
        {
          "attributeId": 47,
          "customAttributeValue": "Red"
        }
      ]
    }
  ]
}
```
**Response:**
```json
{
  "batchRequestId": "batch-id-here"
}
```
**Key Rules:**
- Max 1000 items per request
- Multiple variants of same product → send as separate items with same `productMainId`
- Slicer attributes (e.g., color) open separate content pages
- Varianter attributes (e.g., size) are variants within same content
- Always check result via `getBatchRequestResult` with the returned `batchRequestId`
- `fastDeliveryType` requires `deliveryDuration` = 1

### 5.7 Product Update (updateProducts)
```
PUT https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products
```
**Request Body:**
```json
{
  "items": [
    {
      "barcode": "barkod-1234",
      "title": "Updated Product Title",
      "productMainId": "1234BT",
      "brandId": 1791,
      "categoryId": 411,
      "stockCode": "STK-123",
      "dimensionalWeight": 12,
      "description": "Updated description",
      "vatRate": 0,
      "images": [
        {
          "url": "https://example.com/new_image.jpg"
        }
      ],
      "attributes": [
        {
          "attributeId": 338,
          "attributeValueId": 6980
        },
        {
          "attributeId": 343,
          "attributeValueId": 4294
        },
        {
          "attributeId": 47,
          "customAttributeValue": "COLOUR"
        }
      ],
      "cargoCompanyId": 10,
      "shipmentAddressId": 0,
      "returningAddressId": 0
    }
  ]
}
```
**Parameters:**
| Parameter | Required | Description | Type | Max Length |
|---|---|---|---|---|
| barcode | Yes | Product barcode. Special chars: `.` `-` `_` allowed | string | 40 |
| title | Yes | Product name | string | 100 |
| productMainId | Yes | Main product code | string | 40 |
| brandId | Yes | Trendyol Brand ID | integer | - |
| categoryId | Yes | Trendyol Category ID | integer | - |
| stockCode | Yes | Unique stock code in supplier system | string | 100 |
| dimensionalWeight | Yes | Desi amount | number | - |
| description | Yes | Product description (HTML allowed) | string | 30,000 |
| currencyType | Yes | Must be "TRY" | string | - |
| cargoCompanyId | Yes | Trendyol cargo company ID | integer | - |
| deliveryDuration | No | Shipment duration | integer | - |
| images | Yes | Product image URLs (HTTPS, max 8) | list | - |
| vatRate | Yes | VAT rate (0, 1, 10, 20) | integer | - |
| shipmentAddressId | No | Shipment warehouse address ID | integer | - |
| returningAddressId | No | Return warehouse address ID | integer | - |
| attributes | Yes | Category attributes/specifications | list | - |

**Important:**
- This service is for product **information** only — use `updatePriceAndInventory` for stock/price
- Product status changes to "Content Check Pending" after update
- For approved products: `barcode`, `productMainId`, `brandId`, `categoryId`, slicer/varianter attributes **cannot** be updated
- Max 1000 items per request
- Check result via `getBatchRequestResult`

### 5.8 Stock and Price Update (updatePriceAndInventory)
```
PUT https://apigw.trendyol.com/integration/inventory/sellers/{sellerId}/products/price-and-inventory
```
**Request Body:**
```json
{
  "items": [
    {
      "barcode": "barkod-1234",
      "quantity": 100,
      "salePrice": 120.50,
      "listPrice": 150.00
    }
  ]
}
```
| Parameter | Required | Description |
|---|---|---|
| barcode | Yes | Product barcode |
| quantity | Yes | Stock quantity |
| salePrice | Yes | Sale price (must be ≤ listPrice) |
| listPrice | Yes | List/original price |

### 5.9 Product Delete
```
DELETE https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products
```
**Request Body:**
```json
{
  "items": [
    {
      "barcode": "barkod-1234"
    }
  ]
}
```

### 5.10 Batch Request Result (getBatchRequestResult)
```
GET https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products/batch-requests/{batchRequestId}
```
Returns status of a batch operation including per-item success/failure details.
**Response includes:**
- `status`: "IN_PROGRESS", "COMPLETED", "FAILED"
- `items[].status`: per-item status
- `items[].failureReasons`: error details if failed

### 5.11 Product Filter (filterProducts)
```
GET https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products
```
**Query Parameters:**
- `barcode` - Filter by barcode
- `productMainId` - Filter by main product ID
- `brandId` - Filter by brand
- `categoryId` - Filter by category
- `approved` - true/false
- `onSale` - true/false
- `page` - Page number (0-indexed)
- `size` - Page size (max 200)
- `dateQueryType` - CREATED_DATE or LAST_MODIFIED_DATE
- `startDate` - Epoch timestamp (ms)
- `endDate` - Epoch timestamp (ms)

### 5.12 Product Archive
```
PUT https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products/archive
```
```json
{
  "items": [
    {
      "barcode": "barkod-1234"
    }
  ]
}
```

### 5.13 Product Buybox Check
```
GET https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products/{barcode}/buybox
```

### 5.14 Product Unlock
```
PUT https://apigw.trendyol.com/integration/product/sellers/{sellerId}/products/unlock
```

---

## 6. Order Integration

### Order Flow States
```
Awaiting → Created → Picking → Invoiced → Shipped → Delivered → Undelivered → Cancelled → Unsupplied
```

### 6.1 Get Order Packages (getShipmentPackages)
```
GET https://apigw.trendyol.com/integration/order/sellers/{sellerId}/orders
```
**Recommended Endpoint:**
```
GET https://apigw.trendyol.com/integration/order/sellers/{sellerId}/orders?status=Created&startDate={startDate}&endDate={endDate}&orderByField=PackageLastModifiedDate&orderByDirection=DESC&size=50
```
**Query Parameters:**
- `status` - Created, Picking, Invoiced, Shipped, Cancelled, Delivered, etc.
- `startDate` / `endDate` - Epoch timestamps (ms)
- `orderByField` - PackageLastModifiedDate, CreatedDate
- `orderByDirection` - ASC, DESC
- `size` - Page size (max 200)
- `page` - Page number
- `orderNumber` - Filter by order number
- `shipmentPackageIds` - Filter by package IDs

**Response Model (key fields):**
```json
{
  "content": [
    {
      "shipmentAddress": {
        "firstName": "",
        "lastName": "",
        "address1": "",
        "city": "",
        "district": "",
        "postalCode": "",
        "countryCode": ""
      },
      "invoiceAddress": { ... },
      "orderNumber": "10654411111",
      "grossAmount": 498.90,
      "totalDiscount": 0.00,
      "id": 33301111111,
      "shipmentPackageId": 3330111111,
      "cargoTrackingNumber": 7280027504111111,
      "cargoTrackingLink": "https://tracking.trendyol.com/...",
      "cargoProviderName": "Trendyol Express",
      "lines": [
        {
          "quantity": 1,
          "merchantSku": "111111",
          "sku": "8683771111111",
          "barcode": "8683772071724",
          "productName": "Product Name",
          "productCode": 1239111111,
          "amount": 498.90,
          "discount": 0.00,
          "currencyCode": "TRY",
          "vatRate": 20.00,
          "price": 498.90,
          "orderLineItemStatusName": "Created"
        }
      ],
      "orderDate": 1762253333685,
      "shipmentPackageStatus": "Created",
      "status": "Created",
      "deliveryType": "normal",
      "estimatedDeliveryStartDate": 1762858136000,
      "estimatedDeliveryEndDate": 1763030936000,
      "totalPrice": 498.90,
      "lastModifiedDate": 1762865408581,
      "commercial": false,
      "warehouseId": 372389
    }
  ],
  "page": 0,
  "size": 50,
  "totalPages": 1,
  "totalElements": 1
}
```

**Order Status Flow:**
- **Awaiting** → Order placed, turns to Created immediately. No seller action needed.
- **Created** → Seller should start processing.
- **Picking** → Shows customer that package is being prepared.
- **Invoiced** → Optional, should be sent before Shipped.
- **Shipped** → Package handed to cargo company.
- **Delivered** → Successfully delivered.
- **Cancelled** → Order cancelled.
- **Unsupplied** → Seller cannot supply the product.

### 6.2 Get Awaiting Confirmation Packages
```
GET https://apigw.trendyol.com/integration/order/sellers/{sellerId}/orders?status=Awaiting
```

### 6.3 Update Tracking Number
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/tracking-number
```
```json
{
  "trackingNumber": "CARGO_TRACKING_CODE"
}
```

### 6.4 Notify Packages (updatePackage) — Status Updates
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}
```
**Set to Picking:**
```json
{
  "status": "Picking",
  "lines": [{ "lineId": 123456, "quantity": 1 }]
}
```
**Set to Invoiced:**
```json
{
  "status": "Invoiced",
  "invoiceNumber": "INV-2024-001",
  "lines": [{ "lineId": 123456, "quantity": 1 }]
}
```
**Set to Shipped:**
```json
{
  "status": "Shipped",
  "lines": [{ "lineId": 123456, "quantity": 1 }]
}
```

### 6.5 Cancel Order Package Item
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}
```
```json
{
  "status": "Unsupplied",
  "lines": [
    {
      "lineId": 123456,
      "quantity": 1
    }
  ]
}
```

### 6.6 Split Order Package Item
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/split
```

### 6.7 Notify Deci and Box Info
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/box-info
```
```json
{
  "boxQuantity": 2,
  "deci": 15
}
```

### 6.8 Shipping Alternative Delivery
For alternative delivery methods beyond standard cargo.

### 6.9 Change Cargo Provider
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/cargo-provider
```
```json
{
  "cargoCompanyId": 10
}
```

### 6.10 Update Warehouse Information
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/warehouse
```

### 6.11 Additional Supply Time Definition
For requesting extra time to prepare an order.

### 6.12 Address Information
Retrieve shipping and invoice address details from order data.

### 6.13 Update Labor Cost
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/labor-cost
```

---

## 7. Delivery Integration

### 7.1 Create Common Label (createCommonLabel)
```
POST https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/common-label
```

### 7.2 Get Common Label (getCommonLabel)
```
GET https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/common-label
```

### 7.3 Compensation Integration
For managing cargo compensation claims.

---

## 8. Returned Orders Integration

### 8.1 Getting Returned Orders (getClaims)
```
GET https://apigw.trendyol.com/integration/order/sellers/{sellerId}/claims
```
**Query Parameters:**
- `claimIds` - Filter by claim IDs
- `claimItemStatus` - Filter by status
- `startDate` / `endDate` - Epoch timestamps
- `page`, `size`

### 8.2 Return Reasons
Pre-defined return reason codes from Trendyol.

### 8.3 Approve Returned Orders
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/claims/{claimId}/items/{claimItemId}/approve
```

### 8.4 Create Rejection Request
```
POST https://apigw.trendyol.com/integration/order/sellers/{sellerId}/claims/{claimId}/issue
```

### 8.5 Claim Issue Reasons
```
GET https://apigw.trendyol.com/integration/order/sellers/{sellerId}/claims/issue-reasons
```

### 8.6 Get Claim Audit Information
For tracking return process audit trail.

### 8.7 Create a Return Request
```
POST https://apigw.trendyol.com/integration/order/sellers/{sellerId}/claims
```

---

## 9. Question & Answer Integration

### 9.1 Getting Customer Questions
```
GET https://apigw.trendyol.com/integration/sellers/{sellerId}/questions
```
**Query Parameters:**
- `status` - WAITING_FOR_ANSWER, ANSWERED, etc.
- `page`, `size`
- `startDate`, `endDate`

### 9.2 Answering Customer Questions
```
POST https://apigw.trendyol.com/integration/sellers/{sellerId}/questions/{questionId}/answers
```
```json
{
  "text": "Your answer to the customer question"
}
```

---

## 10. Webhook Integration

### 10.1 Webhook Model
Webhooks automatically notify your application when order events occur, eliminating the need to poll via `getShipmentPackages`.

**Supported Order Statuses:**
- `CREATED`, `PICKING`, `INVOICED`, `SHIPPED`
- `CANCELLED`, `DELIVERED`, `UNDELIVERED`
- `RETURNED`, `UNSUPPLIED`, `AWAITING`
- `UNPACKED`, `AT_COLLECTION_POINT`, `VERIFIED`

**Authorization Types:**
- `BASIC_AUTHENTICATION` → requires `username` and `password`
- `API_KEY` → requires `apiKey` (sent as `x-api-key` header)

**`createdBy` field values:**
- `order-creation` → Package created with incoming order
- `cancel` → Package created after partial cancellation
- `split` → Package created from package split
- `transfer` → Order transferred from another seller

**Webhook Push Model (same as getShipmentPackages response):**
```json
{
  "shipmentAddress": {
    "id": 11111111,
    "firstName": "Trendyol",
    "lastName": "Customer",
    "address1": "Full address here",
    "city": "İstanbul",
    "cityCode": 34,
    "district": "Sarıyer",
    "districtId": 54,
    "postalCode": "34200",
    "countryCode": "TR",
    "fullAddress": "...",
    "fullName": "Trendyol Customer"
  },
  "orderNumber": "10654411111",
  "grossAmount": 498.90,
  "totalDiscount": 0.00,
  "invoiceAddress": { ... },
  "id": 33301111111,
  "shipmentPackageId": 3330111111,
  "cargoTrackingNumber": 7280027504111111,
  "cargoProviderName": "Trendyol Express",
  "lines": [
    {
      "quantity": 1,
      "merchantSku": "111111",
      "barcode": "8683772071724",
      "productName": "Product Name",
      "amount": 498.90,
      "price": 498.90,
      "vatRate": 20.00,
      "orderLineItemStatusName": "Delivered",
      "commission": 13
    }
  ],
  "orderDate": 1762253333685,
  "shipmentPackageStatus": "Delivered",
  "status": "Delivered",
  "deliveryType": "normal",
  "totalPrice": 498.90,
  "lastModifiedDate": 1762865408581,
  "commercial": false,
  "warehouseId": 372389,
  "micro": true,
  "isCod": false,
  "createdBy": "order-creation"
}
```

**GULF Region specific fields:**
- `shortAddress`, `stateName` in address objects

**Micro Export specific fields:**
- `etgbNo`, `etgbDate`, `containsDangerousProduct`, `hsCode`

**Best Practices:**
- Failed webhook requests are retried every 5 minutes until success
- Still recommended to periodically sync via `getShipmentPackages` as backup
- Endpoint URL must not contain "Trendyol", "Dolap", or "localhost"
- Max 15 webhooks per seller (including deactivated ones)
- Deactivated webhooks count toward the limit — delete unused ones

**Retry & Deactivation:**
1. On error: Trendyol sends email about the failing webhook ID and retry period
2. After retry period expires: Trendyol sends email that webhook has been deactivated
3. Fix your service, then manually reactivate

### 10.2 Webhook Create
```
POST https://apigw.trendyol.com/integration/order/sellers/{sellerId}/webhooks
```

### 10.3 Webhook Filter
```
GET https://apigw.trendyol.com/integration/order/sellers/{sellerId}/webhooks
```

### 10.4 Webhook Update
```
PUT https://apigw.trendyol.com/integration/order/sellers/{sellerId}/webhooks/{webhookId}
```

### 10.5 Webhook Delete
```
DELETE https://apigw.trendyol.com/integration/order/sellers/{sellerId}/webhooks/{webhookId}
```

### 10.6 Webhook Active/Passive Status
Toggle webhook active/passive state.

---

## 11. Seller Information Integration

### 11.1 Supplier Addresses (getSuppliersAddresses)
```
GET https://apigw.trendyol.com/integration/product/sellers/{sellerId}/addresses
```
Returns shipping, return, and invoice addresses with their IDs. Required for `shipmentAddressId` and `returningAddressId` in product create/update.

**Response:**
```json
{
  "supplierAddresses": [
    {
      "id": 1,
      "addressType": "Shipment",
      "city": "İstanbul",
      "district": "Sarıyer",
      "address": "Address details",
      "returningAddress": false,
      "shipmentAddress": true,
      "invoiceAddress": false,
      "default": true
    }
  ]
}
```

---

## 12. Invoice Integration

### 12.1 Send Invoice Link
```
POST https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/invoice-link
```
```json
{
  "invoiceLink": "https://your-domain.com/invoice/12345.pdf"
}
```

### 12.2 Delete Invoice Link
```
DELETE https://apigw.trendyol.com/integration/order/sellers/{sellerId}/shipment-packages/{shipmentPackageId}/invoice-link
```

### 12.3 Send Invoice File
Upload invoice file directly.

---

## 13. Product Integration V2
V2 adds enhanced capabilities:
- **Category Attribute List v2** — includes `allowMultipleAttributeValues` field
- **Category Attribute Values List v2** — separate endpoint for attribute values
- **Product Create v2** — supports `attributeValueIds` array for multi-value attributes
- **Product Update v2** — separate endpoints for approved vs unapproved products
- **Product Filtering v2** — separate endpoints for basic info, approved, and unapproved products

Key V2 differences:
- Attributes now support multiple values via `attributeValueIds: [1, 2, 3]`
- `allowMultipleAttributeValues` flag indicates if attribute accepts multiple values
- Approved/unapproved products have separate update and filter endpoints

---

## 14. Accounting and Finance Integration

### Current Account Statement
```
GET https://apigw.trendyol.com/integration/finance/sellers/{sellerId}/settlements
```

### Cargo Invoice Details
```
GET https://apigw.trendyol.com/integration/finance/sellers/{sellerId}/cargo-invoices
```

---

## 15. Postman Collections

**Trendyol API Collection:**
```
https://api.postman.com/collections/36945960-f299f4ac-3cc4-4046-9265-3ca292b35deb?access_key=PMAT-01JP73Q6C4P7EJV2P4WF4MVN3E
```

**Trendyol Webhook Collection:**
```
https://api.postman.com/collections/36945960-f8cac0c6-61f5-4cae-acdd-8c8bf5d2a7f2?access_key=PMAT-01JP73ZAWG57SVKBW7VKYCAYBS
```
Import via: Postman > Import > Link

---

## Quick Reference: Common URL Patterns
All endpoints follow:
```
https://apigw.trendyol.com/integration/{service}/sellers/{sellerId}/{resource}
```
| Service Area | URL Prefix |
|---|---|
| Products | `/integration/product/sellers/{sellerId}/` |
| Stock & Price | `/integration/inventory/sellers/{sellerId}/` |
| Orders | `/integration/order/sellers/{sellerId}/` |
| Q&A | `/integration/sellers/{sellerId}/questions` |
| Finance | `/integration/finance/sellers/{sellerId}/` |
| Brands | `/integration/product/brands` |
| Categories | `/integration/product/product-categories` |

---
*Document generated from Trendyol Developer Documentation v2.0 for use as an AI skill reference.*
