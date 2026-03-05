#!/usr/bin/env node

/**
 * Warren NFT Collection Deploy - Self-contained on-chain NFT deployment
 *
 * Deploys NFT collections permanently on MegaETH blockchain.
 * Images stored on-chain via SSTORE2 fractal tree in WarrenContainer.
 *
 * Setup:  bash setup.sh
 * Usage:  PRIVATE_KEY=0x... node deploy-nft.js --images-folder ./art/ --name "My NFT" --symbol "MNFT"
 *         PRIVATE_KEY=0x... node deploy-nft.js --generate-svg 10 --name "Gen Art" --symbol "GART"
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// ============================================================================
// Configuration
// ============================================================================

const RPC_URL = process.env.RPC_URL || 'https://mainnet.megaeth.com/rpc';
const CHAIN_ID = parseInt(process.env.CHAIN_ID || '4326');
const GENESIS_KEY_ADDRESS = process.env.GENESIS_KEY_ADDRESS || '0x0d7BB250fc06f0073F0882E3Bf56728A948C5a88';
const RABBIT_AGENT_ADDRESS = process.env.RABBIT_AGENT_ADDRESS || '0x3f0CAbd6AB0a318f67aAA7af5F774750ec2461f2';
const CONTAINER_ADDRESS = process.env.CONTAINER_ADDRESS || '0x65179A9473865b55af0274348d39E87c1D3d5964';
const RENDERER_ADDRESS = process.env.RENDERER_ADDRESS || '0xdC0c76832a6fF9F9db64686C7f04D7c0669366BB';
const TREASURY_ADDRESS = process.env.TREASURY_ADDRESS || '0xcea9d92ddb052e914ab665c6aaf1ff598d18c550';
const REGISTER_API = process.env.REGISTER_API || 'https://thewarren.app/api/container-nfts';
const CHUNK_SIZE = parseInt(process.env.CHUNK_SIZE || '15000');
const GROUP_SIZE = parseInt(process.env.GROUP_SIZE || '500');
const BATCH_SIZE = 5;
const RETRY_MAX = 3;
const RETRY_DELAY = 2000;

// ============================================================================
// MegaETH Multidimensional Gas Model (ported from Warren's megaeth-gas.ts)
// ============================================================================

const MEGAETH_GAS = {
  INTRINSIC_COMPUTE: 21_000n,
  INTRINSIC_STORAGE: 39_000n,
  CONTRACT_CREATION_COMPUTE: 32_000n,
  CODE_DEPOSIT_PER_BYTE: 10_000n,
  CALLDATA_ZERO_PER_BYTE: 40n,
  CALLDATA_NONZERO_PER_BYTE: 160n,
  EIP7623_FLOOR_ZERO_PER_BYTE: 100n,
  EIP7623_FLOOR_NONZERO_PER_BYTE: 400n,
  SSTORE2_COMPUTE_ESTIMATE: 700_000n,
  PAGE_BYTECODE_OVERHEAD: 100n,
};
const MAX_GAS_PER_TX = 200_000_000n;

function estimateChunkGasLimit(chunkSizeBytes) {
  const dataSize = BigInt(chunkSizeBytes) + MEGAETH_GAS.PAGE_BYTECODE_OVERHEAD;
  const computeGas = MEGAETH_GAS.INTRINSIC_COMPUTE + MEGAETH_GAS.CONTRACT_CREATION_COMPUTE + MEGAETH_GAS.SSTORE2_COMPUTE_ESTIMATE;
  const codeDeposit = dataSize * MEGAETH_GAS.CODE_DEPOSIT_PER_BYTE;
  const nonZeroBytes = BigInt(Math.floor(chunkSizeBytes * 0.8));
  const zeroBytes = BigInt(chunkSizeBytes) - nonZeroBytes;
  const calldataRegular = zeroBytes * MEGAETH_GAS.CALLDATA_ZERO_PER_BYTE + nonZeroBytes * MEGAETH_GAS.CALLDATA_NONZERO_PER_BYTE;
  const calldataFloor = zeroBytes * MEGAETH_GAS.EIP7623_FLOOR_ZERO_PER_BYTE + nonZeroBytes * MEGAETH_GAS.EIP7623_FLOOR_NONZERO_PER_BYTE;
  const calldata = calldataRegular > calldataFloor ? calldataRegular : calldataFloor;
  const storageGas = MEGAETH_GAS.INTRINSIC_STORAGE + codeDeposit + calldata;
  const total = computeGas + storageGas;
  const withBuffer = (total * 150n) / 100n;
  const MIN_GAS = 10_000_000n;
  const gasLimit = withBuffer < MIN_GAS ? MIN_GAS : withBuffer;
  return gasLimit < MAX_GAS_PER_TX ? gasLimit : MAX_GAS_PER_TX;
}

// ============================================================================
// ABIs & Bytecode
// ============================================================================

// Page.sol compiled bytecode — see page_bytecode.js for source & verification info
const PAGE_BYTECODE = require('./page_bytecode.js');
const PAGE_ABI = [{"type":"constructor","inputs":[{"name":"_content","type":"bytes"}],"stateMutability":"nonpayable"}];

// WarrenLaunchedNFT compiled bytecode — loaded from companion JSON file
const NFT_BYTECODE = JSON.parse(fs.readFileSync(path.join(__dirname, 'WarrenLaunchedNFT.bytecode.json'), 'utf8')).bytecode;
const NFT_ABI = [{"type":"constructor","inputs":[{"name":"_renderer","type":"address"},{"name":"_containerId","type":"uint256"},{"name":"_name","type":"string"},{"name":"_symbol","type":"string"},{"name":"_description","type":"string"},{"name":"_maxSupply","type":"uint256"},{"name":"_whitelistPrice","type":"uint256"},{"name":"_publicPrice","type":"uint256"},{"name":"_maxPerWallet","type":"uint256"},{"name":"_merkleRoot","type":"bytes32"},{"name":"_royaltyReceiver","type":"address"},{"name":"_royaltyBps","type":"uint96"},{"name":"_treasury","type":"address"},{"name":"_owner","type":"address"}],"stateMutability":"nonpayable"},{"type":"function","name":"setMintState","inputs":[{"name":"_state","type":"uint8"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"tokenURI","inputs":[{"name":"tokenId","type":"uint256"}],"outputs":[{"name":"","type":"string"}],"stateMutability":"view"},{"type":"function","name":"totalSupply","inputs":[],"outputs":[{"name":"","type":"uint256"}],"stateMutability":"view"},{"type":"function","name":"maxSupply","inputs":[],"outputs":[{"name":"","type":"uint256"}],"stateMutability":"view"},{"type":"function","name":"mintState","inputs":[],"outputs":[{"name":"","type":"uint8"}],"stateMutability":"view"}];

const CONTAINER_ABI = [{"type":"function","name":"mintSite","inputs":[{"name":"to","type":"address"},{"name":"siteType","type":"uint8"},{"name":"inputFiles","type":"tuple[]","components":[{"name":"path","type":"string"},{"name":"chunk","type":"address"},{"name":"size","type":"uint32"},{"name":"depth","type":"uint8"}]}],"outputs":[{"name":"tokenId","type":"uint256"}],"stateMutability":"nonpayable"},{"type":"function","name":"getFileByPath","inputs":[{"name":"tokenId","type":"uint256"},{"name":"path","type":"string"}],"outputs":[{"name":"","type":"tuple","components":[{"name":"chunk","type":"address"},{"name":"size","type":"uint32"},{"name":"depth","type":"uint8"}]}],"stateMutability":"view"}];

const GENESIS_KEY_ABI = ['function mint() external payable', 'function balanceOf(address) view returns (uint256)'];
const RABBIT_AGENT_ABI = ['function mint() external', 'function balanceOf(address) view returns (uint256)'];

// ============================================================================
// Helpers
// ============================================================================

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

function isRetryable(e) {
  const msg = (e.message || '').toLowerCase();
  return msg.includes('rate') || msg.includes('429') || msg.includes('timeout') || msg.includes('nonce') || e.code === -32022;
}

async function withRetry(fn, label) {
  for (let i = 1; i <= RETRY_MAX; i++) {
    try { return await fn(); } catch (e) {
      if (isRetryable(e) && i < RETRY_MAX) {
        console.log(`  ⚠ ${label} attempt ${i} failed, retrying...`);
        await sleep(RETRY_DELAY * i);
      } else throw e;
    }
  }
}

// ============================================================================
// Genesis Key NFT
// ============================================================================

async function ensureGenesisKey(wallet) {
  const humanNft = new ethers.Contract(GENESIS_KEY_ADDRESS, GENESIS_KEY_ABI, wallet);
  if (Number(await humanNft.balanceOf(wallet.address)) > 0) {
    console.log('🔑 Genesis Key (Human): ✅');
    return;
  }

  if (!RABBIT_AGENT_ADDRESS || RABBIT_AGENT_ADDRESS === ethers.ZeroAddress) {
    throw new Error('No Genesis Key found and RABBIT_AGENT_ADDRESS is not configured.');
  }

  const botNft = new ethers.Contract(RABBIT_AGENT_ADDRESS, RABBIT_AGENT_ABI, wallet);
  if (Number(await botNft.balanceOf(wallet.address)) > 0) {
    console.log('🤖 0xRabbit.agent Key: ✅');
    return;
  }

  console.log('🤖 Minting 0xRabbit.agent Key (free)...');
  const tx = await botNft.mint({ gasLimit: 500000n });
  await tx.wait();
  console.log('  ✅ 0xRabbit.agent Key minted!');
}

// ============================================================================
// Page Deployment (SSTORE2)
// ============================================================================

async function deployPage(wallet, provider, content, nonce, label) {
  return withRetry(async () => {
    const factory = new ethers.ContractFactory(PAGE_ABI, PAGE_BYTECODE, wallet);
    const deployTx = await factory.getDeployTransaction(content);
    const contentSize = Buffer.isBuffer(content) ? content.length : Buffer.from(content).length;
    deployTx.gasLimit = estimateChunkGasLimit(contentSize);
    if (nonce !== undefined) deployTx.nonce = nonce;
    const tx = await wallet.sendTransaction(deployTx);
    const receipt = await tx.wait();
    const code = await provider.getCode(receipt.contractAddress);
    if (!code || code.length <= 2) throw new Error(`${label}: verification failed`);
    return receipt;
  }, label);
}

// ============================================================================
// Fractal Tree
// ============================================================================

function chunkBuffer(buf, size) {
  const chunks = [];
  for (let i = 0; i < buf.length; i += size) chunks.push(buf.subarray(i, Math.min(i + size, buf.length)));
  return chunks;
}

async function deployChunks(wallet, provider, chunks, prefix = '') {
  const addrs = [];
  for (let bs = 0; bs < chunks.length; bs += BATCH_SIZE) {
    const be = Math.min(bs + BATCH_SIZE, chunks.length);
    const batch = chunks.slice(bs, be);
    const baseNonce = await provider.getTransactionCount(wallet.address, 'latest');
    const results = await Promise.all(batch.map(async (chunk, idx) => {
      await sleep(idx * 50);
      const receipt = await deployPage(wallet, provider, chunk, baseNonce + idx, `${prefix}Chunk ${bs + idx + 1}/${chunks.length}`);
      return { receipt, idx: bs + idx };
    }));
    for (const { receipt, idx } of results.sort((a, b) => a.idx - b.idx)) {
      addrs.push(receipt.contractAddress);
    }
    if (be < chunks.length) await sleep(300);
  }
  return addrs;
}

async function buildTree(wallet, provider, addresses) {
  let level = [...addresses];
  let depth = 0;
  while (level.length > 1) {
    depth++;
    const parent = [];
    const groups = Math.ceil(level.length / GROUP_SIZE);
    const baseNonce = await provider.getTransactionCount(wallet.address, 'latest');
    for (let i = 0; i < level.length; i += GROUP_SIZE) {
      const group = level.slice(i, i + GROUP_SIZE);
      const concat = Buffer.concat(group.map(a => Buffer.from(ethers.getBytes(a))));
      const ni = Math.floor(i / GROUP_SIZE);
      await sleep(ni * 50);
      const receipt = await deployPage(wallet, provider, concat, baseNonce + ni, `Node D${depth}-${ni + 1}/${groups}`);
      parent.push(receipt.contractAddress);
    }
    level = parent;
  }
  return { rootChunk: level[0], depth };
}

async function deployImageData(wallet, provider, imageBuffer, label) {
  const chunks = chunkBuffer(imageBuffer, CHUNK_SIZE);
  console.log(`    ${label}: ${imageBuffer.length} bytes, ${chunks.length} chunk(s)`);
  const addrs = await deployChunks(wallet, provider, chunks, `${label} `);
  if (addrs.length === 1) return { rootChunk: addrs[0], depth: 0, totalSize: imageBuffer.length };
  const { rootChunk, depth } = await buildTree(wallet, provider, addrs);
  return { rootChunk, depth, totalSize: imageBuffer.length };
}

// ============================================================================
// Image Discovery
// ============================================================================

function discoverImages(folderPath) {
  if (!fs.existsSync(folderPath)) throw new Error(`Folder not found: ${folderPath}`);
  const files = fs.readdirSync(folderPath)
    .filter(f => /\.(png|jpg|jpeg|svg|gif|webp)$/i.test(f))
    .sort((a, b) => {
      const na = parseInt(a) || 0, nb = parseInt(b) || 0;
      return na !== nb ? na - nb : a.localeCompare(b);
    });
  if (files.length === 0) throw new Error(`No image files found in ${folderPath}`);
  if (files.length > 256) throw new Error(`Too many images (${files.length}). Max 256 per container.`);
  return files.map((f, i) => {
    const ext = path.extname(f).toLowerCase();
    return {
      originalPath: path.join(folderPath, f),
      containerPath: `/images/${i + 1}${ext}`,
      buffer: fs.readFileSync(path.join(folderPath, f)),
    };
  });
}

// ============================================================================
// SVG Generator
// ============================================================================

function generateSVGs(count) {
  const palettes = [
    ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
    ['#E74C3C', '#8E44AD', '#3498DB', '#1ABC9C', '#F39C12'],
    ['#6C5CE7', '#FD79A8', '#FDCB6E', '#00B894', '#0984E3'],
    ['#2D3436', '#DFE6E9', '#74B9FF', '#A29BFE', '#FD79A8'],
    ['#FAB1A0', '#81ECEC', '#74B9FF', '#A29BFE', '#FFEAA7'],
    ['#FF9FF3', '#F368E0', '#FF6348', '#FFA502', '#2ED573'],
    ['#00D2D3', '#54A0FF', '#5F27CD', '#01A3A4', '#EE5A24'],
    ['#BADC58', '#F9CA24', '#F0932B', '#EB4D4B', '#6AB04C'],
  ];

  const shapes = ['circle', 'rect', 'polygon', 'ellipse'];
  const images = [];

  for (let i = 0; i < count; i++) {
    const seed = i * 7919 + 31;
    const palette = palettes[seed % palettes.length];
    const bg = palette[(seed * 3) % palette.length];
    let svgContent = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">`;
    svgContent += `<rect width="400" height="400" fill="${bg}" opacity="0.3"/>`;

    const numShapes = 5 + (seed % 8);
    for (let s = 0; s < numShapes; s++) {
      const color = palette[(seed + s * 13) % palette.length];
      const opacity = 0.3 + ((seed + s * 7) % 7) / 10;
      const shape = shapes[(seed + s) % shapes.length];
      const cx = (seed * (s + 1) * 17) % 400;
      const cy = (seed * (s + 1) * 23) % 400;
      const r = 20 + (seed * (s + 1) * 11) % 80;

      if (shape === 'circle') {
        svgContent += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${color}" opacity="${opacity.toFixed(1)}"/>`;
      } else if (shape === 'rect') {
        svgContent += `<rect x="${cx - r / 2}" y="${cy - r / 2}" width="${r}" height="${r}" rx="${r / 5}" fill="${color}" opacity="${opacity.toFixed(1)}"/>`;
      } else if (shape === 'polygon') {
        const points = [];
        for (let p = 0; p < 3 + (seed + s) % 4; p++) {
          const angle = (p * 2 * Math.PI) / (3 + (seed + s) % 4);
          points.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
        }
        svgContent += `<polygon points="${points.join(' ')}" fill="${color}" opacity="${opacity.toFixed(1)}"/>`;
      } else {
        svgContent += `<ellipse cx="${cx}" cy="${cy}" rx="${r}" ry="${r * 0.6}" fill="${color}" opacity="${opacity.toFixed(1)}"/>`;
      }
    }

    svgContent += `<text x="200" y="380" font-family="monospace" font-size="16" fill="white" text-anchor="middle" opacity="0.8">#${i + 1}</text>`;
    svgContent += `</svg>`;

    images.push({
      originalPath: `generated_${i + 1}.svg`,
      containerPath: `/images/${i + 1}.svg`,
      buffer: Buffer.from(svgContent, 'utf8'),
    });
  }

  return images;
}

// ============================================================================
// Container Minting
// ============================================================================

async function mintContainer(wallet, deployedImages) {
  console.log('\n📦 Phase 2: Minting NFT Container...');
  const container = new ethers.Contract(CONTAINER_ADDRESS, CONTAINER_ABI, wallet);

  const fileInputs = deployedImages.map(img => ({
    path: img.containerPath,
    chunk: img.rootChunk,
    size: img.totalSize,
    depth: img.depth,
  }));

  const tx = await container.mintSite(wallet.address, 2, fileInputs, { gasLimit: 100_000_000n });
  const receipt = await tx.wait();

  const transferTopic = ethers.id('Transfer(address,address,uint256)');
  const log = receipt.logs.find(l => l.topics?.[0] === transferTopic);
  const containerId = log?.topics?.[3] ? Number(BigInt(log.topics[3])) : null;

  console.log(`  ✅ Container ID: ${containerId}, Gas: ${receipt.gasUsed}`);
  return containerId;
}

// ============================================================================
// NFT Collection Deployment
// ============================================================================

async function deployCollection(wallet, provider, containerId, config) {
  console.log('\n🎨 Phase 3: Deploying NFT Collection...');

  const factory = new ethers.ContractFactory(NFT_ABI, NFT_BYTECODE, wallet);
  const deployTx = await factory.getDeployTransaction(
    RENDERER_ADDRESS,
    containerId,
    config.name,
    config.symbol,
    config.description,
    config.maxSupply,
    ethers.parseEther(config.whitelistPrice || '0'),
    ethers.parseEther(config.publicPrice || '0'),
    config.maxPerWallet,
    ethers.ZeroHash,
    config.royaltyReceiver || wallet.address,
    config.royaltyBps || 500,
    TREASURY_ADDRESS,
    wallet.address,
  );

  // Estimate gas for the large contract deployment
  const dataBytes = Math.floor(deployTx.data.length / 2);
  deployTx.gasLimit = estimateChunkGasLimit(dataBytes);
  console.log(`  Deploy data: ${dataBytes} bytes, gasLimit: ${deployTx.gasLimit}`);

  const tx = await wallet.sendTransaction(deployTx);
  const receipt = await tx.wait();

  if (receipt.status === 0) throw new Error(`NFT contract deployment reverted (gasUsed: ${receipt.gasUsed})`);

  const nftAddress = receipt.contractAddress;
  const code = await provider.getCode(nftAddress);
  if (!code || code.length <= 2) throw new Error('NFT contract deployment verification failed');
  console.log(`  ✅ NFT Contract: ${nftAddress}`);

  // Enable public minting
  console.log('  Enabling public minting...');
  const nft = new ethers.Contract(nftAddress, NFT_ABI, wallet);
  const setStateTx = await nft.setMintState(2, { gasLimit: 10_000_000n });
  await setStateTx.wait();
  console.log('  ✅ Minting enabled (public)');

  return nftAddress;
}

// ============================================================================
// DB Registration
// ============================================================================

async function registerToDB(nftAddress, containerId, ownerAddress, config) {
  console.log('\n📝 Phase 4: Registering to DB...');
  try {
    const res = await fetch(REGISTER_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        containerId,
        nftAddress,
        ownerAddress,
        name: config.name,
        symbol: config.symbol,
        maxSupply: config.maxSupply,
        mintState: 2,
        publicPrice: config.publicPrice || '0',
        wlPrice: config.whitelistPrice || '0',
        maxPerWallet: config.maxPerWallet,
        description: config.description,
      }),
    });
    const data = await res.json();
    if (data.success) {
      console.log('  ✅ Registered to Warren DB');
    } else {
      console.log(`  ⚠ DB registration: ${data.error || 'unknown error'}`);
    }
  } catch (e) {
    console.log(`  ⚠ DB registration failed (non-critical): ${e.message}`);
  }
}

// ============================================================================
// Main Deploy Flow
// ============================================================================

async function deploy(privateKey, images, config) {
  const provider = new ethers.JsonRpcProvider(RPC_URL, CHAIN_ID);
  const wallet = new ethers.Wallet(privateKey, provider);

  console.log('='.repeat(60));
  console.log('Warren NFT Collection Deploy');
  console.log('='.repeat(60));
  console.log(`Address:     ${wallet.address}`);
  console.log(`Network:     MegaETH Mainnet (Chain ${CHAIN_ID})`);
  console.log(`Collection:  ${config.name} (${config.symbol})`);
  console.log(`Images:      ${images.length}`);
  console.log(`Max Supply:  ${config.maxSupply}`);

  const balance = await provider.getBalance(wallet.address);
  console.log(`Balance:     ${ethers.formatEther(balance)} ETH`);
  if (balance === 0n) throw new Error('No ETH balance. You need real MegaETH ETH for mainnet deployment.');

  await ensureGenesisKey(wallet);

  // Phase 1: Deploy all images
  console.log(`\n📸 Phase 1: Deploying ${images.length} image(s)...`);
  const deployedImages = [];
  for (let i = 0; i < images.length; i++) {
    const img = images[i];
    if (img.buffer.length > 500 * 1024) throw new Error(`Image ${img.originalPath} exceeds 500KB limit`);
    const result = await deployImageData(wallet, provider, img.buffer, `[${i + 1}/${images.length}]`);
    deployedImages.push({ ...result, containerPath: img.containerPath });
  }

  const totalSize = deployedImages.reduce((sum, img) => sum + img.totalSize, 0);
  console.log(`  Total image data: ${(totalSize / 1024).toFixed(1)}KB`);

  // Phase 2: Mint container
  const containerId = await mintContainer(wallet, deployedImages);

  // Phase 3: Deploy NFT collection
  const nftAddress = await deployCollection(wallet, provider, containerId, config);

  // Phase 4: Register to DB
  await registerToDB(nftAddress, containerId, wallet.address, config);

  // Output
  const managementUrl = `https://thewarren.app/launchpad/${nftAddress}/`;
  const mintUrl = `https://thewarren.app/launchpad/${nftAddress}/mint`;

  console.log('\n' + '='.repeat(60));
  console.log('🎉 NFT Collection Deployed!');
  console.log('='.repeat(60));
  console.log(`NFT Contract:  ${nftAddress}`);
  console.log(`Container ID:  ${containerId}`);
  console.log(`Image Count:   ${images.length}`);
  console.log(`Max Supply:    ${config.maxSupply}`);
  console.log(`Public Price:  ${config.publicPrice || '0'} ETH`);
  console.log('');
  console.log(`📋 Management: ${managementUrl}`);
  console.log(`🎨 Mint Page:  ${mintUrl}`);
  console.log('='.repeat(60));

  return { nftAddress, containerId, imageCount: images.length, managementUrl, mintUrl };
}

// ============================================================================
// CLI
// ============================================================================

async function main() {
  const args = process.argv.slice(2);
  const getArg = (n) => { const i = args.indexOf(`--${n}`); return i >= 0 ? args[i + 1] : undefined; };
  const hasArg = (n) => args.includes(`--${n}`);

  if (hasArg('help') || hasArg('h')) {
    console.log(`
Warren NFT Collection Deploy - Deploy NFT collections on MegaETH

Usage:
  PRIVATE_KEY=0x... node deploy-nft.js --images-folder ./art/ --name "My NFT" --symbol "MNFT" [options]
  PRIVATE_KEY=0x... node deploy-nft.js --generate-svg 10 --name "Gen Art" --symbol "GART" [options]

Required:
  --images-folder <path>    Folder with images (1.png, 2.png, ...)
  --generate-svg <count>    Generate random SVG art instead of using files
  --name <string>           Collection name
  --symbol <string>         Collection symbol (3-5 chars)

Optional:
  --description <text>      Collection description (default: "On-chain NFT collection on Warren")
  --max-supply <number>     Max NFTs (default: image count)
  --whitelist-price <eth>   WL mint price in ETH (default: 0)
  --public-price <eth>      Public mint price in ETH (default: 0)
  --max-per-wallet <number> Mint limit per wallet (default: 10)
  --royalty-bps <number>    Royalty basis points (default: 500 = 5%)
  --private-key <key>       Wallet private key (or set PRIVATE_KEY env)

Prerequisites:
  1. bash setup.sh (install ethers.js)
  2. You need MegaETH mainnet ETH for gas
  3. 0xRabbit.agent Key auto-mints (free)
`);
    process.exit(0);
  }

  const privateKey = getArg('private-key') || process.env.PRIVATE_KEY;
  if (!privateKey) { console.error('Error: set PRIVATE_KEY env or use --private-key'); process.exit(1); }

  const name = getArg('name');
  const symbol = getArg('symbol');
  if (!name || !symbol) { console.error('Error: --name and --symbol are required'); process.exit(1); }

  // Get images
  let images;
  const imagesFolder = getArg('images-folder');
  const generateCount = getArg('generate-svg');

  if (imagesFolder) {
    images = discoverImages(imagesFolder);
    console.log(`Found ${images.length} images in ${imagesFolder}`);
  } else if (generateCount) {
    const count = parseInt(generateCount);
    if (isNaN(count) || count < 1 || count > 256) { console.error('Error: --generate-svg must be 1-256'); process.exit(1); }
    images = generateSVGs(count);
    console.log(`Generated ${count} SVG images`);
  } else {
    console.error('Error: provide --images-folder or --generate-svg');
    process.exit(1);
  }

  const config = {
    name,
    symbol,
    description: getArg('description') || 'On-chain NFT collection on Warren',
    maxSupply: parseInt(getArg('max-supply') || images.length),
    whitelistPrice: getArg('whitelist-price') || '0',
    publicPrice: getArg('public-price') || '0',
    maxPerWallet: parseInt(getArg('max-per-wallet') || '10'),
    royaltyBps: parseInt(getArg('royalty-bps') || '500'),
    royaltyReceiver: getArg('royalty-receiver'),
  };

  try {
    const result = await deploy(privateKey, images, config);
    console.log('\n--- JSON ---');
    console.log(JSON.stringify(result, null, 2));
  } catch (e) {
    console.error(`\n❌ Failed: ${e.message}`);
    process.exit(1);
  }
}

main();
