import { AgentXPaySkill } from "./runtime";
import { ALL_TOOLS, SKILL_METADATA } from "./schemas";
import type {
  AgentXPaySkillConfig,
  DiscoverServicesParams,
  PayAndCallParams,
  ManageWalletParams,
  SubscribeServiceParams,
  CreateEscrowParams,
  SmartCallParams,
  ToolDefinition,
} from "./types";

// ─── Re-exports ────────────────────────────────────────────

export { AgentXPaySkill } from "./runtime";
export { ALL_TOOLS, SKILL_METADATA } from "./schemas";
export {
  TOOL_DISCOVER_SERVICES,
  TOOL_PAY_AND_CALL,
  TOOL_MANAGE_WALLET,
  TOOL_SUBSCRIBE_SERVICE,
  TOOL_CREATE_ESCROW,
  TOOL_SMART_CALL,
  TOOL_GET_AGENT_INFO,
} from "./schemas";
export type {
  AgentXPaySkillConfig,
  DiscoverServicesParams,
  DiscoverServicesResult,
  PayAndCallParams,
  PayAndCallResult,
  ManageWalletParams,
  WalletInfo,
  SubscribeServiceParams,
  SubscribeResult,
  CreateEscrowParams,
  EscrowResult,
  SmartCallParams,
  SmartCallResult,
  ServiceInfo,
  ToolDefinition,
  SkillMetadata,
} from "./types";

// ─── Tool Handler Type ─────────────────────────────────────

type ToolHandler = (params: Record<string, unknown>) => Promise<unknown>;

interface ToolRegistration {
  definition: ToolDefinition;
  handler: ToolHandler;
}

// ─── Skill Registry (Generic Integration Interface) ────────

export class AgentXPaySkillRegistry {
  private skill: AgentXPaySkill;
  private toolMap: Map<string, ToolRegistration>;

  constructor(config: AgentXPaySkillConfig) {
    this.skill = new AgentXPaySkill(config);
    this.toolMap = new Map();
    this._registerAllTools();
  }

  private _registerAllTools(): void {
    const tools = ALL_TOOLS;

    // Map tool name → handler
    const handlers: Record<string, ToolHandler> = {
      agentxpay_discover_services: (params) =>
        this.skill.discoverServices(params as DiscoverServicesParams),

      agentxpay_pay_and_call: (params) =>
        this.skill.payAndCall(params as unknown as PayAndCallParams),

      agentxpay_manage_wallet: (params) =>
        this.skill.manageWallet(params as unknown as ManageWalletParams),

      agentxpay_subscribe: (params) =>
        this.skill.subscribeService(params as unknown as SubscribeServiceParams),

      agentxpay_create_escrow: (params) =>
        this.skill.createEscrow(params as unknown as CreateEscrowParams),

      agentxpay_smart_call: (params) =>
        this.skill.smartCall(params as unknown as SmartCallParams),

      agentxpay_get_agent_info: () => this.skill.getAgentInfo(),
    };

    for (const tool of tools) {
      const handler = handlers[tool.name] as ToolHandler | undefined;
      if (handler) {
        this.toolMap.set(tool.name, {
          definition: tool,
          handler,
        });
      }
    }
  }

  /** List all available tool definitions (for MCP tools/list or Function Calling) */
  listTools(): ToolDefinition[] {
    return Array.from(this.toolMap.values()).map((t) => t.definition);
  }

  /** Execute a tool by name (for MCP tools/call or Function Calling dispatch) */
  async callTool(
    name: string,
    params: Record<string, unknown>
  ): Promise<unknown> {
    const registration = this.toolMap.get(name);
    if (!registration) {
      throw new Error(
        `Unknown tool: ${name}. Available tools: ${Array.from(this.toolMap.keys()).join(", ")}`
      );
    }

    try {
      const result = await registration.handler(params);
      return result;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : String(error);
      throw new Error(`Tool "${name}" failed: ${message}`);
    }
  }

  /** Get skill metadata */
  getMetadata() {
    return SKILL_METADATA;
  }

  /** Get underlying skill instance for advanced usage */
  getSkill(): AgentXPaySkill {
    return this.skill;
  }
}

// ─── OpenAI Function Calling Format Export ──────────────────

export function toOpenAIFunctions(): Array<{
  type: "function";
  function: {
    name: string;
    description: string;
    parameters: Record<string, unknown>;
  };
}> {
  return ALL_TOOLS.map((tool) => ({
    type: "function" as const,
    function: {
      name: tool.name,
      description: tool.description,
      parameters: tool.parameters,
    },
  }));
}

// ─── MCP Protocol Adapter ──────────────────────────────────

export function toMCPToolsList(): Array<{
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}> {
  return ALL_TOOLS.map((tool) => ({
    name: tool.name,
    description: tool.description,
    inputSchema: tool.parameters,
  }));
}

// ─── Quick Factory ─────────────────────────────────────────

export function createAgentXPaySkill(
  config: AgentXPaySkillConfig
): AgentXPaySkillRegistry {
  return new AgentXPaySkillRegistry(config);
}

// ─── System Prompt Snippet ─────────────────────────────────

export const SYSTEM_PROMPT_SNIPPET = `
You have access to AgentXPay capabilities for autonomous AI service discovery and payment on the Monad blockchain.

Available tools:
- agentxpay_discover_services: Find AI services registered on-chain (filter by category/price)
- agentxpay_pay_and_call: Call an AI service with automatic x402 payment (HTTP 402 → auto-pay → retry)
- agentxpay_smart_call: One-step intelligent service discovery + payment + call
- agentxpay_manage_wallet: Create/manage Agent smart contract wallets with daily spending limits, authorize/revoke agents, and pay for services using wallet balance
- agentxpay_subscribe: Subscribe to recurring AI service plans
- agentxpay_create_escrow: Lock funds in escrow for custom AI jobs
- agentxpay_get_agent_info: Check agent wallet address and balance

When a user asks to use an external AI service (image generation, code assistant, etc.):
1. Use agentxpay_discover_services to find available services and prices
2. Confirm with the user before making payment
3. Use agentxpay_pay_and_call or agentxpay_smart_call to execute

Agent Wallet payment flow (for authorized agents):
1. Create a wallet: manage_wallet action="create" dailyLimit="1.0"
2. Fund the wallet: manage_wallet action="fund" walletAddress="0x..." amount="10.0"
3. Authorize an agent: manage_wallet action="authorize_agent" walletAddress="0x..." agentAddress="0x..."
4. Pay via wallet: manage_wallet action="pay" walletAddress="0x..." serviceId=1 amount="0.01"

All payments are transparent on-chain and verifiable via transaction hash.
`.trim();
