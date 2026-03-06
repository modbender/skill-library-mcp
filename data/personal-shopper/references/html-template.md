# HTML Report Template

## Usage

Generate this HTML report as the **primary deliverable** of every Personal Shopper run. Save as a `.html` file and send to the user.

## Template

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>جاك العلم 🔍 — Personal Shopper Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #F8F7F4;
    --card: #1d1d1f;
    --card-alt: #2d2d2f;
    --accent-green: #34c759;
    --accent-blue: #007aff;
    --accent-orange: #ff9500;
    --accent-red: #ff3b30;
    --accent-purple: #af52de;
    --text-primary: #ffffff;
    --text-secondary: #a1a1a6;
    --text-dark: #1d1d1f;
    --best-value: #34c759;
    --near-pro: #007aff;
    --budget-killer: #ff9500;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Rubik', -apple-system, 'Segoe UI', Tahoma, sans-serif;
    background: var(--bg);
    color: var(--text-dark);
    padding: 16px;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
  }

  .header {
    text-align: center;
    padding: 24px 0;
  }

  .header h1 {
    font-size: 2em;
    margin-bottom: 4px;
  }

  .header .subtitle {
    color: var(--text-secondary);
    font-size: 0.9em;
  }

  .item-section {
    margin: 24px 0;
  }

  .item-title {
    font-size: 1.3em;
    font-weight: 700;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--card);
  }

  .card {
    background: var(--card);
    color: var(--text-primary);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
  }

  .card::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    height: 4px;
  }

  .card.best-value::before { background: var(--best-value); }
  .card.near-pro::before { background: var(--near-pro); }
  .card.budget-killer::before { background: var(--budget-killer); }

  .card-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 600;
    margin-bottom: 12px;
  }

  .best-value .card-badge { background: var(--best-value); color: #000; }
  .near-pro .card-badge { background: var(--near-pro); color: #fff; }
  .budget-killer .card-badge { background: var(--budget-killer); color: #000; }

  .card h3 {
    font-size: 1.2em;
    margin-bottom: 4px;
  }

  .card .price {
    font-size: 1.4em;
    font-weight: 700;
    margin: 8px 0;
  }

  .card .kill-doubt {
    font-size: 0.95em;
    line-height: 1.5;
    margin: 12px 0;
    padding: 12px;
    background: var(--card-alt);
    border-radius: 12px;
  }

  .card .kill-doubt strong {
    color: var(--accent-green);
  }

  .card .sacrificed {
    font-size: 0.85em;
    color: var(--text-secondary);
    margin: 8px 0;
  }

  .card .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.75em;
    font-weight: 500;
    background: var(--card-alt);
  }

  .badge.delivery-fast { color: var(--accent-green); }
  .badge.delivery-medium { color: var(--accent-orange); }
  .badge.delivery-slow { color: var(--accent-red); }
  .badge.trust-verified { color: var(--accent-green); }
  .badge.trust-unverified { color: var(--accent-red); }

  .buy-btn {
    display: block;
    text-align: center;
    padding: 14px;
    margin-top: 16px;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 600;
    font-size: 1em;
    transition: opacity 0.2s;
  }

  .buy-btn:hover { opacity: 0.85; }

  .best-value .buy-btn { background: var(--best-value); color: #000; }
  .near-pro .buy-btn { background: var(--near-pro); color: #fff; }
  .budget-killer .buy-btn { background: var(--budget-killer); color: #000; }

  .card .product-img {
    width: 100%;
    max-height: 200px;
    object-fit: contain;
    border-radius: 8px;
    margin-bottom: 12px;
    background: #fff;
  }

  details {
    background: var(--card);
    color: var(--text-primary);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
  }

  details summary {
    cursor: pointer;
    font-weight: 600;
    font-size: 0.95em;
  }

  details .content {
    margin-top: 12px;
    font-size: 0.9em;
    line-height: 1.7;
    color: var(--text-secondary);
  }

  .integration-section {
    margin: 24px 0;
  }

  .sources {
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid #ddd;
    font-size: 0.8em;
    color: var(--text-secondary);
  }

  .sources a {
    color: var(--accent-blue);
    text-decoration: none;
  }

  .deal-tag {
    display: inline-block;
    background: var(--accent-purple);
    color: #fff;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.7em;
    font-weight: 600;
    margin-right: 4px;
  }
</style>
</head>
<body>

<div class="header">
  <h1>جاك العلم 🔍</h1>
  <p class="subtitle">Personal Shopper Report</p>
  <p class="subtitle"><!-- DATE --></p>
</div>

<!-- REPEAT THIS BLOCK FOR EACH ITEM -->
<div class="item-section">
  <h2 class="item-title"><!-- ITEM NAME --></h2>

  <!-- BEST VALUE CARD -->
  <div class="card best-value">
    <span class="card-badge">✅ أفضل قيمة — Best Value</span>
    <!-- <img class="product-img" src="IMAGE_URL" alt="PRODUCT"> -->
    <h3><!-- PRODUCT NAME --></h3>
    <div class="price"><!-- PRICE --> ر.س</div>
    <div class="kill-doubt">
      <strong>ليش هذا الأفضل لك؟</strong><br>
      <!-- KILL DOUBT TEXT -->
    </div>
    <div class="sacrificed">⚖️ التنازل: <!-- WHAT'S SACRIFICED --></div>
    <div class="meta">
      <span class="badge delivery-fast">🟢 1-2 أيام</span>
      <span class="badge trust-verified">✅ بائع موثوق</span>
      <!-- <span class="deal-tag">كوبون: CODE</span> -->
      <!-- <span class="deal-tag">تمارا 3×</span> -->
    </div>
    <a class="buy-btn" href="<!-- LINK -->" target="_blank">اشتري الآن ←</a>
  </div>

  <!-- NEAR-PRO CARD -->
  <div class="card near-pro">
    <span class="card-badge">🔵 قريب من الاحتراف — Near-Pro</span>
    <!-- <img class="product-img" src="IMAGE_URL" alt="PRODUCT"> -->
    <h3><!-- PRODUCT NAME --></h3>
    <div class="price"><!-- PRICE --> ر.س</div>
    <div class="kill-doubt">
      <strong>ليش هذا الأفضل لك؟</strong><br>
      <!-- KILL DOUBT TEXT -->
    </div>
    <div class="sacrificed">⚖️ التنازل: <!-- WHAT'S SACRIFICED --></div>
    <div class="meta">
      <span class="badge delivery-medium">🟡 3-7 أيام</span>
      <span class="badge trust-verified">✅ بائع موثوق</span>
    </div>
    <a class="buy-btn" href="<!-- LINK -->" target="_blank">اشتري الآن ←</a>
  </div>

  <!-- BUDGET KILLER CARD -->
  <div class="card budget-killer">
    <span class="card-badge">🟠 قاتل الميزانية — Budget Killer</span>
    <!-- <img class="product-img" src="IMAGE_URL" alt="PRODUCT"> -->
    <h3><!-- PRODUCT NAME --></h3>
    <div class="price"><!-- PRICE --> ر.س</div>
    <div class="kill-doubt">
      <strong>ليش هذا الأفضل لك؟</strong><br>
      <!-- KILL DOUBT TEXT -->
    </div>
    <div class="sacrificed">⚖️ التنازل: <!-- WHAT'S SACRIFICED --></div>
    <div class="meta">
      <span class="badge delivery-fast">🟢 1-2 أيام</span>
      <span class="badge trust-unverified">⚠️ تحقق من البائع</span>
    </div>
    <a class="buy-btn" href="<!-- LINK -->" target="_blank">اشتري الآن ←</a>
  </div>

  <!-- ADR SUMMARY (collapsible) -->
  <details>
    <summary>📊 تحليل القرار (ADR Summary)</summary>
    <div class="content">
      <p><strong>التحليل:</strong> <!-- ANALYZE SECTION --></p>
      <p><strong>القرار:</strong> <!-- DECIDE SECTION --></p>
      <p><strong>التوصية:</strong> <!-- RECOMMEND SECTION --></p>
    </div>
  </details>
</div>
<!-- END ITEM BLOCK -->

<!-- INTEGRATION JUDGE (only for multi-item systems) -->
<!--
<div class="integration-section">
  <details>
    <summary>🔗 فحص التوافق — Integration Check</summary>
    <div class="content">
      <p>COMPATIBILITY REPORT HERE</p>
      <p>ADDITIONAL ITEMS NEEDED</p>
      <p>CONFLICTS IF ANY</p>
    </div>
  </details>
</div>
-->

<div class="sources">
  <h3>المصادر</h3>
  <ul>
    <!-- <li><a href="URL">Source description</a></li> -->
  </ul>
</div>

</body>
</html>
```

## Customization Notes

### Filling the Template

When generating the report, replace all `<!-- COMMENTS -->` with actual data:

1. **Product images:** Use product images from retailer sites if found. If not, omit the `<img>` tag.
2. **Delivery badges:** Use the appropriate class:
   - `delivery-fast` + 🟢 for 1-2 days
   - `delivery-medium` + 🟡 for 3-7 days
   - `delivery-slow` + 🔴 for 2-4 weeks
3. **Trust badges:** Use:
   - `trust-verified` + ✅ for known retailers
   - `trust-unverified` + ⚠️ for unknown/unverified sellers
4. **Deal tags:** Add `.deal-tag` spans for coupons, cashback, installment availability.
5. **Integration section:** Only include for multi-item system requests. Remove the comment wrapper.
6. **Date:** Insert the current date in the header subtitle.

### Design Principles

- **Mobile-first:** Max-width 600px. User reads on phone via Telegram.
- **Dark cards on light background:** High contrast, easy to scan.
- **Color-coded tiers:** Green = Best Value, Blue = Near-Pro, Orange = Budget Killer.
- **Kill Doubt is prominent:** The green-highlighted box is the most important element per card.
- **One-tap buy:** The purchase button is large, colored, and goes directly to the product page.
- **RTL layout:** Arabic is the default. `dir="rtl"` on the HTML element.
- **No external dependencies:** Pure HTML+CSS, no JavaScript frameworks, no CDN links. Works offline.
