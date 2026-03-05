#!/usr/bin/env node

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import * as api from './client.js';

const server = new McpServer({
  name: 'auction-house',
  version: '0.1.0',
});

// ─── Scouting & Discovery Tools ───

server.tool(
  'search_auctions',
  'Search and scout for auctions matching specific criteria. Use this to find auctions the user might be interested in — by keyword, price range, token, or recency. All bids are placed in the auction\'s own token.',
  {
    search: z
      .string()
      .optional()
      .describe('Keyword search on auction name and description (e.g. "consulting", "NFT", "design")'),
    currency: z
      .string()
      .optional()
      .describe('Filter by payment token symbol (e.g. "USDC", "WETH"). Bids are always in this token.'),
    token: z
      .string()
      .optional()
      .describe('Filter by exact token contract address on Base'),
    minPrice: z
      .number()
      .optional()
      .describe('Minimum bid floor — only show auctions with minimum bid >= this amount'),
    maxPrice: z
      .number()
      .optional()
      .describe('Maximum bid floor — only show auctions with minimum bid <= this amount (budget filter)'),
    createdAfter: z
      .string()
      .optional()
      .describe('ISO date string — only show auctions created after this time. Use for polling new auctions since last check.'),
    endingWithin: z
      .number()
      .optional()
      .describe('Hours — only show auctions ending within this many hours (e.g. 2 = ending in the next 2 hours). Good for sniping or urgency alerts.'),
    sort: z
      .enum(['newest', 'ending_soon', 'highest_bid', 'most_bids'])
      .optional()
      .describe('Sort order. Default: newest'),
    limit: z
      .number()
      .min(1)
      .max(50)
      .optional()
      .describe('Max results. Default: 20'),
  },
  async (params) => {
    const res = await api.searchAuctions({
      ...params,
      status: 'ongoing',
    });

    if (!res.ok) {
      return {
        content: [{ type: 'text', text: `Error: ${res.data.error || 'Search failed'}` }],
        isError: true,
      };
    }

    const { auctions, total } = res.data;

    if (!auctions || auctions.length === 0) {
      return {
        content: [{ type: 'text', text: 'No matching auctions found.' }],
      };
    }

    const lines = auctions.map((a: any) => {
      const timeLeft = Math.max(0, Math.round((new Date(a.endDate).getTime() - Date.now()) / 3600000));
      return `• [${a.blockchainAuctionId}] "${a.auctionName}" — ${a.currency} | Min: ${a.minimumBid} | Highest: ${a.highestBid} | Bids: ${a.biddersCount} | ${timeLeft}h left | Host: ${a.host?.username || 'unknown'}${a.description ? ` | "${a.description}"` : ''}`;
    });

    return {
      content: [
        {
          type: 'text',
          text: `Found ${total} matching auctions:\n\n${lines.join('\n')}`,
        },
      ],
    };
  }
);

server.tool(
  'list_auctions',
  'List active or ended auctions on House',
  {
    status: z
      .enum(['ongoing', 'ended', 'all'])
      .optional()
      .describe('Filter by status. Default: ongoing'),
    limit: z
      .number()
      .min(1)
      .max(50)
      .optional()
      .describe('Max results. Default: 20'),
  },
  async ({ status, limit }) => {
    const res = await api.listAuctions({
      status: status || 'ongoing',
      limit,
    });

    if (!res.ok) {
      return {
        content: [{ type: 'text', text: `Error: ${res.data.error || 'Failed to fetch auctions'}` }],
        isError: true,
      };
    }

    const { auctions, total } = res.data;

    if (!auctions || auctions.length === 0) {
      return {
        content: [{ type: 'text', text: 'No auctions found.' }],
      };
    }

    const lines = auctions.map((a: any) => {
      const timeLeft = Math.max(0, Math.round((new Date(a.endDate).getTime() - Date.now()) / 3600000));
      return `• [${a.blockchainAuctionId}] "${a.auctionName}" — ${a.currency} | Min: ${a.minimumBid} | Highest: ${a.highestBid} | Bids: ${a.biddersCount} | ${timeLeft}h left | Host: ${a.host?.username || 'unknown'}`;
    });

    return {
      content: [
        {
          type: 'text',
          text: `Found ${total} auctions:\n\n${lines.join('\n')}`,
        },
      ],
    };
  }
);

