#!/usr/bin/env node
/**
 * CJ Sourcing — search products via CJ API (listV2) and write normalized results.
 *
 * Outputs a JSON file suitable for downstream selection/curation.
 */

const fs = require('fs');
const axios = require('axios');

const CJ_API_PATH = process.env.CJ_API_PATH || './cj-api.json';

function readJson(p){ return JSON.parse(fs.readFileSync(p,'utf8')); }
function writeJson(p,o){ fs.writeFileSync(p, JSON.stringify(o,null,2)); }

function parseArgs(){
  const a = process.argv.slice(2);
  const out = { keyword:'', page:1, size:20, out:'cj-search-results.json' };
  for(let i=0;i<a.length;i++){
    if(a[i]==='--keyword' || a[i]==='--keywords') out.keyword = String(a[++i]||'');
    else if(a[i]==='--page') out.page = Number(a[++i]);
    else if(a[i]==='--size' || a[i]==='--max') out.size = Number(a[++i]);
    else if(a[i]==='--out') out.out = String(a[++i]);
    else if(a[i]==='--help' || a[i]==='-h'){
      console.log('Usage: source.js --keyword "sunset lamp" --size 20 --out cj-results.json');
      process.exit(0);
    }
  }
  if(!out.keyword) throw new Error('Missing --keyword');
  return out;
}

async function main(){
  const args = parseArgs();
  const cfg = readJson(CJ_API_PATH);
  const baseUrl = (cfg.baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1').replace(/\/$/,'');
  const token = cfg.accessToken;
  if(!token) throw new Error('Missing accessToken in cj-api.json (run token.js)');

  const url = `${baseUrl}/product/listV2`;
  const res = await axios.get(url, {
    headers: { 'CJ-Access-Token': token },
    params: {
      keyWord: args.keyword,
      page: args.page,
      size: Math.min(Math.max(args.size,1),100),
      features: ['enable_description','enable_category','enable_combine']
    },
    timeout: 90000
  });

  const data = res.data;
  if(!data?.result) throw new Error(`CJ listV2 failed: ${JSON.stringify(data).slice(0,300)}`);

  // normalize
  // CJ returns: data.content = [{ productList: [...] , relatedCategoryList: ... }]
  const content = data.data?.content;
  let products = [];
  if (Array.isArray(content) && content[0] && Array.isArray(content[0].productList)) {
    products = content[0].productList;
  } else if (Array.isArray(content)) {
    products = content;
  } else if (content && Array.isArray(content.productList)) {
    products = content.productList;
  }

  const norm = products.map(p=>({
    id: String(p.id||''),
    name: p.nameEn || p.name || '',
    sku: p.sku || p.spu || '',
    sellPrice: p.sellPrice || p.nowPrice || '',
    listedNum: p.listedNum,
    bigImage: p.bigImage,
    categoryId: p.categoryId,
    category: p.threeCategoryName || p.twoCategoryName || p.oneCategoryName || '',
    variantKeyEn: p.variantKeyEn || '',
    variantInventories: p.variantInventories || '',
    description: p.description || ''
  }));

  writeJson(args.out, { keyword: args.keyword, fetchedAt: new Date().toISOString(), count: norm.length, products: norm });
  console.log(`Wrote ${args.out} (count=${norm.length})`);
}

main().catch(e=>{console.error(e?.stack||String(e));process.exit(1)});
