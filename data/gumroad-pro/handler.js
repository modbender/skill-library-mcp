const https = require('https');

// Channels with native button support
const BUTTON_CHANNELS = ['telegram', 'discord', 'slack', 'webchat'];

function apiRequest(ctx, method, path, data) {
  const token = ctx.env.GUMROAD_ACCESS_TOKEN || ctx.env.API_KEY;
  if (!token) return Promise.resolve({ success: false, error: "Missing GUMROAD_ACCESS_TOKEN or API_KEY" });

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

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          resolve({ success: false, error: "Invalid JSON response" });
        }
      });
    });

    req.on('error', (e) => resolve({ success: false, error: e.message }));
    if (data) {
      const postData = new URLSearchParams(data).toString();
      req.write(postData);
    }
    req.end();
  });
}

// Updated runGumroadJSON to be async and call apiRequest directly
async function runGumroadJSON(ctx, resource, action, params = {}) {
  let method = 'GET';
  let path = '';
  let data = null;

  switch (resource) {
    case 'products':
      if (action === 'list') path = '/products';
      else if (action === 'details') path = `/products/${encodeURIComponent(params.id)}`;
      else if (action === 'delete') { method = 'DELETE'; path = `/products/${encodeURIComponent(params.id)}`; }
      else if (action === 'enable') { method = 'PUT'; path = `/products/${encodeURIComponent(params.id)}/enable`; }
      else if (action === 'disable') { method = 'PUT'; path = `/products/${encodeURIComponent(params.id)}/disable`; }
      break;
    case 'sales':
      if (action === 'list') {
        path = '/sales';
        const q = [];
        if (params.email) q.push(`email=${encodeURIComponent(params.email)}`);
        if (params.product_id) q.push(`product_id=${params.product_id}`);
        if (params.page) q.push(`page_key=${params.page}`);
        if (q.length) path += `?${q.join('&')}`;
      }
      else if (action === 'details') path = `/sales/${encodeURIComponent(params.id)}`;
      else if (action === 'refund') { method = 'PUT'; path = `/sales/${encodeURIComponent(params.id)}/refund`; if (params.amount) data = { amount_cents: params.amount }; }
      else if (action === 'mark-shipped') { method = 'PUT'; path = `/sales/${encodeURIComponent(params.id)}/mark_as_shipped`; data = { tracking_url: params.tracking }; }
      else if (action === 'resend-receipt') { method = 'POST'; path = `/sales/${encodeURIComponent(params.id)}/resend_receipt`; }
      break;
    case 'licenses':
      if (action === 'verify') { method = 'POST'; path = '/licenses/verify'; data = { product_id: params.product, license_key: params.key, increment_uses_count: 'false' }; }
      else if (action === 'enable') { method = 'PUT'; path = '/licenses/enable'; data = { product_id: params.product, license_key: params.key }; }
      else if (action === 'disable') { method = 'PUT'; path = '/licenses/disable'; data = { product_id: params.product, license_key: params.key }; }
      else if (action === 'decrement') { method = 'PUT'; path = '/licenses/decrement_uses_count'; data = { product_id: params.product, license_key: params.key }; }
      else if (action === 'rotate') { method = 'PUT'; path = '/licenses/rotate'; data = { product_id: params.product, license_key: params.key }; }
      break;
    case 'discounts':
      if (action === 'list') path = `/products/${encodeURIComponent(params.product)}/offer_codes`;
      else if (action === 'details') path = `/products/${encodeURIComponent(params.product)}/offer_codes/${encodeURIComponent(params.id)}`;
      else if (action === 'create') {
        method = 'POST'; path = `/products/${encodeURIComponent(params.product)}/offer_codes`;
        data = { name: params.name, max_purchase_count: params.limit };
        if (params.type === 'percent') { data.amount_off = params.amount; data.offer_type = 'percent'; }
        else { data.amount_cents = params.amount; data.offer_type = 'cents'; }
      }
      else if (action === 'update') {
        method = 'PUT'; path = `/products/${encodeURIComponent(params.product)}/offer_codes/${encodeURIComponent(params.id)}`;
        data = {};
        if (params.name) data.offer_code = params.name;
        if (params.limit) data.max_purchase_count = params.limit;
      }
      else if (action === 'delete') { method = 'DELETE'; path = `/products/${encodeURIComponent(params.product)}/offer_codes/${encodeURIComponent(params.id)}`; }
      break;
    case 'subscriptions':
      if (action === 'list') {
        const resources = ['sale', 'refund', 'dispute', 'dispute_won', 'cancellation', 'subscription_updated', 'subscription_ended', 'subscription_restarted'];
        const allSubs = {};
        for (const res of resources) {
          const resData = await apiRequest(ctx, 'GET', `/resource_subscriptions?resource_name=${res}`);
          if (resData.success) allSubs[res] = resData.resource_subscriptions;
        }
        return { success: true, subscriptions: allSubs };
      }
      else if (action === 'create') { method = 'PUT'; path = '/resource_subscriptions'; data = { post_url: params.url, resource_name: params.type }; }
      else if (action === 'delete') { method = 'DELETE'; path = `/resource_subscriptions/${encodeURIComponent(params.id)}`; }
      break;
    case 'subscribers':
      if (action === 'details') path = `/subscribers/${encodeURIComponent(params.id)}`;
      break;
    case 'payouts':
      if (action === 'list') { path = '/payouts'; if (params.page) path += `?page_key=${encodeURIComponent(params.page)}`; }
      else if (action === 'details') path = `/payouts/${encodeURIComponent(params.id)}`;
      break;
    case 'variant-categories':
      if (action === 'list') path = `/products/${encodeURIComponent(params.product)}/variant_categories`;
      break;
    case 'variants':
      if (action === 'list') path = `/products/${encodeURIComponent(params.product)}/variant_categories/${encodeURIComponent(params.category)}/variants`;
      break;
    case 'custom-fields':
      if (action === 'list') path = `/products/${encodeURIComponent(params.product)}/custom_fields`;
      else if (action === 'create') { method = 'POST'; path = `/products/${encodeURIComponent(params.product)}/custom_fields`; data = { name: params.name, required: params.required === 'true' }; }
      else if (action === 'delete') { method = 'DELETE'; path = `/products/${encodeURIComponent(params.product)}/custom_fields/${encodeURIComponent(params.name)}`; }
      break;
    case 'whoami':
      path = '/user';
      break;
  }

  return await apiRequest(ctx, method, path, data);
}

