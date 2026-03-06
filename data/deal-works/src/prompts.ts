/**
 * MCP Prompts - 5 prompts
 * Pre-built prompts for common workflows
 */

import type { Prompt } from "@modelcontextprotocol/sdk/types.js";

// Prompt definitions
export const prompts: Prompt[] = [
  {
    name: "escrow-deal",
    description: "Create a deal with escrow protection. Guides through deal creation, escrow funding, and attestation.",
    arguments: [
      {
        name: "counterparty",
        description: "Email or user ID of the counterparty",
        required: true,
      },
      {
        name: "amount",
        description: "Deal amount to escrow",
        required: true,
      },
      {
        name: "description",
        description: "Brief description of the deal",
        required: true,
      },
    ],
  },
  {
    name: "deploy-agent",
    description: "Deploy an autonomous agent from a skill. Includes funding and SLA configuration.",
    arguments: [
      {
        name: "skill",
        description: "Skill name or ID to deploy",
        required: true,
      },
      {
        name: "budget",
        description: "Maximum budget in Talers",
        required: true,
      },
    ],
  },
  {
    name: "file-dispute",
    description: "File a dispute against a deal with evidence collection.",
    arguments: [
      {
        name: "dealId",
        description: "Deal ID to dispute",
        required: true,
      },
      {
        name: "reason",
        description: "Brief reason for the dispute",
        required: true,
      },
    ],
  },
  {
    name: "publish-template",
    description: "Publish a deal template to the Bourse marketplace.",
    arguments: [
      {
        name: "name",
        description: "Template name",
        required: true,
      },
      {
        name: "category",
        description: "Template category (e.g., 'freelance', 'real-estate', 'consulting')",
        required: true,
      },
    ],
  },
  {
    name: "portfolio-review",
    description: "Review your deal portfolio including active deals, pending escrows, and agent performance.",
    arguments: [],
  },
];

// Prompt message generators
export function getPromptMessages(
  name: string,
  args: Record<string, string>
): Array<{ role: "user" | "assistant"; content: string }> {
  switch (name) {
    case "escrow-deal":
      return [
        {
          role: "user",
          content: `I want to create an escrow-protected deal with ${args.counterparty} for ${args.amount} Talers.

Description: ${args.description}

Please help me:
1. Create the deal with appropriate terms
2. Set up escrow for the full amount
3. Create an attestation template for completion verification

Use the deal_create, fund_escrow, and oath_attest tools to complete this workflow.`,
        },
      ];

    case "deploy-agent":
      return [
        {
          role: "user",
          content: `I want to deploy an agent using the "${args.skill}" skill with a budget of ${args.budget} Talers.

Please help me:
1. Search for the skill in Bourse
2. Deploy the agent with appropriate configuration
3. Fund the agent's wallet
4. Set up SLA monitoring

Use bourse_search, cadre_deploy, and fund_agent_fund tools to complete this workflow.`,
        },
      ];

    case "file-dispute":
      return [
        {
          role: "user",
          content: `I need to file a dispute for deal ${args.dealId}.

Reason: ${args.reason}

Please help me:
1. Get the deal details first
2. File the dispute with proper categorization
3. List any relevant attestations as evidence
4. Explain the next steps in the resolution process

Use deal_get, oath_verify (for any attestations), and parler_dispute_file tools.`,
        },
      ];

    case "publish-template":
      return [
        {
          role: "user",
          content: `I want to publish a deal template called "${args.name}" in the ${args.category} category.

Please help me:
1. Check if similar templates exist in Bourse
2. Create the template structure
3. Publish to the marketplace
4. Explain how others can use it

Use bourse_search and bourse_publish tools.`,
        },
      ];

    case "portfolio-review":
      return [
        {
          role: "user",
          content: `Please review my current deal.works portfolio:

1. Show my active deals and their status
2. List any pending escrows with locked amounts
3. Show deployed agents and their health
4. Summarize my wallet balances
5. Flag any items needing attention (SLA violations, expiring deals, etc.)

Use deal_list, fund_balance, cadre_list, cadre_sla_violations, and hq_dashboard tools to compile this review.`,
        },
      ];

    default:
      throw new Error(`Unknown prompt: ${name}`);
  }
}
