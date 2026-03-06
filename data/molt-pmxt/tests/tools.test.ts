
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as pmxt from 'pmxtjs';
import { pmxt_search, pmxt_quote, pmxt_order } from '../src/tools';

// Mock pmxtjs module
vi.mock('pmxtjs', () => {
    // Base Exchange class mock
    class MockExchange {
        fetchMarkets(args?: any): Promise<any[]> { return Promise.resolve([]); }
        fetchOrderBook(id?: string): Promise<any> { return Promise.resolve({ bids: [], asks: [] }); }
        createOrder(args?: any): Promise<any> { return Promise.resolve({ id: 'order-123' }); }
    }

    // Specific Exchange mocks
    class MockPolymarket extends MockExchange {
        fetchMarkets({ query }: { query: string }) {
            return Promise.resolve([
                {
                    id: 'poly-1',
                    question: `Polymarket: ${query}`,
                    volume24h: 1000,
                    closed: false
                }
            ]);
        }

        fetchOrderBook(marketId: string) {
            return Promise.resolve({
                bids: [{ price: 0.4 }],
                asks: [{ price: 0.6 }]
            });
        }
    }

    class MockKalshi extends MockExchange {
        fetchMarkets({ query }: { query: string }) {
            return Promise.resolve([
                {
                    ticker: 'kalshi-1',
                    title: `Kalshi: ${query}`,
                    volume: 500,
                    status: 'active'
                }
            ]);
        }

        fetchOrderBook(marketId: string) {
            // Kalshi logic often involves different price scale, but let's stick to simple mock
            return Promise.resolve({
                bids: [{ price: 40 }], // 40 cents
                asks: [{ price: 60 }]  // 60 cents
            });
        }
    }

    class MockLimitless extends MockExchange {
        fetchMarkets({ query }: { query: string }) {
            // Mock Limitless returns
            return Promise.resolve([
                {
                    id: 'limitless-1',
                    title: `Limitless: ${query}`,
                    volume: 200,
                    resolved: false
                }
            ]);
        }
    }

    return {
        Exchange: MockExchange,
        Polymarket: MockPolymarket,
        Kalshi: MockKalshi,
        Limitless: MockLimitless,
        __esModule: true,
    };
});


describe('pmxt tools', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Since tools.ts initializes exchanges on load, we might need to reset module registry 
        // or just rely on the fact that it uses the mocked pmxtjs.
        // The dynamic import in tools.ts happens at top level, so mocks need to be in place before import.
        // Vitest hoist mocks so this should work.
    });

    describe('pmxt_search', () => {
        it('should search across all available exchanges by default', async () => {
            // The tools.ts initializes exchanges on module load.
            // If we mock correctly, it should pick up Polymarket and Kalshi.
            const result = await pmxt_search('election');

            expect(result.success).toBe(true);
            expect(result.data).toHaveLength(3);

            // sort to ensure order doesn't flake
            const sortedData = (result.data as any[]).sort((a, b) => a.exchange.localeCompare(b.exchange));

            expect(sortedData[0].exchange).toBe('kalshi');
            expect(sortedData[0].title).toContain('Kalshi: election');

            expect(sortedData[1].exchange).toBe('limitless');
            expect(sortedData[1].title).toContain('Limitless: election');

            expect(sortedData[2].exchange).toBe('polymarket');
            expect(sortedData[2].title).toContain('Polymarket: election');
        });

        it('should filter by specific exchange', async () => {
            const result = await pmxt_search('election', 'polymarket');

            expect(result.success).toBe(true);
            expect(result.data).toHaveLength(1);
            expect(result.data![0].exchange).toBe('polymarket');
        });

        it('should return error for unsupported exchange', async () => {
            const result = await pmxt_search('election', 'unsupported-exchange');

            expect(result.success).toBe(false);
            expect(result.error).toContain('Unsupported exchange');
        });
    });

    describe('pmxt_quote', () => {
        it('should fetch quote from polymarket', async () => {
            const result = await pmxt_quote('poly-1', 'polymarket');

            expect(result.success).toBe(true);
            // In tools.ts: yes = bestAsk (0.6), no = 1 - bestBid (1 - 0.4 = 0.6)
            expect(result.data.yes).toBe(0.6);
            expect(result.data.no).toBeCloseTo(0.6);
        });

        it('should fetch quote from kalshi', async () => {
            // Kalshi logic in tools.ts: yes = bestAsk (60).
            // no: if bestBid is not null, it's 100 - bestBid (100 - 40 = 60).
            const result = await pmxt_quote('kalshi-1', 'kalshi');

            expect(result.success).toBe(true);
            expect(result.data.yes).toBe(60);
            expect(result.data.no).toBe(60);
        });

        it('should handle missing exchange', async () => {
            const result = await pmxt_quote('id', 'unknown');
            expect(result.success).toBe(false);
        });
    });

    describe('pmxt_order', () => {
        it('should place an order successfully', async () => {
            const result = await pmxt_order('mkt-1', 'yes', 10, 'buy', 'polymarket');

            expect(result.success).toBe(true);
            expect(result.data).toBeDefined();
        });

        it('should fail for unsupported exchange', async () => {
            const result = await pmxt_order('mkt-1', 'yes', 10, 'buy', 'magic-exchange');

            expect(result.success).toBe(false);
            expect(result.error).toContain('Unsupported exchange');
        });
    });
});
