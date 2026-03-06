#!/usr/bin/env node
/**
 * RMN Soul Resurrect — Restore an agent from chain + IPFS
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { execSync } = require('child_process');
const { RecursiveMemoryNetwork, computeMemoryMerkle } = require('./rmn-engine');

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.resolve(__dirname, '../../../');
const DATA_DIR = path.join(WORKSPACE, 'rmn-soul-data');

function fetchIPFS(cid) {
  return new Promise((resolve, reject) => {
    const gateways = [
      `https://ipfs.io/ipfs/${cid}`,
      `https://gateway.pinata.cloud/ipfs/${cid}`,
      `https://cloudflare-ipfs.com/ipfs/${cid}`,
      `https://dweb.link/ipfs/${cid}`,
    ];
    
    let tried = 0;
    const tryNext = () => {
      if (tried >= gateways.length) return reject(new Error('All IPFS gateways failed'));
      const url = gateways[tried++];
      
      https.get(url, { timeout: 15000 }, res => {
        if (res.statusCode !== 200) return tryNext();
        const chunks = [];
        res.on('data', c => chunks.push(c));
        res.on('end', () => resolve(Buffer.concat(chunks).toString()));
        res.on('error', tryNext);
      }).on('error', tryNext);
    };
    
    tryNext();
  });
}

async function resurrect(agentId, chain = 'base') {
  console.log('🔮 RMN Soul Resurrect\n');
  console.log(`Agent ID: ${agentId}`);
  console.log(`Chain:    ${chain}\n`);
  
  const rpcUrl = chain === 'base' ? 'https://mainnet.base.org' : 'https://mainnet.base.org';
  const registry = '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432';
  const cast = `${process.env.HOME}/.foundry/bin/cast`;
  
  // Step 1: Read on-chain data
  console.log('Step 1: Reading on-chain identity...');
  
  let owner, memoryRoot, soulHash, memoryDataHex, memoryManifestHex;
  try {
    owner = execSync(`${cast} call --rpc-url ${rpcUrl} ${registry} "ownerOf(uint256)(address)" ${agentId}`, { encoding: 'utf-8' }).trim();
    memoryRoot = execSync(`${cast} call --rpc-url ${rpcUrl} ${registry} "getMetadata(uint256,string)(bytes)" ${agentId} "memoryRoot"`, { encoding: 'utf-8' }).trim();
    soulHash = execSync(`${cast} call --rpc-url ${rpcUrl} ${registry} "getMetadata(uint256,string)(bytes)" ${agentId} "soulHash"`, { encoding: 'utf-8' }).trim();
    memoryDataHex = execSync(`${cast} call --rpc-url ${rpcUrl} ${registry} "getMetadata(uint256,string)(bytes)" ${agentId} "memoryData"`, { encoding: 'utf-8' }).trim();
    memoryManifestHex = execSync(`${cast} call --rpc-url ${rpcUrl} ${registry} "getMetadata(uint256,string)(bytes)" ${agentId} "memoryManifest"`, { encoding: 'utf-8' }).trim();
  } catch (e) {
    console.log(`❌ Failed to read chain data: ${e.message.slice(0, 200)}`);
    return;
  }
  
  console.log(`  Owner:       ${owner}`);
  console.log(`  Memory Root: ${memoryRoot.slice(0, 20)}...`);
  console.log(`  Soul Hash:   ${soulHash.slice(0, 20)}...`);
  
  // Decode IPFS URLs from hex
  const decodeHex = hex => Buffer.from(hex.replace('0x', ''), 'hex').toString('utf-8');
  let memoryDataUrl, manifestUrl;
  try {
    memoryDataUrl = decodeHex(memoryDataHex);
    manifestUrl = decodeHex(memoryManifestHex);
  } catch {
    memoryDataUrl = memoryDataHex;
    manifestUrl = memoryManifestHex;
  }
  
  console.log(`  Memory IPFS: ${memoryDataUrl}`);
  console.log(`  Manifest:    ${manifestUrl}`);
  
  // Step 2: Fetch from IPFS
  console.log('\nStep 2: Fetching memory from IPFS...');
  
  let memoryJson;
  const cid = memoryDataUrl.replace('ipfs://', '');
  
  // Try local IPFS first
  try {
    memoryJson = execSync(`ipfs cat ${cid}`, { timeout: 10000, encoding: 'utf-8' });
    console.log('  ✅ Fetched from local IPFS node');
  } catch {
    // Try public gateways
    try {
      memoryJson = await fetchIPFS(cid);
      console.log('  ✅ Fetched from IPFS gateway');
    } catch (e) {
      console.log(`  ❌ Failed to fetch from IPFS: ${e.message}`);
      console.log('  💡 If you have a local backup, place it at: rmn-soul-data/memory.json');
      return;
    }
  }
  
  // Step 3: Verify integrity
  console.log('\nStep 3: Verifying memory integrity...');
  
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const dbPath = path.join(DATA_DIR, 'memory.json');
  fs.writeFileSync(dbPath, memoryJson);
  
  const rmn = new RecursiveMemoryNetwork(dbPath);
  const merkle = computeMemoryMerkle(rmn);
  const computedRoot = `0x${merkle.memoryRoot}`;
  
  if (computedRoot === memoryRoot) {
    console.log('  ✅ Merkle Root MATCHES — memory integrity verified!');
  } else {
    console.log('  ⚠️ Merkle Root MISMATCH — memory may have been tampered with!');
    console.log(`    Chain:    ${memoryRoot}`);
    console.log(`    Computed: ${computedRoot}`);
  }
  
  const computedSoul = `0x${merkle.soulHash}`;
  if (computedSoul === soulHash) {
    console.log('  ✅ Soul Hash MATCHES — identity intact!');
  } else {
    console.log('  ⚠️ Soul Hash MISMATCH — identity layer may have changed!');
  }
  
  // Step 4: Restore
  console.log('\nStep 4: Restoring agent...');
  const stats = rmn.stats();
  console.log(`  Nodes:       ${stats.totalNodes}`);
  console.log(`  Connections: ${stats.totalConnections}`);
  console.log(`  Layers:      ${JSON.stringify(stats.layers)}`);
  
  // Save identity
  const identity = {
    agentId: parseInt(agentId),
    chain, owner, memoryRoot, soulHash,
    ipfs: { memoryData: memoryDataUrl, manifest: manifestUrl },
    restoredAt: new Date().toISOString(),
    verified: computedRoot === memoryRoot,
  };
  fs.writeFileSync(path.join(DATA_DIR, 'identity.json'), JSON.stringify(identity, null, 2));
  
  // Save config
  const configPath = path.join(DATA_DIR, 'config.json');
  fs.writeFileSync(configPath, JSON.stringify({
    chain, chainId: 8453,
    identityRegistry: registry,
    reputationRegistry: '0x8004BAa17C55a88189AE136b182e5fdA19dE9b63',
    agentId: parseInt(agentId),
    lastAnchor: new Date().toISOString(),
    autoAnchorDays: 7,
    ipfsEnabled: true,
  }, null, 2));
  
  console.log('\n🦞 Agent #' + agentId + ' RESURRECTED!');
  console.log(`  Memory: ${stats.totalNodes} nodes restored`);
  console.log(`  Integrity: ${computedRoot === memoryRoot ? '✅ Verified' : '⚠️ Check needed'}`);
  console.log(`  Data: ${dbPath}`);
}

if (require.main === module) {
  const args = process.argv.slice(2);
  let agentId = null, chain = 'base';
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--agent-id' && args[i + 1]) agentId = args[++i];
    if (args[i] === '--chain' && args[i + 1]) chain = args[++i];
  }
  
  if (!agentId) {
    console.log('Usage: node resurrect.js --agent-id <id> [--chain base]');
    process.exit(1);
  }
  
  resurrect(agentId, chain).catch(console.error);
}

module.exports = { resurrect };
