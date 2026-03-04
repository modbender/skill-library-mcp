#!/usr/bin/env node

const fs = require('fs');
const https = require('https');

const apiKey = process.argv[2];
const inputFile = process.argv[3];

if (!apiKey || !inputFile) {
  console.error("Usage: node fetch_ai_overview.mjs <api_key> <input_json_file>");
  process.exit(1);
}

const raw = fs.readFileSync(inputFile, 'utf8');
let data;
try {
  data = JSON.parse(raw);
} catch (e) {
  console.error("Failed to parse input JSON");
  process.exit(1);
}

// Logic: Look for a token to fetch the full AI Overview.
// The user specified: https://serpapi.com/google-ai-overview-api
// This endpoint typically takes 'token' and 'api_key'.
// We look for 'ai_overview.token' or 'ai_overview_token'.

const token = data.ai_overview?.token || data.ai_overview_token;

if (!token) {
  // No token found, return original data as-is (maybe AI overview is already there or not triggered).
  console.log(JSON.stringify(data));
  process.exit(0);
}

const url = `https://serpapi.com/google-ai-overview-api?api_key=${apiKey}&token=${token}&output=json`;

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            reject(new Error("Failed to parse AI Overview response"));
          }
        } else {
          reject(new Error(`AI Overview API failed: ${res.statusCode} ${body}`));
        }
      });
    }).on('error', reject);
  });
}

fetchJson(url).then(result => {
  // Merge the result.
  // If the result is the AI overview object itself, we replace/enrich data.ai_overview.
  // Usually the API returns { ai_overview: { ... } } or just the object.
  // Let's assume it returns the standard SerpAPI structure.

  if (result.ai_overview) {
    data.ai_overview = result.ai_overview;
  } else {
    // If the response is the overview itself (less likely but possible)
    // or has a different structure, we attach it.
    // Safest is to attach the whole result to a debug field if unsure, 
    // but typically it mimics the main search structure.
    // We'll trust the 'ai_overview' key presence.
    // If not present, we might attach 'result' to ai_overview to be safe.
    data.ai_overview_fetched = result;
  }
  
  // Clear the token to avoid confusion? No, keep it for provenance.
  console.log(JSON.stringify(data));
}).catch(err => {
  // On error, print the original data but maybe log a warning to stderr
  console.error(`[serpapi-mcp] Failed to fetch AI Overview: ${err.message}`);
  console.log(JSON.stringify(data));
});
