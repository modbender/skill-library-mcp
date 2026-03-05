# skill-dropshipping-product-launcher

**One command: CJ Dropshipping product → WooCommerce draft listing.**

Fetches product data from CJ, downloads images, uploads to WordPress media library, calculates margin, and creates a WooCommerce draft product — with variants if CJ has them.

---

## Inputs

| Argument | Required | Description |
|---|---|---|
| `--product` / `-p` | ✅ | CJ Dropshipping product ID (e.g. `CJA123456789`) |
| `--price` | ✅ | Your sell price in **AED** |
| `--category` / `-c` | ❌ | Category name or WooCommerce category ID |
| `--dry-run` | ❌ | Preview without creating anything in WooCommerce |

---

## Outputs

```
✅ Product created!
   WooCommerce ID : 4821
   Margin         : 42.3%
   Admin URL      : https://tech1mart.com/wp-admin/post.php?post=4821&action=edit
   Product URL    : https://tech1mart.com/?p=4821
```

Machine-readable JSON block at end of stdout (key: `__RESULT__`):
```json
{
  "wooProductId": 4821,
  "margin": "42.3",
  "productUrl": "https://tech1mart.com/?p=4821",
  "adminUrl": "https://tech1mart.com/wp-admin/post.php?post=4821&action=edit",
  "title": "Product Name",
  "cjProductId": "CJA123456789",
  "sellPriceAED": 149.99,
  "cjPriceUSD": 22.5
}
```

---

## Auth Config

- **CJ API**: `~/cj-api.json` — fields: `apiKey`, `accessToken`, `tokenExpiry`
- **WooCommerce**: `~/woo-api.json` — fields: `url`, `consumerKey`, `consumerSecret`

Tokens are refreshed automatically.

---

## Pipeline

1. Fetch product from CJ (`/product/query` + `/product/variant/query`)
2. Download images → `/tmp/product-images/<product_id>/`
3. Upload images → WooCommerce media library (`/wp-json/wp/v2/media`)
4. Calculate margin: `((sellAED - cjUSD × 3.67) / sellAED × 100)`  — warns if < 30%
5. Create WooCommerce draft product (`/wp-json/wc/v3/products`) with:
   - Title, description, images
   - `regular_price` (AED)
   - `type: variable` + variations if CJ has multiple variants
   - `meta_data: _cj_product_id`
6. Output: product ID, margin %, admin + storefront URLs

---

## Usage Examples

```bash
# Basic launch
node scripts/launch.js --product CJA123456789 --price 149.99

# With category
node scripts/launch.js --product CJA123456789 --price 149.99 --category Electronics

# Dry run (preview only, no WooCommerce writes)
node scripts/launch.js --product CJA123456789 --price 149.99 --dry-run

# Check CJ product data only
node scripts/cj-fetch.js CJA123456789
```

---

## Dependencies

```bash
cd scripts
npm install axios form-data
```

Or from skill root:
```bash
npm install
```

---

## Files

```
skill-dropshipping-product-launcher/
├── SKILL.md              ← this file
├── package.json
└── scripts/
    ├── launch.js         ← main entry point
    ├── cj-fetch.js       ← CJ API fetcher + token refresh
    └── woo-create.js     ← WooCommerce uploader + product creator
```

---

## Margin Formula

```js
const cjPriceAED = cjPriceUSD * 3.67;
const margin = ((sellPriceAED - cjPriceAED) / sellPriceAED * 100).toFixed(1);
```

⚠️ Warning shown if margin < 30%.
