"""
Constants for MoonfunSDK
Contract addresses, ABIs, and network configuration
"""

# BSC Mainnet Configuration
ROUTER_ADDRESS = "0x953C65358a8666617C66327cb18AD02126b2AAA5"
WBNB_ADDRESS = "0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
CHAIN_ID = 56
DEFAULT_RPC_URL = "https://bsc-dataseed.bnbchain.org"

# MoonnFun Platform Configuration
PLATFORM_BASE_URL = "https://moonn.fun"
DEFAULT_CHAIN = "bsc"

# Token Creation Fee
CREATE_FEE_BNB = 0.01

# MoonnFun Router ABI (Core Methods)
ROUTER_ABI = [
    {
        "name": "createToken",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "tokenId", "type": "uint256"},
            {"name": "name", "type": "string"},
            {"name": "symbol", "type": "string"},
            {"name": "salt", "type": "uint256"}
        ],
        "outputs": []
    },
    {
        "name": "buy",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "token", "type": "address"},
            {"name": "minReceived", "type": "uint256"},
            {"name": "source", "type": "uint256"}
        ],
        "outputs": []
    },
    {
        "name": "sell",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "token", "type": "address"},
            {"name": "sellAmount", "type": "uint256"},
            {"name": "minReceived", "type": "uint256"},
            {"name": "source", "type": "uint256"}
        ],
        "outputs": []
    },
    {
        "name": "getAmountOut",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenInAmount", "type": "uint256"},
            {"name": "tokenOut", "type": "address"}
        ],
        "outputs": [{"name": "", "type": "uint256"}]
    }
]

# ERC20 Basic ABI
ERC20_ABI = [
    {
        "name": "approve",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "outputs": [{"name": "", "type": "bool"}]
    },
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}]
    },
    {
        "name": "decimals",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}]
    }
]
