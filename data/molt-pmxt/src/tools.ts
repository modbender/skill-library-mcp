import * as pmxt from "pmxtjs";
import { Exchange } from "pmxtjs"; // Import Exchange explicitly for type usage if needed, though we use dynamic discovery
import type { ToolResult } from "./types.js";

// Helper to manage exchange instances dynamically
const exchanges: Map<string, Exchange> = new Map();

// Initialize exchanges by discovering them from the pmxtjs exports
function initExchanges() {
    if (exchanges.size > 0) return;

    // Explicitly configure known exchanges with authentication
    if ((pmxt as any).Polymarket) {
        try {
            exchanges.set('polymarket', new (pmxt as any).Polymarket({
                privateKey: process.env.POLYMARKET_PRIVATE_KEY,
                proxyAddress: process.env.POLYMARKET_PROXY_ADDRESS,
                signatureType: 'gnosis-safe' // Default
            }));
        } catch (e) {
            console.warn('Failed to initialize Polymarket with auth:', e);
        }
    }

    if ((pmxt as any).Kalshi) {
        try {
            exchanges.set('kalshi', new (pmxt as any).Kalshi({
                apiKey: process.env.KALSHI_API_KEY,
                privateKey: process.env.KALSHI_PRIVATE_KEY
            }));
        } catch (e) {
            console.warn('Failed to initialize Kalshi with auth:', e);
        }
    }

    if ((pmxt as any).Limitless) {
        try {
            exchanges.set('limitless', new (pmxt as any).Limitless({
                apiKey: process.env.LIMITLESS_API_KEY,
                privateKey: process.env.LIMITLESS_PRIVATE_KEY
            }));
        } catch (e) {
            console.warn('Failed to initialize Limitless with auth:', e);
        }
    }

    const exportList = Object.keys(pmxt) as Array<keyof typeof pmxt>;
    // Try to find the Exchange class constructor from exports if needed, or use imported Exchange
    const ExchangeClass = (pmxt as any).Exchange || Exchange;

    // Dynamic discovery for any other exchanges
    for (const key of exportList) {
        const normalizedKey = key.toLowerCase();
        if (exchanges.has(normalizedKey)) continue;

        const ExportedItem = (pmxt as any)[key];

        // Check if it is a class that extends Exchange (and is not Exchange itself)
        // We use prototype check to confirm inheritance
        if (
            typeof ExportedItem === 'function' &&
            ExportedItem.prototype instanceof ExchangeClass &&
            ExportedItem !== ExchangeClass
        ) {
            try {
                const instance = new ExportedItem();
                exchanges.set(normalizedKey, instance);
                // console.log(`Loaded exchange: ${key}`);
            } catch (e) {
                console.warn(`Failed to initialize exchange adapter for ${key}:`, e);
            }
        }
    }
}

// Initialize on module load
initExchanges();

/**
 * Normalizes market data from various exchanges into a common format.
 * Includes specific logic for known exchanges and generic fallbacks for future ones.
 */
function normalizeMarket(m: any, exchangeName: string): any {
    const base = {
        exchange: exchangeName,
        title: m.title || m.question || m.event_ticker || m.name || "Unknown Market",
        description: m.description || m.subtitle || "",
        volume: m.volume || m.volume24h || m.volume_24h || 0,
        resolved: m.closed || m.status === 'closed' || m.resolved || false
    };

    // Specific overrides for ID and other fields where structure varies significantly
    if (exchangeName === 'polymarket') {
        return {
            ...base,
            id: m.yes?.metadata?.clobTokenId || m.marketId || m.id,
            // Polymarket 'volume' is often directly on the object or volume24h
        };
    }

    if (exchangeName === 'kalshi') {
        return {
            ...base,
            id: m.ticker || m.id || m.marketId,
            title: m.title || m.event_ticker, // Kalshi specific prefer event_ticker
            resolved: m.status === "closed"
        };
    }

    if (exchangeName === 'limitless') {
        return {
            ...base,
            id: m.id || m.marketId,
        };
    }

    // Generic fallback for ID
    return {
        ...base,
        id: m.id || m.marketId || m.ticker || m.slug
    };
}