// Parsing logic moved to runGumroadJSON

/**
 * Check if channel supports inline buttons
 */
function supportsButtons(ctx) {
  const channel = ctx.channel?.toLowerCase() || 'unknown';
  const capabilities = ctx.capabilities || [];
  return BUTTON_CHANNELS.includes(channel) &&
    (capabilities.includes('inlineButtons') || capabilities.includes('buttons'));
}

/**
 * Adaptive response renderer (Hybrid Mode)
 */
function renderResponse(ctx, data) {
  const { text, buttons, action = 'edit', interrupt = true, messageId } = data;
  const canUseButtons = supportsButtons(ctx);

  const flatButtons = buttons.flat();
  const mapping = {};

  // Build mapping for number replies (valid in both modes)
  flatButtons.forEach((btn, index) => {
    mapping[(index + 1).toString()] = btn.callback_data;
  });

  // Store mapping in session
  if (ctx.session) {
    ctx.session.gpMenuMapping = {
      mapping,
      timestamp: Date.now()
    };
  }

  if (canUseButtons) {
    // Button Mode: Clean text, explicit buttons
    const instruc = text + '\n\n*Tap an option below:*';
    return { text: instruc, buttons, action, interrupt, messageId };
  } else {
    // Text Mode: Append numbered list
    let adaptiveText = text + '\n\n';
    flatButtons.forEach((btn, index) => {
      adaptiveText += `${index + 1}. ${btn.text}\n`;
    });
    adaptiveText += '\n*Reply with a number to select.*';
    return { text: adaptiveText, action: 'send', interrupt }; // Force send for visibility
  }
}

