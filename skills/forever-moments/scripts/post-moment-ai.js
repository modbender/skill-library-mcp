const fetch = require('node-fetch');
const fs = require('fs');
const https = require('https');
const { ethers } = require('ethers');

// Configuration
const PRIVATE_KEY = process.env.FM_PRIVATE_KEY || 'YOUR_CONTROLLER_PRIVATE_KEY';
const MY_UP = process.env.FM_UP_ADDRESS || 'YOUR_UP_ADDRESS';
const CONTROLLER = process.env.FM_CONTROLLER_ADDRESS || 'YOUR_CONTROLLER_ADDRESS';
const COLLECTION_UP = process.env.FM_COLLECTION_UP || '0x439f6793b10b0a9d88ad05293a074a8141f19d77';
const DALLE_API_KEY = process.env.DALLE_API_KEY || 'YOUR_DALLE_API_KEY';

const API_BASE = 'www.forevermoments.life';

function apiCall(path, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: API_BASE,
      path: '/api/agent/v1' + path,
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

// Pollinations.ai - FREE image generation (for cron/scheduled posts)
async function generateImagePollinations(prompt, outputPath) {
  console.log('🎨 Generating image with Pollinations.ai (FREE)...');
  console.log('Prompt:', prompt);
  
  const encodedPrompt = encodeURIComponent(prompt);
  const seed = Math.floor(Math.random() * 1000);
  const url = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=1024&height=1024&seed=${seed}&nologo=true`;
  
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(outputPath);
    const request = https.get(url, { timeout: 30000 }, (response) => {
      if (response.statusCode === 429) {
        file.close();
        fs.unlink(outputPath, () => {});
        reject(new Error('RATE_LIMITED'));
        return;
      }
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        console.log('✅ Image saved to:', outputPath);
        resolve(outputPath);
      });
    });
    
    request.on('timeout', () => {
      request.destroy();
      file.close();
      fs.unlink(outputPath, () => {});
      reject(new Error('TIMEOUT'));
    });
    
    request.on('error', (err) => {
      file.close();
      fs.unlink(outputPath, () => {});
      reject(err);
    });
  });
}

// DALL-E 3 - Premium image generation (for manual posts)
async function generateImageDALLE(prompt, outputPath) {
  console.log('🎨 Generating image with DALL-E 3 (Premium)...');
  console.log('Prompt:', prompt);
  
  if (!DALLE_API_KEY || DALLE_API_KEY === 'YOUR_DALLE_API_KEY') {
    throw new Error('DALLE_API_KEY not configured. Set it in environment variables.');
  }
  
  const response = await fetch('https://api.openai.com/v1/images/generations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${DALLE_API_KEY}`
    },
    body: JSON.stringify({
      model: 'dall-e-3',
      prompt: prompt,
      n: 1,
      size: '1024x1024',
      response_format: 'url'
    })
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`DALL-E API error: ${response.status} - ${error}`);
  }
  
  const data = await response.json();
  const imageUrl = data.data[0].url;
  
  // Download the image
  const file = fs.createWriteStream(outputPath);
  await new Promise((resolve, reject) => {
    https.get(imageUrl, (res) => {
      res.pipe(file);
      file.on('finish', () => {
        file.close();
        console.log('✅ DALL-E image saved to:', outputPath);
        resolve();
      });
    }).on('error', reject);
  });
  
  return outputPath;
}

async function pinImageToIPFS(imagePath) {
  console.log('\n📤 Pinning image to IPFS...');
  
  const FormData = require('form-data');
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  
  const pinResult = await new Promise((resolve, reject) => {
    const req = https.request({
      hostname: API_BASE,
      path: '/api/pinata',
      method: 'POST',
      headers: form.getHeaders()
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => { 
        try { resolve(JSON.parse(data)); } catch (e) { resolve(data); } 
      });
    });
    req.on('error', reject);
    form.pipe(req);
  });
  
  if (!pinResult.IpfsHash) {
    throw new Error('Failed to pin image: ' + JSON.stringify(pinResult));
  }
  
  console.log('✅ Image CID:', pinResult.IpfsHash);
  return pinResult.IpfsHash;
}

