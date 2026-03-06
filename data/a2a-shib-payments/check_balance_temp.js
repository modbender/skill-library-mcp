const { ethers } = require('ethers');

async function check() {
  const provider = new ethers.JsonRpcProvider('https://polygon-rpc.com');
  const address = '0xDBD846593c1C89014a64bf0ED5802126912Ba99A';
  
  // Check POL balance
  const polBalance = await provider.getBalance(address);
  console.log(`POL Balance: ${ethers.formatEther(polBalance)} POL`);
  
  // Check SHIB balance
  const shibContract = '0x6f8a06447ff6fcf75d803135a7de15ce88c1d4ec';
  const shibAbi = ['function balanceOf(address) view returns (uint256)', 'function decimals() view returns (uint8)'];
  const shibToken = new ethers.Contract(shibContract, shibAbi, provider);
  
  const shibBalance = await shibToken.balanceOf(address);
  const decimals = await shibToken.decimals();
  console.log(`SHIB Balance: ${ethers.formatUnits(shibBalance, decimals)} SHIB`);
  
  console.log(`\nExplorer: https://polygonscan.com/address/${address}`);
}

check().catch(console.error);
