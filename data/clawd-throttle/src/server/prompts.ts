import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

export function registerPrompts(server: McpServer): void {
  server.prompt(
    'cost-report',
    'Generate a human-readable cost savings report from routing stats',
    {
      days: {
        description: 'Lookback period in days (default: 30)',
        required: false,
      },
    },
    ({ days }) => ({
      messages: [{
        role: 'user' as const,
        content: {
          type: 'text' as const,
          text: `Use the get_routing_stats tool with days=${days ?? '30'} to gather data, then generate a clear cost report including:

1. Total requests and total cost
2. What it would have cost using Opus for everything
3. How much was saved (dollars and percentage)
4. Which models handled the most requests
5. Complexity tier breakdown
6. A brief recommendation on whether the current mode is optimal

Format it as a clean, readable summary. Use dollar amounts with 2 decimal places.`,
        },
      }],
    }),
  );
}
