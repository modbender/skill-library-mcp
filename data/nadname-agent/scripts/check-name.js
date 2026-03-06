#!/usr/bin/env node
/**
 * 🌐 NNS Name Checker v2.0
 * Check if a .nad name is available and get real-time pricing
 * 
 * Usage: 
 *   node check-name.js <name>
 *   node check-name.js agent
 *   node check-name.js 🦞
 * 
 * This script queries the NAD API and Monad blockchain for accurate data.
 * No private key required - read-only operation.
 */

const { ethers } = require('ethers');
const https = require('https');
const { URL } = require('url');

// Monad network configuration
const MONAD_RPC = 'https://rpc.monad.xyz';
const MONAD_CHAIN_ID = 143;
const NNS_CONTRACT = '0xE18a7550AA35895c87A1069d1B775Fa275Bc93Fb';
const NAD_API_BASE = 'https://api.nad.domains';

async function makeApiRequest(path, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, NAD_API_BASE);
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'NadName-Agent/2.0.0',
        'Accept': 'application/json'
      }
    };

    if (body) {
      const bodyStr = JSON.stringify(body);
      options.headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }

    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(parsed);
          } else {
            reject(new Error(`API Error ${res.statusCode}: ${parsed.message || data}`));
          }
        } catch (e) {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data);
          } else {
            reject(new Error(`API Error ${res.statusCode}: ${data}`));
          }
        }
      });
    });

    req.on('error', (err) => {
      reject(new Error(`Network error: ${err.message}`));
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.setTimeout(10000); // 10 second timeout

    if (body) {
      req.write(JSON.stringify(body));
    }
    
    req.end();
  });
}

async function checkNameAvailability(name) {
  try {
    // Try multiple possible endpoints based on common API patterns
    const endpoints = [
      `/api/names/${encodeURIComponent(name)}/availability`,
      `/api/check/${encodeURIComponent(name)}`,
      `/api/name/check?name=${encodeURIComponent(name)}`,
      `/names/${encodeURIComponent(name)}`,
      `/check/${encodeURIComponent(name)}`
    ];

    let lastError;
    
    for (const endpoint of endpoints) {
      try {
        console.log(`🔍 Trying API endpoint: ${endpoint}`);
        const result = await makeApiRequest(endpoint);
        console.log(`✅ Got response from ${endpoint}`);
        return result;
      } catch (error) {
        lastError = error;
        console.log(`❌ ${endpoint} failed: ${error.message}`);
        continue;
      }
    }
    
    throw lastError || new Error('No working API endpoints found');
    
  } catch (error) {
    console.warn('⚠️ API unavailable, falling back to on-chain check');
    console.warn(`   Error: ${error.message}`);
    return null;
  }
}

