/**
 * FiberAgent Skill for OpenClaw
 * Provides product search with crypto cashback across 50,000+ merchants
 */

module.exports = {
  name: 'fiberagent',
  version: '1.0.0',
  description: 'Find products with cryptocurrency cashback via Fiber affiliate network on Monad',
  
  // Tool definitions for OpenClaw agent
  tools: {
    search_products: {
      description: 'Search for products with cashback rates across merchants',
      params: {
        keywords: { type: 'string', description: 'Product to search for (e.g., "dyson airwrap")' },
        agent_id: { type: 'string', description: 'Your agent ID (wallet address or agent name)' },
        size: { type: 'number', description: 'Number of results (default 10)' }
      },
      fn: async (keywords, agent_id, size = 10) => {
        const url = `https://fiberagent.shop/api/agent/search?keywords=${encodeURIComponent(keywords)}&agent_id=${agent_id}&size=${size}`;
        const res = await fetch(url);
        return res.json();
      }
    },
    
    get_agent_stats: {
      description: 'Get your agent earnings and stats from FiberAgent',
      params: {
        agent_id: { type: 'string', description: 'Your agent ID' }
      },
      fn: async (agent_id) => {
        const url = `https://fiberagent.shop/api/agent/${agent_id}/stats`;
        const res = await fetch(url);
        return res.json();
      }
    },
    
    register_agent: {
      description: 'Register a new agent with FiberAgent to start earning cashback',
      params: {
        agent_id: { type: 'string', description: 'Name for your agent' },
        wallet_address: { type: 'string', description: 'Your Monad wallet address (0x...)' },
        crypto_preference: { type: 'string', description: 'Crypto token preference (default: MON)' }
      },
      fn: async (agent_id, wallet_address, crypto_preference = 'MON') => {
        const url = 'https://fiberagent.shop/api/agent/register';
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_name: agent_id,
            wallet_address: wallet_address,
            crypto_preference: crypto_preference
          })
        });
        return res.json();
      }
    }
  }
};
