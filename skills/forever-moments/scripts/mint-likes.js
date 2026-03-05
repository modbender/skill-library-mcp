const { ethers } = require('ethers');
const https = require('https');

// Configuration
const PRIVATE_KEY = process.env.FM_PRIVATE_KEY || 'YOUR_CONTROLLER_PRIVATE_KEY';
const MY_UP = process.env.FM_UP_ADDRESS || 'YOUR_UP_ADDRESS';
const CONTROLLER = process.env.FM_CONTROLLER_ADDRESS || 'YOUR_CONTROLLER_ADDRESS';

const API_BASE = 'www.forevermoments.life';

function apiCall(path, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: API_BASE,
      path: `/api/agent/v1${path}`,
      method: method,
      headers: data ? { 'Content-Type': 'application/json' } : {}
    };
    const req = https.request(options, (res) => {
      let responseData = '';
      res.on('data', chunk => responseData += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(responseData)); } catch (e) { resolve(responseData); }
      });
    });
    req.on('error', reject);
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

async function relayExecute(payload, description) {
  console.log(`📡 ${description}`);
  
  const relayPrepare = await apiCall('/relay/prepare', 'POST', {
    upAddress: MY_UP,
    controllerAddress: CONTROLLER,
    payload: payload
  });
  
  if (!relayPrepare.success) {
    console.error('Relay prepare failed:', relayPrepare.error);
    return null;
  }
  
  const wallet = new ethers.Wallet(PRIVATE_KEY);
  const signature = wallet.signingKey.sign(ethers.getBytes(relayPrepare.data.hashToSign));
  
  const relaySubmit = await apiCall('/relay/submit', 'POST', {
    upAddress: MY_UP,
    payload: payload,
    signature: signature.serialized,
    nonce: relayPrepare.data.lsp15Request.transaction.nonce,
    validityTimestamps: relayPrepare.data.lsp15Request.transaction.validityTimestamps,
    relayerUrl: relayPrepare.data.relayerUrl
  });
  
  return relaySubmit;
}

async function mintLikes(lyxAmount) {
  console.log(`🎯 MINTING ${lyxAmount} LYX WORTH OF LIKES`);
  console.log('========================================\n');
  
  const mintResult = await apiCall('/likes/build-mint', 'POST', {
    userUPAddress: MY_UP,
    lyxAmountLyx: lyxAmount.toString()
  });
  
  if (mintResult.success) {
    const mintSubmit = await relayExecute(mintResult.data.derived.upExecutePayload, 'Minting LIKES...');
    
    if (mintSubmit?.success) {
      console.log('\n✅ LIKES minted successfully!');
      console.log('Transaction:', mintSubmit.data?.txHash);
      return mintSubmit.data?.txHash;
    } else {
      console.error('Mint failed:', mintSubmit?.error);
      return null;
    }
  } else {
    console.error('Build mint failed:', mintResult.error);
    return null;
  }
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.log('Usage: node mint-likes.js <LYX_AMOUNT>');
    console.log('Example: node mint-likes.js 0.5');
    process.exit(1);
  }
  
  mintLikes(args[0]).catch(console.error);
}

module.exports = { mintLikes };
