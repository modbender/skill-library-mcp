#!/usr/bin/env node
/**
 * cj-fetch.js — Fetch product data from CJ Dropshipping API
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

const CJ_CONFIG_PATH = process.env.CJ_API_PATH || require('os').homedir() + '/cj-api.json';

function loadConfig() {
  return JSON.parse(fs.readFileSync(CJ_CONFIG_PATH, 'utf8'));
}

async function getAccessToken(config) {
  // If token is still valid (with 5min buffer), reuse it
  if (config.accessToken && config.tokenExpiry) {
    const expiry = new Date(config.tokenExpiry).getTime();
    if (Date.now() < expiry - 5 * 60 * 1000) {
      return config.accessToken;
    }
  }

  // Refresh token using apiKey
  const res = await axios.post('https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken', {
    apiKey: config.apiKey,
  });

  if (!res.data || res.data.result !== true) {
    throw new Error(`CJ auth failed: ${JSON.stringify(res.data)}`);
  }

  const { accessToken, accessTokenExpiryDate } = res.data.data;

  // Update config file with new token
  const updated = { ...config, accessToken, tokenExpiry: accessTokenExpiryDate };
  fs.writeFileSync(CJ_CONFIG_PATH, JSON.stringify(updated, null, 2));

  return accessToken;
}

async function fetchProduct(productId) {
  const config = loadConfig();
  const token = await getAccessToken(config);

  const baseUrl = config.baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1';

  // Fetch product details
  const res = await axios.get(`${baseUrl}/product/query`, {
    params: { pid: productId },
    headers: { 'CJ-Access-Token': token },
  });

  if (!res.data || res.data.result !== true) {
    throw new Error(`CJ product fetch failed: ${JSON.stringify(res.data)}`);
  }

  const product = res.data.data;

  // Fetch variants if not included
  let variants = product.variants || product.productVariants || [];

  if (variants.length === 0) {
    try {
      const varRes = await axios.get(`${baseUrl}/product/variant/query`, {
        params: { pid: productId },
        headers: { 'CJ-Access-Token': token },
      });
      if (varRes.data && varRes.data.result === true) {
        variants = varRes.data.data || [];
      }
    } catch (e) {
      // variants optional
    }
  }

  return { product, variants };
}

module.exports = { fetchProduct, getAccessToken };

// CLI usage: node cj-fetch.js <product_id>
if (require.main === module) {
  const productId = process.argv[2];
  if (!productId) {
    console.error('Usage: node cj-fetch.js <cj_product_id>');
    process.exit(1);
  }
  fetchProduct(productId)
    .then(data => console.log(JSON.stringify(data, null, 2)))
    .catch(err => { console.error(err.message); process.exit(1); });
}
