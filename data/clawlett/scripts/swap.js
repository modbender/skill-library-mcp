#!/usr/bin/env node

/**
 * Swap tokens via KyberSwap Aggregator (via Safe + Zodiac Roles)
 *
 * Uses KyberSwap's aggregator API to find optimal swap routes across
 * multiple DEXs on Base. Supports all ERC20 tokens with liquidity.
 *
 * Features:
 * - Resolves token symbols to addresses
 * - Safeguards for common tokens (ETH, USDC, USDT, etc.)
 * - Gets optimal routes across multiple DEXs
 * - 0.5% partner fee (same as CoW Protocol)
 * - Executes swaps via Zodiac Roles delegatecall
 *
 * Usage:
 *   node kyber.js --from ETH --to USDC --amount 0.1
 *   node kyber.js --from USDC --to ETH --amount 100 --execute
 *
 * ETH is handled natively by KyberSwap (no wrapping needed).
 */

import { ethers } from 'ethers'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { VERIFIED_TOKENS, ERC20_ABI, resolveToken } from './tokens.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const DEFAULT_RPC_URL = 'https://mainnet.base.org'

// Contracts
const WETH_ADDRESS = '0x4200000000000000000000000000000000000006'
const NATIVE_ETH = '0x0000000000000000000000000000000000000000'
const KYBER_NATIVE_TOKEN = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

// KyberSwap API constants
const KYBER_API_BASE = 'https://aggregator-api.kyberswap.com'
const KYBER_CHAIN = 'base'
const KYBER_CLIENT_ID = 'clawlett'

// Partner fee (0.5% = 50 bps)
const FEE_BPS = 50
const FEE_RECEIVER = '0xCB52B32D872e496fccb84CeD21719EC9C560dFd4'

// ABIs
const ROLES_ABI = [
    'function execTransactionWithRole(address to, uint256 value, bytes data, uint8 operation, bytes32 roleKey, bool shouldRevert) returns (bool)',
]

const ZODIAC_HELPERS_ABI = [
    'function wrapETH(uint256 amount) external',
    'function unwrapWETH(uint256 amount) external',
    'function kyberSwap(address tokenIn, address tokenOut, uint256 amountIn, uint256 minAmountOut, bytes swapData, uint256 ethValue) external',
]

// ============================================================================
// KYBERSWAP API
// ============================================================================

async function getKyberRoute(tokenIn, tokenOut, amountIn, safeAddress) {
    const params = new URLSearchParams({
        tokenIn: tokenIn.kyberAddress,
        tokenOut: tokenOut.kyberAddress,
        amountIn: amountIn.toString(),
        // Partner fee parameters (0.1%)
        feeAmount: String(FEE_BPS),
        chargeFeeBy: 'currency_in',
        isInBps: 'true',
        feeReceiver: FEE_RECEIVER,
    })

    const url = `${KYBER_API_BASE}/${KYBER_CHAIN}/api/v1/routes?${params}`

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'X-Client-Id': KYBER_CLIENT_ID,
            'Accept': 'application/json',
        },
    })

    const data = await response.json()

    if (!response.ok || data.code !== 0) {
        const errorMsg = data.message || data.description || JSON.stringify(data)
        throw new Error(`KyberSwap route failed: ${errorMsg}`)
    }

    if (!data.data || !data.data.routeSummary) {
        throw new Error('KyberSwap: No route found for this pair')
    }

    return data.data
}

async function buildKyberSwap(routeData, safeAddress, slippageTolerance) {
    const url = `${KYBER_API_BASE}/${KYBER_CHAIN}/api/v1/route/build`

    const requestBody = {
        routeSummary: routeData.routeSummary,
        sender: safeAddress,
        recipient: safeAddress,
        slippageTolerance: slippageTolerance, // in bps, e.g., 50 = 0.5%
    }

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-Client-Id': KYBER_CLIENT_ID,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify(requestBody),
    })

    const data = await response.json()

    if (!response.ok || data.code !== 0) {
        const errorMsg = data.message || data.description || JSON.stringify(data)
        throw new Error(`KyberSwap build failed: ${errorMsg}`)
    }

    return data.data
}

// ============================================================================
// HELPERS
// ============================================================================

function formatAmount(amount, decimals, symbol) {
    const formatted = ethers.formatUnits(amount, decimals)
    const num = parseFloat(formatted)
    if (num < 0.01) return `${formatted} ${symbol}`
    return `${num.toLocaleString(undefined, { maximumFractionDigits: 6 })} ${symbol}`
}

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
        from: null,
        to: null,
        amount: null,
        configDir: process.env.WALLET_CONFIG_DIR || path.join(__dirname, '..', 'config'),
        rpc: process.env.BASE_RPC_URL || DEFAULT_RPC_URL,
        slippage: 50, // 0.5% default in bps
        execute: false,
    }

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--from':
            case '-f':
                result.from = args[++i]
                break
            case '--to':
            case '-t':
                result.to = args[++i]
                break
            case '--amount':
            case '-a':
                result.amount = args[++i]
                break
            case '--slippage':
                // Accept slippage as percentage (e.g., 0.5 for 0.5%) or bps (e.g., 50)
                const slipVal = parseFloat(args[++i])
                result.slippage = slipVal < 1 ? Math.round(slipVal * 100) : Math.round(slipVal)
                break
            case '--execute':
            case '-x':
                result.execute = true
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
Usage: node kyber.js --from <TOKEN> --to <TOKEN> --amount <AMOUNT> [--execute]

