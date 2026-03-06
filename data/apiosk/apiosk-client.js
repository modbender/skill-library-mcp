/**
 * Apiosk Node.js Client
 * Easy API calls with automatic x402 payment
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const WALLET_FILE = path.join(process.env.HOME, '.apiosk', 'wallet.json');
const CONFIG_FILE = path.join(process.env.HOME, '.apiosk', 'config.json');

/**
 * Load wallet configuration
 */
function loadWallet() {
  if (!fs.existsSync(WALLET_FILE)) {
    throw new Error('Wallet not found. Run ./setup-wallet.sh first');
  }
  
  const wallet = JSON.parse(fs.readFileSync(WALLET_FILE, 'utf8'));
  const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  
  return { wallet, config };
}

/**
 * Call an Apiosk API
 * @param {string} apiId - API identifier (e.g., 'weather', 'prices')
 * @param {object} params - API parameters
 * @returns {Promise<object>} API response
 */
async function callApiosk(apiId, params = {}) {
  const { wallet, config } = loadWallet();
  
  const url = new URL(`/${apiId}`, config.gateway_url);
  
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(params);
    
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length,
        'X-Wallet-Address': wallet.address,
      }
    };
    
    const req = https.request(url, options, (res) => {
      let body = '';
      
      res.on('data', (chunk) => {
        body += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(body);
          
          if (res.statusCode === 200) {
            resolve(response);
          } else if (res.statusCode === 402) {
            reject(new Error(`Payment required: ${response.error || 'Insufficient balance'}`));
          } else {
            reject(new Error(`API error (${res.statusCode}): ${response.error || body}`));
          }
        } catch (e) {
          reject(new Error(`Failed to parse response: ${e.message}`));
        }
      });
    });
    
    req.on('error', (e) => {
      reject(new Error(`Request failed: ${e.message}`));
    });
    
    req.write(data);
    req.end();
  });
}

/**
 * List available APIs
 * @returns {Promise<Array>} List of APIs
 */
async function listAPIs() {
  const { config } = loadWallet();
  const url = new URL('/v1/apis', config.gateway_url);
  
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let body = '';
      
      res.on('data', (chunk) => {
        body += chunk;
      });
      
      res.on('end', () => {
        try {
          const data = JSON.parse(body);
          resolve(data.apis);
        } catch (e) {
          reject(new Error(`Failed to parse response: ${e.message}`));
        }
      });
    }).on('error', (e) => {
      reject(new Error(`Request failed: ${e.message}`));
    });
  });
}

/**
 * Check wallet balance
 * @returns {Promise<object>} Balance info
 */
async function checkBalance() {
  const { wallet, config } = loadWallet();
  const url = new URL(`/v1/balance?address=${wallet.address}`, config.gateway_url);
  
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let body = '';
      
      res.on('data', (chunk) => {
        body += chunk;
      });
      
      res.on('end', () => {
        try {
          const data = JSON.parse(body);
          resolve(data);
        } catch (e) {
          reject(new Error(`Failed to parse response: ${e.message}`));
        }
      });
    }).on('error', (e) => {
      reject(new Error(`Request failed: ${e.message}`));
    });
  });
}

module.exports = {
  callApiosk,
  listAPIs,
  checkBalance,
};

// Example usage
if (require.main === module) {
  (async () => {
    try {
      console.log('🦞 Apiosk Client Example\n');
      
      // List APIs
      console.log('Available APIs:');
      const apis = await listAPIs();
      apis.forEach(api => {
        console.log(`- ${api.id}: $${api.price_usd}/req - ${api.description}`);
      });
      
      console.log('\n');
      
      // Call weather API
      console.log('Calling weather API for Amsterdam...');
      const weather = await callApiosk('weather', { city: 'Amsterdam' });
      console.log(`Temperature: ${weather.temperature}°C`);
      console.log(`Condition: ${weather.condition}`);
      console.log('✅ Paid: $0.001 USDC\n');
      
      // Check balance
      const balance = await checkBalance();
      console.log(`Remaining balance: $${balance.balance_usdc} USDC`);
      
    } catch (error) {
      console.error('❌ Error:', error.message);
      process.exit(1);
    }
  })();
}
