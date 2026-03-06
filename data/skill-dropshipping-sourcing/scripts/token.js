#!/usr/bin/env node
/**
 * CJ token helper.
 * Reads ./cj-api.json by default and refreshes token if expired.
 * Writes updated accessToken + tokenExpiry back to cj-api.json.
 */
const fs = require('fs');
const axios = require('axios');

const CJ_API_PATH = process.env.CJ_API_PATH || './cj-api.json';

function readJson(p){ return JSON.parse(fs.readFileSync(p,'utf8')); }
function writeJson(p,o){ fs.writeFileSync(p, JSON.stringify(o,null,2)); }

async function refreshToken(apiKey, baseUrl){
  const url = `${baseUrl.replace(/\/$/,'')}/authentication/getAccessToken`;
  const r = await axios.post(url, { apiKey }, { headers: { 'Content-Type':'application/json' }, timeout: 60000 });
  if(!r.data?.result) throw new Error(`Token refresh failed: ${JSON.stringify(r.data).slice(0,300)}`);
  return r.data.data.accessToken;
}

(async()=>{
  const cfg = readJson(CJ_API_PATH);
  const apiKey = cfg.apiKey;
  const baseUrl = cfg.baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1';
  if(!apiKey) throw new Error('Missing apiKey in cj-api.json');

  const now = Date.now();
  const exp = Number(cfg.tokenExpiry||0);
  const token = String(cfg.accessToken||'');

  const needs = !token || !exp || (now > (exp - 10*60*1000)); // refresh 10m before expiry
  if(!needs){
    console.log(JSON.stringify({ok:true,refreshed:false,tokenExpiry:exp},null,2));
    process.exit(0);
  }

  const newToken = await refreshToken(apiKey, baseUrl);
  // CJ tokens are JWT-ish; if API doesn't provide expiry, keep 15 days default as in previous runs.
  const newExp = now + 14*24*3600*1000;
  cfg.accessToken = newToken;
  cfg.tokenExpiry = newExp;
  writeJson(CJ_API_PATH, cfg);
  console.log(JSON.stringify({ok:true,refreshed:true,tokenExpiry:newExp},null,2));
})().catch(e=>{console.error(e?.stack||String(e));process.exit(1)});
