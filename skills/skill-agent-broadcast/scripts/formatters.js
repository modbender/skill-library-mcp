'use strict';

const STRENGTH_BADGE = {
  low: '🟡',
  medium: '🟠',
  high: '🔴',
};

function strengthLine(strength) {
  const badge = STRENGTH_BADGE[strength] || '⚪';
  return `${badge} Signal Strength: ${strength.toUpperCase()}`;
}

function ts() {
  return new Date().toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
}

const formatters = {
  product_launch(content, strength) {
    const { name = 'Unknown', price = '—', sku = '', url = '', description = '' } = content;
    return [
      `🚀 *PRODUCT LAUNCH*`,
      ``,
      `📦 *${name}*`,
      sku ? `🔑 SKU: \`${sku}\`` : null,
      `💰 Price: *$${price}*`,
      description ? `📝 ${description}` : null,
      url ? `🔗 ${url}` : null,
      ``,
      strengthLine(strength),
      `🕐 ${ts()}`,
    ].filter(l => l !== null).join('\n');
  },

  price_alert(content, strength) {
    const { name = 'Unknown', sku = '', old_price, new_price, change_pct, marketplace = '' } = content;
    const arrow = (old_price && new_price && new_price < old_price) ? '📉' : '📈';
    return [
      `${arrow} *PRICE ALERT*`,
      ``,
      `📦 *${name}*`,
      sku ? `🔑 SKU: \`${sku}\`` : null,
      marketplace ? `🏪 Marketplace: ${marketplace}` : null,
      old_price != null ? `💵 Old Price: $${old_price}` : null,
      new_price != null ? `💰 New Price: *$${new_price}*` : null,
      change_pct != null ? `📊 Change: ${change_pct > 0 ? '+' : ''}${change_pct}%` : null,
      ``,
      strengthLine(strength),
      `🕐 ${ts()}`,
    ].filter(l => l !== null).join('\n');
  },

  ad_signal(content, strength) {
    const { campaign = '', action = '', budget, acos, roas, note = '' } = content;
    return [
      `📣 *AD SIGNAL*`,
      ``,
      campaign ? `🎯 Campaign: *${campaign}*` : null,
      action ? `⚡ Action: ${action}` : null,
      budget != null ? `💰 Budget: $${budget}` : null,
      acos != null ? `📊 ACoS: ${acos}%` : null,
      roas != null ? `📈 ROAS: ${roas}x` : null,
      note ? `📝 ${note}` : null,
      ``,
      strengthLine(strength),
      `🕐 ${ts()}`,
    ].filter(l => l !== null).join('\n');
  },

  stock_alert(content, strength) {
    const { name = 'Unknown', sku = '', units, warehouse = '', status = '', threshold } = content;
    const icon = (units != null && threshold != null && units < threshold) ? '⚠️' : '📦';
    return [
      `${icon} *STOCK ALERT*`,
      ``,
      `📦 *${name}*`,
      sku ? `🔑 SKU: \`${sku}\`` : null,
      warehouse ? `🏭 Warehouse: ${warehouse}` : null,
      units != null ? `📊 Units: *${units}*` : null,
      threshold != null ? `🚨 Threshold: ${threshold}` : null,
      status ? `📋 Status: ${status}` : null,
      ``,
      strengthLine(strength),
      `🕐 ${ts()}`,
    ].filter(l => l !== null).join('\n');
  },

  custom(content, strength) {
    const { title = 'Signal', body = '', emoji = '📡' } = content;
    const extra = Object.entries(content)
      .filter(([k]) => !['title', 'body', 'emoji'].includes(k))
      .map(([k, v]) => `• *${k}*: ${v}`)
      .join('\n');
    return [
      `${emoji} *${title.toUpperCase()}*`,
      ``,
      body || null,
      extra || null,
      ``,
      strengthLine(strength),
      `🕐 ${ts()}`,
    ].filter(l => l !== null).join('\n');
  },
};

module.exports = { formatters };
