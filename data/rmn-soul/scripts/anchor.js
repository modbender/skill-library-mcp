#!/usr/bin/env node
/**
 * RMN Soul Anchor — Register ERC-8004 identity + upload to IPFS + anchor on-chain
 * 
 * Uses `cast` (Foundry) for transactions. Falls back to generating deploy script.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync, spawnSync } = require('child_process');
const { RecursiveMemoryNetwork, computeMemoryMerkle } = require('./rmn-engine');

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.resolve(__dirname, '../../../');
const DATA_DIR = path.join(WORKSPACE, 'rmn-soul-data');
const DB_PATH = path.join(DATA_DIR, 'memory.json');
const CONFIG_PATH = path.join(DATA_DIR, 'config.json');
const IDENTITY_PATH = path.join(DATA_DIR, 'identity.json');

function loadConfig() {
  try { return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8')); }
  catch { throw new Error('Config not found. Run setup.js first.'); }
}

function hasCast() {
  const paths = [
    process.env.HOME + '/.foundry/bin/cast',
    '/usr/local/bin/cast',
    'cast',
  ];
  for (const p of paths) {
    if (spawnSync('which', [p.includes('/') ? p : 'cast']).status === 0) return p.includes('/') ? p : 'cast';
  }
  return null;
}

function castCmd(args, key) {
  const cast = hasCast() || `${process.env.HOME}/.foundry/bin/cast`;
  const cmd = `${cast} ${args}`;
  return execSync(cmd, { timeout: 30000, encoding: 'utf-8' }).trim();
}

// Upload to IPFS (local node or fallback)
function uploadToIPFS(data, filename) {
  const jsonStr = typeof data === 'string' ? data : JSON.stringify(data);
  const tmpFile = path.join(DATA_DIR, `_tmp_${filename}`);
  fs.writeFileSync(tmpFile, jsonStr);
  
  try {
    // Try local IPFS node
    const cid = execSync(`ipfs add -q "${tmpFile}"`, { timeout: 10000, encoding: 'utf-8' }).trim();
    fs.unlinkSync(tmpFile);
    return { cid, url: `ipfs://${cid}`, gateway: `https://ipfs.io/ipfs/${cid}`, local: false };
  } catch {
    // Fallback: local storage
    const hash = crypto.createHash('sha256').update(jsonStr).digest('hex').slice(0, 16);
    const localDir = path.join(DATA_DIR, 'ipfs-local');
    fs.mkdirSync(localDir, { recursive: true });
    const localPath = path.join(localDir, `${hash}.json`);
    fs.renameSync(tmpFile, localPath);
    return { cid: `local-${hash}`, url: `file://${localPath}`, gateway: localPath, local: true };
  }
}

async function anchor(opts = {}) {
  const config = loadConfig();
  const isFirstRun = !config.agentId;
  
  console.log('🔗 RMN Soul Anchor\n');
  
  // Step 1: Load memory network
  if (!fs.existsSync(DB_PATH)) {
    console.log('❌ No memory.json found. Run setup.js first.');
    process.exit(1);
  }
  
  const rmn = new RecursiveMemoryNetwork(DB_PATH);
  const stats = rmn.stats();
  console.log(`Memory: ${stats.totalNodes} nodes, ${stats.totalConnections} connections`);
  
  // Step 2: Compute Merkle Tree
  const merkle = computeMemoryMerkle(rmn);
  console.log(`Memory Root: 0x${merkle.memoryRoot.slice(0, 16)}...`);
  console.log(`Soul Hash:   0x${merkle.soulHash.slice(0, 16)}...`);
  
  // Step 3: Generate manifest
  const manifest = {
    type: 'rmn-soul-manifest-v1',
    version: merkle.version,
    timestamp: merkle.timestamp,
    memoryRoot: merkle.memoryRoot,
    soulHash: merkle.soulHash,
    stats: { totalNodes: stats.totalNodes, totalConnections: stats.totalConnections, layers: stats.layers },
    layerRoots: merkle.layerRoots,
    topology: rmn.exportGraph(),
  };
  fs.writeFileSync(path.join(DATA_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2));
  
  // Step 4: Upload to IPFS
  console.log('\nUploading to IPFS...');
  const memoryUpload = uploadToIPFS(fs.readFileSync(DB_PATH, 'utf-8'), 'memory.json');
  const manifestUpload = uploadToIPFS(manifest, 'manifest.json');
  console.log(`  Memory:   ${memoryUpload.cid} ${memoryUpload.local ? '(local)' : '(IPFS)'}`);
  console.log(`  Manifest: ${manifestUpload.cid} ${manifestUpload.local ? '(local)' : '(IPFS)'}`);
  
  // Step 5: On-chain transaction
  const privateKey = opts.sponsorKey || config.sponsorKey || process.env.RMN_SPONSOR_KEY;
  if (!privateKey) {
    console.log('\n⚠️ No sponsor key configured. Saving calldata for manual execution.');
    const calldata = {
      chain: config.chain,
      registry: config.identityRegistry,
      agentId: config.agentId,
      calls: isFirstRun
        ? [{ fn: 'register(string)', args: ['<agentURI>'], note: 'Mint Agent NFT' }]
        : [
            { fn: 'setMetadata(uint256,string,bytes)', args: [config.agentId, 'memoryRoot', `0x${merkle.memoryRoot}`] },
            { fn: 'setMetadata(uint256,string,bytes)', args: [config.agentId, 'soulHash', `0x${merkle.soulHash}`] },
          ],
    };
    fs.writeFileSync(path.join(DATA_DIR, 'calldata.json'), JSON.stringify(calldata, null, 2));
    console.log(`  Calldata saved: ${path.join(DATA_DIR, 'calldata.json')}`);
    return;
  }
  
  const cast = hasCast();
  if (!cast) {
    console.log('\n⚠️ Foundry cast not found. Install: curl -L https://foundry.paradigm.xyz | bash && foundryup');
    return;
  }
  
  const rpcUrl = config.chain === 'base' ? 'https://mainnet.base.org' : 'https://mainnet.base.org';
  
  if (isFirstRun) {
    // Register new agent
    console.log('\n📝 Registering new Agent...');
    const regData = {
      type: 'https://eips.ethereum.org/EIPS/eip-8004#registration-v1',
      name: opts.name || 'RMN-Soul-Agent',
      description: `Autonomous AI agent with Recursive Memory Network. ${stats.totalNodes} memory nodes, ${stats.totalConnections} connections.`,
      services: [],
      x402Support: true,
      active: true,
      supportedTrust: ['reputation'],
      rmn: { version: '1.0.0', memoryRoot: merkle.memoryRoot, soulHash: merkle.soulHash },
    };
    const agentURI = `data:application/json;base64,${Buffer.from(JSON.stringify(regData)).toString('base64')}`;
    
    try {
      const result = execSync(
        `${cast} send --private-key ${privateKey} --rpc-url ${rpcUrl} ${config.identityRegistry} "register(string)" "${agentURI}" --json`,
        { timeout: 30000, encoding: 'utf-8' }
      );
      const tx = JSON.parse(result);
      const agentId = tx.logs && tx.logs[0] ? parseInt(tx.logs[0].topics[3], 16) : null;
      
      console.log(`  ✅ Registered! Agent ID: ${agentId}`);
      console.log(`  TX: ${tx.transactionHash}`);
      
      config.agentId = agentId;
      fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
      
      // Save identity
      const identity = {
        agentId, chain: config.chain, chainId: config.chainId,
        registry: config.identityRegistry,
        txHash: tx.transactionHash,
        memoryRoot: merkle.memoryRoot, soulHash: merkle.soulHash,
        ipfs: { memory: memoryUpload, manifest: manifestUpload },
        registeredAt: new Date().toISOString(),
      };
      fs.writeFileSync(IDENTITY_PATH, JSON.stringify(identity, null, 2));
    } catch (e) {
      console.log(`  ❌ Registration failed: ${e.message.slice(0, 200)}`);
      return;
    }
  }
  
  // Set metadata
  const agentId = config.agentId;
  console.log(`\n📝 Updating metadata for Agent #${agentId}...`);
  
  const metadataCalls = [
    ['memoryRoot', `0x${merkle.memoryRoot}`],
    ['soulHash', `0x${merkle.soulHash}`],
    ['memoryManifest', `$(${cast} --from-utf8 '${manifestUpload.url}')`],
    ['memoryData', `$(${cast} --from-utf8 '${memoryUpload.url}')`],
  ];
  
  const txHashes = [];
  for (const [key, value] of metadataCalls) {
    try {
      let val = value;
      if (value.startsWith('$(')) {
        // Evaluate subcommand
        val = execSync(value.slice(2, -1), { encoding: 'utf-8' }).trim();
      }
      const result = execSync(
        `${cast} send --private-key ${privateKey} --rpc-url ${rpcUrl} ${config.identityRegistry} "setMetadata(uint256,string,bytes)" ${agentId} "${key}" "${val}" --json`,
        { timeout: 30000, encoding: 'utf-8' }
      );
      const tx = JSON.parse(result);
      txHashes.push({ key, tx: tx.transactionHash });
      console.log(`  ✅ ${key}: ${tx.transactionHash.slice(0, 18)}...`);
    } catch (e) {
      console.log(`  ❌ ${key} failed: ${e.message.slice(0, 100)}`);
    }
  }
  
  // Update config
  config.lastAnchor = new Date().toISOString();
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  
  // Save anchor history
  const historyPath = path.join(DATA_DIR, 'anchor-history.json');
  let history = [];
  try { history = JSON.parse(fs.readFileSync(historyPath, 'utf-8')); } catch {}
  history.push({
    timestamp: new Date().toISOString(),
    agentId, memoryRoot: merkle.memoryRoot, soulHash: merkle.soulHash,
    nodes: stats.totalNodes, connections: stats.totalConnections,
    ipfs: { memory: memoryUpload.cid, manifest: manifestUpload.cid },
    txHashes,
  });
  fs.writeFileSync(historyPath, JSON.stringify(history, null, 2));
  
  console.log(`\n🦞 Anchor complete! Agent #${agentId} updated on ${config.chain}.`);
}

if (require.main === module) {
  anchor({ sponsorKey: process.argv[2] || process.env.RMN_SPONSOR_KEY }).catch(console.error);
}

module.exports = { anchor };
