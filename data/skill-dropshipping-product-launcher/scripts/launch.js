#!/usr/bin/env node
/**
 * launch.js — CJ Dropshipping → WooCommerce Product Launcher
 * 
 * Usage:
 *   node launch.js --product <cj_product_id> --price <sell_price_aed> [--category <name_or_id>]
 * 
 * Example:
 *   node launch.js --product CJA123456789 --price 149.99 --category Electronics
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { fetchProduct } = require('./cj-fetch');
const { uploadImages, createProduct } = require('./woo-create');

const WOO_CONFIG_PATH = process.env.WOO_API_PATH || require('os').homedir() + '/woo-api.json';
const IMAGE_DIR = '/tmp/product-images';

// ─── CLI Arg Parser ───────────────────────────────────────────────────────────
function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--product' || args[i] === '-p' || args[i] === '--cj-pid') opts.productId = args[++i];
    else if (args[i] === '--price') opts.sellPrice = parseFloat(args[++i]);
    else if (args[i] === '--category' || args[i] === '-c') opts.category = args[++i];
    else if (args[i] === '--status') opts.status = args[++i]; // draft|publish
    else if (args[i] === '--images') opts.imageCount = parseInt(args[++i], 10);
    else if (args[i] === '--dry-run') opts.dryRun = true;
  }
  return opts;
}

// ─── Image Downloader ─────────────────────────────────────────────────────────
function downloadImage(url, dest) {
  return new Promise((resolve, reject) => {
    const proto = url.startsWith('https') ? https : http;
    const file = fs.createWriteStream(dest);
    proto.get(url, res => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        file.close();
        fs.unlink(dest, () => {});
        return downloadImage(res.headers.location, dest).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        file.close();
        fs.unlink(dest, () => {});
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      res.pipe(file);
      file.on('finish', () => file.close(resolve));
      file.on('error', reject);
    }).on('error', reject);
  });
}

async function downloadImages(imageUrls, productId) {
  fs.mkdirSync(IMAGE_DIR, { recursive: true });
  const dir = path.join(IMAGE_DIR, productId.replace(/[^a-z0-9]/gi, '_'));
  fs.mkdirSync(dir, { recursive: true });

  const localPaths = [];
  for (let i = 0; i < imageUrls.length; i++) {
    const url = imageUrls[i];
    const ext = (url.split('?')[0].match(/\.(jpg|jpeg|png|webp|gif)$/i) || ['', '.jpg'])[1];
    const dest = path.join(dir, `image_${i + 1}${ext}`);
    try {
      console.log(`  ⬇ Downloading image ${i + 1}/${imageUrls.length}...`);
      await downloadImage(url, dest);
      localPaths.push(dest);
    } catch (e) {
      console.warn(`  ⚠ Failed to download image ${i + 1}: ${e.message}`);
    }
  }
  return localPaths;
}

// ─── Margin Calculator ────────────────────────────────────────────────────────
function calcMargin(sellPriceAED, cjPriceUSD) {
  const cjPriceAED = cjPriceUSD * 3.67;
  const margin = ((sellPriceAED - cjPriceAED) / sellPriceAED * 100);
  return margin;
}

// ─── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs();

  if (!opts.productId || !opts.sellPrice) {
    console.error('❌ Missing required args: --product <cj_product_id> --price <sell_price_aed>');
    console.error('   Example: node launch.js --product CJA123456789 --price 149.99');
    process.exit(1);
  }

  const { productId, sellPrice, category, dryRun } = opts;
  const status = opts.status || 'draft';
  const imageCount = opts.imageCount || 4;
  const wooConfig = JSON.parse(fs.readFileSync(WOO_CONFIG_PATH, 'utf8'));

  console.log(`\n🚀 Product Launcher`);
  console.log(`   CJ Product ID : ${productId}`);
  console.log(`   Sell Price    : ${sellPrice} AED`);
  if (category) console.log(`   Category      : ${category}`);
  if (dryRun) console.log(`   Mode          : DRY RUN (no WooCommerce writes)`);

  // ── Step 1: Fetch from CJ ──────────────────────────────────────────────────
  console.log(`\n📦 Fetching product from CJ Dropshipping...`);
  const { product, variants } = await fetchProduct(productId);

  const title = product.productNameEn || product.productName || 'Untitled Product';
  const description = product.description || product.productNameEn || '';
  const cjPriceUSD = parseFloat(product.sellPrice || product.productPrice || 0);

  // Collect image URLs
  const imageUrls = [];
  if (product.productImage) imageUrls.push(product.productImage);
  if (Array.isArray(product.productImageSet)) {
    product.productImageSet.forEach(img => {
      const u = typeof img === 'string' ? img : img.imageUrl || img.url || img;
      if (u && !imageUrls.includes(u)) imageUrls.push(u);
    });
  }

  console.log(`   ✅ "${title}"`);
  console.log(`   CJ Price      : $${cjPriceUSD} USD`);
  console.log(`   Images found  : ${imageUrls.length}`);
  console.log(`   Variants      : ${variants.length}`);

  // ── Step 2: Margin Check ───────────────────────────────────────────────────
  const margin = calcMargin(sellPrice, cjPriceUSD);
  const marginStr = margin.toFixed(1);
  console.log(`\n💰 Margin: ${marginStr}%`);
  if (margin < 30) {
    console.warn(`   ⚠️  WARNING: Margin below 30%! Consider raising price or sourcing cheaper.`);
  } else {
    console.log(`   ✅ Margin looks good.`);
  }

  if (dryRun) {
    console.log('\n✅ Dry run complete. No products created.');
    console.log({ title, cjPriceUSD, sellPrice, margin: marginStr, variants: variants.length, images: imageUrls.length });
    return;
  }

  // ── Step 3: Download Images ────────────────────────────────────────────────
  console.log(`\n🖼  Downloading images...`);
  const localPaths = imageUrls.length > 0 ? await downloadImages(imageUrls.slice(0, imageCount), productId) : [];
  console.log(`   Downloaded ${localPaths.length} images.`);

  // ── Step 4: Upload to WooCommerce ──────────────────────────────────────────
  console.log(`\n☁️  Uploading images to WooCommerce...`);
  const uploadedImages = localPaths.length > 0 ? await uploadImages(localPaths, wooConfig) : [];
  console.log(`   Uploaded ${uploadedImages.length} images.`);

  // ── Step 5: Create Product ─────────────────────────────────────────────────
  console.log(`\n🛒 Creating WooCommerce draft product...`);
  const wooProduct = await createProduct({
    name: title,
    description,
    sellPrice,
    images: uploadedImages,
    variants,
    cjProductId: productId,
    category,
  }, wooConfig);

  const productUrl = `${wooConfig.url}/?p=${wooProduct.id}`;
  const adminUrl = `${wooConfig.url}/wp-admin/post.php?post=${wooProduct.id}&action=edit`;

  // ── Output ─────────────────────────────────────────────────────────────────
  console.log(`\n✅ Product created!`);
  console.log(`   WooCommerce ID : ${wooProduct.id}`);
  console.log(`   Margin         : ${marginStr}%`);
  console.log(`   Admin URL      : ${adminUrl}`);
  console.log(`   Product URL    : ${wooProduct.permalink || productUrl}`);
  console.log();

  // Machine-readable output for pipeline use
  const result = {
    wooProductId: wooProduct.id,
    margin: marginStr,
    productUrl: wooProduct.permalink || productUrl,
    adminUrl,
    title,
    cjProductId: productId,
    sellPriceAED: sellPrice,
    cjPriceUSD,
  };

  process.stdout.write('\n__RESULT__\n' + JSON.stringify(result, null, 2) + '\n');
}

main().catch(err => {
  console.error(`\n❌ Error: ${err.message}`);
  if (process.env.DEBUG) console.error(err.stack);
  process.exit(1);
});