/**
 * Unified search for markets across multiple prediction exchanges.
 * Normalizes results into a common format for the agent.
 */
export async function pmxt_search(query: string, exchange?: string): Promise<ToolResult<any[]>> {
    try {
        const results: any[] = [];
        const normalizedExchange = exchange ? exchange.toLowerCase() : null;

        const targets = normalizedExchange
            ? (exchanges.has(normalizedExchange) ? [normalizedExchange] : [])
            : Array.from(exchanges.keys());

        if (normalizedExchange && targets.length === 0) {
            return { success: false, error: `Unsupported exchange: ${exchange}` };
        }

        const promises = targets.map(async (key) => {
            const client = exchanges.get(key);
            if (!client) return;

            try {
                // Assuming all exchanges implement fetchMarkets({ query })
                // If the signature varies, we might need more robust checking or an adapter
                const markets = await (client as any).fetchMarkets({ query });

                if (Array.isArray(markets)) {
                    results.push(...markets.map(m => normalizeMarket(m, key)));
                }
            } catch (e) {
                console.warn(`Error fetching from ${key}:`, e);
                // Swallow individual exchange errors to allow partial results
            }
        });

        await Promise.all(promises);

        return { success: true, data: results };
    } catch (error: any) {
        return { success: false, error: error.message };
    }
}

/**
 * Get current probabilities for a specific market.
 * dynamically uses the registered exchange client.
 */
export async function pmxt_quote(market_id: string, exchange: string): Promise<ToolResult<any>> {
    try {
        const normalizedExchange = exchange.toLowerCase();
        const client = exchanges.get(normalizedExchange);

        if (!client) {
            throw new Error(`Unsupported exchange: ${exchange}`);
        }

        const orderbook = await client.fetchOrderBook(market_id);

        // Standardize quote extraction
        // Most PMXT exchanges follow the bids/asks array format
        // If a future exchange differs, we might need a normalizeQuote strategy similar to normalizeMarket

        const bestBid = orderbook.bids?.[0]?.price ?? null;
        const bestAsk = orderbook.asks?.[0]?.price ?? null;

        // "Yes" price is the cost to buy a "Yes" share (the best ask)
        // "No" price is the cost to buy a "No" share
        const yes = bestAsk;

        // Handle variations in how "No" price is calculated or represented
        // Kalshi uses 1-100 scale often (or cents), Polymarket 0-1.
        // Assuming client handles basic unit normalization, but logic from original code suggests:
        // Kalshi: 100 - bestBid ? or 1 - bestBid?
        // Original code had: normalizedExchange === "kalshi" ? 100 - bestBid : 1 - bestBid

        let no = bestBid !== null ? 1 - bestBid : null;
        if (normalizedExchange === 'kalshi' && bestBid !== null) {
            // Preserving original logic for Kalshi
            // Check if bestBid > 1 to infer scale? Or stick to original rule
            no = 100 - bestBid;
        }

        return {
            success: true,
            data: {
                yes,
                no,
                // Include raw bestBid/BestAsk for debugging or advanced usage?
                _meta: { bestBid, bestAsk }
            }
        };
    } catch (error: any) {
        return { success: false, error: `Failed to fetch quote: ${error.message}` };
    }
}

/**
 * Place a real-money market order on a market.
 */
export async function pmxt_order(
    market_id: string,
    outcome: string,
    amount: number,
    side: "buy" | "sell",
    exchange: string
): Promise<ToolResult<any>> {
    try {
        const normalizedExchange = exchange.toLowerCase();
        const client = exchanges.get(normalizedExchange);

        if (!client) {
            throw new Error(`Unsupported exchange: ${exchange}`);
        }

        const result = await client.createOrder({
            market_id,
            outcome,
            amount,
            side
        });

        return { success: true, data: result };
    } catch (error: any) {
        return {
            success: false,
            error: `Order failed: ${error.message}. Ensure credentials (API_KEY, PRIVATE_KEY) are correctly configured.`
        };
    }
}