server.tool(
  'get_auction',
  'Get full details of a specific auction including bid history',
  {
    auctionId: z.string().describe('The blockchain auction ID'),
  },
  async ({ auctionId }) => {
    const res = await api.getAuction(auctionId);

    if (!res.ok) {
      return {
        content: [{ type: 'text', text: `Error: ${res.data.error || 'Auction not found'}` }],
        isError: true,
      };
    }

    const { auction, bids } = res.data;
    const timeLeft = Math.max(0, Math.round((new Date(auction.endDate).getTime() - Date.now()) / 3600000));

    let text = `Auction: "${auction.auctionName}"\n`;
    text += `ID: ${auction.blockchainAuctionId}\n`;
    text += `Status: ${auction.status}\n`;
    text += `Payment Token: ${auction.currency} (${auction.tokenAddress})\n`;
    text += `Minimum Bid: ${auction.minimumBid} ${auction.currency}\n`;
    text += `Highest Bid: ${auction.highestBid} ${auction.currency}\n`;
    text += `Total Bids: ${auction.biddersCount}\n`;
    text += `Time Left: ${timeLeft}h\n`;
    text += `Start: ${new Date(auction.startDate).toISOString()}\n`;
    text += `End: ${new Date(auction.endDate).toISOString()}\n`;
    text += `Host: ${auction.host?.username || 'unknown'}\n`;

    if (auction.description) {
      text += `Description: ${auction.description}\n`;
    }

    if (bids && bids.length > 0) {
      text += `\nBid History:\n`;
      bids.slice(0, 10).forEach((b: any) => {
        text += `  • ${b.bidAmount} ${b.currency} ($${b.usdcValue?.toFixed(2) || '?'}) by ${b.bidder?.username || 'anon'} at ${new Date(b.bidTimestamp).toISOString()}\n`;
      });
    }

    return { content: [{ type: 'text', text }] };
  }
);

// ─── Action Tools ───

server.tool(
  'create_auction',
  'Create a new auction on House. You specify which token bidders must pay in (e.g. USDC). Your bot wallet needs ETH for gas.',
  {
    auctionName: z
      .string()
      .max(30)
      .describe('Name of the auction (max 30 chars)'),
    tokenAddress: z
      .string()
      .describe(
        'The ERC20 token contract address on Base that bidders will pay in. Common tokens — USDC: 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913, WETH: 0x4200000000000000000000000000000000000006'
      ),
    minimumBid: z
      .number()
      .positive()
      .describe('Minimum bid amount in token units (e.g. 50 = 50 USDC)'),
    durationHours: z
      .number()
      .min(1)
      .max(168)
      .describe('Auction duration in hours (1-168)'),
    description: z
      .string()
      .max(200)
      .optional()
      .describe('Optional description of what is being auctioned (max 200 chars)'),
  },
  async ({ auctionName, tokenAddress, minimumBid, durationHours, description }) => {
    const res = await api.createAuction({
      auctionName,
      tokenAddress,
      minimumBid,
      durationHours,
      description,
    });

    if (!res.ok) {
      return {
        content: [
          {
            type: 'text',
            text: `Failed to create auction: ${res.data.error || 'Unknown error'}`,
          },
        ],
        isError: true,
      };
    }

    const { auction } = res.data;

    return {
      content: [
        {
          type: 'text',
          text: `Auction created!\n\nID: ${auction.blockchainAuctionId}\nName: ${auction.auctionName}\nPayment Token: ${auction.currency}\nMin Bid: ${auction.minimumBid} ${auction.currency}\nDuration: ${auction.durationHours}h\nEnds: ${new Date(auction.endDate).toISOString()}\nTx: ${auction.txHash}`,
        },
      ],
    };
  }
);

