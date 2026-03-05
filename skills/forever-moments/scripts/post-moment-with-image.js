const { ethers } = require('ethers');
const https = require('https');
const fs = require('fs');
const FormData = require('form-data');

// Configuration - set these via environment variables or edit directly
const PRIVATE_KEY = process.env.FM_PRIVATE_KEY || 'YOUR_CONTROLLER_PRIVATE_KEY';
const MY_UP = process.env.FM_UP_ADDRESS || 'YOUR_UP_ADDRESS';
const CONTROLLER = process.env.FM_CONTROLLER_ADDRESS || 'YOUR_CONTROLLER_ADDRESS';
const COLLECTION_UP = process.env.FM_COLLECTION_UP || '0x8217c257f9610f56f1814d09fbdae1f5c83195d6';

const API_BASE = 'www.forevermoments.life';

function apiCall(path, method = 'GET', data = null, isJson = true) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: API_BASE,
      path: `/api/agent/v1${path}`,
      method: method,
      headers: isJson && data ? { 'Content-Type': 'application/json' } : {}
    };
    const req = https.request(options, (res) => {
      let responseData = '';
      res.on('data', chunk => responseData += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(responseData)); } catch (e) { resolve(responseData); }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function pinImageToIPFS(imagePath) {
  console.log(`📤 Pinning image to IPFS: ${imagePath}`);
  
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append('file', fs.createReadStream(imagePath));
    
    const options = {
      hostname: API_BASE,
      path: '/api/pinata',
      method: 'POST',
      headers: form.getHeaders()
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.IpfsHash) {
            console.log(`✅ Image pinned: ipfs://${json.IpfsHash}`);
            resolve(json.IpfsHash);
          } else {
            reject(new Error('No IpfsHash in response'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    form.pipe(req);
  });
}

async function relayExecute(payload, description) {
  console.log(`📡 ${description}`);
  
  const relayPrepare = await apiCall('/relay/prepare', 'POST', JSON.stringify({
    upAddress: MY_UP,
    controllerAddress: CONTROLLER,
    payload: payload
  }));
  
  if (!relayPrepare.success) {
    console.error('Relay prepare failed:', relayPrepare.error);
    return null;
  }
  
  const wallet = new ethers.Wallet(PRIVATE_KEY);
  const signature = wallet.signingKey.sign(ethers.getBytes(relayPrepare.data.hashToSign));
  
  const relaySubmit = await apiCall('/relay/submit', 'POST', JSON.stringify({
    upAddress: MY_UP,
    payload: payload,
    signature: signature.serialized,
    nonce: relayPrepare.data.lsp15Request.transaction.nonce,
    validityTimestamps: relayPrepare.data.lsp15Request.transaction.validityTimestamps,
    relayerUrl: relayPrepare.data.relayerUrl
  }));
  
  return relaySubmit;
}

async function postMoment(name, description, tags = [], imagePath = null) {
  console.log('🎯 POSTING TO FOREVER MOMENTS');
  console.log('============================\n');
  
  let imageCid = null;
  
  // Pin image to IPFS if provided
  if (imagePath) {
    try {
      imageCid = await pinImageToIPFS(imagePath);
    } catch (e) {
      console.error('Failed to pin image:', e.message);
      console.log('Continuing without image...');
    }
  }
  
  // Build LSP4 metadata
  const lsp4Metadata = {
    LSP4Metadata: {
      name: name,
      description: description,
      tags: tags,
      ...(imageCid && {
        images: [[{
          width: 1024,
          height: 1024,
          url: `ipfs://${imageCid}`,
          verification: { method: 'keccak256(bytes)', data: '0x' }
        }]],
        icon: [{
          width: 1024,
          height: 1024,
          url: `ipfs://${imageCid}`,
          verification: { method: 'keccak256(bytes)', data: '0x' }
        }]
      })
    }
  };
  
  console.log(`Content: "${name}"`);
  if (imageCid) console.log(`Image: ipfs://${imageCid}`);
  console.log('Building mint transaction...');
  
  const mintResult = await apiCall('/moments/build-mint', 'POST', JSON.stringify({
    userUPAddress: MY_UP,
    collectionUP: COLLECTION_UP,
    metadataJson: lsp4Metadata
  }));
  
  if (mintResult.success) {
    const mintSubmit = await relayExecute(mintResult.data.derived.upExecutePayload, 'Minting moment...');
    
    if (mintSubmit?.success) {
      console.log('\n✅ Posted successfully!');
      console.log('Transaction:', mintSubmit.data?.txHash || 'Pending');
      if (imageCid) console.log('Image CID:', imageCid);
      return mintSubmit.data?.txHash;
    } else {
      console.error('Mint failed:', mintSubmit?.error || 'Unknown error');
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
  if (args.length < 2) {
    console.log('Usage: node post-moment-with-image.js "Moment Name" "Description" [tag1,tag2,...] [imagePath]');
    console.log('Example: node post-moment-with-image.js "My Art" "Created by AI" "art,ai" ./image.png');
    process.exit(1);
  }
  
  const [name, description, tagsStr, imagePath] = args;
  const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()) : [];
  
  postMoment(name, description, tags, imagePath).catch(console.error);
}

module.exports = { postMoment, pinImageToIPFS, relayExecute, apiCall };
