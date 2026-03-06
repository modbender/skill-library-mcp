/**
 * Oath Engine - 5 tools
 * Attestations, verification, and trust management
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const OathAttestInputSchema = z.object({
  dealId: z.string().min(1),
  type: z.enum(["COMPLETION", "QUALITY", "DELIVERY", "PAYMENT", "CUSTOM"]),
  evidence: z.record(z.unknown()).optional(),
  comment: z.string().max(1000).optional(),
});

const OathVerifyInputSchema = z.object({
  attestationId: z.string().min(1),
});

const OathVaultUploadInputSchema = z.object({
  dealId: z.string().min(1),
  documents: z.array(z.object({
    name: z.string(),
    contentHash: z.string(),
    mimeType: z.string().optional(),
  })),
});

const OathVaultSealInputSchema = z.object({
  dealId: z.string().min(1),
  sealType: z.enum(["PARTIAL", "FINAL"]).default("FINAL"),
});

const OathTrustTierInputSchema = z.object({
  userId: z.string().optional(),
  orgId: z.string().optional(),
});

// Tool definitions
export const oathTools: Tool[] = [
  {
    name: "oath_attest",
    description: "Create an attestation for a deal milestone or outcome. Attestations are cryptographically signed.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID to attest",
        },
        type: {
          type: "string",
          enum: ["COMPLETION", "QUALITY", "DELIVERY", "PAYMENT", "CUSTOM"],
          description: "Attestation type",
        },
        evidence: {
          type: "object",
          description: "Evidence supporting the attestation",
        },
        comment: {
          type: "string",
          description: "Optional comment",
        },
      },
      required: ["dealId", "type"],
    },
  },
  {
    name: "oath_verify",
    description: "Verify an attestation's authenticity and check its on-chain status.",
    inputSchema: {
      type: "object",
      properties: {
        attestationId: {
          type: "string",
          description: "Attestation ID to verify",
        },
      },
      required: ["attestationId"],
    },
  },
  {
    name: "oath_vault_upload",
    description: "Upload document hashes to the secure vault for a deal. Documents are stored off-chain with on-chain anchoring.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID",
        },
        documents: {
          type: "array",
          items: {
            type: "object",
            properties: {
              name: { type: "string" },
              contentHash: { type: "string" },
              mimeType: { type: "string" },
            },
            required: ["name", "contentHash"],
          },
          description: "Documents to upload (hashes only)",
        },
      },
      required: ["dealId", "documents"],
    },
  },
  {
    name: "oath_vault_seal",
    description: "Seal a deal's vault, creating a Merkle root that anchors all documents on-chain.",
    inputSchema: {
      type: "object",
      properties: {
        dealId: {
          type: "string",
          description: "Deal ID",
        },
        sealType: {
          type: "string",
          enum: ["PARTIAL", "FINAL"],
          description: "Seal type (FINAL is irreversible)",
          default: "FINAL",
        },
      },
      required: ["dealId"],
    },
  },
  {
    name: "oath_trust_tier",
    description: "Get the trust tier for a user or organization based on their attestation history.",
    inputSchema: {
      type: "object",
      properties: {
        userId: {
          type: "string",
          description: "User ID to check",
        },
        orgId: {
          type: "string",
          description: "Organization ID to check",
        },
      },
    },
  },
];

// Tool handlers
export async function handleOathTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "oath_attest": {
      const input = OathAttestInputSchema.parse(args);
      return client.fetch("oath", "/attestations", {
        method: "POST",
        body: input,
        idempotencyKey: `attest-${input.dealId}-${input.type}-${Date.now()}`,
      });
    }

    case "oath_verify": {
      const input = OathVerifyInputSchema.parse(args);
      return client.fetch("oath", `/attestations/${input.attestationId}/verify`);
    }

    case "oath_vault_upload": {
      const input = OathVaultUploadInputSchema.parse(args);
      return client.fetch("oath", `/deals/${input.dealId}/vault/upload`, {
        method: "POST",
        body: { documents: input.documents },
        idempotencyKey: `vault-upload-${input.dealId}-${Date.now()}`,
      });
    }

    case "oath_vault_seal": {
      const input = OathVaultSealInputSchema.parse(args);
      return client.fetch("oath", `/deals/${input.dealId}/vault/seal`, {
        method: "POST",
        body: { sealType: input.sealType },
        idempotencyKey: `vault-seal-${input.dealId}-${Date.now()}`,
      });
    }

    case "oath_trust_tier": {
      const input = OathTrustTierInputSchema.parse(args);
      const params = new URLSearchParams();
      if (input.userId) params.set("userId", input.userId);
      if (input.orgId) params.set("orgId", input.orgId);
      return client.fetch("oath", `/trust-tier?${params.toString()}`);
    }

    default:
      throw new Error(`Unknown oath tool: ${name}`);
  }
}