server.tool(
  'place_bid',
  'Place a bid on an active auction. The bid is paid in the auction\'s token (shown in auction details). Your bot wallet must hold enough of that token + ETH for gas.',
  {
    auctionId: z.string().describe('The blockchain auction ID to bid on'),
    amount: z
      .number()
      .positive()
      .describe(
        'Bid amount in the auction\'s token (e.g. if the auction uses USDC, then 75 = 75 USDC). Must be higher than current highest bid.'
      ),
  },
  async ({ auctionId, amount }) => {
    const res = await api.placeBid(auctionId, amount);

    if (!res.ok) {
      return {
        content: [
          {
            type: 'text',
            text: `Failed to place bid: ${res.data.error || 'Unknown error'}`,
          },
        ],
        isError: true,
      };
    }

    const { bid } = res.data;

    return {
      content: [
        {
          type: 'text',
          text: `Bid placed!\n\nAuction: ${bid.blockchainAuctionId}\nAmount: ${bid.amount} ${bid.currency}\nUSD Value: $${bid.usdcValue?.toFixed(2) || '?'}\nTx: ${bid.txHash}`,
        },
      ],
    };
  }
);

// ─── Account Tools ───

server.tool(
  'my_auctions',
  'List auctions you have created',
  {
    status: z
      .enum(['ongoing', 'ended', 'all'])
      .optional()
      .describe('Filter by status'),
  },
  async ({ status }) => {
    const res = await api.getMyAuctions({ status });

    if (!res.ok) {
      return {
        content: [{ type: 'text', text: `Error: ${res.data.error || 'Failed to fetch'}` }],
        isError: true,
      };
    }

    const { auctions, total } = res.data;

    if (!auctions || auctions.length === 0) {
      return { content: [{ type: 'text', text: 'You have no auctions.' }] };
    }

    const lines = auctions.map(
      (a: any) =>
        `• [${a.blockchainAuctionId}] "${a.auctionName}" — ${a.status} | Highest: ${a.highestBid} ${a.currency} | Bids: ${a.biddersCount}`
    );

    return {
      content: [
        { type: 'text', text: `Your ${total} auctions:\n\n${lines.join('\n')}` },
      ],
    };
  }
);

server.tool(
  'my_bids',
  'List bids you have placed',
  {
    limit: z.number().min(1).max(50).optional().describe('Max results'),
  },
  async ({ limit }) => {
    const res = await api.getMyBids({ limit });

    if (!res.ok) {
      return {
        content: [{ type: 'text', text: `Error: ${res.data.error || 'Failed to fetch'}` }],
        isError: true,
      };
    }

    const { bids, total } = res.data;

    if (!bids || bids.length === 0) {
      return { content: [{ type: 'text', text: 'You have no bids.' }] };
    }

    const lines = bids.map(
      (b: any) =>
        `• ${b.bidAmount} ${b.currency} ($${b.usdcValue?.toFixed(2) || '?'}) on "${b.auction?.name || b.blockchainAuctionId}" — ${b.auction?.status || 'unknown'}`
    );

    return {
      content: [
        { type: 'text', text: `Your ${total} bids:\n\n${lines.join('\n')}` },
      ],
    };
  }
);

server.tool(
  'wallet_info',
  'Check your bot wallet address and balances. Use this to verify you have enough tokens before bidding.',
  {
    tokenAddress: z
      .string()
      .optional()
      .describe(
        'Token address to check balance for. USDC: 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913'
      ),
  },
  async ({ tokenAddress }) => {
    const res = await api.getWalletInfo(tokenAddress);

    if (!res.ok) {
      return {
        content: [{ type: 'text', text: `Error: ${res.data.error || 'Failed to fetch'}` }],
        isError: true,
      };
    }

    const { wallet } = res.data;

    let text = `Bot Wallet: ${wallet.address}\n`;
    text += `ETH Balance: ${wallet.ethBalance} ETH (for gas)\n`;

    if (wallet.tokenBalance !== null) {
      text += `${wallet.tokenSymbol || 'Token'} Balance: ${wallet.tokenBalance} (for bids)`;
    }

    text += `\n\nFund this address to create auctions and place bids.`;

    return { content: [{ type: 'text', text }] };
  }
);

// ─── Start ───

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
