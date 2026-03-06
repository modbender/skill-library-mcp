#!/usr/bin/env node
const http = require('https');

const token = process.env.GUMROAD_ACCESS_TOKEN || process.env.API_KEY;
if (!token) {
  if (process.argv.includes('--json')) {
    console.log(JSON.stringify({ success: false, error: "Error: GUMROAD_ACCESS_TOKEN or API_KEY environment variable not set.", code: "NO_TOKEN" }));
  } else {
    console.error("Error: GUMROAD_ACCESS_TOKEN or API_KEY environment variable not set.");
  }
  process.exit(1);
}

const args = process.argv.slice(2);
const command = args[0];
const subCommand = args[1];

// --- Helpers ---

const apiRequest = (method, path, data) => {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.gumroad.com',
      port: 443,
      path: `/v2${path}`,
      method: method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          resolve({ success: false, error: "Invalid JSON response", raw: body });
        }
      });
    });

    req.on('error', (e) => reject(e));
    if (data) {
      const postData = new URLSearchParams(data).toString();
      req.write(postData);
    }
    req.end();
  });
};

const parseNamedArgs = () => {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].substring(2);
      const value = args[i + 1];
      // Handle flags (args without values) or next arg is another flag
      if (value && !value.startsWith('--')) {
        result[key] = value;
      } else {
        result[key] = true;
      }
    }
  }
  return result;
};

const outputJSON = (data) => console.log(JSON.stringify(data, null, 2));
const outputError = (msg, data = null, json = false) => {
  if (json) console.log(JSON.stringify({ success: false, error: msg, details: data }));
  else console.error(msg, data || '');
};

// --- Main Logic ---