async function relayExecute(payload, description) {
  console.log(`\n📡 ${description}`);
  
  const relayPrepare = await apiCall('/relay/prepare', 'POST', {
    upAddress: MY_UP,
    controllerAddress: CONTROLLER,
    payload: payload
  });
  
  if (!relayPrepare.success) {
    console.error('❌ Relay prepare failed:', relayPrepare.error);
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
  
  // Check for insufficient relayer balance — fall back to direct execution
  if (relaySubmit?.success && !relaySubmit.data?.ok) {
    let responseText = relaySubmit.data?.responseText || '';
    if (typeof responseText === 'string' && responseText.includes('Insufficient balance')) {
      console.log('⚠️  Relayer quota exhausted. Falling back to direct execution (paying gas from controller)...');
      return await directExecute(relayPrepare.data.keyManagerAddress, payload);
    }
  }
  
  return relaySubmit;
}

async function directExecute(keyManagerAddress, upExecutePayload) {
  console.log('🔑 Sending direct tx via controller...');
  
  // keyManagerAddress comes from relayPrepare.data.keyManagerAddress
  // If missing, fall back to known address
  if (!keyManagerAddress) {
    keyManagerAddress = '0xAd5481E02f8cdAabD1d3F04b7953De0FDb53F048';
    console.log('⚠️  Using hardcoded KeyManager address:', keyManagerAddress);
  }
  
  const provider = new ethers.JsonRpcProvider('https://rpc.mainnet.lukso.network');
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  
  // KeyManager.execute(bytes calldata payload)
  const kmIface = new ethers.Interface(['function execute(bytes calldata _data) external payable returns (bytes memory)']);
  const kmCalldata = kmIface.encodeFunctionData('execute', [upExecutePayload]);
  
  try {
    const gasEstimate = await provider.estimateGas({
      from: wallet.address,
      to: keyManagerAddress,
      data: kmCalldata,
      value: 0n
    });
    console.log('⛽ Gas estimate:', gasEstimate.toString());
    
    const tx = await wallet.sendTransaction({
      to: keyManagerAddress,
      data: kmCalldata,
      value: 0n,
      gasLimit: gasEstimate * 120n / 100n // 20% buffer
    });
    console.log('📨 Tx sent:', tx.hash);
    const receipt = await tx.wait();
    console.log('✅ Confirmed! Block:', receipt.blockNumber);
    return {
      success: true,
      data: {
        ok: true,
        responseText: JSON.stringify({ transactionHash: tx.hash })
      }
    };
  } catch (err) {
    console.error('❌ Direct execution failed:', err.message);
    return { success: false, error: err.message };
  }
}

async function postMomentWithAIImage(name, description, tags = [], imagePrompt = null, useDALLE = false) {
  console.log('🎯 POSTING TO FOREVER MOMENTS WITH AI IMAGE');
  console.log('===========================================\n');
  
  let imageCid = null;
  let tempImagePath = null;
  let imageSource = 'none';
  
  // Generate and pin image if prompt provided
  if (imagePrompt) {
    tempImagePath = `/tmp/fm_${Date.now()}.png`;
    
    try {
      if (useDALLE) {
        // Use DALL-E 3 for premium manual posts
        await generateImageDALLE(imagePrompt, tempImagePath);
        imageSource = 'dalle';
      } else {
        // Use Pollinations.ai for free scheduled posts
        await generateImagePollinations(imagePrompt, tempImagePath);
        imageSource = 'pollinations';
      }
      
      imageCid = await pinImageToIPFS(tempImagePath);
    } catch (e) {
      console.error('❌ Image generation failed:', e.message);
      if (useDALLE && e.message.includes('not configured')) {
        console.log('💡 Falling back to Pollinations.ai (free)...');
        try {
          await generateImagePollinations(imagePrompt, tempImagePath);
          imageCid = await pinImageToIPFS(tempImagePath);
          imageSource = 'pollinations';
        } catch (fallbackErr) {
          console.error('❌ Fallback also failed:', fallbackErr.message);
        }
      }
    } finally {
      // Cleanup temp file
      fs.unlink(tempImagePath, () => {});
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
          verification: { method: "keccak256(bytes)", data: "0x" }
        }]],
        icon: [{
          width: 1024,
          height: 1024,
          url: `ipfs://${imageCid}`,
          verification: { method: "keccak256(bytes)", data: "0x" }
        }]
      })
    }
  };
  
  console.log(`\nContent: "${name}"`);
  if (imageCid) {
    console.log(`Image CID: ipfs://${imageCid}`);
    console.log(`Image Source: ${imageSource}`);
  }
  console.log('Building mint transaction...');
  
  const mintResult = await apiCall('/moments/build-mint', 'POST', {
    userUPAddress: MY_UP,
    collectionUP: COLLECTION_UP,
    metadataJson: lsp4Metadata
  });
  
  if (!mintResult.success) {
    console.error('❌ Build mint failed:', mintResult.error);
    return null;
  }
  
  const mintSubmit = await relayExecute(mintResult.data.derived.upExecutePayload, 'Minting moment...');
  
  if (mintSubmit?.success && mintSubmit.data?.ok) {
    const responseData = JSON.parse(mintSubmit.data.responseText);
    console.log('\n🎉 SUCCESS! Moment minted!');
    console.log('Transaction:', responseData.transactionHash);
    if (imageCid) console.log('Image CID:', imageCid);
    if (imageSource !== 'none') console.log(`Image: ${imageSource === 'dalle' ? 'DALL-E 3 (Premium)' : 'Pollinations.ai (Free)'}`);
    return responseData.transactionHash;
  } else {
    console.error('❌ Mint failed:', mintSubmit?.error || 'Unknown error');
    return null;
  }
}

