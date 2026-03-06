/**
 * PancakeSwap Real Data Reader
 * Reads live pool data and calculates real APR/slippage
 */

const { ethers } = require('ethers');

const RPC_URL = 'https://bsc-testnet.publicnode.com';

// Pair ABI
const PAIR_ABI = [
  'function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)',
  'function token0() external view returns (address)',
  'function token1() external view returns (address)',
];

// ERC20 ABI
const ERC20_ABI = [
  'function decimals() external view returns (uint8)',
  'function symbol() external view returns (string)',
];

class PancakeSwapReader {
  constructor(poolAddress) {
    this.provider = new ethers.providers.JsonRpcProvider(RPC_URL);
    this.poolAddress = poolAddress;
    this.pair = null;
    this.token0 = null;
    this.token1 = null;
    this.decimals0 = 18;
    this.decimals1 = 18;
    this.symbol0 = 'TOKEN0';
    this.symbol1 = 'TOKEN1';
  }

  async initialize() {
    console.log('🔧 Initializing PancakeSwap Reader...');
    
    try {
      this.pair = new ethers.Contract(this.poolAddress, PAIR_ABI, this.provider);
      
      const token0Addr = await this.pair.token0();
      const token1Addr = await this.pair.token1();

      const token0Contract = new ethers.Contract(token0Addr, ERC20_ABI, this.provider);
      const token1Contract = new ethers.Contract(token1Addr, ERC20_ABI, this.provider);

      this.decimals0 = await token0Contract.decimals();
      this.decimals1 = await token1Contract.decimals();
      this.symbol0 = await token0Contract.symbol();
      this.symbol1 = await token1Contract.symbol();

      console.log(`✓ Pool initialized: ${this.symbol0}-${this.symbol1}`);
    } catch (error) {
      console.error('✗ Initialization failed:', error.message);
      throw error;
    }
  }

  async getPoolData() {
    try {
      const [reserve0, reserve1, blockTimestamp] = await this.pair.getReserves();

      const normalizedReserve0 = parseFloat(ethers.utils.formatUnits(reserve0, this.decimals0));
      const normalizedReserve1 = parseFloat(ethers.utils.formatUnits(reserve1, this.decimals1));

      return {
        reserve0,
        reserve1,
        normalizedReserve0,
        normalizedReserve1,
        blockTimestamp,
        symbol0: this.symbol0,
        symbol1: this.symbol1,
        pair: `${this.symbol0}-${this.symbol1}`,
      };
    } catch (error) {
      console.error('✗ Error reading pool data:', error.message);
      return null;
    }
  }

  async calculatePrice() {
    const data = await this.getPoolData();
    if (!data) return null;

    // Price of token1 in token0 (e.g., price of LINK in WBNB)
    const price = data.normalizedReserve0 / data.normalizedReserve1;

    return {
      price,
      inverse: 1 / price,
      symbol0: data.symbol0,
      symbol1: data.symbol1,
      liquidity: {
        token0: data.normalizedReserve0,
        token1: data.normalizedReserve1,
      },
    };
  }

  async calculateAPR(tradingVolume24h = 0) {
    const data = await this.getPoolData();
    if (!data) return null;

    // Simplified APR calculation
    // APR = (Daily Fee Volume / Pool TVL) * 365 * 100
    // Assuming 0.25% swap fee and some volume
    const tvl = data.normalizedReserve0 + data.normalizedReserve1; // Simplified TVL
    
    // Estimated daily volume (in WBNB equivalent)
    const estimatedDailyVolume = tradingVolume24h || tvl * 0.1; // 10% of TVL as default estimate
    const feePercentage = 0.0025; // 0.25% swap fee
    const dailyFees = estimatedDailyVolume * feePercentage;
    
    const apr = (dailyFees / tvl) * 365 * 100;

    return {
      apr: parseFloat(apr.toFixed(2)),
      estimatedDailyVolume: parseFloat(estimatedDailyVolume.toFixed(2)),
      dailyFees: parseFloat(dailyFees.toFixed(4)),
      tvl: parseFloat(tvl.toFixed(2)),
      feePercentage: feePercentage * 100,
    };
  }

  async getSlippage(amountIn, isToken0) {
    const data = await this.getPoolData();
    if (!data) return null;

    // Simple slippage calculation
    const [reserveIn, reserveOut] = isToken0 
      ? [data.normalizedReserve0, data.normalizedReserve1]
      : [data.normalizedReserve1, data.normalizedReserve0];

    // y = x * y / (x + dx)
    const denominator = reserveIn + amountIn;
    const numerator = reserveIn * reserveOut;
    const amountOut = reserveOut - (numerator / denominator);

    // Without slippage: amountOut = amountIn * (reserveOut / reserveIn)
    const idealPrice = reserveOut / reserveIn;
    const actualPrice = amountOut / amountIn;
    const slippage = ((idealPrice - actualPrice) / idealPrice) * 100;

    return {
      amountIn,
      amountOut: parseFloat(amountOut.toFixed(6)),
      slippage: parseFloat(slippage.toFixed(2)),
      priceImpact: parseFloat(((1 - (amountOut / (amountIn * idealPrice))) * 100).toFixed(2)),
    };
  }
}

module.exports = PancakeSwapReader;
