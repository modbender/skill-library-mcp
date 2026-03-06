import { InwxClient } from "./client";
import { assertToolAllowed } from "./guards";
import { Domain, DomainCheckResult, DnsRecord, DnssecKey, JsonMap, PluginConfig, ToolContext, ToolHandler, TldPricing } from "./types";

async function withClient<T>(context: ToolContext, toolName: string, fn: (client: InwxClient) => Promise<T>): Promise<T> {
  assertToolAllowed(context.config, toolName);
  const client = new InwxClient(context.config);
  try {
    return await fn(client);
  } finally {
    await client.logout();
  }
}

function asArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function mapCheckResult(item: JsonMap): DomainCheckResult {
  const domain = String(item.domain ?? item.domainName ?? "");
  const avail = Boolean(item.avail ?? item.available ?? false);
  return {
    domain,
    avail,
    price: typeof item.price === "number" ? item.price : undefined,
    currency: typeof item.currency === "string" ? item.currency : undefined,
    period: typeof item.period === "number" ? item.period : undefined,
    premium: typeof item.premium === "boolean" ? item.premium : undefined,
    reason: typeof item.reason === "string" ? item.reason : undefined,
    ...item,
  };
}

export function createTools(): ToolHandler[] {
  return [
    {
      name: "inwx_domain_check",
      description: "Check domain availability and pricing",
      run: async (params, context) => withClient(context, "inwx_domain_check", async (client) => {
        const domain = String(params.domain ?? "").trim();
        if (!domain) throw new Error("domain is required");
        const res = await client.call<JsonMap>("domain.check", { domain });
        const checks = asArray<JsonMap>(res.checks ?? res.domain ?? res.domains);
        if (checks.length > 0) {
          return checks.map(mapCheckResult);
        }
        return mapCheckResult({ domain, ...(res as JsonMap) });
      }),
    },
    {
      name: "inwx_domain_register",
      description: "Register a new domain",
      run: async (params, context) => withClient(context, "inwx_domain_register", async (client) => {
        const domain = String(params.domain ?? "").trim();
        if (!domain) throw new Error("domain is required");
        return client.call<JsonMap>("domain.create", {
          domain,
          period: Number(params.period ?? 1),
          contacts: params.contacts,
          ns: params.ns,
          owner: params.owner,
        });
      }),
    },
    {
      name: "inwx_domain_list",
      description: "List domains in the account",
      run: async (params, context) => withClient(context, "inwx_domain_list", async (client) => {
        const res = await client.call<JsonMap>("domain.list", params);
        const list = asArray<Domain>(res.domain ?? res.domains ?? res.list);
        return { total: list.length, domains: list, raw: res };
      }),
    },
    {
      name: "inwx_domain_info",
      description: "Get detailed information for a domain",
      run: async (params, context) => withClient(context, "inwx_domain_info", async (client) => {
        const domain = String(params.domain ?? "").trim();
        if (!domain) throw new Error("domain is required");
        return client.call<JsonMap>("domain.info", { domain });
      }),
    },
    {
      name: "inwx_domain_update",
      description: "Update domain settings",
      run: async (params, context) => withClient(context, "inwx_domain_update", async (client) => client.call<JsonMap>("domain.update", params)),
    },
    {
      name: "inwx_domain_delete",
      description: "Delete or cancel a domain",
      run: async (params, context) => withClient(context, "inwx_domain_delete", async (client) => client.call<JsonMap>("domain.delete", params)),
    },
    {
      name: "inwx_domain_transfer",
      description: "Transfer a domain to INWX",
      run: async (params, context) => withClient(context, "inwx_domain_transfer", async (client) => client.call<JsonMap>("domain.transfer", params)),
    },
    {
      name: "inwx_domain_renew",
      description: "Renew a domain",
      run: async (params, context) => withClient(context, "inwx_domain_renew", async (client) => client.call<JsonMap>("domain.renew", params)),
    },
    {
      name: "inwx_domain_pricing",
      description: "Get pricing for one or more domains or TLDs",
      run: async (params, context) => withClient(context, "inwx_domain_pricing", async (client) => {
        const domainsInput = params.domains;
        const domains = Array.isArray(domainsInput) ? domainsInput.map(String) : [String(params.domain ?? "")].filter(Boolean);
        if (domains.length === 0) {
          throw new Error("domain or domains[] is required");
        }
        const res = await client.call<JsonMap>("domain.check", { domain: domains });
        const checks = asArray<JsonMap>(res.checks ?? res.domain ?? res.domains);
        const pricing: TldPricing[] = checks.map((item) => ({
          tld: String(item.tld ?? item.domain ?? ""),
          registrationPrice: typeof item.price === "number" ? item.price : undefined,
          renewalPrice: typeof item.renewalPrice === "number" ? item.renewalPrice : undefined,
          transferPrice: typeof item.transferPrice === "number" ? item.transferPrice : undefined,
          currency: typeof item.currency === "string" ? item.currency : undefined,
          ...item,
        }));
        return { total: pricing.length, pricing, raw: res };
      }),
    },
    {
      name: "inwx_nameserver_list",
      description: "List nameserver setup",
      run: async (params, context) => withClient(context, "inwx_nameserver_list", async (client) => {
        const domain = String(params.domain ?? "").trim();
        if (domain) {
          return client.call<JsonMap>("domain.info", { domain });
        }
        return client.call<JsonMap>("nameserver.list", params);
      }),
    },
    {
      name: "inwx_nameserver_set",
      description: "Set nameservers for a domain",
      run: async (params, context) => withClient(context, "inwx_nameserver_set", async (client) => {
        const domain = String(params.domain ?? "").trim();
        const ns = Array.isArray(params.ns) ? params.ns : [];
        if (!domain || ns.length === 0) {
          throw new Error("domain and ns[] are required");
        }
        return client.call<JsonMap>("domain.update", { domain, ns });
      }),
    },
    {
      name: "inwx_dns_record_list",
      description: "List DNS records for a domain",
      run: async (params, context) => withClient(context, "inwx_dns_record_list", async (client) => {
        const domain = String(params.domain ?? "").trim();
        if (!domain) throw new Error("domain is required");
        const res = await client.call<JsonMap>("nameserver.info", { domain });
        const records = asArray<DnsRecord>(res.record ?? res.records);
        return { total: records.length, records, raw: res };
      }),
    },
    {
      name: "inwx_dns_record_add",
      description: "Add a DNS record",
      run: async (params, context) => withClient(context, "inwx_dns_record_add", async (client) => client.call<JsonMap>("nameserver.createRecord", params)),
    },
    {
      name: "inwx_dns_record_update",
      description: "Update a DNS record",
      run: async (params, context) => withClient(context, "inwx_dns_record_update", async (client) => client.call<JsonMap>("nameserver.updateRecord", params)),
    },
    {
      name: "inwx_dns_record_delete",
      description: "Delete a DNS record",
      run: async (params, context) => withClient(context, "inwx_dns_record_delete", async (client) => client.call<JsonMap>("nameserver.deleteRecord", params)),
    },
    {
      name: "inwx_dnssec_list",
      description: "List DNSSEC keys and status",
      run: async (params, context) => withClient(context, "inwx_dnssec_list", async (client) => {
        const res = await client.call<JsonMap>("dnssec.info", params);
        const keys = asArray<DnssecKey>(res.key ?? res.keys);
        return { total: keys.length, keys, raw: res };
      }),
    },
    {
      name: "inwx_dnssec_enable",
      description: "Enable DNSSEC for a domain",
      run: async (params, context) => withClient(context, "inwx_dnssec_enable", async (client) => client.call<JsonMap>("dnssec.create", params)),
    },
    {
      name: "inwx_dnssec_disable",
      description: "Disable DNSSEC for a domain",
      run: async (params, context) => withClient(context, "inwx_dnssec_disable", async (client) => client.call<JsonMap>("dnssec.delete", params)),
    },
    {
      name: "inwx_contact_list",
      description: "List contacts in account",
      run: async (params, context) => withClient(context, "inwx_contact_list", async (client) => client.call<JsonMap>("contact.list", params)),
    },
    {
      name: "inwx_contact_create",
      description: "Create contact",
      run: async (params, context) => withClient(context, "inwx_contact_create", async (client) => client.call<JsonMap>("contact.create", params)),
    },
    {
      name: "inwx_contact_update",
      description: "Update contact",
      run: async (params, context) => withClient(context, "inwx_contact_update", async (client) => client.call<JsonMap>("contact.update", params)),
    },
    {
      name: "inwx_whois",
      description: "Get WHOIS data for a domain",
      run: async (params, context) => withClient(context, "inwx_whois", async (client) => {
        const domain = String(params.domain ?? "").trim();
        if (!domain) throw new Error("domain is required");
        return client.call<JsonMap>("domain.whois", { domain });
      }),
    },
    {
      name: "inwx_account_info",
      description: "Get INWX account info and balance",
      run: async (_params, context) => withClient(context, "inwx_account_info", async (client) => client.call<JsonMap>("account.info", {})),
    },
  ];
}
