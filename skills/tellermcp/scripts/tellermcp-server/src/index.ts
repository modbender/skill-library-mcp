import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import * as z from 'zod';
import { TellerApiClient } from './client.js';

const server = new McpServer({
  name: 'tellermcp',
  version: '0.1.0',
  description: 'Expose Teller delta-neutral and lending workflows via MCP tools'
});

const client = new TellerApiClient();

const jsonResponse = (summary: string, data: unknown) => ({
  content: [
    {
      type: 'text' as const,
      text: summary
    }
  ],
  structuredContent: {
    payload: data
  }
});

server.registerTool(
  'get-delta-neutral-opportunities',
  {
    description: 'List delta-neutral arbitrage opportunities from Teller perps endpoint',
    inputSchema: z
      .object({
        chainId: z
          .number()
          .describe('Chain ID to filter opportunities')
          .int()
          .positive()
          .optional(),
        coin: z
          .string()
          .describe('Token symbol to filter (e.g., ETH, ARB)')
          .trim()
          .transform(value => value.toUpperCase())
          .optional(),
        limit: z
          .number()
          .describe('Maximum number of opportunities to return')
          .int()
          .min(1)
          .max(50)
          .optional(),
        minNetAprPct: z
          .number()
          .describe('Minimum net APR percentage to include')
          .optional()
      })
      .optional()
  },
  async input => {
    const data = await client.getDeltaNeutralOpportunities({
      chainId: input?.chainId,
      coin: input?.coin,
      limit: input?.limit,
      minNetAprPct: input?.minNetAprPct
    });
    const count = data.count ?? data.opportunities.length;
    return jsonResponse(`Returned ${count} delta-neutral opportunit${count === 1 ? 'y' : 'ies'}.`, data);
  }
);

server.registerTool(
  'get-borrow-pools',
  {
    description: 'Get Teller borrow pools with optional filters',
    inputSchema: z
      .object({
        chainId: z.number().int().positive().optional(),
        collateralTokenAddress: z
          .string()
          .trim()
          .regex(/^0x[a-fA-F0-9]{40}$/u, 'Must be a valid address')
          .optional(),
        borrowTokenAddress: z
          .string()
          .trim()
          .regex(/^0x[a-fA-F0-9]{40}$/u, 'Must be a valid address')
          .optional(),
        poolAddress: z
          .string()
          .trim()
          .regex(/^0x[a-fA-F0-9]{40}$/u, 'Must be a valid address')
          .optional(),
        ttl: z
          .number()
          .describe('Cache TTL override in seconds')
          .int()
          .min(60)
          .max(86_400)
          .optional()
      })
      .optional()
  },
  async input => {
    const data = await client.getBorrowPools({
      chainId: input?.chainId,
      collateralTokenAddress: input?.collateralTokenAddress,
      borrowTokenAddress: input?.borrowTokenAddress,
      poolAddress: input?.poolAddress,
      ttl: input?.ttl
    });
    return jsonResponse(`Returned ${data.count} borrow pool${data.count === 1 ? '' : 's'}.`, data);
  }
);

server.registerTool(
  'get-borrow-terms',
  {
    description: 'Calculate borrow terms for a specific wallet, collateral token, and pool',
    inputSchema: z.object({
      wallet: z
        .string()
        .trim()
        .regex(/^0x[a-fA-F0-9]{40}$/u, 'Wallet must be a valid address'),
      chainId: z.number().int().positive(),
      collateralToken: z
        .string()
        .trim()
        .regex(/^0x[a-fA-F0-9]{40}$/u, 'Collateral token must be a valid address'),
      poolAddress: z
        .string()
        .trim()
        .regex(/^0x[a-fA-F0-9]{40}$/u, 'Pool address must be valid')
    })
  },
  async ({ wallet, chainId, collateralToken, poolAddress }) => {
    const data = await client.getBorrowTerms({ wallet, chainId, collateralToken, poolAddress });
    const maxUsd = typeof data.maxBorrowUsd === 'number' ? data.maxBorrowUsd.toFixed(2) : 'unknown';
    return jsonResponse(`Borrow terms ready — est. max borrow ${maxUsd} USD.`, data);
  }
);

server.registerTool(
  'build-borrow-transactions',
  {
    description: 'Return encoded transactions required to borrow from a Teller pool',
    inputSchema: z.object({
      walletAddress: z
        .string()
        .trim()
        .regex(/^0x[a-fA-F0-9]{40}$/u, 'Wallet must be a valid address'),
      collateralTokenAddress: z
        .string()
        .trim()
        .regex(/^0x[a-fA-F0-9]{40}$/u, 'Collateral token must be valid'),
      chainId: z.number().int().positive(),
      poolAddress: z
        .string()
        .trim()
        .regex(/^0x[a-fA-F0-9]{40}$/u, 'Pool address must be valid'),
      collateralAmount: z
        .string()
        .min(1, 'Provide the collateral amount in wei/base units'),
      principalAmount: z
        .string()
        .min(1, 'Provide the principal amount in wei/base units'),
      loanDuration: z
        .number()
        .describe('Loan duration in seconds (defaults to 30 days if omitted)')
        .int()
        .positive()
        .optional()
    })
  },
  async input => {
    const data = await client.getBorrowTransactions(input);
    return jsonResponse(
      `Prepared ${data.summary.totalTransactions} borrow transaction${data.summary.totalTransactions === 1 ? '' : 's'}.`,
      data
    );
  }
);

server.registerTool(
  'get-wallet-loans',
  {
    description: 'List active and historical Teller loans for a wallet',
    inputSchema: z.object({
      walletAddress: z
        .string()
        .trim()
        .regex(/^0x[a-fA-F0-9]{40}$/u, 'Wallet must be a valid address'),
      chainId: z.number().int().positive()
    })
  },
  async ({ walletAddress, chainId }) => {
    const data = await client.getLoans({ walletAddress, chainId });
    return jsonResponse(`Found ${data.count} loan${data.count === 1 ? '' : 's'} for this wallet.`, data);
  }
);

server.registerTool(
  'build-repay-transactions',
  {
    description: 'Build repayment approval + repay transactions for a Teller loan',
    inputSchema: z.object({
      bidId: z.number().int().nonnegative(),
      chainId: z.number().int().positive(),
      walletAddress: z
        .string()
        .trim()
        .regex(/^0x[a-fA-F0-9]{40}$/u, 'Wallet must be a valid address'),
      amount: z
        .string()
        .min(1, 'Optional partial repayment amount in wei')
        .optional()
    })
  },
  async ({ bidId, chainId, walletAddress, amount }) => {
    const data = await client.getRepayTransactions({ bidId, chainId, walletAddress, amount });
    const detail = data.summary.isFullRepayment ? 'full repayment' : 'partial repayment';
    return jsonResponse(`Prepared ${detail} transactions for loan #${data.summary.loanId}.`, data);
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('tellermcp MCP server listening on stdio');
}

main().catch(error => {
  console.error('tellermcp server error:', error);
  process.exit(1);
});
