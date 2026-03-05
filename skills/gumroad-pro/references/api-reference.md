# Gumroad Pro API Reference

This document provides detailed command specifications and usage examples for the Gumroad Pro skill. 

## 🛠️ Command Reference

All commands follow this pattern:
`node scripts/gumroad-pro.js <resource> <action> [flags] --json`

### 1. Products
Manage your digital products.

#### List Products
- **Command**: `node scripts/gumroad-pro.js products list --json`
- **Success Output**: `{"success": true, "products": [{ "id": "...", "name": "...", "price": "...", "published": true }]}`

#### Product Details
- **Command**: `node scripts/gumroad-pro.js products details --id <PRODUCT_ID> --json`

#### Create Product
- **Command**: `node scripts/gumroad-pro.js products create --name "<NAME>" --price <CENTS> --json`

#### Update Product
- **Command**: `node scripts/gumroad-pro.js products update --id <PRODUCT_ID> [--name "<NAME>"] [--price <CENTS>] [--description "<TEXT>"] --json`

#### Delete Product
- **Command**: `node scripts/gumroad-pro.js products delete --id <PRODUCT_ID> --json`

#### Enable/Disable Product
- **Command**: `node scripts/gumroad-pro.js products enable --id <PRODUCT_ID> --json`
- **Command**: `node scripts/gumroad-pro.js products disable --id <PRODUCT_ID> --json`

---

### 2. Sales
View and manage customer transactions.

#### List Sales
- **List Sales**: `node scripts/gumroad-pro.js sales list [--email <email>] [--product <id>] [--page <key>] [--json]`
    - View recent transactions.
    - Filter by customer email or product ID.

#### Sale Details
- **Command**: `node scripts/gumroad-pro.js sales details --id <SALE_ID> --json`

#### Refund Sale
- **Command**: `node scripts/gumroad-pro.js sales refund --id <SALE_ID> --json`

#### Mark as Shipped (Physical Products)
- **Command**: `node scripts/gumroad-pro.js sales mark-shipped --id <SALE_ID> --tracking "<URL_OR_NUMBER>" --json`

---

### 3. Licenses
Verify and manage license keys.

#### Verify License
- **Command**: `node scripts/gumroad-pro.js licenses verify --product <PRODUCT_ID> --key <LICENSE_KEY> --json`

#### Enable/Disable License
- **Command**: `node scripts/gumroad-pro.js licenses enable --product <PRODUCT_ID> --key <LICENSE_KEY> --json`
- **Command**: `node scripts/gumroad-pro.js licenses disable --product <PRODUCT_ID> --key <LICENSE_KEY> --json`

#### Decrement Use Count
- **Command**: `node scripts/gumroad-pro.js licenses decrement --product <PRODUCT_ID> --key <LICENSE_KEY> --json`

#### Rotate License Key
- **Command**: `node scripts/gumroad-pro.js licenses rotate --product <PRODUCT_ID> --key <LICENSE_KEY> --json`

---

### 4. Discounts (Offer Codes)
#### List Discounts
- **Command**: `node scripts/gumroad-pro.js discounts list --product <PRODUCT_ID> --json`

#### Create Discount
- **Command**: `node scripts/gumroad-pro.js discounts create --product <PRODUCT_ID> --name "<CODE>" --amount <VALUE> --type <cents|percent> --json`

#### Delete Discount
- **Command**: `node scripts/gumroad-pro.js discounts delete --product <PRODUCT_ID> --id <DISCOUNT_ID> --json`

---

### 5. Payouts
#### List Payouts
- **Command**: `node scripts/gumroad-pro.js payouts list --json`

#### Payout Details
- **Command**: `node scripts/gumroad-pro.js payouts details --id <PAYOUT_ID> --json`

---

### 6. Subscriptions (Webhooks)
#### List Webhooks
- **Command**: `node scripts/gumroad-pro.js subscriptions list --json`

#### Create Webhook
- **Command**: `node scripts/gumroad-pro.js subscriptions create --type <EVENT_TYPE> --url "<TARGET_URL>" --json`

#### Delete Webhook
- **Command**: `node scripts/gumroad-pro.js subscriptions delete --id <SUBSCRIPTION_ID> --json`

---

### 7. Custom Fields
#### List/Create/Delete Custom Fields
- **List**: `node scripts/gumroad-pro.js custom-fields list --product <PRODUCT_ID> --json`
- **Create**: `node scripts/gumroad-pro.js custom-fields create --product <PRODUCT_ID> --name "<FIELD_NAME>" --required true --json`
- **Delete**: `node scripts/gumroad-pro.js custom-fields delete --product <PRODUCT_ID> --name "<FIELD_NAME>" --json`

---

### 8. User Info
- **Command**: `node scripts/gumroad-pro.js whoami --json`

---

## 📝 Usage Example: Selling a Product

1. **Create Product**:
   `node scripts/gumroad-pro.js products create --name "Art Pack 1" --price 2500 --json`
2. **Add Custom Field**:
   `node scripts/gumroad-pro.js custom-fields create --product <ID> --name "Size" --required true --json`
3. **Publish Product**:
   `node scripts/gumroad-pro.js products enable --id <ID> --json`
