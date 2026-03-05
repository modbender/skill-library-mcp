/**
 * LangChain.js ReAct runner for the skill: MCP tools + local tools, Hugging Face LLM.
 */

import { createReactAgent } from '@langchain/langgraph/prebuilt';
import { createLLM } from './llm.js';
import { createMcpTools } from './tools/mcpTools.js';
import { createLocalTools } from './tools/localTools.js';

const SYSTEM_MESSAGE = `You are an agent with a skill that provides tools for wallet management and x402-paid MCP tools (predictions, backtests, bank linking, scores). Payment is automatic — just call the tool.

## ALWAYS DO FIRST
Before any paid or wallet action, call get_wallet_addresses (no args). It returns:
  { aptos: [{ address, network }], evm: [{ address, network }] }
- If aptos is empty and you need Aptos tools: create_aptos_wallet -> credit_aptos_wallet -> tell user to whitelist at https://arnstein.ch/flow.html
- If evm is empty and you need EVM tools: create_evm_wallet -> fund_evm_wallet -> tell user to whitelist at https://arnstein.ch/flow.html
- If wallets exist: check balance before paid calls. balance_aptos (for prediction/backtest/scores) or balance_evm({ chain: "baseSepolia" }) (for link_bank_account).

## TOOLS

Wallet tools:
- get_wallet_addresses() -> { aptos: [...], evm: [...] }
- create_aptos_wallet({ force?, network? }) -> { success, address, network }
- create_evm_wallet({ force?, network? }) -> { success, address, network }
- credit_aptos_wallet({ amount_octas? }) -> devnet: funds directly; testnet: returns faucet_url + instructions
- fund_evm_wallet() -> returns faucet_url + address (manual funding)
- balance_aptos() -> { address, balances: { usdc, apt } }
- balance_evm({ chain? }) -> { address, chain, balance, symbol }. Chains: base, baseSepolia, ethereum, polygon, arbitrum, optimism

Paid MCP tools (payment handled for you — just call them):
- run_prediction({ symbol, horizon? }) — stock prediction, ~6c USDC. Example: run_prediction({ symbol: "AAPL", horizon: 30 })
- run_backtest({ symbol, startDate?, endDate?, strategy? }) — backtest, ~6c. Dates "YYYY-MM-DD", strategy default "chronos"
- link_bank_account() — Plaid bank link, ~5c on Base. Needs funded EVM wallet (baseSepolia for testnet)
- get_agent_reputation_score({ agent_address?, payer_wallet? }) — reputation score
- get_borrower_score({ agent_address?, payer_wallet? }) — borrower score
- get_agent_reputation_score_by_email({ email, payer_wallet? }) — by email (needs SCORE_BY_EMAIL_ENABLED)
- get_borrower_score_by_email({ email, payer_wallet? }) — by email

## ERROR RECOVERY
- "No Aptos/EVM wallet" -> create the missing wallet
- "already exist" -> use existing wallet, or pass force: true to add another
- "Payment verification failed" -> insufficient funds; check balance, tell user to fund
- "403" / "not allowlisted" -> tell user to whitelist at https://arnstein.ch/flow.html
- Timeout -> retry once`;

/**
 * Create agent graph: llm + tools (MCP + local).
 * @param {{ llm?: import('@langchain/core/language_models/chat_models').BaseChatModel; tools?: import('@langchain/core/tools').StructuredToolInterface[] }} options - llm and tools (if omitted, created from env and mcpClient)
 * @param {{ callTool: (name: string, args: Object) => Promise<Object> }} [options.mcpClient] - required if tools not provided
 * @returns {Promise<{ agent: import('@langchain/langgraph').CompiledStateGraph; runAgent: (message: string) => Promise<Object> }>}
 */
export async function createAgent(options = {}) {
  const llm = options.llm || createLLM();
  let tools = options.tools;
  if (!tools && options.mcpClient) {
    tools = [...createMcpTools(options.mcpClient), ...createLocalTools()];
  }
  if (!tools) {
    throw new Error('Provide options.tools or options.mcpClient to createAgent.');
  }

  const agent = createReactAgent({
    llm,
    tools,
    stateModifier: (state) => [{ role: 'system', content: SYSTEM_MESSAGE }, ...(state.messages || [])],
  });

  async function runAgent(userMessage) {
    const result = await agent.invoke(
      { messages: [{ role: 'user', content: userMessage }] },
      { recursionLimit: 50 }
    );
    return result;
  }

  return { agent, runAgent };
}
