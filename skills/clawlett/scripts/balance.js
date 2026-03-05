#!/usr/bin/env node

/**
 * Check Safe balances
 *
 * Usage:
 *   node balance.js              # ETH balance
 *   node balance.js --token USDC # Specific token
 *   node balance.js --all        # All verified tokens
 */

import { ethers } from 'ethers'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const DEFAULT_RPC_URL = 'https://mainnet.base.org'

const VERIFIED_TOKENS = {
    'ETH': '0x4200000000000000000000000000000000000006',
    'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    'USDT': '0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2',
    'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
    'AERO': '0x940181a94A35A4569E4529A3CDfB74e38FD98631',
    'cbBTC': '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',
    'VIRTUAL': '0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b',
    'DEGEN': '0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed',
    'BRETT': '0x532f27101965dd16442E59d40670FaF5eBB142E4',
    'TOSHI': '0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4',
    'WELL': '0xA88594D404727625A9437C3f886C7643872296AE',
    'BID': '0xa1832f7f4e534ae557f9b5ab76de54b1873e498b',
}

const ERC20_ABI = [
    'function symbol() view returns (string)',
    'function decimals() view returns (uint8)',
    'function balanceOf(address) view returns (uint256)',
]

function loadConfig(configDir) {
    const configPath = path.join(configDir, 'wallet.json')
    if (!fs.existsSync(configPath)) {
        throw new Error(`Config not found: ${configPath}\nRun initialize.js first.`)
    }
    return JSON.parse(fs.readFileSync(configPath, 'utf8'))
}

function parseArgs() {
    const args = process.argv.slice(2)
    const result = {
        token: null,
        all: false,
        configDir: process.env.WALLET_CONFIG_DIR || path.join(__dirname, '..', 'config'),
        rpc: process.env.BASE_RPC_URL || DEFAULT_RPC_URL,
    }

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--token':
            case '-t':
                result.token = args[++i]
                break
            case '--all':
            case '-a':
                result.all = true
                break
            case '--config-dir':
            case '-c':
                result.configDir = args[++i]
                break
            case '--rpc':
            case '-r':
                result.rpc = args[++i]
                break
            case '--help':
            case '-h':
                printHelp()
                process.exit(0)
        }
    }

    return result
}

function printHelp() {
    console.log(`
Usage: node balance.js [options]

Options:
  --token, -t      Check specific token balance
  --all, -a        Check all verified token balances
  --config-dir, -c Config directory
  --rpc, -r        RPC URL (default: ${DEFAULT_RPC_URL})

Examples:
  node balance.js              # ETH balance only
  node balance.js --token USDC # USDC balance
  node balance.js --all        # All token balances
`)
}

function formatAmount(amount, decimals, symbol) {
    const formatted = ethers.formatUnits(amount, decimals)
    const num = parseFloat(formatted)
    if (num === 0) return `0 ${symbol}`
    if (num < 0.0001) return `${formatted} ${symbol}`
    return `${num.toLocaleString(undefined, { maximumFractionDigits: 6 })} ${symbol}`
}

async function getTokenBalance(provider, safeAddress, tokenAddress) {
    const contract = new ethers.Contract(tokenAddress, ERC20_ABI, provider)
    const [symbol, decimals, balance] = await Promise.all([
        contract.symbol(),
        contract.decimals(),
        contract.balanceOf(safeAddress),
    ])
    return { symbol, decimals: Number(decimals), balance }
}

async function main() {
    const args = parseArgs()

    let config
    try {
        config = loadConfig(args.configDir)
    } catch (error) {
        console.error(`Error: ${error.message}`)
        process.exit(1)
    }

    const provider = new ethers.JsonRpcProvider(args.rpc)
    const safeAddress = config.safe

    console.log(`\nSafe: ${safeAddress}\n`)

    // Always show ETH
    const ethBalance = await provider.getBalance(safeAddress)
    console.log(`ETH:    ${formatAmount(ethBalance, 18, 'ETH')}`)

    if (args.all) {
        // Show all verified tokens
        console.log('')
        for (const [symbol, address] of Object.entries(VERIFIED_TOKENS)) {
            if (symbol === 'ETH') continue
            try {
                const { balance, decimals } = await getTokenBalance(provider, safeAddress, address)
                if (balance > 0n) {
                    console.log(`${symbol.padEnd(8)} ${formatAmount(balance, decimals, symbol)}`)
                }
            } catch {
                // Token might not exist or have issues
            }
        }
    } else if (args.token) {
        // Show specific token
        const symbol = args.token.toUpperCase().replace(/^\$/, '')
        let address = VERIFIED_TOKENS[symbol]

        if (!address) {
            if (args.token.startsWith('0x') && args.token.length === 42) {
                address = args.token
            } else {
                console.error(`\nToken "${args.token}" not found. Use address or one of:`)
                console.error(Object.keys(VERIFIED_TOKENS).join(', '))
                process.exit(1)
            }
        }

        try {
            const { symbol: tokenSymbol, balance, decimals } = await getTokenBalance(provider, safeAddress, address)
            console.log(`${tokenSymbol}:    ${formatAmount(balance, decimals, tokenSymbol)}`)
        } catch (error) {
            console.error(`\nFailed to get token balance: ${error.message}`)
            process.exit(1)
        }
    }

    console.log('')
}

main().catch(error => {
    console.error(`\n❌ Error: ${error.message}`)
    process.exit(1)
})
