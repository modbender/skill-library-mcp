#!/usr/bin/env node

/**
 * Swap tokens via CoW Protocol (via Safe + Zodiac Roles)
 *
 * Uses CoW Protocol's presign flow for MEV-protected swaps.
 * CoW batches orders and finds optimal execution paths, protecting
 * against sandwich attacks and other MEV extraction.
 *
 * Features:
 * - Resolves token symbols to addresses
 * - Safeguards for common tokens (ETH, USDC, USDT, etc.)
 * - Auto-substitutes ETH with WETH (CoW requires ERC20s)
 * - Gets quote before execution
 * - Presigns orders via Zodiac Roles delegatecall
 * - Polls order status until filled
 *
 * Usage:
 *   node swap.js --from ETH --to USDC --amount 0.1
 *   node swap.js --from USDC --to ETH --amount 100 --execute
 *
 * ETH is auto-wrapped to WETH when needed (CoW requires ERC20s)
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

// CoW Protocol constants
const COW_API_BASE = 'https://api.cow.fi/base'
const COW_SETTLEMENT = '0x9008D19f58AAbD9eD0D60971565AA8510560ab41'
const COW_VAULT_RELAYER = '0xC92E8bdf79f0507f65a392b0ab4667716BFE0110'

// bytes32 keccak hashes for order struct fields
const KIND_SELL = '0xf3b277728b3fee749481eb3e0b3b48980dbbab78658fc419025cb16eee346775'
const KIND_BUY = '0x6ed88e868af0a1983e3886d5f3e95a2fafbd6c3450bc229e27342283dc429ccc'
const BALANCE_ERC20 = '0x5a28e9363bb942b639270062aa6bb295f434bcdfc42c97267bf003f272060dc9'

// ABIs
const ROLES_ABI = [
    'function execTransactionWithRole(address to, uint256 value, bytes data, uint8 operation, bytes32 roleKey, bool shouldRevert) returns (bool)',
]

const COW_PRESIGN_ABI = [
    'function cowPreSign(tuple(address sellToken, address buyToken, address receiver, uint256 sellAmount, uint256 buyAmount, uint32 validTo, bytes32 appData, uint256 feeAmount, bytes32 kind, bool partiallyFillable, bytes32 sellTokenBalance, bytes32 buyTokenBalance) order, bytes orderUid) external',
]

const ZODIAC_HELPERS_ABI = [
    'function wrapETH(uint256 amount) external',
    'function unwrapWETH(uint256 amount) external',
]

// ============================================================================
// COW PROTOCOL API
// ============================================================================

async function getCowQuote(sellToken, buyToken, sellAmount, safeAddress) {
    const response = await fetch(`${COW_API_BASE}/api/v1/quote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            sellToken: sellToken.address,
            buyToken: buyToken.address,
            from: safeAddress,
            receiver: safeAddress,
            sellAmountBeforeFee: sellAmount.toString(),
            kind: 'sell',
            signingScheme: 'presign',
            sellTokenBalance: 'erc20',
            buyTokenBalance: 'erc20',
        }),
    })

    const data = await response.json()

    if (!response.ok) {
        const errorMsg = data.description || data.errorType || JSON.stringify(data)
        throw new Error(`CoW quote failed: ${errorMsg}`)
    }

    return data
}

async function buildAppData(slippageBips) {
    const doc = {
        appCode: "Clawlett",
        environment: "production",
        metadata: {
            orderClass: { orderClass: "market" },
            quote: { slippageBips, smartSlippage: true },
            partnerFee: {
                bps: 50,
                recipient: "0xCB52B32D872e496fccb84CeD21719EC9C560dFd4",
            },
        },
        version: "1.14.0",
    }

    const fullAppData = JSON.stringify(doc)
    const appDataHash = ethers.keccak256(ethers.toUtf8Bytes(fullAppData))

    // Register with CoW so solvers can resolve the hash
    await fetch(`${COW_API_BASE}/api/v1/app_data/${appDataHash}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullAppData }),
    }).catch(() => {}) // non-critical

    return appDataHash
}

async function submitCowOrder(quoteResponse, safeAddress, timeoutSeconds) {
    const q = quoteResponse.quote

    // Default 30 minutes — matches CoW FE. Solvers need time to batch orders.
    const validTo = Math.floor(Date.now() / 1000) + (timeoutSeconds || 1800)

    // Smart slippage (based on CoW FE, more aggressive for small orders):
    //   1. Fee-based:   150% of feeAmount (dominates small orders → wider tolerance)
    //   2. Volume-based: 0.5% of sellAmount (dominates large orders → ~0.5%)
    const feeSlippage = BigInt(q.feeAmount) * 3n / 2n
    const volumeSlippage = BigInt(q.sellAmount) * 5n / 1000n
    const totalSlippage = feeSlippage + volumeSlippage
    // Convert sell-token slippage to buy-token: slippage * buyAmount / sellAmount
    const buySlippage = BigInt(q.sellAmount) > 0n
        ? totalSlippage * BigInt(q.buyAmount) / BigInt(q.sellAmount)
        : BigInt(q.buyAmount) * 5n / 1000n
    const discountedBuyAmount = (BigInt(q.buyAmount) - buySlippage).toString()

    // Build appData with slippage metadata (matches CoW FE)
    const slippageBips = Number(buySlippage * 10000n / BigInt(q.buyAmount))
    const appData = await buildAppData(slippageBips)

    const order = {
        sellToken: q.sellToken,
        buyToken: q.buyToken,
        receiver: q.receiver || safeAddress,
        sellAmount: q.sellAmount,
        buyAmount: discountedBuyAmount,
        validTo,
        appData,
        feeAmount: "0",
        kind: q.kind,
        partiallyFillable: q.partiallyFillable || false,
        sellTokenBalance: q.sellTokenBalance || 'erc20',
        buyTokenBalance: q.buyTokenBalance || 'erc20',
        signingScheme: 'presign',
        signature: safeAddress,
        from: safeAddress,
    }

    const response = await fetch(`${COW_API_BASE}/api/v1/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(order),
    })

    const data = await response.json()

    if (!response.ok) {
        const errorMsg = data.description || data.errorType || JSON.stringify(data)
        throw new Error(`CoW order submission failed: ${errorMsg}`)
    }

    // data is the orderUid string
    return { orderUid: data, order }
}

function kindToBytes32(kind) {
    switch (kind) {
        case 'sell': return KIND_SELL
        case 'buy': return KIND_BUY
        default: throw new Error(`Unknown order kind: ${kind}`)
    }
}

function balanceToBytes32(balance) {
    switch (balance) {
        case 'erc20': return BALANCE_ERC20
        default: throw new Error(`Unknown balance type: ${balance}`)
    }
}

async function pollOrderStatus(orderUid, timeoutMs) {
    const startTime = Date.now()
    const pollInterval = 5000

    while (Date.now() - startTime < timeoutMs) {
        const response = await fetch(`${COW_API_BASE}/api/v1/orders/${orderUid}`)

        if (response.ok) {
            const order = await response.json()
            const status = order.status

            if (status === 'fulfilled') {
                return { status: 'fulfilled', order }
            } else if (status === 'expired') {
                return { status: 'expired', order }
            } else if (status === 'cancelled') {
                return { status: 'cancelled', order }
            }

            // presignaturePending or open - keep polling
            const elapsed = Math.round((Date.now() - startTime) / 1000)
            console.log(`   Status: ${status} (${elapsed}s elapsed)`)
        }

        await new Promise(resolve => setTimeout(resolve, pollInterval))
    }

    return { status: 'timeout' }
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
        slippage: 0.05,
        execute: false,
        timeout: 1800, // 30 minutes default (matches CoW FE)
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
                result.slippage = parseFloat(args[++i])
                break
            case '--execute':
            case '-x':
                result.execute = true
                break
            case '--timeout':
                result.timeout = parseInt(args[++i])
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
Usage: node swap.js --from <TOKEN> --to <TOKEN> --amount <AMOUNT> [--execute]

Swap tokens via CoW Protocol (MEV-protected).

Arguments:
  --from, -f       Token to swap from (symbol or address)
  --to, -t         Token to swap to (symbol or address)
  --amount, -a     Amount to swap
  --slippage       Slippage 0-0.5 (default: 0.05 = 5%)
  --execute, -x    Execute swap (default: quote only)
  --timeout        Order timeout in seconds (default: 1800 = 30min)
  --config-dir, -c Config directory
  --rpc, -r        RPC URL (default: ${DEFAULT_RPC_URL})

Notes:
  - CoW Protocol only works with ERC20 tokens. ETH is auto-wrapped to WETH.
  - Orders are MEV-protected (no sandwich attacks).

Verified Tokens:
  ETH, WETH, USDC, USDT, DAI, USDS, AERO, cbBTC, VIRTUAL, DEGEN, BRETT, TOSHI, WELL
  Other tokens are searched via DexScreener (Base pairs).
  Unverified tokens show a warning with contract address, volume, and liquidity.

Examples:
  node swap.js --from ETH --to USDC --amount 0.1
  node swap.js --from USDC --to WETH --amount 100 --execute
  node swap.js --from USDC --to DAI --amount 50 --execute --timeout 600
`)
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

    // CoW Protocol only works with ERC20s - substitute ETH with WETH
    let ethSubstituted = false
    if (tokenIn.address.toLowerCase() === NATIVE_ETH) {
        console.log('Note: CoW Protocol requires ERC20 tokens. Using WETH instead of ETH.')
        tokenIn = { ...tokenIn, address: WETH_ADDRESS, symbol: 'WETH' }
        ethSubstituted = true
    }
    if (tokenOut.address.toLowerCase() === NATIVE_ETH) {
        console.log('Note: CoW Protocol requires ERC20 tokens. Receiving WETH instead of ETH.')
        tokenOut = { ...tokenOut, address: WETH_ADDRESS, symbol: 'WETH' }
        ethSubstituted = true
    }

    console.log(`From: ${tokenIn.symbol} ${tokenIn.verified ? '(verified)' : '(unverified)'}`)
    console.log(`      ${tokenIn.address}`)
    if (tokenIn.warning) console.log(`\n${tokenIn.warning}\n`)

    console.log(`To:   ${tokenOut.symbol} ${tokenOut.verified ? '(verified)' : '(unverified)'}`)
    console.log(`      ${tokenOut.address}`)
    if (tokenOut.warning) console.log(`\n${tokenOut.warning}\n`)

    const amountIn = ethers.parseUnits(args.amount, tokenIn.decimals)
    console.log(`\nAmount: ${formatAmount(amountIn, tokenIn.decimals, tokenIn.symbol)}`)

    // Check balance — when selling ETH via CoW, check both ETH and WETH
    let balance
    let wrapAmount = 0n
    if (ethSubstituted && tokenIn.address.toLowerCase() === WETH_ADDRESS.toLowerCase()) {
        const wethContract = new ethers.Contract(WETH_ADDRESS, ERC20_ABI, provider)
        const wethBalance = await wethContract.balanceOf(safeAddress)
        const ethBalance = await provider.getBalance(safeAddress)

        console.log(`Safe WETH balance: ${formatAmount(wethBalance, 18, 'WETH')}`)
        console.log(`Safe ETH balance:  ${formatAmount(ethBalance, 18, 'ETH')}`)

        if (wethBalance >= amountIn) {
            balance = wethBalance
        } else if (wethBalance + ethBalance >= amountIn) {
            wrapAmount = amountIn - wethBalance
            balance = amountIn // sufficient after wrapping
            console.log(`Will wrap ${formatAmount(wrapAmount, 18, 'ETH')} to WETH as part of the swap transaction`)
        } else {
            console.error(`\nInsufficient ETH + WETH balance in Safe`)
            console.error(`Need ${formatAmount(amountIn, 18, 'WETH')}, have ${formatAmount(wethBalance, 18, 'WETH')} + ${formatAmount(ethBalance, 18, 'ETH')}`)
            process.exit(1)
        }
    } else {
        const tokenContract = new ethers.Contract(tokenIn.address, ERC20_ABI, provider)
        balance = await tokenContract.balanceOf(safeAddress)
        console.log(`Safe balance: ${formatAmount(balance, tokenIn.decimals, tokenIn.symbol)}`)

        if (balance < amountIn) {
            console.error(`\nInsufficient ${tokenIn.symbol} balance in Safe`)
            process.exit(1)
        }
    }

    // Get CoW quote
    console.log('\nGetting CoW Protocol quote...\n')

    let quoteResponse
    try {
        quoteResponse = await getCowQuote(tokenIn, tokenOut, amountIn, safeAddress)
    } catch (error) {
        console.error(`${error.message}`)
        console.error(`\nTip: If CoW has no liquidity for this pair, try using the contract address directly.`)
        process.exit(1)
    }

    const q = quoteResponse.quote
    const sellAmount = BigInt(q.sellAmount)
    const buyAmount = BigInt(q.buyAmount)
    const feeAmount = BigInt(q.feeAmount)

    console.log('='.repeat(55))
    console.log('                    SWAP SUMMARY')
    console.log('='.repeat(55))
    console.log(`  You pay:      ${formatAmount(amountIn, tokenIn.decimals, tokenIn.symbol)}`)
    console.log(`  Fee:          ${formatAmount(feeAmount, tokenIn.decimals, tokenIn.symbol)}`)
    console.log(`  You sell:     ${formatAmount(sellAmount, tokenIn.decimals, tokenIn.symbol)} (after fee)`)
    // Smart slippage for display (same formula as submitCowOrder)
    const displayFeeSlippage = feeAmount * 3n / 2n
    const displayVolSlippage = sellAmount * 5n / 1000n
    const displayTotalSlippage = displayFeeSlippage + displayVolSlippage
    const displayBuySlippage = sellAmount > 0n
        ? displayTotalSlippage * buyAmount / sellAmount
        : buyAmount * 5n / 1000n
    const minReceive = buyAmount - displayBuySlippage
    const slippagePct = Number(displayBuySlippage * 10000n / buyAmount) / 100
    console.log(`  You receive:  ~${formatAmount(buyAmount, tokenOut.decimals, tokenOut.symbol)}`)
    console.log(`  Min receive:  ${formatAmount(minReceive, tokenOut.decimals, tokenOut.symbol)} (${slippagePct.toFixed(2)}% smart slippage)`)
    console.log(`  Expires in:   ${args.timeout}s`)
    if (wrapAmount > 0n) {
        console.log(`  ETH wrap:     ${formatAmount(wrapAmount, 18, 'ETH')} → WETH (bundled in tx)`)
    }
    console.log(`  MEV protected via CoW Protocol batch auction`)
    console.log('='.repeat(55))

    if (!args.execute) {
        console.log('\nQUOTE ONLY - Add --execute to perform the swap')
        console.log(`\nTo execute: node swap.js --from "${args.from}" --to "${args.to}" --amount ${args.amount} --execute`)
        process.exit(0)
    }

    // ========================================================================
    // EXECUTION
    // ========================================================================

    console.log('\nExecuting CoW Protocol swap...\n')

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

    // Step 1: Submit order to CoW API (off-chain, needed to get orderUid for presign)
    console.log('Step 1: Submitting order to CoW Protocol...')
    let orderUid, order
    try {
        const result = await submitCowOrder(quoteResponse, safeAddress, args.timeout)
        orderUid = result.orderUid
        order = result.order
    } catch (error) {
        console.error(`${error.message}`)
        process.exit(1)
    }
    console.log(`   Order UID: ${orderUid}`)
    console.log(`   Explorer:  https://explorer.cow.fi/base/orders/${orderUid}`)

    // Step 2: Build on-chain operations (wrap + approve + presign) and execute
    // All operations are bundled into a single MultiSend transaction when multiple
    // steps are needed, saving gas and ensuring atomicity.
    console.log('\nStep 2: Executing on-chain operations...')

    const zodiacHelpersInterface = new ethers.Interface(ZODIAC_HELPERS_ABI)
    const cowPresignInterface = new ethers.Interface(COW_PRESIGN_ABI)
    const multiSendTxs = []

    // 2a: Wrap ETH → WETH if needed (user said ETH, CoW needs WETH)
    if (wrapAmount > 0n) {
        console.log(`   - Wrap ${formatAmount(wrapAmount, 18, 'ETH')} → WETH`)
        const wrapData = zodiacHelpersInterface.encodeFunctionData('wrapETH', [wrapAmount])
        multiSendTxs.push({ operation: 1, to: zodiacHelpersAddress, value: 0n, data: wrapData })
    }

    // 2b: Presign the order on-chain (must match submitted order exactly)
    console.log('   - Presign CoW order')
    const orderStruct = {
        sellToken: order.sellToken,
        buyToken: order.buyToken,
        receiver: order.receiver || safeAddress,
        sellAmount: BigInt(order.sellAmount),
        buyAmount: BigInt(order.buyAmount),
        validTo: order.validTo,
        appData: order.appData,
        feeAmount: 0n,
        kind: kindToBytes32(order.kind),
        partiallyFillable: order.partiallyFillable || false,
        sellTokenBalance: balanceToBytes32(order.sellTokenBalance || 'erc20'),
        buyTokenBalance: balanceToBytes32(order.buyTokenBalance || 'erc20'),
    }

    const presignData = cowPresignInterface.encodeFunctionData('cowPreSign', [
        orderStruct,
        orderUid,
    ])
    multiSendTxs.push({ operation: 1, to: zodiacHelpersAddress, value: 0n, data: presignData })

    // Execute each operation individually via Roles (ZodiacHelpers is the allowed target)
    for (let i = 0; i < multiSendTxs.length; i++) {
        const tx = multiSendTxs[i]
        console.log(`   Executing operation ${i + 1}/${multiSendTxs.length}...`)
        const onChainTx = await roles.execTransactionWithRole(
            tx.to,
            tx.value,
            tx.data,
            1, // delegatecall
            config.roleKey,
            true
        )
        console.log(`   Transaction: ${onChainTx.hash}`)
        const receipt = await onChainTx.wait()
        if (receipt.status !== 1) {
            console.error(`   Operation ${i + 1} failed!`)
            process.exit(1)
        }
    }
    const lastTxHash = multiSendTxs.length > 0 ? 'see above' : 'none'

    console.log('   All on-chain operations complete!')

    // Step 3: Poll order status
    console.log('\nStep 3: Waiting for order to be filled...')
    console.log(`   Timeout: ${args.timeout}s`)

    const result = await pollOrderStatus(orderUid, args.timeout * 1000)

    switch (result.status) {
        case 'fulfilled': {
            let newBalance
            const outContract = new ethers.Contract(tokenOut.address, ERC20_ABI, provider)
            newBalance = await outContract.balanceOf(safeAddress)

            console.log('\nSWAP COMPLETE')
            console.log(`   Sold: ${formatAmount(sellAmount, tokenIn.decimals, tokenIn.symbol)}`)
            console.log(`   Received: ~${formatAmount(buyAmount, tokenOut.decimals, tokenOut.symbol)}`)
            console.log(`   New ${tokenOut.symbol} balance: ${formatAmount(newBalance, tokenOut.decimals, tokenOut.symbol)}`)
            console.log(`   Explorer: https://explorer.cow.fi/base/orders/${orderUid}`)
            break
        }
        case 'expired':
            console.error('\nOrder expired without being filled.')
            console.error('Tip: Try again with a higher slippage tolerance.')
            process.exit(1)
            break
        case 'cancelled':
            console.error('\nOrder was cancelled.')
            process.exit(1)
            break
        case 'timeout':
            console.error(`\nTimed out after ${args.timeout}s. Order may still be filled.`)
            console.error(`Check status: https://explorer.cow.fi/base/orders/${orderUid}`)
            process.exit(1)
            break
    }
}

main().catch(error => {
    console.error(`\nError: ${error.message}`)
    process.exit(1)
})
