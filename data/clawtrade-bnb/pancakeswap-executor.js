/**
 * PancakeSwap Real Transaction Executor
 * Executes real swaps and LP operations on PancakeSwap testnet
 */

const { ethers } = require('ethers');
const fs = require('fs');

const RPC_URL = 'https://bsc-testnet.publicnode.com';
const PANCAKESWAP_ROUTER = '0xD99D0BC5273d5aeB3f8b81e34e64bF1b92ac1d5a'; // Testnet Router V2

const ROUTER_ABI = [
  'function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline) returns (uint[] memory amounts)',
  'function swapTokensForExactTokens(uint amountOut, uint amountInMax, address[] calldata path, address to, uint deadline) returns (uint[] memory amounts)',
  'function addLiquidity(address tokenA, address tokenB, uint amountADesired, uint amountBDesired, uint amountAMin, uint amountBMin, address to, uint deadline) returns (uint amountA, uint amountB, uint liquidity)',
];

const ERC20_ABI = [
  'function approve(address spender, uint256 amount) external returns (bool)',
  'function balanceOf(address account) external view returns (uint256)',
  'function allowance(address owner, address spender) external view returns (uint256)',
];

class PancakeSwapExecutor {
  constructor(privateKey, poolAddress, token0, token1) {
    this.provider = new ethers.providers.JsonRpcProvider(RPC_URL);
    this.wallet = new ethers.Wallet(privateKey, this.provider);
    this.router = new ethers.Contract(PANCAKESWAP_ROUTER, ROUTER_ABI, this.wallet);
    this.poolAddress = poolAddress;
    this.token0 = token0;
    this.token1 = token1;
  }

  async executeSwap(amountIn, minAmountOut, isToken0ToToken1 = true, logFile = './execution-log.jsonl') {
    console.log(`\n💰 Executing PancakeSwap swap...`);
    
    try {
      const path = isToken0ToToken1 
        ? [this.token0, this.token1]
        : [this.token1, this.token0];

      const deadline = Math.floor(Date.now() / 1000) + 300; // 5 min deadline
      
      // Approve token
      const tokenContract = new ethers.Contract(path[0], ERC20_ABI, this.wallet);
      const allowance = await tokenContract.allowance(this.wallet.address, PANCAKESWAP_ROUTER);
      
      if (allowance.lt(ethers.utils.parseEther(amountIn.toString()))) {
        console.log('  Approving token for router...');
        const approveTx = await tokenContract.approve(
          PANCAKESWAP_ROUTER,
          ethers.constants.MaxUint256
        );
        await approveTx.wait();
        console.log(`  ✓ Approved`);
      }

      // Execute swap
      console.log(`  Swapping ${amountIn} ${isToken0ToToken1 ? 'Token0' : 'Token1'}...`);
      
      const amountInWei = ethers.utils.parseEther(amountIn.toString());
      const minAmountOutWei = ethers.utils.parseEther(minAmountOut.toString());

      const tx = await this.router.swapExactTokensForTokens(
        amountInWei,
        minAmountOutWei,
        path,
        this.wallet.address,
        deadline
      );

      console.log(`  TX Hash: ${tx.hash}`);
      console.log(`  Waiting for confirmation...`);

      const receipt = await tx.wait();

      console.log(`  ✅ Swap executed!`);
      console.log(`  Gas used: ${receipt.gasUsed.toString()}`);

      // Log execution
      const executionRecord = {
        timestamp: Math.floor(Date.now() / 1000),
        cycle: this.getCycleNumber(),
        action: 'PANCAKESWAP_SWAP',
        vault_id: 'wbnb-link-pool',
        vault_name: 'PancakeSwap WBNB-LINK',
        direction: isToken0ToToken1 ? 'token0->token1' : 'token1->token0',
        amountIn,
        minAmountOut,
        tx_hash: tx.hash,
        status: 'success',
        gas_used: receipt.gasUsed.toNumber(),
        block_number: receipt.blockNumber,
      };

      fs.appendFileSync(logFile, JSON.stringify(executionRecord) + '\n');
      console.log(`  Logged to: ${logFile}\n`);

      return executionRecord;
    } catch (error) {
      console.error(`  ❌ Swap failed: ${error.message}\n`);

      // Log error
      const errorRecord = {
        timestamp: Math.floor(Date.now() / 1000),
        action: 'PANCAKESWAP_SWAP_ERROR',
        vault_id: 'wbnb-link-pool',
        error: error.message,
        status: 'failed',
      };

      fs.appendFileSync(logFile, JSON.stringify(errorRecord) + '\n');
      
      throw error;
    }
  }

  getCycleNumber() {
    const logFile = './execution-log.jsonl';
    if (!fs.existsSync(logFile)) return 1;
    
    const lines = fs.readFileSync(logFile, 'utf8').split('\n').filter(l => l);
    return lines.length + 1;
  }

  async getWalletBalance(tokenAddress) {
    try {
      const tokenContract = new ethers.Contract(tokenAddress, ERC20_ABI, this.provider);
      const balance = await tokenContract.balanceOf(this.wallet.address);
      return ethers.utils.formatEther(balance);
    } catch (error) {
      console.error('Error getting balance:', error.message);
      return '0';
    }
  }
}

module.exports = PancakeSwapExecutor;