Swap tokens via KyberSwap Aggregator (optimal routes across DEXs).

Arguments:
  --from, -f       Token to swap from (symbol or address)
  --to, -t         Token to swap to (symbol or address)
  --amount, -a     Amount to swap
  --slippage       Slippage in % or bps (default: 0.5% = 50 bps)
  --execute, -x    Execute swap (default: quote only)
  --config-dir, -c Config directory
  --rpc, -r        RPC URL (default: ${DEFAULT_RPC_URL})

Notes:
  - KyberSwap aggregates liquidity from multiple DEXs for optimal rates.
  - Native ETH is supported directly (no wrapping needed).
  - A 0.5% partner fee is applied (same as CoW Protocol).

Verified Tokens:
  ETH, WETH, USDC, USDT, DAI, USDS, AERO, cbBTC, VIRTUAL, DEGEN, BRETT, TOSHI, WELL
  Other tokens are searched via DexScreener (Base pairs).
  Unverified tokens show a warning with contract address, volume, and liquidity.

Examples:
  node kyber.js --from ETH --to USDC --amount 0.1
  node kyber.js --from USDC --to WETH --amount 100 --execute
  node kyber.js --from USDC --to DAI --amount 50 --execute --slippage 1
`)
}

// Convert token address to KyberSwap format
function toKyberAddress(address) {
    if (address.toLowerCase() === NATIVE_ETH) {
        return KYBER_NATIVE_TOKEN
    }
    return address
}

// ============================================================================
// MAIN
// ============================================================================

async function main() {
    const args = parseArgs()

    if (!args.from || !args.to || !args.amount) {
        console.error('Error: --from, --to, and --amount are required')
        printHelp()
        process.exit(1)
    }

    let config
    try {
        config = loadConfig(args.configDir)
    } catch (error) {
        console.error(`Error: ${error.message}`)
        process.exit(1)
    }

    const provider = new ethers.JsonRpcProvider(args.rpc)
    const safeAddress = config.safe

    console.log('\nResolving tokens...\n')

    let tokenIn, tokenOut
    try {
        tokenIn = await resolveToken(args.from, provider)
    } catch (error) {
        console.error(`\n${error.message}`)
        process.exit(1)
    }

    try {
        tokenOut = await resolveToken(args.to, provider)
    } catch (error) {
        console.error(`\n${error.message}`)
        process.exit(1)
    }

    // Add KyberSwap-specific address format
    tokenIn.kyberAddress = toKyberAddress(tokenIn.address)
    tokenOut.kyberAddress = toKyberAddress(tokenOut.address)

    const isNativeIn = tokenIn.address.toLowerCase() === NATIVE_ETH
    const isNativeOut = tokenOut.address.toLowerCase() === NATIVE_ETH

    console.log(`From: ${tokenIn.symbol} ${tokenIn.verified ? '(verified)' : '(unverified)'}`)
    console.log(`      ${tokenIn.address}`)
    if (tokenIn.warning) console.log(`\n${tokenIn.warning}\n`)

    console.log(`To:   ${tokenOut.symbol} ${tokenOut.verified ? '(verified)' : '(unverified)'}`)
    console.log(`      ${tokenOut.address}`)
    if (tokenOut.warning) console.log(`\n${tokenOut.warning}\n`)

    const amountIn = ethers.parseUnits(args.amount, tokenIn.decimals)
    console.log(`\nAmount: ${formatAmount(amountIn, tokenIn.decimals, tokenIn.symbol)}`)

    // Check balance
    let balance
    if (isNativeIn) {
        balance = await provider.getBalance(safeAddress)
        console.log(`Safe ETH balance: ${formatAmount(balance, 18, 'ETH')}`)
    } else {
        const tokenContract = new ethers.Contract(tokenIn.address, ERC20_ABI, provider)
        balance = await tokenContract.balanceOf(safeAddress)
        console.log(`Safe balance: ${formatAmount(balance, tokenIn.decimals, tokenIn.symbol)}`)
    }

    if (balance < amountIn) {
        console.error(`\nInsufficient ${tokenIn.symbol} balance in Safe`)
        process.exit(1)
    }

    // Get KyberSwap route
    console.log('\nGetting KyberSwap route...\n')

    let routeData
    try {
        routeData = await getKyberRoute(tokenIn, tokenOut, amountIn, safeAddress)
    } catch (error) {
        console.error(`${error.message}`)
        console.error(`\nTip: If KyberSwap has no liquidity for this pair, try CoW Protocol instead.`)
        process.exit(1)
    }

    const routeSummary = routeData.routeSummary
    const amountOut = BigInt(routeSummary.amountOut)
    const gasEstimate = routeSummary.gas || '0'
    const gasPriceGwei = routeSummary.gasPrice ? (Number(routeSummary.gasPrice) / 1e9).toFixed(2) : 'N/A'

    // Calculate fee amount (0.5% of input)
    const feeAmount = amountIn * BigInt(FEE_BPS) / 10000n

    // Calculate minimum output with slippage
    const minAmountOut = amountOut * BigInt(10000 - args.slippage) / 10000n
    const slippagePct = args.slippage / 100

    console.log('='.repeat(55))
    console.log('                    SWAP SUMMARY')
    console.log('='.repeat(55))
    console.log(`  You pay:      ${formatAmount(amountIn, tokenIn.decimals, tokenIn.symbol)}`)
    console.log(`  You receive:  ~${formatAmount(amountOut, tokenOut.decimals, tokenOut.symbol)}`)
    console.log(`  Min receive:  ${formatAmount(minAmountOut, tokenOut.decimals, tokenOut.symbol)} (${slippagePct}% slippage)`)
    console.log(`  Gas estimate: ${gasEstimate} (${gasPriceGwei} gwei)`)
    console.log(`  Router:       ${routeData.routerAddress}`)
    console.log(`  Route:        ${routeSummary.route?.length || 1} hop(s) via KyberSwap Aggregator`)
    console.log('='.repeat(55))

    if (!args.execute) {
        console.log('\nQUOTE ONLY - Add --execute to perform the swap')
        console.log(`\nTo execute: node kyber.js --from "${args.from}" --to "${args.to}" --amount ${args.amount} --execute`)
        process.exit(0)
    }

    // ========================================================================
    // EXECUTION
    // ========================================================================

    console.log('\nExecuting KyberSwap...\n')

    const agentPkPath = path.join(args.configDir, 'agent.pk')
    if (!fs.existsSync(agentPkPath)) {
        console.error('Error: Agent private key not found')
        process.exit(1)
    }
    let privateKey = fs.readFileSync(agentPkPath, 'utf8').trim()
    if (!privateKey.startsWith('0x')) privateKey = '0x' + privateKey

    const wallet = new ethers.Wallet(privateKey, provider)
    const roles = new ethers.Contract(config.roles, ROLES_ABI, wallet)

    const zodiacHelpersAddress = config.contracts?.ZodiacHelpers
    if (!zodiacHelpersAddress) {
        console.error('Error: ZodiacHelpers address not found in config. Re-run initialize.js.')
        process.exit(1)
    }

    // Step 1: Build swap transaction from KyberSwap API
    console.log('Step 1: Building swap transaction...')
    let buildData
    try {
        buildData = await buildKyberSwap(routeData, safeAddress, args.slippage)
    } catch (error) {
        console.error(`${error.message}`)
        process.exit(1)
    }
    console.log(`   Router: ${buildData.routerAddress}`)
    console.log(`   Data length: ${buildData.data.length} bytes`)

    // Step 2: Execute via ZodiacHelpers.kyberSwap
    console.log('\nStep 2: Executing swap via ZodiacHelpers...')

    const zodiacHelpersInterface = new ethers.Interface(ZODIAC_HELPERS_ABI)

    // For native ETH swaps, we need to pass the ethValue
    const ethValue = isNativeIn ? amountIn : 0n

    // Encode the kyberSwap call
    const swapData = zodiacHelpersInterface.encodeFunctionData('kyberSwap', [
        isNativeIn ? NATIVE_ETH : tokenIn.address,
        isNativeOut ? NATIVE_ETH : tokenOut.address,
        amountIn,
        minAmountOut,
        buildData.data,
        ethValue,
    ])

    // Execute via Roles (delegatecall to ZodiacHelpers)
    console.log('   Executing on-chain...')
    const tx = await roles.execTransactionWithRole(
        zodiacHelpersAddress,
        0n, // value is 0 - ethValue is passed in swapData
        swapData,
        1, // delegatecall
        config.roleKey,
        true
    )
    console.log(`   Transaction: ${tx.hash}`)

    const receipt = await tx.wait()
    if (receipt.status !== 1) {
        console.error('Transaction failed!')
        process.exit(1)
    }

    // Step 3: Show results
    console.log('\nSWAP COMPLETE')
    console.log(`   Sold: ${formatAmount(amountIn, tokenIn.decimals, tokenIn.symbol)}`)
    console.log(`   Received: ~${formatAmount(amountOut, tokenOut.decimals, tokenOut.symbol)}`)

    // Get new balance
    if (isNativeOut) {
        const newBalance = await provider.getBalance(safeAddress)
        console.log(`   New ETH balance: ${formatAmount(newBalance, 18, 'ETH')}`)
    } else {
        const outContract = new ethers.Contract(tokenOut.address, ERC20_ABI, provider)
        const newBalance = await outContract.balanceOf(safeAddress)
        console.log(`   New ${tokenOut.symbol} balance: ${formatAmount(newBalance, tokenOut.decimals, tokenOut.symbol)}`)
    }

    console.log(`   Tx: https://basescan.org/tx/${receipt.hash}`)
}

main().catch(error => {
    console.error(`\nError: ${error.message}`)
    process.exit(1)
})