async function run() {
  const namedArgs = parseNamedArgs();

  try {
    // --- PRODUCTS ---
    if (command === 'products') {
      if (subCommand === 'list') {
        const data = await apiRequest('GET', '/products');
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log("\n📦 Products List:");
          data.products.forEach(p => {
            console.log(`- ${p.name} (ID: ${p.id}) | Price: ${p.formatted_price} | Sales: ${p.sales_count} | Published: ${p.published}`);
          });
        } else {
          outputError("Failed to fetch products:", data, namedArgs.json);
        }
      }
      else if (subCommand === 'details') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const data = await apiRequest('GET', `/products/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          const p = data.product;
          console.log(`\n📦 Product Details:
- Name: ${p.name}
- ID: ${p.id}
- Price: ${p.formatted_price}
- Sales: ${p.sales_count}
- Published: ${p.published}
- URL: ${p.short_url}
- Description: ${p.description || '(none)'}
- Thumbnail: ${p.thumbnail_url || '(none)'}
- Require Shipping: ${p.require_shipping}`);
        } else {
          outputError("Failed to fetch product:", data, namedArgs.json);
        }
      }
      else if (subCommand === 'create') {
        if (!namedArgs.name || !namedArgs.price) {
          outputError("Usage: products create --name \"Name\" --price 1000 [--description \"...\"]", null, namedArgs.json);
          return;
        }
        const data = await apiRequest('POST', '/products', {
          name: namedArgs.name,
          price: namedArgs.price,
          description: namedArgs.description || "",
          url: namedArgs.url,
          taxable: namedArgs.taxable,
          currency: namedArgs.currency || 'usd'
        });
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Created: ${data.product.name} (ID: ${data.product.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'update') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const params = {};
        if (namedArgs.name) params.name = namedArgs.name;
        if (namedArgs.price) params.price = namedArgs.price;
        if (namedArgs.description) params.description = namedArgs.description;
        if (namedArgs.url) params.url = namedArgs.url; // custom permalink
        // 'published' field in update is not the right way to toggle status for Gumroad API v2, use enable/disable endpoints

        const data = await apiRequest('PUT', `/products/${namedArgs.id}`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Updated: ${data.product.name}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'delete') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const data = await apiRequest('DELETE', `/products/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Deleted Product (ID: ${namedArgs.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'enable') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const data = await apiRequest('PUT', `/products/${namedArgs.id}/enable`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Published: ${data.product.name}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'disable') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const data = await apiRequest('PUT', `/products/${namedArgs.id}/disable`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Unpublished: ${data.product.name}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
    }

    // --- SALES ---
    else if (command === 'sales') {
      if (subCommand === 'list' || !subCommand) {
        let path = '/sales';
        const queryParams = [];
        if (namedArgs.after) queryParams.push(`after=${namedArgs.after}`);
        if (namedArgs.before) queryParams.push(`before=${namedArgs.before}`);
        if (namedArgs.page) queryParams.push(`page_key=${namedArgs.page}`);
        const productId = namedArgs.product_id || namedArgs.product;
        if (productId) queryParams.push(`product_id=${productId}`);
        if (namedArgs.email) queryParams.push(`email=${encodeURIComponent(namedArgs.email)}`);
        if (namedArgs.order_id) queryParams.push(`order_id=${namedArgs.order_id}`);

        if (queryParams.length > 0) path += `?${queryParams.join('&')}`;

        const data = await apiRequest('GET', path);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`\n💸 Sales Report:`);
          data.sales.forEach(s => {
            console.log(`- ${s.product_name} | ${s.formatted_total_price} | ${s.daystamp} | ${s.email} | ID: ${s.id}`);
          });

          if (data.next_page_key) {
            console.log(`🔑 NEXT_PAGE_KEY: ${data.next_page_key}`);
          }
        } else {
          console.error("Failed:", data);
        }
      }
      else if (subCommand === 'details') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const data = await apiRequest('GET', `/sales/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          const s = data.sale;

          // 1. Header
          console.log(`\n📦 ${s.product_name}`);
          console.log(`💰 Price: ${s.formatted_total_price}`);
          console.log(`📅 ${s.daystamp}`);

          // 2. Status Alerts (Always Visible)
          const refundStatus = s.refunded ? '💸 REFUNDED' : (s.partially_refunded ? `💸 PARTIAL REFUND ($${s.amount_refundable_in_currency} refundable)` : '💸 Refunded: No');
          console.log(refundStatus);

          const disputeStatus = s.disputed ? (s.dispute_won ? '✅ DISPUTE WON' : '⚠️ DISPUTED') : '⚖️ Disputed: No';
          console.log(disputeStatus);

          // 3. Subscription Context
          if (s.is_recurring_billing) {
            if (s.cancelled) console.log(`🚫 SUB CANCELLED`);
            else if (s.ended) console.log(`⏹️ SUB ENDED`);
            else console.log(`🔄 SUB ACTIVE`);

            if (s.subscription_duration) console.log(`📅 Frequency: ${s.subscription_duration}`);
            if (s.subscription_id) console.log(`🆔 Subscription ID: ${s.subscription_id}`);
          }

          // 4. Identity
          console.log(`👤 Customer: ${s.email}`);
          if (s.purchase_email && s.purchase_email.toLowerCase() !== s.email.toLowerCase()) {
            console.log(`🎁 Purchaser: ${s.purchase_email}`);
          }

          // 5. Product Details
          if (s.has_variants) {
            const v = s.variants_and_quantity || JSON.stringify(s.variants).replace(/[{"}]/g, '').replace(/:/g, ': ');
            console.log(`🎨 Variant: ${v}`);
          }

          if (s.has_custom_fields && Object.keys(s.custom_fields).length > 0) {
            console.log(`📝 Custom Fields:`);
            for (const [key, val] of Object.entries(s.custom_fields)) {
              console.log(`   • ${key}: ${val}`);
            }
          }

          if (s.license_key) {
            console.log(`🔑 License: ${s.license_key}`);
          }

          // 6. Shipping
          if (s.is_product_physical) {
            const shipStatus = s.shipped ? '✅ Shipped' : '📦 Processing';
            console.log(`🚚 ${shipStatus}`);
            if (s.tracking_url) console.log(`📍 Track: ${s.tracking_url}`);
            if (s.street_address) {
              console.log(`🏠 Address: ${s.full_name}, ${s.street_address}, ${s.city}, ${s.zip_code}, ${s.country}`);
            }
          }

          // 7. Affiliate
          if (s.affiliate) {
            console.log(`🤝 Affiliate: ${s.affiliate.email} (${s.affiliate.amount})`);
          }

          // 8. Meta
          console.log(`🆔 ID: ${s.id}`);
          console.log(`📦 Product ID: ${s.product_id}`);
          console.log(`📦 Physical: ${s.is_product_physical}`);
          if (s.order_id) console.log(`📄 Order #: ${s.order_id}`);

        } else {
          console.error("Failed:", data);
        }
      }
      else if (subCommand === 'refund') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const params = {};
        if (namedArgs.amount) params.amount_cents = namedArgs.amount;

        const data = await apiRequest('PUT', `/sales/${namedArgs.id}/refund`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Refund processed for Sale ID: ${namedArgs.id}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'mark-shipped') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const params = {};
        if (namedArgs.tracking) params.tracking_url = namedArgs.tracking;

        const data = await apiRequest('PUT', `/sales/${namedArgs.id}/mark_as_shipped`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Marked as Shipped: ${data.sale.product_name} (Tracking: ${data.sale.tracking_url || 'None'})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'resend-receipt') {
        if (!namedArgs.id) { return outputError("Error: --id required", null, namedArgs.json); }
        const data = await apiRequest('POST', `/sales/${namedArgs.id}/resend_receipt`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Receipt Resent for Sale ID: ${namedArgs.id}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
    }

    // --- LICENSES ---
    else if (command === 'licenses') {
      if (!namedArgs.product || !namedArgs.key) {
        outputError("Error: --product <id> and --key <license_key> required", null, namedArgs.json);
        return;
      }

      if (subCommand === 'verify') {
        const data = await apiRequest('POST', '/licenses/verify', {
          product_id: namedArgs.product,
          license_key: namedArgs.key,
          increment_uses_count: 'false' // Default to false for checking state
        });

        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          const p = data.purchase;
          const disabled = p.license_disabled ? '🔴 DISABLED' : '🟢 ENABLED';
          console.log(`\n🔑 License Info:
Status: ${disabled}
Uses: ${data.uses}
Key: ${p.license_key}
Email: ${p.email}
Refunded: ${p.refunded}
Subscription: ${p.subscription_cancelled_at ? 'Cancelled' : (p.subscription_failed_at ? 'Failed' : 'Active')}`);
        } else {
          outputError("Failed to verify license:", data, namedArgs.json);
        }
      }
      else if (subCommand === 'enable') {
        const data = await apiRequest('PUT', '/licenses/enable', {
          product_id: namedArgs.product,
          license_key: namedArgs.key
        });
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ License Enabled: ${namedArgs.key}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'decrement') {
        const data = await apiRequest('PUT', '/licenses/decrement_uses_count', {
          product_id: namedArgs.product,
          license_key: namedArgs.key
        });
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`📉 Usage Decremented. New Count: ${data.uses}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'rotate') {
        const data = await apiRequest('PUT', '/licenses/rotate', {
          product_id: namedArgs.product,
          license_key: namedArgs.key
        });
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`🔄 Key Rotated.\nNew Key: ${data.purchase.license_key}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
    }

    // --- DISCOUNTS (OFFER CODES) ---
    else if (command === 'discounts') {
      if (!namedArgs.product) { console.error("Error: --product <id> required"); return; }

      if (subCommand === 'list') {
        const data = await apiRequest('GET', `/products/${namedArgs.product}/offer_codes`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`\n🎟️ Discount Codes (Product: ${namedArgs.product}):`);
          data.offer_codes.forEach(o => {
            console.log(`- ${o.name} (ID: ${o.id}) | Used: ${o.times_used}/${o.max_purchase_count || '∞'} | Val: ${o.amount_cents ? '$' + (o.amount_cents / 100) : o.percent_off + '%'}`);
          });
        } else { outputError("Failed:", data, namedArgs.json); }
      }
      else if (subCommand === 'details') {
        if (!namedArgs.id) { console.error("Error: --id <discount_id> required"); return; }
        const data = await apiRequest('GET', `/products/${namedArgs.product}/offer_codes/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          const o = data.offer_code;
          console.log(`\n🎟️ Discount Details:
- Name: ${o.name}
- ID: ${o.id}
- Amount: ${o.amount_cents ? '$' + (o.amount_cents / 100) : o.percent_off + '%'}
- Usage: ${o.times_used} / ${o.max_purchase_count || '∞'}
- Universal: ${o.universal || 'false'}`);
        } else { outputError("Failed:", data, namedArgs.json); }
      }
      else if (subCommand === 'create') {
        if (!namedArgs.name || !namedArgs.amount) {
          console.error("Usage: discounts create --product <id> --name \"CODE\" --amount <val> --type <cents|percent>");
          return;
        }
        const params = { name: namedArgs.name, max_purchase_count: namedArgs.limit };
        if (namedArgs.type === 'percent') { params.amount_off = namedArgs.amount; params.offer_type = 'percent'; }
        else { params.amount_cents = namedArgs.amount; params.offer_type = 'cents'; }

        const data = await apiRequest('POST', `/products/${namedArgs.product}/offer_codes`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Created: ${data.offer_code.name} (ID: ${data.offer_code.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'update') {
        if (!namedArgs.id) { console.error("Error: --id <discount_id> required"); return; }
        const params = {};
        if (namedArgs.name) params.offer_code = namedArgs.name;
        if (namedArgs.limit) params.max_purchase_count = namedArgs.limit;
        if (namedArgs.amount) {
          if (namedArgs.type === 'percent') { params.amount_off = namedArgs.amount; params.offer_type = 'percent'; }
          else { params.amount_cents = namedArgs.amount; params.offer_type = 'cents'; }
        }
        const data = await apiRequest('PUT', `/products/${namedArgs.product}/offer_codes/${namedArgs.id}`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Updated: ${data.offer_code.name}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'delete') {
        if (!namedArgs.id) { console.error("Error: --id <discount_id> required"); return; }
        const data = await apiRequest('DELETE', `/products/${namedArgs.product}/offer_codes/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Deleted Discount (ID: ${namedArgs.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
    }

    // --- SUBSCRIBERS ---
    else if (command === 'subscribers') {
      if (subCommand === 'details') {
        if (!namedArgs.id) { console.error("Error: --id <subscriber_id> required"); return; }
        const data = await apiRequest('GET', `/subscribers/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          const s = data.subscriber;
          console.log(`\n👤 Subscriber Details:
- ID: ${s.id}
- Email: ${s.user_email}
- Status: ${s.status}
- Started: ${s.created_at}
- Recurrence: ${s.recurrence}
- Charge Count: ${s.charge_occurrence_count || 0}
- Cancelled At: ${s.cancelled_at || 'Active'}
- Ended At: ${s.ended_at || 'Active'}`);
        } else { outputError("Failed:", data, namedArgs.json); }
      }
      else {
        if (!namedArgs.product) { console.error("Error: --product <id> required"); return; }
        const data = await apiRequest('GET', `/products/${namedArgs.product}/subscribers`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`\n👥 Subscribers (Product: ${namedArgs.product}):`);
          data.subscribers.forEach(s => {
            console.log(`- ${s.user_email} (ID: ${s.id}) | Status: ${s.status} | Paid: ${s.charge_occurrence_count}`);
          });
        } else { outputError("Failed:", data, namedArgs.json); }
      }
    }

    // --- PAYOUTS ---
    else if (command === 'payouts') {
      if (subCommand === 'list' || !subCommand) {
        let path = '/payouts';
        const queryParams = [];
        if (namedArgs.after) queryParams.push(`after=${namedArgs.after}`);
        if (namedArgs.before) queryParams.push(`before=${namedArgs.before}`);
        if (namedArgs.page) queryParams.push(`page_key=${namedArgs.page}`);
        if (namedArgs.upcoming === 'false') queryParams.push(`include_upcoming=false`);

        if (queryParams.length > 0) path += `?${queryParams.join('&')}`;

        const data = await apiRequest('GET', path);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`\n💰 Payouts Report:`);
          data.payouts.forEach(p => {
            const label = p.id ? p.id : "✨ Upcoming";
            console.log(`- ${p.amount} ${p.currency} | ${p.status} | ${p.created_at} | ID: ${label}`);
          });

          if (data.next_page_key) {
            console.log(`🔑 NEXT_PAGE_KEY: ${data.next_page_key}`);
          }
        } else {
          outputError("Failed:", data, namedArgs.json);
        }
      }
      else if (subCommand === 'details') {
        if (!namedArgs.id) { console.error("Error: --id required"); return; }
        const data = await apiRequest('GET', `/payouts/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          const p = data.payout;
          console.log(`\n💰 Payout Details:
- ID: ${p.id}
- Amount: ${p.amount} ${p.currency}
- Status: ${p.status}
- Created: ${p.created_at}
- Processed: ${p.processed_at || 'Pending'}
- Processor: ${p.payment_processor}`);
        } else {
          outputError("Failed:", data, namedArgs.json);
        }
      }
    }

    // --- VARIANT CATEGORIES ---
    else if (command === 'variant-categories') {
      if (!namedArgs.product) { console.error("Error: --product <id> required"); return; }

      if (subCommand === 'list') {
        const data = await apiRequest('GET', `/products/${namedArgs.product}/variant_categories`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`\n🎨 Variant Categories (Product: ${namedArgs.product}):`);
          data.variant_categories.forEach(vc => {
            console.log(`- ${vc.title} (ID: ${vc.id})`);
          });
        } else { outputError("Failed:", data, namedArgs.json); }
      }
      else if (subCommand === 'create') {
        if (!namedArgs.title) { console.error("Error: --title <name> required"); return; }
        const data = await apiRequest('POST', `/products/${namedArgs.product}/variant_categories`, { title: namedArgs.title });
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Created Category: ${data.variant_category.title} (ID: ${data.variant_category.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'update') {
        if (!namedArgs.id || !namedArgs.title) { console.error("Error: --id <id> and --title <name> required"); return; }
        const data = await apiRequest('PUT', `/products/${namedArgs.product}/variant_categories/${namedArgs.id}`, { title: namedArgs.title });
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Updated Category: ${data.variant_category.title}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'delete') {
        if (!namedArgs.id) { console.error("Error: --id <id> required"); return; }
        const data = await apiRequest('DELETE', `/products/${namedArgs.product}/variant_categories/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Deleted Category (ID: ${namedArgs.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
    }

    // --- VARIANTS ---
    else if (command === 'variants') {
      if (!namedArgs.product) { console.error("Error: --product <id> required"); return; }
      if (!namedArgs.category) { console.error("Error: --category <id> required"); return; }

      if (subCommand === 'list') {
        const data = await apiRequest('GET', `/products/${namedArgs.product}/variant_categories/${namedArgs.category}/variants`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`\n🎨 Variants (Category: ${namedArgs.category}):`);
          data.variants.forEach(v => {
            console.log(`- ${v.name} (ID: ${v.id}) | Price Diff: ${v.price_difference_cents} cents | Max: ${v.max_purchase_count || '∞'}`);
          });
        } else { outputError("Failed:", data, namedArgs.json); }
      }
      else if (subCommand === 'create') {
        if (!namedArgs.name) { console.error("Error: --name <name> required"); return; }
        const params = { name: namedArgs.name };
        if (namedArgs.price) params.price_difference_cents = namedArgs.price;
        if (namedArgs.limit) params.max_purchase_count = namedArgs.limit;

        const data = await apiRequest('POST', `/products/${namedArgs.product}/variant_categories/${namedArgs.category}/variants`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Created Variant: ${data.variant.name} (ID: ${data.variant.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'update') {
        if (!namedArgs.id) { console.error("Error: --id <id> required"); return; }
        const params = {};
        if (namedArgs.name) params.name = namedArgs.name;
        if (namedArgs.price) params.price_difference_cents = namedArgs.price;
        if (namedArgs.limit) params.max_purchase_count = namedArgs.limit;

        const data = await apiRequest('PUT', `/products/${namedArgs.product}/variant_categories/${namedArgs.category}/variants/${namedArgs.id}`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Updated Variant: ${data.variant.name}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'delete') {
        if (!namedArgs.id) { console.error("Error: --id <id> required"); return; }
        const data = await apiRequest('DELETE', `/products/${namedArgs.product}/variant_categories/${namedArgs.category}/variants/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Deleted Variant (ID: ${namedArgs.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
    }

    // --- CUSTOM FIELDS ---
    else if (command === 'custom-fields') {
      if (!namedArgs.product) { console.error("Error: --product <id> required"); return; }

      if (subCommand === 'list') {
        const data = await apiRequest('GET', `/products/${namedArgs.product}/custom_fields`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`\n📝 Custom Fields (Product: ${namedArgs.product}):`);
          data.custom_fields.forEach(f => {
            console.log(`- ${f.name} | Required: ${f.required}`);
          });
        } else { outputError("Failed:", data, namedArgs.json); }
      }
      else if (subCommand === 'create') {
        if (!namedArgs.name) { console.error("Error: --name <name> required"); return; }
        const params = { name: namedArgs.name, required: namedArgs.required === 'true' };
        const data = await apiRequest('POST', `/products/${namedArgs.product}/custom_fields`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Created Field: ${data.custom_field.name}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'update') {
        if (!namedArgs.name) { console.error("Error: --name <name> required"); return; }
        // API uses field name in URL path
        const encodedName = encodeURIComponent(namedArgs.name);
        const params = { required: namedArgs.required === 'true' };
        const data = await apiRequest('PUT', `/products/${namedArgs.product}/custom_fields/${encodedName}`, params);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Updated Field: ${data.custom_field.name}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'delete') {
        if (!namedArgs.name) { console.error("Error: --name <name> required"); return; }
        const encodedName = encodeURIComponent(namedArgs.name);
        const data = await apiRequest('DELETE', `/products/${namedArgs.product}/custom_fields/${encodedName}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Deleted Field: ${namedArgs.name}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
    }

    else if (command === 'subscriptions') {
      if (subCommand === 'list' || !subCommand) {
        // List all resources if no type is given
        const resources = ['sale', 'refund', 'dispute', 'dispute_won', 'cancellation', 'subscription_updated', 'subscription_ended', 'subscription_restarted'];
        const filter = namedArgs.type ? [namedArgs.type] : resources;

        if (namedArgs.json) {
          const allSubs = {};
          for (const res of filter) {
            const data = await apiRequest('GET', `/resource_subscriptions?resource_name=${res}`);
            if (data.success) allSubs[res] = data.resource_subscriptions;
          }
          return outputJSON({ success: true, subscriptions: allSubs });
        }

        console.log(`\n📡 Webhooks (Resource Subscriptions):`);
        for (const res of filter) {
          const data = await apiRequest('GET', `/resource_subscriptions?resource_name=${res}`);
          if (data.success && data.resource_subscriptions.length > 0) {
            console.log(`\n[${res.toUpperCase()}]`);
            data.resource_subscriptions.forEach(s => console.log(`- ${s.post_url} (ID: ${s.id})`));
          } else if (namedArgs.type) {
            console.log(`\n[${res.toUpperCase()}] - No active subscriptions.`);
          }
        }
      }
      else if (subCommand === 'create') {
        if (!namedArgs.url || !namedArgs.type) {
          console.error("Usage: subscriptions create --url <http://...> --type <sale|refund|...>");
          return;
        }
        const data = await apiRequest('PUT', '/resource_subscriptions', {
          post_url: namedArgs.url,
          resource_name: namedArgs.type
        });
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Subscribed [${data.resource_subscription.resource_name}]: ${data.resource_subscription.post_url}`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
      else if (subCommand === 'delete') {
        if (!namedArgs.id) { console.error("Error: --id <subscription_id> required"); return; }
        const data = await apiRequest('DELETE', `/resource_subscriptions/${namedArgs.id}`);
        if (data.success) {
          if (namedArgs.json) return outputJSON(data);
          console.log(`✅ Deleted Subscription (ID: ${namedArgs.id})`);
        }
        else outputError("Failed:", data, namedArgs.json);
      }
    }

    // --- USER ---
    else if (command === 'user' || command === 'whoami') {
      const data = await apiRequest('GET', '/user');
      if (data.success) {
        if (namedArgs.json) return outputJSON(data);
        console.log(`\n👤 User Info:
- Name: ${data.user.name}
- Email: ${data.user.email}
- ID: ${data.user.id}
- URL: ${data.user.url}
- Currency: ${data.user.currency_type}`);
      } else { outputError("Failed:", data, namedArgs.json); }
    }

    else {
      console.log(`
Usage: gumroad-pro <command> [subcommand] [flags]

Commands:
  products
    list
    details --id <id>
    create --name "X" --price 100
    update --id <id> [--name "X"] [--price 100] [--published true|false]
    delete --id <id>
    enable --id <id>
    disable --id <id>
    
  sales
    list [--after YYYY-MM-DD]
    details --id <id>
    refund --id <id>
    
  discounts
    list --product <pid>
    create --product <pid> --name "CODE" --amount 500 --type cents|percent
    update --product <pid> --id <did> ...
    delete --product <pid> --id <did>
    
  subscribers
    list --product <pid>
    
  user
`);
    }

  } catch (err) {
    outputError("System Error:", err.message, namedArgs.json);
  }
}

run();