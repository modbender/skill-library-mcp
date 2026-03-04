#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

const baseUrl = process.env.GODADDY_API_BASE_URL;
const apiKey = process.env.GODADDY_API_KEY;
const apiSecret = process.env.GODADDY_API_SECRET;

if (!baseUrl || !apiKey || !apiSecret) {
  console.error("Missing required env vars: GODADDY_API_BASE_URL, GODADDY_API_KEY, GODADDY_API_SECRET");
  process.exit(1);
}

type ToolDef = {
  name: string;
  description: string;
  schema: z.ZodTypeAny;
  handler: (input: any) => Promise<unknown>;
};

const doRequest = async (method: string, path: string, query?: Record<string, unknown>, body?: unknown) => {
  const url = new URL(path, baseUrl);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    }
  }

  const res = await fetch(url.toString(), {
    method,
    headers: {
      Authorization: `sso-key ${apiKey}:${apiSecret}`,
      Accept: "application/json",
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });

  const text = await res.text();
  let parsed: unknown = text;
  try {
    parsed = text ? JSON.parse(text) : null;
  } catch {
    // keep text fallback
  }

  return {
    status: res.status,
    ok: res.ok,
    path,
    method,
    data: parsed,
  };
};

const str = z.string().min(1);
const queryStr = z.string().optional();
const jsonAny = z.any();

