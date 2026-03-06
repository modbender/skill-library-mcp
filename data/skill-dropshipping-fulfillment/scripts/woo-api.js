/**
 * WooCommerce API helper
 * Reads ./woo-api.json: { url, consumerKey, consumerSecret }
 */
const axios = require('axios');
const fs = require('fs');

const WOO_API_PATH = process.env.WOO_API_PATH || './woo-api.json';

function getCfg() {
  return JSON.parse(fs.readFileSync(WOO_API_PATH, 'utf8'));
}

function client() {
  const { url, consumerKey, consumerSecret } = getCfg();
  const base = url.replace(/\/$/, '') + '/wp-json/wc/v3';
  const auth = { username: consumerKey, password: consumerSecret };
  return { base, auth };
}

async function getOrders(status = 'processing', perPage = 50) {
  const { base, auth } = client();
  const res = await axios.get(`${base}/orders`, {
    auth,
    params: { status, per_page: perPage, orderby: 'date', order: 'asc' },
    timeout: 30000,
  });
  return res.data;
}

async function updateOrderStatus(orderId, status, note = '') {
  const { base, auth } = client();
  const res = await axios.put(`${base}/orders/${orderId}`, {
    status,
    ...(note ? { customer_note: note } : {}),
  }, { auth, timeout: 30000 });
  return res.data;
}

async function addOrderNote(orderId, note, customerNote = false) {
  const { base, auth } = client();
  const res = await axios.post(`${base}/orders/${orderId}/notes`, {
    note,
    customer_note: customerNote,
  }, { auth, timeout: 30000 });
  return res.data;
}

module.exports = { getOrders, updateOrderStatus, addOrderNote };