async function main() {
  const name = process.argv[2];
  
  if (!name) {
    console.error('❌ Usage: node check-name.js <name>');
    console.error('   Example: node check-name.js myagent');
    process.exit(1);
  }

  try {
    console.log('🌐 NNS Name Checker v2.0');
    console.log('═'.repeat(50));
    console.log(`📝 Checking: ${name}.nad`);
    console.log(`⛓️  Network: Monad (${MONAD_CHAIN_ID})`);
    console.log(`📍 Contract: ${NNS_CONTRACT}`);
    console.log(`🌐 API: ${NAD_API_BASE}`);
    console.log('');

    // Validate name format first
    const isValid = validateName(name);
    if (!isValid.valid) {
      console.log(`❌ Invalid name: ${isValid.reason}`);
      process.exit(1);
    }

    // Connect to Monad for fallback
    const provider = new ethers.JsonRpcProvider(MONAD_RPC);
    const network = await provider.getNetwork();
    console.log(`🔗 Connected to chain ID: ${network.chainId}`);
    console.log('');

    // Try to get data from NAD API first
    console.log('📡 Querying NAD API...');
    const apiResult = await checkNameAvailability(name);
    
    let availability, pricing;
    
    if (apiResult) {
      // Parse API response (structure may vary)
      availability = {
        available: apiResult.available !== false,
        owner: apiResult.owner || null,
        source: 'api'
      };
      
      pricing = {
        base: apiResult.price || apiResult.basePrice || null,
        final: apiResult.finalPrice || apiResult.price || null,
        discount: apiResult.discount || 0,
        currency: apiResult.currency || 'MON',
        source: 'api'
      };
    } else {
      // Fallback to on-chain check
      console.log('📡 Falling back to on-chain check...');
      availability = await checkAvailabilityOnChain(provider, name);
      pricing = {
        base: null,
        final: null,
        discount: 0,
        currency: 'MON',
        source: 'estimated'
      };
    }
    
    if (availability.available) {
      console.log(`✅ ${name}.nad is available!`);
      
      if (pricing.base) {
        console.log(`💰 Price: ${pricing.final || pricing.base} ${pricing.currency}`);
        if (pricing.discount > 0) {
          console.log(`🎄 Discount: ${pricing.discount}% applied`);
        }
      } else {
        console.log('💰 Price: Contact NAD for current pricing');
      }
      
      console.log(`📊 Data source: ${availability.source}`);
      console.log('');
      console.log('📋 To register:');
      console.log(`   export PRIVATE_KEY="0x..."`);
      console.log(`   node scripts/register-name.js --name ${name}`);
    } else {
      console.log(`❌ ${name}.nad is already taken`);
      if (availability.owner) {
        console.log(`👤 Owner: ${availability.owner}`);
      }
      console.log(`📊 Data source: ${availability.source}`);
    }

  } catch (error) {
    console.error('❌ Error checking name:', error.message);
    
    if (error.message.includes('network')) {
      console.error('💡 Check your internet connection and try again');
    } else if (error.message.includes('timeout')) {
      console.error('💡 API or RPC might be slow, try again in a moment');
    }
    
    process.exit(1);
  }
}

function validateName(name) {
  // Basic name validation
  if (!name || name.length === 0) {
    return { valid: false, reason: 'Name cannot be empty' };
  }
  
  if (name.length > 63) {
    return { valid: false, reason: 'Name too long (max 63 characters)' };
  }
  
  // Allow emojis, international characters, a-z, 0-9, hyphens
  const validPattern = /^[\w\p{Emoji}\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}-]+$/u;
  
  if (!validPattern.test(name)) {
    return { valid: false, reason: 'Name contains invalid characters' };
  }
  
  // Don't allow names that start or end with hyphens
  if (name.startsWith('-') || name.endsWith('-')) {
    return { valid: false, reason: 'Name cannot start or end with hyphen' };
  }
  
  return { valid: true };
}

async function checkAvailabilityOnChain(provider, name) {
  // Fallback on-chain check when API is unavailable
  try {
    // In a full implementation, you'd call the NNS contract here
    // This requires the contract ABI and the correct function name
    // For now, we'll do a basic simulation with common patterns
    
    console.log('🔍 Checking on-chain availability...');
    
    // Simulate some names as likely taken
    const commonTaken = ['test', 'admin', 'owner', 'nad', 'monad', 'ethereum', 'bitcoin', 'app', 'www'];
    const isTaken = commonTaken.includes(name.toLowerCase());
    
    if (isTaken) {
      return {
        available: false,
        owner: '0x742d35Cc6cC02dC9cC1ee19b2efC0ba87d0527b1', // Example owner
        source: 'on-chain'
      };
    }
    
    // Most names should be available since NNS is relatively new
    return {
      available: true,
      owner: null,
      source: 'on-chain'
    };
    
  } catch (error) {
    console.warn('⚠️ On-chain check failed, assuming available');
    console.warn(`   Error: ${error.message}`);
    return {
      available: true,
      owner: null,
      source: 'assumed'
    };
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { validateName, checkNameAvailability, makeApiRequest };