const tools: ToolDef[] = [
  {
    name: "domains_list",
    description: "List domains",
    schema: z.object({}),
    handler: async () => doRequest("GET", "/v1/domains"),
  },
  {
    name: "domains_get",
    description: "Get domain details",
    schema: z.object({ domain: str }),
    handler: async ({ domain }) => doRequest("GET", `/v1/domains/${domain}`),
  },
  {
    name: "domains_available",
    description: "Check domain availability",
    schema: z.object({ domain: str, checkType: z.enum(["FAST", "FULL"]).default("FAST"), forTransfer: z.boolean().default(false) }),
    handler: async ({ domain, checkType, forTransfer }) =>
      doRequest("GET", "/v1/domains/available", { domain, checkType, forTransfer }),
  },
  {
    name: "domains_available_bulk",
    description: "Check bulk domain availability",
    schema: z.object({ domains: z.array(str).min(1), checkType: z.enum(["FAST", "FULL"]).default("FAST") }),
    handler: async ({ domains, checkType }) => doRequest("POST", "/v1/domains/available", { checkType }, domains),
  },
  {
    name: "domains_validate_purchase",
    description: "Validate domain purchase payload",
    schema: z.object({ payload: jsonAny }),
    handler: async ({ payload }) => doRequest("POST", "/v1/domains/purchase/validate", undefined, payload),
  },
  {
    name: "domains_purchase",
    description: "Purchase domain",
    schema: z.object({ payload: jsonAny }),
    handler: async ({ payload }) => doRequest("POST", "/v1/domains/purchase", undefined, payload),
  },
  {
    name: "domains_renew",
    description: "Renew domain",
    schema: z.object({ domain: str, period: z.number().int().min(1) }),
    handler: async ({ domain, period }) => doRequest("POST", `/v1/domains/${domain}/renew`, undefined, { period }),
  },
  {
    name: "domains_transfer",
    description: "Transfer domain in",
    schema: z.object({ domain: str, payload: jsonAny }),
    handler: async ({ domain, payload }) => doRequest("POST", `/v1/domains/${domain}/transfer`, undefined, payload),
  },
  {
    name: "domains_update",
    description: "Update domain settings",
    schema: z.object({ domain: str, payload: jsonAny }),
    handler: async ({ domain, payload }) => doRequest("PATCH", `/v1/domains/${domain}`, undefined, payload),
  },
  {
    name: "domains_update_contacts",
    description: "Update domain contacts",
    schema: z.object({ domain: str, payload: jsonAny }),
    handler: async ({ domain, payload }) => doRequest("PATCH", `/v1/domains/${domain}/contacts`, undefined, payload),
  },
  {
    name: "domains_delete",
    description: "Cancel/delete domain",
    schema: z.object({ domain: str }),
    handler: async ({ domain }) => doRequest("DELETE", `/v1/domains/${domain}`),
  },
  {
    name: "domains_privacy_enable",
    description: "Enable privacy on domain",
    schema: z.object({ domain: str }),
    handler: async ({ domain }) => doRequest("PUT", `/v1/domains/${domain}/privacy`, undefined, {}),
  },
  {
    name: "domains_privacy_disable",
    description: "Disable privacy on domain",
    schema: z.object({ domain: str }),
    handler: async ({ domain }) => doRequest("DELETE", `/v1/domains/${domain}/privacy`),
  },
  {
    name: "domains_agreements_get",
    description: "Get domain agreements",
    schema: z.object({ tlds: z.string().optional(), privacy: z.boolean().optional(), forTransfer: z.boolean().optional() }),
    handler: async ({ tlds, privacy, forTransfer }) => doRequest("GET", "/v1/domains/agreements", { tlds, privacy, forTransfer }),
  },
  {
    name: "domains_agreements_accept",
    description: "Accept domain agreements",
    schema: z.object({ payload: jsonAny }),
    handler: async ({ payload }) => doRequest("POST", "/v1/domains/agreements", undefined, payload),
  },

  { name: "dns_get_all", description: "Get all DNS records", schema: z.object({ domain: str }), handler: async ({ domain }) => doRequest("GET", `/v1/domains/${domain}/records`) },
  { name: "dns_get_type", description: "Get DNS records by type", schema: z.object({ domain: str, type: str }), handler: async ({ domain, type }) => doRequest("GET", `/v1/domains/${domain}/records/${type}`) },
  { name: "dns_get", description: "Get DNS records by type and name", schema: z.object({ domain: str, type: str, name: str }), handler: async ({ domain, type, name }) => doRequest("GET", `/v1/domains/${domain}/records/${type}/${name}`) },
  { name: "dns_add", description: "Add/update DNS records (PATCH)", schema: z.object({ domain: str, records: z.array(z.record(z.any())).min(1) }), handler: async ({ domain, records }) => doRequest("PATCH", `/v1/domains/${domain}/records`, undefined, records) },
  { name: "dns_replace_all", description: "Replace all DNS records", schema: z.object({ domain: str, records: z.array(z.record(z.any())) }), handler: async ({ domain, records }) => doRequest("PUT", `/v1/domains/${domain}/records`, undefined, records) },
  { name: "dns_replace_type", description: "Replace DNS records for type", schema: z.object({ domain: str, type: str, records: z.array(z.record(z.any())) }), handler: async ({ domain, type, records }) => doRequest("PUT", `/v1/domains/${domain}/records/${type}`, undefined, records) },
  { name: "dns_replace_type_name", description: "Replace DNS records for type+name", schema: z.object({ domain: str, type: str, name: str, records: z.array(z.record(z.any())) }), handler: async ({ domain, type, name, records }) => doRequest("PUT", `/v1/domains/${domain}/records/${type}/${name}`, undefined, records) },
  { name: "dns_delete_type_name", description: "Delete DNS records for type+name", schema: z.object({ domain: str, type: str, name: str }), handler: async ({ domain, type, name }) => doRequest("DELETE", `/v1/domains/${domain}/records/${type}/${name}`) },

  { name: "certs_create", description: "Create certificate order", schema: z.object({ payload: jsonAny }), handler: async ({ payload }) => doRequest("POST", "/v1/certificates", undefined, payload) },
  { name: "certs_validate", description: "Validate certificate order payload", schema: z.object({ payload: jsonAny }), handler: async ({ payload }) => doRequest("POST", "/v1/certificates/validate", undefined, payload) },
  { name: "certs_get", description: "Get certificate details", schema: z.object({ certificateId: str }), handler: async ({ certificateId }) => doRequest("GET", `/v1/certificates/${certificateId}`) },
  { name: "certs_actions", description: "Get certificate actions", schema: z.object({ certificateId: str }), handler: async ({ certificateId }) => doRequest("GET", `/v1/certificates/${certificateId}/actions`) },
  { name: "certs_download", description: "Download certificate", schema: z.object({ certificateId: str }), handler: async ({ certificateId }) => doRequest("GET", `/v1/certificates/${certificateId}/download`) },
  { name: "certs_renew", description: "Renew certificate", schema: z.object({ certificateId: str, payload: jsonAny }), handler: async ({ certificateId, payload }) => doRequest("POST", `/v1/certificates/${certificateId}/renew`, undefined, payload) },
  { name: "certs_reissue", description: "Reissue certificate", schema: z.object({ certificateId: str, payload: jsonAny }), handler: async ({ certificateId, payload }) => doRequest("POST", `/v1/certificates/${certificateId}/reissue`, undefined, payload) },
  { name: "certs_revoke", description: "Revoke certificate", schema: z.object({ certificateId: str, payload: jsonAny }), handler: async ({ certificateId, payload }) => doRequest("POST", `/v1/certificates/${certificateId}/revoke`, undefined, payload) },
  { name: "certs_verify_domain_control", description: "Verify certificate domain control", schema: z.object({ certificateId: str, payload: jsonAny }), handler: async ({ certificateId, payload }) => doRequest("POST", `/v1/certificates/${certificateId}/verifyDomainControl`, undefined, payload) },

  { name: "shoppers_get", description: "Get shopper details", schema: z.object({ shopperId: str }), handler: async ({ shopperId }) => doRequest("GET", `/v1/shoppers/${shopperId}`) },
  { name: "shoppers_update", description: "Update shopper", schema: z.object({ shopperId: str, payload: jsonAny }), handler: async ({ shopperId, payload }) => doRequest("PATCH", `/v1/shoppers/${shopperId}`, undefined, payload) },
  { name: "shoppers_delete", description: "Delete shopper", schema: z.object({ shopperId: str }), handler: async ({ shopperId }) => doRequest("DELETE", `/v1/shoppers/${shopperId}`) },

  { name: "subscriptions_list", description: "List subscriptions", schema: z.object({}), handler: async () => doRequest("GET", "/v1/subscriptions") },
  { name: "subscriptions_get", description: "Get subscription details", schema: z.object({ subscriptionId: str }), handler: async ({ subscriptionId }) => doRequest("GET", `/v1/subscriptions/${subscriptionId}`) },
  { name: "subscriptions_cancel", description: "Cancel subscription", schema: z.object({ subscriptionId: str, payload: jsonAny.optional() }), handler: async ({ subscriptionId, payload }) => doRequest("POST", `/v1/subscriptions/${subscriptionId}/cancel`, undefined, payload ?? {}) },

  { name: "agreements_list", description: "List legal agreements", schema: z.object({ queryString: queryStr }), handler: async ({ queryString }) => doRequest("GET", "/v1/agreements", queryString ? Object.fromEntries(new URLSearchParams(queryString)) : undefined) },
  { name: "countries_list", description: "List countries", schema: z.object({}), handler: async () => doRequest("GET", "/v1/countries") },

  { name: "aftermarket_listings_list", description: "List aftermarket listings", schema: z.object({ queryString: queryStr }), handler: async ({ queryString }) => doRequest("GET", "/v1/aftermarket/listings", queryString ? Object.fromEntries(new URLSearchParams(queryString)) : undefined) },
  { name: "aftermarket_listings_get", description: "Get aftermarket listing details", schema: z.object({ listingId: str }), handler: async ({ listingId }) => doRequest("GET", `/v1/aftermarket/listings/${listingId}`) },
];

const byName = new Map(tools.map((t) => [t.name, t]));

const server = new Server(
  {
    name: "godaddy-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: { tools: {} },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: tools.map((t) => ({
    name: t.name,
    description: t.description,
    inputSchema: zodToJsonSchema(t.schema, { target: "jsonSchema7" }),
  })),
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const tool = byName.get(req.params.name);
  if (!tool) {
    return { content: [{ type: "text", text: JSON.stringify({ error: `Unknown tool: ${req.params.name}` }) }], isError: true };
  }

  try {
    const input = tool.schema.parse(req.params.arguments ?? {});
    const result = await tool.handler(input);
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  } catch (error: any) {
    return {
      content: [{ type: "text", text: JSON.stringify({ error: error?.message ?? String(error) }) }],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