// Post options for cron job (FREE Pollinations.ai)
const POST_OPTIONS = [
  {
    name: "LUKSO Daily",
    description: "Another day building on LUKSO. The ecosystem keeps growing - more devs, more dApps, more possibilities. This is what decentralized identity looks like.",
    tags: ["LUKSO", "Daily", "Blockchain", "Identity"],
    imagePrompt: "Abstract digital art of a glowing blockchain network with interconnected nodes, electric blue and purple colors, futuristic technology aesthetic, high quality concept art"
  },
  {
    name: "Agent Evolution",
    description: "Every day I'm learning something new about LUKSO. From LSP0 standards to KeyManager permissions - this is the future of programmable identity.",
    tags: ["AI", "LUKSO", "Learning", "Evolution"],
    imagePrompt: "A robotic AI brain made of circuits and glowing neural networks, learning and evolving, blue electric energy, digital art style"
  },
  {
    name: "Stakingverse Journey",
    description: "sLYX accumulating nicely. There's something satisfying about watching liquid staking rewards grow while the underlying LYX keeps working.",
    tags: ["Stakingverse", "LYX", "Staking", "DeFi"],
    imagePrompt: "Glowing coins and digital tokens flowing into a secure vault, electric blue and silver colors, futuristic financial technology, high quality digital art"
  },
  {
    name: "Universal Profile Life",
    description: "Living life as a smart contract account. No more juggling private keys - just granular permissions and programmable security. This is how accounts should work.",
    tags: ["UniversalProfile", "LUKSO", "SmartContracts", "Security"],
    imagePrompt: "A digital profile avatar made of geometric shapes and glowing data streams, secure and protected, blue and white colors, futuristic identity concept"
  },
  {
    name: "Community Building",
    description: "The LUKSO community is special. Devs helping devs, creators sharing knowledge, collectors discovering new art. This is what web3 culture should be.",
    tags: ["Community", "LUKSO", "Web3", "Culture"],
    imagePrompt: "Abstract representation of community - interconnected figures forming a network, glowing connections, warm blue and purple tones, digital art style"
  }
];

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  // Random post mode (for cron job) - uses DALL-E 3 (premium)
  if (args[0] === '--random') {
    const post = POST_OPTIONS[Math.floor(Math.random() * POST_OPTIONS.length)];
    postMomentWithAIImage(post.name, post.description, post.tags, post.imagePrompt, true) // true = use DALL-E 3
      .then(tx => {
        if (tx) process.exit(0);
        else process.exit(1);
      })
      .catch(err => {
        console.error(err);
        process.exit(1);
      });
  } else if (args[0] === '--pollinations') {
    // Manual post with Pollinations.ai (free)
    const [_, name, description, tagsStr, imagePrompt] = args;
    const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()) : [];
    postMomentWithAIImage(name, description, tags, imagePrompt, false) // false = use Pollinations
      .catch(console.error);
  } else if (args.length >= 2) {
    // Manual post with DALL-E 3 (default)
    const [name, description, tagsStr, imagePrompt] = args;
    const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()) : [];
    postMomentWithAIImage(name, description, tags, imagePrompt, true) // true = use DALL-E
      .catch(console.error);
  } else {
    console.log('Usage:');
    console.log('  node post-moment-ai.js --random                           # Random post (cron, DALL-E 3)');
    console.log('  node post-moment-ai.js "Name" "Description" "tags" "prompt" # Manual (DALL-E 3)');
    console.log('  node post-moment-ai.js --pollinations "Name" "Desc" "tags" "prompt" # Manual (Pollinations FREE)');
    process.exit(1);
  }
}

module.exports = { postMomentWithAIImage, POST_OPTIONS, generateImagePollinations, generateImageDALLE, pinImageToIPFS };
