#!/usr/bin/env node
/**
 * woo-create.js — Upload images & create WooCommerce draft product
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

const WOO_CONFIG_PATH = process.env.WOO_API_PATH || require('os').homedir() + '/woo-api.json';

function loadConfig() {
  return JSON.parse(fs.readFileSync(WOO_CONFIG_PATH, 'utf8'));
}

function wooAuth(config) {
  return {
    username: config.consumerKey,
    password: config.consumerSecret,
  };
}

/**
 * Upload a local image file to WooCommerce media library.
 * Returns the WP media object with { id, source_url }
 */
async function uploadImage(localPath, config) {
  const form = new FormData();
  form.append('file', fs.createReadStream(localPath), path.basename(localPath));

  const res = await axios.post(`${config.url}/wp-json/wp/v2/media`, form, {
    auth: wooAuth(config),
    headers: form.getHeaders(),
    maxContentLength: Infinity,
    maxBodyLength: Infinity,
  });

  return { id: res.data.id, src: res.data.source_url };
}

/**
 * Upload multiple images, return array of { id, src }
 */
async function uploadImages(localPaths, config) {
  const results = [];
  for (const p of localPaths) {
    try {
      console.log(`  Uploading ${path.basename(p)}...`);
      const img = await uploadImage(p, config);
      results.push(img);
    } catch (e) {
      console.warn(`  ⚠ Failed to upload ${p}: ${e.message}`);
    }
  }
  return results;
}

/**
 * Create a WooCommerce draft product.
 * @param {Object} opts
 * @param {string} opts.name
 * @param {string} opts.description
 * @param {string} opts.sellPrice  — AED price string
 * @param {Array}  opts.images     — [{ id, src }]
 * @param {Array}  opts.variants   — CJ variant objects (optional)
 * @param {string} opts.cjProductId
 * @param {string} opts.category   — optional category name/id
 * @param {Object} config          — woo config
 */
async function createProduct(opts, config) {
  const { name, description, sellPrice, images, variants, cjProductId, category } = opts;

  const hasVariants = variants && variants.length > 1;

  const body = {
    name,
    status: 'draft',
    description,
    regular_price: String(sellPrice),
    images: images.map(i => ({ id: i.id, src: i.src })),
    meta_data: [{ key: '_cj_product_id', value: cjProductId }],
    type: hasVariants ? 'variable' : 'simple',
  };

  if (category) {
    // Accept numeric id or name
    if (!isNaN(category)) {
      body.categories = [{ id: parseInt(category) }];
    } else {
      // Try to find or create category
      const catId = await findOrCreateCategory(category, config);
      if (catId) body.categories = [{ id: catId }];
    }
  }

  // Create the product
  const res = await axios.post(`${config.url}/wp-json/wc/v3/products`, body, {
    auth: wooAuth(config),
  });

  const product = res.data;

  // Add variations if variable product
  if (hasVariants) {
    await createVariations(product.id, variants, sellPrice, config);
  }

  return product;
}

async function findOrCreateCategory(name, config) {
  try {
    const res = await axios.get(`${config.url}/wp-json/wc/v3/products/categories`, {
      auth: wooAuth(config),
      params: { search: name, per_page: 5 },
    });
    if (res.data && res.data.length > 0) return res.data[0].id;

    // Create it
    const created = await axios.post(`${config.url}/wp-json/wc/v3/products/categories`, { name }, {
      auth: wooAuth(config),
    });
    return created.data.id;
  } catch (e) {
    console.warn(`  ⚠ Could not resolve category "${name}": ${e.message}`);
    return null;
  }
}

async function createVariations(productId, variants, sellPrice, config) {
  for (const v of variants.slice(0, 100)) {
    try {
      const attrs = [];
      if (v.variantName) attrs.push({ name: 'Variant', option: v.variantName });

      await axios.post(`${config.url}/wp-json/wc/v3/products/${productId}/variations`, {
        regular_price: String(sellPrice),
        sku: v.variantSku || v.vid || '',
        attributes: attrs,
        meta_data: [
          { key: '_cj_variant_id', value: v.vid || v.variantId || '' },
          { key: '_cj_variant_sku', value: v.variantSku || '' },
        ],
      }, { auth: wooAuth(config) });
    } catch (e) {
      console.warn(`  ⚠ Failed to create variation: ${e.message}`);
    }
  }
}

module.exports = { uploadImages, createProduct };
