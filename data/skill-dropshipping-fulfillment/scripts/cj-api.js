/**
 * CJ Dropshipping API helper
 * Reads ./cj-api.json: { apiKey, baseUrl, accessToken, tokenExpiry }
 */
const axios = require('axios');
const fs = require('fs');

const CJ_API_PATH = process.env.CJ_API_PATH || './cj-api.json';

function readCfg() { return JSON.parse(fs.readFileSync(CJ_API_PATH, 'utf8')); }
function writeCfg(o) { fs.writeFileSync(CJ_API_PATH, JSON.stringify(o, null, 2)); }

async function ensureToken() {
  const cfg = readCfg();
  const now = Date.now();
  const exp = Number(cfg.tokenExpiry || 0);
  if (cfg.accessToken && exp && now < exp - 10 * 60 * 1000) return cfg.accessToken;

  // Refresh
  const baseUrl = (cfg.baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1').replace(/\/$/, '');
  const res = await axios.post(`${baseUrl}/authentication/getAccessToken`, { apiKey: cfg.apiKey }, {
    headers: { 'Content-Type': 'application/json' }, timeout: 30000,
  });
  if (!res.data?.result) throw new Error(`CJ token refresh failed: ${JSON.stringify(res.data).slice(0, 200)}`);
  const token = res.data.data.accessToken;
  cfg.accessToken = token;
  cfg.tokenExpiry = now + 14 * 24 * 3600 * 1000;
  writeCfg(cfg);
  return token;
}

function baseUrl() {
  return (readCfg().baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1').replace(/\/$/, '');
}

async function headers() {
  return { 'CJ-Access-Token': await ensureToken(), 'Content-Type': 'application/json' };
}

/**
 * Get variant info by CJ variant ID to confirm stock/price.
 */
async function getVariant(variantId) {
  const res = await axios.get(`${baseUrl()}/product/variant/query`, {
    headers: await headers(),
    params: { vid: variantId },
    timeout: 30000,
  });
  return res.data;
}

/**
 * Create an order on CJ.
 * orderData: { orderNumber, shippingZip, shippingCountry, shippingCountryCode,
 *              shippingProvince, shippingCity, shippingAddress, shippingPhone,
 *              shippingCustomerName, shippingEmail, products: [{ vid, quantity }] }
 */
async function createOrder(orderData) {
  const res = await axios.post(`${baseUrl()}/shopping/order/createOrder`, orderData, {
    headers: await headers(),
    timeout: 60000,
  });
  return res.data;
}

module.exports = { ensureToken, getVariant, createOrder };
