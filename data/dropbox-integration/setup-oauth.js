#!/usr/bin/env node

/**
 * Dropbox OAuth 2.0 Setup Script
 * 
 * This script helps you get an access token for your Dropbox account.
 * 
 * Usage:
 *   1. Create credentials.json with your app key and secret
 *   2. Run: node setup-oauth.js
 *   3. Follow the authorization URL in your browser
 *   4. Paste the authorization code when prompted
 */

const http = require('http');
const { URL } = require('url');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Load credentials
const credsPath = path.join(__dirname, 'credentials.json');
if (!fs.existsSync(credsPath)) {
  console.error('❌ credentials.json not found!');
  console.error('\nCreate credentials.json with:');
  console.error(JSON.stringify({
    app_key: 'your_app_key_here',
    app_secret: 'your_app_secret_here'
  }, null, 2));
  process.exit(1);
}

const credentials = JSON.parse(fs.readFileSync(credsPath, 'utf8'));
const { app_key, app_secret } = credentials;

if (!app_key || !app_secret) {
  console.error('❌ Invalid credentials.json - missing app_key or app_secret');
  process.exit(1);
}

const REDIRECT_URI = 'http://localhost:3000/callback';
const TOKEN_PATH = path.join(__dirname, 'token.json');

// Step 1: Generate authorization URL
const authUrl = new URL('https://www.dropbox.com/oauth2/authorize');
authUrl.searchParams.append('client_id', app_key);
authUrl.searchParams.append('response_type', 'code');
authUrl.searchParams.append('redirect_uri', REDIRECT_URI);
authUrl.searchParams.append('token_access_type', 'offline'); // Get refresh token

console.log('\n📦 Dropbox OAuth Setup\n');
console.log('1. Open this URL in your browser:\n');
console.log(`   ${authUrl.toString()}\n`);
console.log('2. Authorize the app');
console.log('3. You\'ll be redirected to localhost (may show an error - that\'s OK)');
console.log('4. Copy the full URL from your browser and paste it here\n');

// Step 2: Start local server to capture redirect
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  
  if (url.pathname === '/callback') {
    const code = url.searchParams.get('code');
    const error = url.searchParams.get('error');
    
    if (error) {
      res.writeHead(400, { 'Content-Type': 'text/html' });
      res.end(`<h1>❌ Authorization failed</h1><p>Error: ${error}</p>`);
      console.error(`\n❌ Authorization failed: ${error}`);
      server.close();
      process.exit(1);
    }
    
    if (!code) {
      res.writeHead(400, { 'Content-Type': 'text/html' });
      res.end('<h1>❌ No authorization code received</h1>');
      console.error('\n❌ No authorization code received');
      server.close();
      process.exit(1);
    }
    
    // Exchange code for token
    try {
      const tokenResponse = await fetch('https://api.dropboxapi.com/oauth2/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          code,
          grant_type: 'authorization_code',
          client_id: app_key,
          client_secret: app_secret,
          redirect_uri: REDIRECT_URI,
        }),
      });
      
      if (!tokenResponse.ok) {
        const errorText = await tokenResponse.text();
        throw new Error(`Token exchange failed: ${errorText}`);
      }
      
      const tokenData = await tokenResponse.json();
      
      // Save token
      fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokenData, null, 2), { mode: 0o600 });
      
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(`
        <h1>✅ Authorization successful!</h1>
        <p>Your access token has been saved to token.json</p>
        <p>You can close this window and return to your terminal.</p>
      `);
      
      console.log('\n✅ Success! Token saved to token.json');
      console.log('\nToken details:');
      console.log(`  - Access token: ${tokenData.access_token.substring(0, 20)}...`);
      if (tokenData.refresh_token) {
        console.log(`  - Refresh token: ${tokenData.refresh_token.substring(0, 20)}...`);
        console.log('  - This token will not expire (use refresh token to get new access tokens)');
      } else {
        console.log(`  - Expires in: ${tokenData.expires_in} seconds`);
      }
      
      server.close();
    } catch (error) {
      console.error('\n❌ Error exchanging code for token:', error.message);
      res.writeHead(500, { 'Content-Type': 'text/html' });
      res.end(`<h1>❌ Error</h1><p>${error.message}</p>`);
      server.close();
      process.exit(1);
    }
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(3000, () => {
  console.log('🌐 Local server started on http://localhost:3000');
  console.log('   Waiting for authorization...\n');
});

// Handle Ctrl+C
process.on('SIGINT', () => {
  console.log('\n\n⚠️  Setup cancelled');
  server.close();
  process.exit(0);
});