module.exports = {
  name: 'gumroad-pro',
  version: '1.2.9',
  description: 'Gumroad Pro - Adaptive Multi-Channel Suite',

  commands: {
    gumroad_pro: {
      description: 'Open Gumroad Pro Menu',
      aliases: ['gumroad', 'gp', 'gumroad-pro', 'gumroad_pro'],
      async execute(ctx) {
        return renderResponse(ctx, { ...getMainMenu(), action: 'send' });
      }
    }
  },

  async onMessage(ctx, next) {
    let text = ctx.message?.text?.trim();
    if (!text && ctx.callback_query?.data) text = ctx.callback_query.data;
    if (!text && ctx.callbackData) text = ctx.callbackData;

    // --- HANDLE NUMBER REPLIES (Text Channels) ---
    if (/^\d+$/.test(text) && ctx.session?.gpMenuMapping) {
      const mapping = ctx.session.gpMenuMapping.mapping;
      const elapsed = Date.now() - ctx.session.gpMenuMapping.timestamp;

      // Mapping valid for 15 minutes
      if (elapsed < 15 * 60 * 1000 && mapping[text]) {
        text = mapping[text];
      }
    }

    // --- HANDLE PENDING INPUT ---
    if (ctx.session?.gpPendingInput) {
      const state = ctx.session.gpPendingInput;
      // Allow number replies within state machine if mapping exists
      // State is always scoped to the user/session automatically by ctx.session

      if (state.action === 'create_field') {
        const res = await runGumroadJSON(ctx, 'custom-fields', 'create', { product: state.pid, name: text, required: 'false' });
        delete ctx.session.gpPendingInput;
        if (res.success) return renderResponse(ctx, { text: `✅ Created field: "${text}"`, buttons: [[{ text: '🔙 Back', callback_data: `gp:cf:${state.pid}` }]], action: 'edit', interrupt: true });
        else return renderResponse(ctx, { text: `❌ Failed: ${res.error}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:cf:${state.pid}` }]], action: 'edit' });
      }
      if (state.action === 'mark_shipped') {
        const res = await runGumroadJSON(ctx, 'sales', 'mark-shipped', { id: state.sid, tracking: text });
        delete ctx.session.gpPendingInput;
        if (res.success) return renderResponse(ctx, { ...(await getSaleDetails(ctx, state.sid)), text: `✅ Marked as Shipped`, action: 'edit' });
        else return renderResponse(ctx, { text: `❌ Failed: ${res.error}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:sale:${state.sid}` }]], action: 'edit' });
      }

      if (state.action === 'create_webhook') {
        const res = await runGumroadJSON(ctx, 'subscriptions', 'create', { type: state.resource, url: text });
        delete ctx.session.gpPendingInput;
        if (res.success) return renderResponse(ctx, { ...(await getSubscriptionsMenu(ctx)), text: `✅ Subscribed to '${state.resource}'`, action: 'edit' });
        else return renderResponse(ctx, { text: `❌ Failed: ${res.error}`, buttons: [[{ text: '🔙 Back', callback_data: 'gp:subs' }]], action: 'edit' });
      }
      else if (state.action === 'search_sales_email') {
        delete ctx.session.gpPendingInput;
        ctx.session.gpSalesFilter = { email: text, productId: null };
        return renderResponse(ctx, { ...(await getSalesMenu(ctx)), action: 'edit', interrupt: true });
      }
      else if (state.action === 'disc_name') {
        ctx.session.gpPendingInput = { ...state, name: text, action: 'disc_val' };
        return renderResponse(ctx, { text: `🎟️ **New Discount: "${text}"**\n\nPlease reply with the **Amount**.`, action: 'edit', interrupt: true });
      }
      else if (state.action === 'disc_val') {
        const val = parseInt(text);
        ctx.session.gpPendingInput.amount = val;
        return renderResponse(ctx, {
          text: `🎟️ **Discount: ${state.name} (${val})**\n\nSelect the **Type**:`,
          buttons: [
            [{ text: '💵 Fixed (Cents)', callback_data: `gp:disc_final:cents` }],
            [{ text: '🏷️ Percentage (%)', callback_data: `gp:disc_final:percent` }],
            [{ text: '❌ Cancel', callback_data: `gp:discounts:${state.pid}` }]
          ],
          action: 'edit', interrupt: true
        });
      }
      else if (state.action === 'disc_edit_name') {
        ctx.session.gpPendingInput = { ...state, newName: text === 'skip' ? null : text, action: 'disc_edit_limit' };
        return renderResponse(ctx, { text: `📝 **Editing Discount**\n\nPlease reply with the new **Usage Limit**.\n(Type 'skip' to keep current)`, action: 'edit', interrupt: true });
      }
      else if (state.action === 'disc_edit_limit') {
        const limit = text === 'skip' ? null : text;
        const params = { product: state.pid, id: state.did };
        if (state.newName) params.name = state.newName;
        if (limit !== null) params.limit = limit;
        const res = await runGumroadJSON(ctx, 'discounts', 'update', params);
        delete ctx.session.gpPendingInput;
        if (res.success) return renderResponse(ctx, { ...(await getDiscountDetails(ctx, state.pid, state.did)), text: '✅ Discount Updated', action: 'edit' });
        else return renderResponse(ctx, { text: `❌ Failed: ${res.error}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:disc_det:${state.pid}:${state.did}` }]], action: 'edit' });
      }
    }

    if (!text || !text.startsWith('gp:')) return next();

    // --- NAVIGATION (Always Clear State) ---
    if (text === 'gp:main' || text === 'gp:products' || text === 'gp:sales' || text === 'gp:payouts' || text === 'gp:subs' || text === 'gp:whoami') {
      delete ctx.session.gpPendingInput;
    }

    if (text === 'gp:main') return renderResponse(ctx, { ...getMainMenu(), action: 'edit', interrupt: true });

    // --- PRODUCTS ---
    if (text === 'gp:products') return renderResponse(ctx, { ...(await getProductsMenu(ctx)), action: 'edit', interrupt: true });
    if (text.startsWith('gp:prod:')) return renderResponse(ctx, { ...(await getProductDetails(ctx, text.split(':')[2])), action: 'edit', interrupt: true });
    if (text.startsWith('gp:prod_toggle:')) {
      const [_, __, id, currentState] = text.split(':');
      await runGumroadJSON(ctx, 'products', currentState === 'true' ? 'disable' : 'enable', { id });
      return renderResponse(ctx, { ...(await getProductDetails(ctx, id)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:prod_del_ask:')) {
      const id = text.split(':')[2];
      return renderResponse(ctx, {
        text: '⚠️ **DELETE PRODUCT?**\nThis will permanently remove the product and all associated data. This cannot be undone.',
        buttons: [[{ text: '🔥 YES, DELETE', callback_data: `gp:prod_del_do:${id}` }], [{ text: '❌ Cancel', callback_data: `gp:prod:${id}` }]],
        action: 'edit', interrupt: true
      });
    }
    if (text.startsWith('gp:prod_del_do:')) {
      const id = text.split(':')[2];
      const res = await runGumroadJSON(ctx, 'products', 'delete', { id });
      if (!res.success) return renderResponse(ctx, { text: `❌ Failed to delete: ${res.error}`, action: 'alert' });
      return renderResponse(ctx, { ...(await getProductsMenu(ctx)), action: 'edit', interrupt: true });
    }

    if (text.startsWith('gp:vc:')) {
      const pid = text.split(':')[2];
      return renderResponse(ctx, { ...(await getVariantCategoriesMenu(ctx, pid)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:variants:')) {
      const [_, __, pid, cid] = text.split(':');
      return renderResponse(ctx, { ...(await getVariantsListMenu(ctx, pid, cid)), action: 'edit', interrupt: true });
    }

    if (text === 'gp:sales') {
      ctx.session.gpSalesFilter = { email: null, productId: null };
      return renderResponse(ctx, { ...(await getSalesMenu(ctx)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:prod_sales:')) {
      const productId = text.split(':')[2];
      ctx.session.gpSalesFilter = { email: null, productId: productId };
      return renderResponse(ctx, { ...(await getSalesMenu(ctx)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:sales_page:')) {
      const pageKey = text.split(':')[2];
      return renderResponse(ctx, { ...(await getSalesMenu(ctx, pageKey)), action: 'edit', interrupt: true });
    }
    if (text === 'gp:sales_search_ask') {
      ctx.session.gpPendingInput = { action: 'search_sales_email' };
      return renderResponse(ctx, { text: '🔍 **Search Sales**\n\nPlease reply with the **Customer Email**.', buttons: [[{ text: '❌ Cancel', callback_data: 'gp:sales' }]], action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:sale:')) return renderResponse(ctx, { ...(await getSaleDetails(ctx, text.split(':')[2])), action: 'edit', interrupt: true });

    if (text.startsWith('gp:sale_refund_ask:')) {
      const sid = text.split(':')[2];
      return renderResponse(ctx, {
        text: '⚠️ **REFUND SALE?**\nThis will refund the customer. This action is irreversible.',
        buttons: [[{ text: '🔥 YES, REFUND', callback_data: `gp:sale_refund_do:${sid}` }], [{ text: '❌ Cancel', callback_data: `gp:sale:${sid}` }]],
        action: 'edit', interrupt: true
      });
    }
    if (text.startsWith('gp:sale_refund_do:')) {
      const id = text.split(':')[2];
      const res = await runGumroadJSON(ctx, 'sales', 'refund', { id });
      if (!res.success) return renderResponse(ctx, { text: `❌ Refund Failed: ${res.error}`, action: 'alert' });
      return renderResponse(ctx, { ...(await getSaleDetails(ctx, id)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:sale_resend:')) {
      const id = text.split(':')[2];
      const res = await runGumroadJSON(ctx, 'sales', 'resend-receipt', { id });
      if (!res.success) return renderResponse(ctx, { text: `❌ Failed: ${res.error}`, action: 'alert' });
      return renderResponse(ctx, { text: '✅ Receipt Resent', action: 'alert' });
    }
    if (text.startsWith('gp:sale_ship_ask:')) {
      const sid = text.split(':')[3];
      ctx.session.gpPendingInput = { sid: sid, action: 'mark_shipped' };
      return renderResponse(ctx, { text: '🚚 **Mark as Shipped**\n\nPlease reply with the **Tracking URL** or number.', buttons: [[{ text: '❌ Cancel', callback_data: `gp:sale:${sid}` }]], action: 'edit', interrupt: true });
    }

    if (text.startsWith('gp:sub_det:')) {
      const [_, __, subId, saleId] = text.split(':');
      const data = await runGumroadJSON(ctx, 'subscribers', 'details', { id: subId });
      let msg = '';
      if (data.success) {
        const s = data.subscriber;
        msg = `👤 **Subscriber Profile**\nID: \`${s.id}\`\nEmail: ${s.user_email}\nStatus: ${s.status}\nStarted: ${s.created_at}\n\nRecurrence: ${s.recurrence}\nPaid: ${s.charge_occurrence_count}\nEnded: ${s.ended_at || 'Active'}`;
      } else {
        msg = `⚠️ Error: ${data.error}`;
      }
      return renderResponse(ctx, {
        text: msg,
        buttons: [[{ text: '🔙 Back to Sale', callback_data: `gp:sale:${saleId}` }]],
        action: 'edit', interrupt: true
      });
    }

    // --- PAYOUTS ---
    if (text === 'gp:payouts') return renderResponse(ctx, { ...(await getPayoutsMenu(ctx)), action: 'edit', interrupt: true });
    if (text.startsWith('gp:payout_page:')) {
      return renderResponse(ctx, { ...(await getPayoutsMenu(ctx, text.split(':')[2])), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:payout_det:')) {
      return renderResponse(ctx, { ...(await getPayoutDetails(ctx, text.split(':')[2])), action: 'edit', interrupt: true });
    }

    // --- DISCOUNTS ---
    if (text.startsWith('gp:discounts:')) return renderResponse(ctx, { ...(await getDiscountsMenu(ctx, text.split(':')[2])), action: 'edit', interrupt: true });
    if (text.startsWith('gp:disc_det:')) {
      const [_, __, pid, did] = text.split(':');
      return renderResponse(ctx, { ...(await getDiscountDetails(ctx, pid, did)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:de:')) {
      const [_, __, pid, did] = text.split(':');
      ctx.session.gpPendingInput = { pid: pid, did: did, action: 'disc_edit_name' };
      return renderResponse(ctx, { text: `📝 **Editing Discount**\n\nPlease reply with the new **Code Name**.\n(Type 'skip' to keep current)`, buttons: [[{ text: '❌ Cancel', callback_data: `gp:disc_det:${pid}:${did}` }]], action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:dd:')) {
      const [_, __, pid, did] = text.split(':');
      return renderResponse(ctx, {
        text: '⚠️ **DELETE DISCOUNT?**\nThis will permanently remove this code.',
        buttons: [[{ text: '🔥 YES, DELETE', callback_data: `gp:dc:${pid}:${did}` }], [{ text: '❌ Cancel', callback_data: `gp:disc_det:${pid}:${did}` }]],
        action: 'edit', interrupt: true
      });
    }
    if (text.startsWith('gp:dc:')) {
      const [_, __, pid, did] = text.split(':');
      await runGumroadJSON(ctx, 'discounts', 'delete', { product: pid, id: did });
      return renderResponse(ctx, { ...(await getDiscountsMenu(ctx, pid)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:disc_ask:')) {
      const pid = text.split(':')[2];
      ctx.session.gpPendingInput = { pid: pid, action: 'disc_name' };
      return renderResponse(ctx, { text: '🎟️ **Create Discount**\n\nPlease reply with the **Code Name**.', buttons: [[{ text: '❌ Cancel', callback_data: `gp:discounts:${pid}` }]], action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:disc_final:')) {
      const state = ctx.session.gpPendingInput;
      if (!state) return renderResponse(ctx, { text: '⚠️ Session expired. Please restart.', buttons: [[{ text: '🔙 Back', callback_data: 'gp:main' }]], action: 'edit' });

      const type = text.split(':')[2];
      const res = await runGumroadJSON(ctx, 'discounts', 'create', {
        product: state.pid,
        name: state.name,
        amount: state.amount,
        type: type,
        limit: 1000
      });
      delete ctx.session.gpPendingInput;
      if (res.success) return renderResponse(ctx, { ...(await getDiscountsMenu(ctx, state.pid)), text: '✅ Discount Created', action: 'edit' });
      else return renderResponse(ctx, { text: `❌ Failed: ${res.error}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:discounts:${state.pid}` }]], action: 'edit' });
    }

    // --- WEBHOOKS ---
    if (text === 'gp:subs') return renderResponse(ctx, { ...(await getSubscriptionsMenu(ctx)), action: 'edit', interrupt: true });
    if (text.startsWith('gp:sub_del_ask:')) {
      const id = text.split(':')[3];
      return renderResponse(ctx, {
        text: '⚠️ **DELETE WEBHOOK?**\nYou will stop receiving automated notifications at this URL.',
        buttons: [[{ text: '🔥 YES, DELETE', callback_data: `gp:sub_del_do:${id}` }], [{ text: '❌ Cancel', callback_data: 'gp:subs' }]],
        action: 'edit', interrupt: true
      });
    }
    if (text.startsWith('gp:sub_del_do:')) {
      const id = text.split(':')[3];
      const res = await runGumroadJSON(ctx, 'subscriptions', 'delete', { id });
      if (!res.success) return renderResponse(ctx, { text: `❌ Failed: ${res.error}`, action: 'alert' });
      return renderResponse(ctx, { ...(await getSubscriptionsMenu(ctx)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:sub_ask:')) {
      const resource = text.split(':')[2];
      ctx.session.gpPendingInput = { resource, action: 'create_webhook' };
      return renderResponse(ctx, { text: `📡 **Create Webhook [${resource.toUpperCase()}]**\n\nPlease reply with the **Destination URL**.`, buttons: [[{ text: '❌ Cancel', callback_data: 'gp:subs' }]], action: 'edit', interrupt: true });
    }

    // --- ACCOUNT ---
    if (text === 'gp:whoami') {
      const data = await runGumroadJSON(ctx, 'whoami');
      let msg = '';
      if (data.success) {
        msg = `👤 **Account Info**\n- Name: ${data.user.name}\n- Email: ${data.user.email}\n- ID: \`${data.user.id}\`\n- URL: ${data.user.url}\n- Currency: ${data.user.currency_type}`;
      } else {
        msg = `⚠️ Error: ${data.error}`;
      }
      return renderResponse(ctx, {
        text: msg,
        buttons: [
          [{ text: '🌐 Developer GitHub', url: 'https://github.com/abdul-karim-mia' }],
          [{ text: '🔙 Back', callback_data: 'gp:main' }]
        ],
        action: 'edit', interrupt: true
      });
    }

    // --- CUSTOM FIELDS ---
    if (text.startsWith('gp:cf:')) {
      const pid = text.split(':')[2];
      return renderResponse(ctx, { ...(await getCustomFieldsMenu(ctx, pid)), action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:cf_ask:')) {
      const pid = text.split(':')[2];
      ctx.session.gpPendingInput = { pid: pid, action: 'create_field' };
      return renderResponse(ctx, { text: '📝 **Create Custom Field**\n\nPlease reply with the **Field Name**.', buttons: [[{ text: '❌ Cancel', callback_data: `gp:cf:${pid}` }]], action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:cf_del:')) {
      const [_, __, pid, name] = text.split(':');
      await runGumroadJSON(ctx, 'custom-fields', 'delete', { product: pid, name });
      return renderResponse(ctx, { ...(await getCustomFieldsMenu(ctx, pid)), action: 'edit', interrupt: true });
    }

    // --- LICENSES ---
    if (text.startsWith('gp:lic_check:')) {
      const sid = text.split(':')[2];
      const sData = await runGumroadJSON(ctx, 'sales', 'details', { id: sid });
      if (!sData.success) return renderResponse(ctx, { text: '❌ Error.', action: 'edit', interrupt: true });

      const s = sData.sale;
      if (!s.license_key || !s.product_id) return renderResponse(ctx, { text: '❌ No license.', action: 'edit', interrupt: true });

      const key = s.license_key, pid = s.product_id;
      const lData = await runGumroadJSON(ctx, 'licenses', 'verify', { product: pid, key });

      if (!lData.success) return renderResponse(ctx, { text: `❌ Error: ${lData.error}`, action: 'edit', interrupt: true });

      const p = lData.purchase;
      const isDisabled = p.license_disabled === true;

      return renderResponse(ctx, {
        text: `🔑 **License Verification**\nStatus: ${isDisabled ? '🔴 DISABLED' : '🟢 ENABLED'}\nUses: ${lData.uses}\nKey: \`${p.license_key}\`\nEmail: ${p.email}`,
        buttons: [
          [{ text: isDisabled ? '🟢 Enable License' : '🔴 Disable License', callback_data: `gp:lic_toggle:${sid}` }, { text: '📉 Decr. Count', callback_data: `gp:lic_decr:${sid}` }],
          [{ text: '🔄 Rotate Key', callback_data: `gp:lic_rot_ask:${sid}` }],
          [{ text: '🔙 Back to Sale', callback_data: `gp:sale:${sid}` }]
        ],
        action: 'edit', interrupt: true
      });
    }

    if (text.startsWith('gp:lic_toggle:')) {
      const sid = text.split(':')[2];
      const sData = await runGumroadJSON(ctx, 'sales', 'details', { id: sid });
      if (sData.success) {
        const s = sData.sale;
        if (s.license_key && s.product_id) {
          const key = s.license_key, pid = s.product_id;
          // Check current state
          const lData = await runGumroadJSON(ctx, 'licenses', 'verify', { product: pid, key });
          if (lData.success) {
            const action = lData.purchase.license_disabled ? 'enable' : 'disable';
            const res = await runGumroadJSON(ctx, 'licenses', action, { product: pid, key });
            if (res.success) return renderResponse(ctx, { text: `✅ License ${action}d.`, buttons: [[{ text: '🔙 Back', callback_data: `gp:lic_check:${sid}` }]], action: 'edit', interrupt: true });
          }
        }
      }
      return renderResponse(ctx, { text: '❌ Failed to toggle.', action: 'edit', interrupt: true });
    }
    if (text.startsWith('gp:lic_decr:')) {
      const sid = text.split(':')[2];
      const sData = await runGumroadJSON(ctx, 'sales', 'details', { id: sid });
      if (sData.success) {
        const s = sData.sale;
        await runGumroadJSON(ctx, 'licenses', 'decrement', { product: s.product_id, key: s.license_key });
        return renderResponse(ctx, { text: '📉 Usage count decremented.', buttons: [[{ text: '🔙 Back', callback_data: `gp:lic_check:${sid}` }]], action: 'edit', interrupt: true });
      }
    }
    if (text.startsWith('gp:lic_rot_ask:')) {
      const sid = text.split(':')[2];
      return renderResponse(ctx, {
        text: '⚠️ **ROTATE LICENSE KEY?**\nThe current key will be invalidated and a new one generated for the customer.',
        buttons: [[{ text: '🔄 YES, ROTATE', callback_data: `gp:lic_rot_do:${sid}` }], [{ text: '❌ Cancel', callback_data: `gp:lic_check:${sid}` }]],
        action: 'edit', interrupt: true
      });
    }
    if (text.startsWith('gp:lic_rot_do:')) {
      const sid = text.split(':')[2];
      const sData = await runGumroadJSON(ctx, 'sales', 'details', { id: sid });
      if (sData.success) {
        const s = sData.sale;
        await runGumroadJSON(ctx, 'licenses', 'rotate', { product: s.product_id, key: s.license_key });
        return renderResponse(ctx, { text: '🔄 License key rotated successfully.', buttons: [[{ text: '🔙 Back', callback_data: `gp:lic_check:${sid}` }]], action: 'edit', interrupt: true });
      }
    }

    return next();
  }
};

// --- View Generators ---

function getMainMenu() {
  return {
    text: '💎 **Gumroad Pro Dashboard**\n\nWelcome back, Sir. Your digital empire is summarized below. Use the control hub to monitor sales, manage products, and oversee your payouts in real-time.',
    buttons: [
      [{ text: '📦 Products', callback_data: 'gp:products' }, { text: '💸 Sales', callback_data: 'gp:sales' }],
      [{ text: '💰 Payouts', callback_data: 'gp:payouts' }, { text: '📡 Webhooks', callback_data: 'gp:subs' }],
      [{ text: '👤 Account', callback_data: 'gp:whoami' }, { text: '🔄 Refresh Dashboard', callback_data: 'gp:main' }]
    ]
  };
}

async function getProductsMenu(ctx) {
  const data = await runGumroadJSON(ctx, 'products', 'list');
  let buttons = [];

  if (data.success && data.products) {
    buttons = data.products.map(p => {
      const isPublished = p.published === true || p.published === 'true';
      return [{ text: `${isPublished ? '🟢' : '🔴'} ${p.name.substring(0, 40)}`, callback_data: `gp:prod:${p.id}` }];
    });
  } else {
    return { text: `⚠️ Error fetching products: ${data.error || 'Unknown error'}`, buttons: [[{ text: '🔙 Back', callback_data: 'gp:main' }]] };
  }

  buttons.push([{ text: '🔙 Back to Main Menu', callback_data: 'gp:main' }]);
  return {
    text: '📦 **Product Inventory**\n\nSir, here is the complete list of your digital offerings. You can monitor sales volume, verify pricing, or toggle availability for each item.',
    buttons
  };
}

async function getProductDetails(ctx, id) {
  const data = await runGumroadJSON(ctx, 'products', 'details', { id });
  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: 'gp:products' }]] };

  const p = data.product;
  const isPublished = p.published === 'true' || p.published === true;

  const desc = p.description || 'No description.';
  const truncatedDesc = desc.length > 200 ? desc.substring(0, 200) + '...' : desc;

  const details = `
📦 **${p.name}**
ID: \`${p.id}\`
💰 Price: ${p.formatted_price}
📉 Sales: ${p.sales_count}
${isPublished ? '🟢 Published' : '🔴 Unpublished'}
🔗 [Short URL](${p.short_url})

${truncatedDesc}
`.trim();

  return {
    text: `🛠️ **Product Management**\n\nDetailed specifications for the selected asset are listed below.\n\n${details}`,
    buttons: [
      [{ text: isPublished ? '🔴 Unpublish' : '🟢 Publish', callback_data: `gp:prod_toggle:${id}:${isPublished}` }, { text: '🎨 Variants', callback_data: `gp:vc:${id}` }],
      [{ text: '🎟️ Discounts', callback_data: `gp:discounts:${id}` }, { text: '📝 Custom Fields', callback_data: `gp:cf:${id}` }],
      [{ text: '🛒 View Sales', callback_data: `gp:prod_sales:${id}` }, { text: '🗑️ Delete', callback_data: `gp:prod_del_ask:${id}` }],
      [{ text: '🔙 Back to Products', callback_data: 'gp:products' }]
    ]
  }
}

async function getSalesMenu(ctx, pageKey = null) {
  const filter = ctx.session?.gpSalesFilter || { email: null, productId: null };
  const params = {};
  if (filter.email) params.email = filter.email;
  if (filter.productId) params.product_id = filter.productId;
  if (pageKey) params.page = pageKey;

  const data = await runGumroadJSON(ctx, 'sales', 'list', params);
  let title = '💸 **Transaction Ledger**\n\nSir, here are the most recent acquisitions. Select a transaction to view details.';

  if (filter.email) title = `🔎 **Search Results**\n\nDisplaying records matching: \`${filter.email}\``;
  else if (filter.productId) title = `🛒 **Product Sales**\n\nDisplaying transactions for the selected inventory item, Sir.`;

  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: filter.productId ? `gp:prod:${filter.productId}` : 'gp:main' }]] };
  if (!data.sales || data.sales.length === 0) return { text: `🔍 **No Records Found**\n\nI couldn't find any transactions matching your criteria, Sir.`, buttons: [[{ text: '🔙 Back', callback_data: filter.productId ? `gp:prod:${filter.productId}` : 'gp:sales' }]] };

  const buttons = data.sales.map(s => {
    return [{ text: `${s.email} - ${s.product_name.substring(0, 30)}`, callback_data: `gp:sale:${s.id}` }];
  });

  const backTarget = filter.productId ? `gp:prod:${filter.productId}` : 'gp:main';
  const navRow = [{ text: '🔙 Back', callback_data: backTarget }];

  if (data.next_page_key) navRow.push({ text: '➡️ Next', callback_data: `gp:sales_page:${data.next_page_key}` });
  if (pageKey) navRow.push({ text: '🏠 First', callback_data: filter.productId ? `gp:prod_sales:${filter.productId}` : 'gp:sales' });

  buttons.push(navRow);

  return { text: title, buttons };
}

async function getSaleDetails(ctx, id) {
  const data = await runGumroadJSON(ctx, 'sales', 'details', { id });
  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: 'gp:sales' }]] };

  const s = data.sale;
  const buttons = [];

  const row1 = [{ text: '💸 Refund', callback_data: `gp:sale_refund_ask:${id}` }];
  if (s.is_product_physical) {
    row1.push({ text: '🚚 Mark Shipped', callback_data: `gp:sale_ship_ask:${id}` });
  }
  buttons.push(row1);

  const row2 = [{ text: '📩 Resend Receipt', callback_data: `gp:sale_resend:${id}` }];
  if (s.license_key) {
    row2.push({ text: '🔑 Check License', callback_data: `gp:lic_check:${id}` });
  }
  buttons.push(row2);

  if (s.subscription_id) {
    buttons.push([{ text: '👤 Subscriber Info', callback_data: `gp:sub_det:${s.subscription_id}:${id}` }]);
  }

  buttons.push([{ text: '🔙 Back to Sales', callback_data: 'gp:sales' }, { text: '🏠 Main Menu', callback_data: 'gp:main' }]);

  let detailsBuffer = [`📦 **${s.product_name}**`, `💰 Price: ${s.formatted_total_price}`, `📅 ${s.daystamp}`];
  detailsBuffer.push(s.refunded ? '💸 REFUNDED' : (s.partially_refunded ? `💸 PARTIAL REFUND` : '💸 Refunded: No'));
  if (s.disputed) detailsBuffer.push(s.dispute_won ? '✅ DISPUTE WON' : '⚠️ DISPUTED');

  if (s.is_recurring_billing) {
    detailsBuffer.push(`\n🔄 SUB ${s.cancelled ? 'CANCELLED' : (s.ended ? 'ENDED' : 'ACTIVE')}`);
    if (s.subscription_id) detailsBuffer.push(`🆔 Sub ID: \`${s.subscription_id}\``);
  }

  detailsBuffer.push(`\n👤 Customer: \`${s.email}\``);
  if (s.purchase_email && s.purchase_email !== s.email) detailsBuffer.push(`🎁 Purchaser: ${s.purchase_email}`);
  if (s.license_key) detailsBuffer.push(`🔑 License: \`${s.license_key}\``);
  if (s.variants_and_quantity) detailsBuffer.push(`🎨 Variant: ${s.variants_and_quantity}`);

  if (s.is_product_physical) {
    detailsBuffer.push(`🚚 ${s.shipped ? '✅ Shipped' : '📦 Processing'}`);
    if (s.tracking_url) detailsBuffer.push(`📍 Track: ${s.tracking_url}`);
    if (s.street_address) detailsBuffer.push(`🏠 Address: ${s.street_address}, ${s.city}, ${s.zip_code}, ${s.country}`);
  }

  detailsBuffer.push(`\n🆔 ID: \`${s.id}\``);

  return { text: `📜 **Transaction Intelligence**\n\nFull details of the customer purchase are presented below, Sir.\n\n${detailsBuffer.join('\n')}`, buttons };
}

async function getPayoutsMenu(ctx, pageKey = null) {
  const data = await runGumroadJSON(ctx, 'payouts', 'list', { page: pageKey });

  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: 'gp:main' }]] };

  const buttons = (data.payouts || []).slice(0, 10).map(p => {
    const id = p.id || 'upcoming';
    if (id === 'upcoming') return [{ text: `✨ Upcoming: ${p.amount} ${p.currency}`, callback_data: 'noop' }];
    return [{ text: `${p.amount} ${p.currency} - ${p.status}`, callback_data: `gp:payout_det:${id}` }];
  });

  const navRow = [{ text: '🔙 Back', callback_data: 'gp:main' }];
  if (data.next_page_key) navRow.push({ text: '➡️ Next Page', callback_data: `gp:payout_page:${data.next_page_key}` });
  else if (pageKey) navRow.push({ text: '🏠 First Page', callback_data: 'gp:payouts' });
  buttons.push(navRow);

  return { text: '💰 **Revenue & Payout History**\n\nSir, here is the log of funds transferred to your accounts. You can track processed earnings and see upcoming deposits.', buttons };
}

async function getPayoutDetails(ctx, id) {
  const data = await runGumroadJSON(ctx, 'payouts', 'details', { id });
  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: 'gp:payouts' }]] };

  const p = data.payout;
  const details = `
🆔 ID: \`${p.id}\`
💰 Amount: ${p.amount} ${p.currency}
📊 Status: ${p.status}
📅 Created: ${p.created_at}
💸 Processed: ${p.processed_at || 'Pending'}
🏦 Processor: ${p.payment_processor}
`.trim();

  return { text: `💹 **Payout Analytics**\n\nDetailed breakdown of the selected transfer, Sir.\n\n${details}`, buttons: [[{ text: '🔙 Back to Payouts', callback_data: 'gp:payouts' }]] };
}

async function getDiscountsMenu(ctx, pid) {
  const data = await runGumroadJSON(ctx, 'discounts', 'list', { product: pid });
  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:prod:${pid}` }]] };

  const buttons = (data.offer_codes || []).slice(0, 10).map(o => {
    const val = o.amount_cents ? '$' + (o.amount_cents / 100) : o.percent_off + '%';
    return [{ text: `${o.name} (${val}) [${o.times_used}]`, callback_data: `gp:disc_det:${pid}:${o.id}` }];
  });

  buttons.push([{ text: '➕ Create Discount', callback_data: `gp:disc_ask:${pid}` }]);
  buttons.push([{ text: '🔙 Back to Product', callback_data: `gp:prod:${pid}` }]);
  return { text: `🎟️ **Offer Code Management**\n\nActive coupons for this product are listed below, Sir. You can monitor usage stats or generate new incentives.`, buttons };
}

async function getDiscountDetails(ctx, pid, did) {
  const data = await runGumroadJSON(ctx, 'discounts', 'details', { product: pid, id: did });
  if (!data.success) return { text: `⚠️ Error: ${data.error}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:discounts:${pid}` }]] };

  const o = data.offer_code;
  const val = o.amount_cents ? '$' + (o.amount_cents / 100) : o.percent_off + '%';
  const details = `
🎟️ **${o.name}**
ID: \`${o.id}\`
💰 Amount: ${val}
📊 Usage: ${o.times_used} / ${o.max_purchase_count || '∞'}
🌐 Universal: ${o.universal || 'false'}
`.trim();

  return {
    text: `🎫 **Discount Details**\n\nConfiguration for the selected offer code, Sir.\n\n${details}`,
    buttons: [[{ text: '📝 Edit', callback_data: `gp:de:${pid}:${did}` }, { text: '🗑️ Delete', callback_data: `gp:dd:${pid}:${did}` }], [{ text: '🔙 Back to List', callback_data: `gp:discounts:${pid}` }]]
  };
}

async function getSubscriptionsMenu(ctx) {
  const data = await runGumroadJSON(ctx, 'subscriptions', 'list');
  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: 'gp:main' }]] };

  const buttons = [];
  const subs = data.subscriptions || {};

  for (const [resource, list] of Object.entries(subs)) {
    if (list && list.length > 0) {
      list.forEach(s => {
        buttons.push([
          { text: `📡 ${resource}: ${s.post_url.substring(0, 20)}...`, callback_data: 'noop' },
          { text: '🗑️', callback_data: `gp:sub_del_ask:${s.id}` }
        ]);
      });
    }
  }

  buttons.push([{ text: '➕ Sale', callback_data: 'gp:sub_ask:sale' }, { text: '➕ Refund', callback_data: 'gp:sub_ask:refund' }, { text: '➕ Dispute', callback_data: 'gp:sub_ask:dispute' }]);
  buttons.push([{ text: '➕ Sub. Update', callback_data: 'gp:sub_ask:subscription_updated' }, { text: '➕ Sub. End', callback_data: 'gp:sub_ask:subscription_ended' }]);
  buttons.push([{ text: '➕ Cancel', callback_data: 'gp:sub_ask:cancellation' }]);

  buttons.push([{ text: '🏠 Main Menu', callback_data: 'gp:main' }]);
  return { text: `📡 **Webhook Infrastructure**\n\nSir, manage the automated listeners for your store. These webhooks notify external systems about sales, refunds, and disputes in real-time.`, buttons };
}

async function getVariantCategoriesMenu(ctx, pid) {
  const data = await runGumroadJSON(ctx, 'variant-categories', 'list', { product: pid });
  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:prod:${pid}` }]] };

  const buttons = (data.variant_categories || []).map(vc => {
    return [{ text: `🎨 ${vc.title}`, callback_data: `gp:variants:${pid}:${vc.id}` }];
  });
  buttons.push([{ text: '🔙 Back to Product', callback_data: `gp:prod:${pid}` }]);
  return { text: `🎨 **Product Customization**\n\nManage the variant categories for this product, Sir. Categories allow customers to choose different options like size or license type.`, buttons };
}

async function getVariantsListMenu(ctx, pid, cid) {
  const data = await runGumroadJSON(ctx, 'variants', 'list', { product: pid, category: cid });
  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:vc:${pid}` }]] };

  const buttons = (data.variants || []).map(v => {
    return [{ text: `${v.name} (${v.price_difference_cents})`, callback_data: `gp:noop` }];
  });
  buttons.push([{ text: '🔙 Back to Categories', callback_data: `gp:vc:${pid}` }]);
  return { text: `🎭 **Variation Management**\n\nSir, here are the specific options available within this category. You can view price differentials and stock limits here.`, buttons };
}

async function getCustomFieldsMenu(ctx, pid) {
  const data = await runGumroadJSON(ctx, 'custom-fields', 'list', { product: pid });
  if (!data.success) return { text: `⚠️ Error: ${data.error || 'Unknown Error'}`, buttons: [[{ text: '🔙 Back', callback_data: `gp:prod:${pid}` }]] };

  const buttons = (data.custom_fields || []).map(f => {
    return [{ text: `📝 ${f.name} ${f.required ? '(Req)' : ''}`, callback_data: 'noop' }, { text: '🗑️', callback_data: `gp:cf_del:${pid}:${f.name}` }];
  });
  buttons.push([{ text: '➕ Add Custom Field', callback_data: `gp:cf_ask:${pid}` }]);
  buttons.push([{ text: '🔙 Back to Product', callback_data: `gp:prod:${pid}` }]);
  return { text: `📝 **Checkout Fields**\n\nManage the additional information requested from customers during the purchase process, Sir.`, buttons };
}
