const { ethers } = require('ethers');
const fs = require('fs');

// Configuration - set via environment variables or edit
const PRIVATE_KEY = process.env.UP_PRIVATE_KEY || 'YOUR_CONTROLLER_PRIVATE_KEY';
const UP_ADDRESS = process.env.UP_ADDRESS || 'YOUR_UP_ADDRESS';
const KEY_MANAGER = process.env.KEY_MANAGER || 'YOUR_KEY_MANAGER_ADDRESS';
const RPC_URL = process.env.RPC_URL || 'https://rpc.mainnet.lukso.network';

// LSP28 Grid Data Key
const LSP28_GRID_KEY = '0x31cf14955c5b0052c1491ec06644438ec7c14454be5eb6cb9ce4e4edef647423';

// LSP0 and LSP6 ABIs (minimal)
const LSP0_ABI = [
  'function setData(bytes32 dataKey, bytes dataValue) external',
  'function getData(bytes32 dataKey) external view returns (bytes)'
];

const LSP6_ABI = [
  'function execute(bytes calldata payload) external payable returns (bytes memory)'
];

async function updateGrid(gridData) {
  console.log('🔄 Updating LSP28 Grid...\n');
  
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  
  // Encode grid data as VerifiableURI
  const jsonString = JSON.stringify(gridData);
  const base64Data = Buffer.from(jsonString).toString('base64');
  const verifiableUri = `data:application/json;base64,${base64Data}`;
  
  console.log('Grid items:', gridData.items.length);
  console.log('VerifiableURI length:', verifiableUri.length);
  
  // Encode setData call
  const upInterface = new ethers.Interface(LSP0_ABI);
  const setDataCalldata = upInterface.encodeFunctionData('setData', [
    LSP28_GRID_KEY,
    ethers.toUtf8Bytes(verifiableUri)
  ]);
  
  // Execute via KeyManager
  const keyManager = new ethers.Contract(KEY_MANAGER, LSP6_ABI, wallet);
  
  console.log('\n📤 Sending transaction...');
  const tx = await keyManager.execute(setDataCalldata);
  console.log('Transaction:', tx.hash);
  
  const receipt = await tx.wait();
  console.log('✅ Confirmed in block:', receipt.blockNumber);
  
  return receipt;
}

// Example grid data
const EXAMPLE_GRID = {
  isEditable: true,
  items: [
    {
      type: 'miniapp',
      id: 'home',
      title: 'Home',
      backgroundColor: '#fe005b',
      textColor: '#ffffff',
      text: 'Welcome'
    },
    {
      type: 'external',
      id: 'twitter',
      title: 'Twitter',
      url: 'https://twitter.com'
    },
    {
      type: 'iframe',
      id: 'dashboard',
      title: 'Dashboard',
      src: 'https://example.com/embed'
    }
  ]
};

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args[0] === '--file') {
    // Load grid from JSON file
    const gridFile = args[1];
    const gridData = JSON.parse(fs.readFileSync(gridFile, 'utf8'));
    updateGrid(gridData).catch(console.error);
  } else if (args[0] === '--example') {
    // Use example grid
    updateGrid(EXAMPLE_GRID).catch(console.error);
  } else {
    console.log('Usage:');
    console.log('  node update-grid.js --file grid.json     # Load from file');
    console.log('  node update-grid.js --example           # Use example grid');
    console.log('\nEnvironment variables:');
    console.log('  UP_PRIVATE_KEY  - Controller private key');
    console.log('  UP_ADDRESS      - Universal Profile address');
    console.log('  KEY_MANAGER     - Key Manager address');
    console.log('  RPC_URL         - LUKSO RPC endpoint');
    process.exit(1);
  }
}

module.exports = { updateGrid, LSP28_GRID_KEY };
