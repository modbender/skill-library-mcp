/**
 * Shared token resolution module
 *
 * Provides verified token lists, symbol resolution, and DexScreener search
 * fallback for tokens not in the hardcoded list.
 */

import { ethers } from 'ethers'

// ============================================================================
// VERIFIED TOKENS - Safeguard against scam tokens
// ============================================================================
const VERIFIED_TOKENS = {
    'ETH': '0x0000000000000000000000000000000000000000',  // Native ETH
    'WETH': '0x4200000000000000000000000000000000000006',
    'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    'USDT': '0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2',
    'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
    'USDS': '0x820C137fa70C8691f0e44Dc420a5e53c168921Dc',
    'AERO': '0x940181a94A35A4569E4529A3CDfB74e38FD98631',
    'cbBTC': '0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf',
    'VIRTUAL': '0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b',
    'DEGEN': '0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed',
    'BRETT': '0x532f27101965dd16442E59d40670FaF5eBB142E4',
    'TOSHI': '0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4',
    'WELL': '0xA88594D404727625A9437C3f886C7643872296AE',
    'BID': '0xa1832f7f4e534ae557f9b5ab76de54b1873e498b',
}

const TOKEN_ALIASES = {
    'ETHEREUM': 'ETH',
    'ETHER': 'ETH',
    'USD COIN': 'USDC',
    'TETHER': 'USDT',
}

const PROTECTED_SYMBOLS = ['ETH', 'WETH', 'USDC', 'USDT', 'DAI', 'USDS', 'AERO', 'cbBTC', 'BID']

const NATIVE_ETH = '0x0000000000000000000000000000000000000000'

// ABIs
const ERC20_ABI = [
    'function symbol() view returns (string)',
    'function decimals() view returns (uint8)',
    'function balanceOf(address) view returns (uint256)',
    'function allowance(address, address) view returns (uint256)',
]

// ============================================================================
// TOKEN SEARCH - DexScreener fallback
// ============================================================================

async function searchToken(symbol) {
    const url = `https://api.dexscreener.com/latest/dex/search?q=${encodeURIComponent(symbol)}`
    const response = await fetch(url)
    if (!response.ok) return null

    const data = await response.json()
    if (!data.pairs || data.pairs.length === 0) return null

    // Filter to Base pairs only, then find exact symbol match on either token
    const basePairs = data.pairs.filter(p => p.chainId === 'base')
    if (basePairs.length === 0) return null

    // Find the token matching the symbol (could be baseToken or quoteToken)
    for (const pair of basePairs) {
        const match = [pair.baseToken, pair.quoteToken].find(
            t => t.symbol.toUpperCase() === symbol.toUpperCase()
        )
        if (match) {
            return {
                id: match.address,
                symbol: match.symbol,
                name: match.name,
                volumeUSD: pair.volume?.h24,
                liquidity: pair.liquidity?.usd,
                dex: pair.dexId,
            }
        }
    }

    return null
}

// ============================================================================
// TOKEN RESOLUTION
// ============================================================================

async function resolveToken(token, provider) {
    token = token.trim()

    if (token.startsWith('0x') && token.length === 42) {
        return resolveByAddress(token, provider)
    }

    const symbol = token.toUpperCase().replace(/^\$/, '')
    const aliasedSymbol = TOKEN_ALIASES[symbol] || symbol

    if (VERIFIED_TOKENS[aliasedSymbol]) {
        const address = VERIFIED_TOKENS[aliasedSymbol]

        // Native ETH doesn't have a contract
        if (address === NATIVE_ETH) {
            return { address, symbol: 'ETH', decimals: 18, verified: true }
        }

        const tokenContract = new ethers.Contract(address, ERC20_ABI, provider)
        const [onChainSymbol, decimals] = await Promise.all([
            tokenContract.symbol(),
            tokenContract.decimals(),
        ])
        return {
            address,
            symbol: onChainSymbol,
            decimals: Number(decimals),
            verified: true,
        }
    }

    if (PROTECTED_SYMBOLS.includes(aliasedSymbol)) {
        throw new Error(
            `SECURITY: "${symbol}" is a protected token but no verified address found.\n` +
            `This could be a scam token. Use contract address directly if intended.`
        )
    }

    // Fallback: search DexScreener for Base token
    const searchResult = await searchToken(aliasedSymbol)

    if (searchResult) {
        const address = ethers.getAddress(searchResult.id)
        const tokenContract = new ethers.Contract(address, ERC20_ABI, provider)
        const [onChainSymbol, decimals] = await Promise.all([
            tokenContract.symbol(),
            tokenContract.decimals(),
        ])

        const volumeStr = searchResult.volumeUSD
            ? `$${Number(searchResult.volumeUSD).toLocaleString(undefined, { maximumFractionDigits: 0 })}`
            : 'unknown'
        const liqStr = searchResult.liquidity
            ? `$${Number(searchResult.liquidity).toLocaleString(undefined, { maximumFractionDigits: 0 })}`
            : 'unknown'

        return {
            address,
            symbol: onChainSymbol,
            decimals: Number(decimals),
            verified: false,
            name: searchResult.name,
            volumeUSD: searchResult.volumeUSD,
            liquidity: searchResult.liquidity,
            dex: searchResult.dex,
            warning:
                `UNVERIFIED TOKEN: ${onChainSymbol} (${address}) found on DexScreener.\n` +
                ` 24h volume: ${volumeStr} | Liquidity: ${liqStr} | DEX: ${searchResult.dex}\n` +
                ` This token is NOT in the verified list. Verify the contract address before proceeding.`,
        }
    }

    throw new Error(
        `Token "${symbol}" not found in verified list or DexScreener (Base).\n` +
        `Use contract address directly: --from 0x...`
    )
}

async function resolveByAddress(address, provider) {
    address = ethers.getAddress(address)

    const verifiedEntry = Object.entries(VERIFIED_TOKENS).find(
        ([, addr]) => addr.toLowerCase() === address.toLowerCase()
    )

    const tokenContract = new ethers.Contract(address, ERC20_ABI, provider)
    const [symbol, decimals] = await Promise.all([
        tokenContract.symbol(),
        tokenContract.decimals(),
    ])

    const result = {
        address,
        symbol,
        decimals: Number(decimals),
        verified: !!verifiedEntry,
    }

    if (!verifiedEntry && PROTECTED_SYMBOLS.includes(symbol.toUpperCase())) {
        result.warning =
            `WARNING: Token has symbol "${symbol}" but is NOT the verified ${symbol}.\n` +
            `Verified address: ${VERIFIED_TOKENS[symbol.toUpperCase()]}\n` +
            `You provided: ${address}\n` +
            `This could be a SCAM TOKEN.`
    }

    return result
}

export {
    VERIFIED_TOKENS,
    TOKEN_ALIASES,
    PROTECTED_SYMBOLS,
    ERC20_ABI,
    resolveToken,
    resolveByAddress,
    searchToken,
}
