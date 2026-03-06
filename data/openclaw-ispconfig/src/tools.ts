import { ISPConfigClient } from "./client";
import { normalizeError } from "./errors";
import { assertToolAllowed } from "./guards";
import { JsonMap, ToolContext, ToolDefinition } from "./types";
import { validateParams } from "./validate";

const KNOWN_METHODS = [
  "server_get_all", "server_get", "client_get_all", "client_get", "client_add", "sites_web_domain_get",
  "sites_web_domain_add", "dns_zone_get_by_user", "dns_zone_add", "dns_rr_get_all_by_zone", "dns_a_add",
  "dns_aaaa_add", "dns_mx_add", "dns_txt_add", "dns_cname_add", "dns_a_delete", "dns_aaaa_delete",
  "dns_mx_delete", "dns_txt_delete", "dns_cname_delete", "mail_domain_get", "mail_domain_add", "mail_user_get",
  "mail_user_add", "mail_user_delete", "sites_database_get_all_by_user", "sites_database_add",
  "sites_database_user_add", "sites_shell_user_add", "sites_ftp_user_add", "sites_cron_get", "sites_cron_add",
  "sites_web_domain_update",
];

function toNumber(value: unknown, fallback?: number): number {
  const n = Number(value);
  if (Number.isFinite(n)) {
    return n;
  }
  if (fallback === undefined) {
    throw new Error(`Expected numeric value, got ${String(value)}`);
  }
  return fallback;
}

function dnsMethodForType(type: string, action: "add" | "delete"): string {
  const suffix = action === "add" ? "add" : "delete";
  switch (type.toUpperCase()) {
    case "A": return `dns_a_${suffix}`;
    case "AAAA": return `dns_aaaa_${suffix}`;
    case "MX": return `dns_mx_${suffix}`;
    case "TXT": return `dns_txt_${suffix}`;
    case "CNAME": return `dns_cname_${suffix}`;
    default: throw new Error(`Unsupported DNS record type: ${type}`);
  }
}

async function withClient<T>(context: ToolContext, toolName: string, fn: (client: ISPConfigClient) => Promise<T>): Promise<T> {
  assertToolAllowed(context.config, toolName);
  const client = new ISPConfigClient(context.config);
  try {
    return await fn(client);
  } finally {
    await client.logout();
  }
}

async function fetchSites(client: ISPConfigClient): Promise<JsonMap[]> {
  const direct = await client.call<JsonMap[]>("sites_web_domain_get", {});
  if (Array.isArray(direct) && direct.length > 0) {
    return direct;
  }

  const fallback: JsonMap[] = [];
  for (let id = 1; id <= 100; id += 1) {
    try {
      const site = await client.call<JsonMap>("sites_web_domain_get", { primary_id: id });
      if (site && typeof site === "object" && site.domain) {
        fallback.push(site);
      }
    } catch {
      // ignore gaps and permission misses
    }
  }
  return fallback;
}

export function createTools(): ToolDefinition[] {
  const raw: ToolDefinition[] = [
    {
      name: "isp_methods_list",
      description: "Discover available ISPConfig API methods (dynamic via get_function_list, falls back to probing known methods)",
      run: async (_params, context) => withClient(context, "isp_methods_list", async (client) => {
        // Try dynamic discovery first (ISPConfig 3.2+)
        try {
          const functions = await client.call<string[]>("get_function_list", {});
          if (Array.isArray(functions) && functions.length > 0) {
            const dynamicSet = new Set(functions);
            const knownAvailable = KNOWN_METHODS.filter((m) => dynamicSet.has(m));
            const knownUnavailable = KNOWN_METHODS.filter((m) => !dynamicSet.has(m));
            const extra = functions.filter((m) => !KNOWN_METHODS.includes(m));
            return {
              discovery: "dynamic",
              available: knownAvailable,
              unavailable: knownUnavailable.map((m) => ({ method: m, reason: "not in get_function_list" })),
              extra,
              totalServer: functions.length,
              totalKnown: KNOWN_METHODS.length,
            };
          }
        } catch {
          // get_function_list not available - fall back to probing
        }

        // Fallback: probe each known method individually
        const available: string[] = [];
        const unavailable: Array<{ method: string; reason: string }> = [];

        for (const method of KNOWN_METHODS) {
          try {
            await client.call(method, {});
            available.push(method);
          } catch (error) {
            const msg = error instanceof Error ? error.message : String(error);
            if (msg.toLowerCase().includes("unknown") || msg.toLowerCase().includes("invalid function")) {
              unavailable.push({ method, reason: msg });
            } else {
              available.push(method);
            }
          }
        }

        return { discovery: "probe", available, unavailable, extra: [], totalServer: 0, totalKnown: KNOWN_METHODS.length };
      }),
    },
    {
      name: "isp_system_info",
      description: "Get ISPConfig server list and server details",
      run: async (_params, context) => withClient(context, "isp_system_info", async (client) => {
        const servers = await client.call<Array<JsonMap>>("server_get_all", {});
        const details: JsonMap[] = [];
        for (const server of servers ?? []) {
          const id = toNumber(server.server_id ?? server.serverid ?? 0, 0);
          if (id > 0) {
            details.push(await client.call<JsonMap>("server_get", { server_id: id }));
          }
        }
        return { servers, details };
      }),
    },
    {
      name: "isp_provision_site",
      description: "Provision client, site, DNS, mail and database in one workflow",
      run: async (params, context) => withClient(context, "isp_provision_site", async (client) => {
        const domain = String(params.domain ?? "").trim();
        const clientName = String(params.clientName ?? "").trim();
        const clientEmail = String(params.clientEmail ?? "").trim();
        const serverIp = String(params.serverIp ?? context.config.defaultServerIp ?? "").trim();
        const createMail = Boolean(params.createMail ?? true);
        const createDb = Boolean(params.createDb ?? true);
        const serverId = toNumber(params.serverId ?? context.config.serverId ?? 1, 1);

        if (!domain || !clientName || !clientEmail) {
          throw new Error("domain, clientName and clientEmail are required");
        }

        const created: JsonMap = {};

        const newClientId = await client.call<number>("client_add", {
          reseller_id: 0,
          params: { company_name: clientName, contact_name: clientName, email: clientEmail },
        });
        created.client_id = newClientId;

        const websiteId = await client.call<number>("sites_web_domain_add", {
          client_id: newClientId,
          params: {
            server_id: serverId,
            ip_address: "*",
            domain,
            type: "vhost",
            active: "y",
            system_user: `web${newClientId}`,
            system_group: `client${newClientId}`,
            php: "php-fpm",
            ssl: "y",
            ssl_letsencrypt: "y",
          },
        });
        created.site_id = websiteId;

        const zoneId = await client.call<number>("dns_zone_add", {
          client_id: newClientId,
          params: {
            server_id: serverId,
            origin: `${domain}.`,
            ns: `ns1.${domain}.`,
            mbox: `hostmaster.${domain}.`,
            active: "Y",
          },
        });
        created.dns_zone_id = zoneId;

        if (serverIp) {
          await client.call("dns_a_add", { client_id: newClientId, params: { zone: zoneId, name: `${domain}.`, data: serverIp, ttl: 3600, active: "Y" } });
          await client.call("dns_cname_add", { client_id: newClientId, params: { zone: zoneId, name: `www.${domain}.`, data: `${domain}.`, ttl: 3600, active: "Y" } });
        }

        await client.call("dns_txt_add", { client_id: newClientId, params: { zone: zoneId, name: `${domain}.`, data: "v=spf1 mx a ~all", ttl: 3600, active: "Y" } });
        await client.call("dns_txt_add", { client_id: newClientId, params: { zone: zoneId, name: `_dmarc.${domain}.`, data: `v=DMARC1; p=none; rua=mailto:postmaster@${domain}`, ttl: 3600, active: "Y" } });

        if (createMail) {
          const mailDomainId = await client.call<number>("mail_domain_add", { client_id: newClientId, params: { server_id: serverId, domain, active: "y" } });
          created.mail_domain_id = mailDomainId;
          await client.call("mail_user_add", { client_id: newClientId, params: { server_id: serverId, login: `info@${domain}`, email: `info@${domain}`, password: `Temp!${Date.now()}` } });
          await client.call("mail_user_add", { client_id: newClientId, params: { server_id: serverId, login: `admin@${domain}`, email: `admin@${domain}`, password: `Temp!${Date.now()}A` } });
        }

        if (createDb) {
          const dbUserId = await client.call<number>("sites_database_user_add", {
            client_id: newClientId,
            params: { server_id: serverId, database_user: `u${newClientId}_${domain.replace(/\W+/g, "").slice(0, 10)}`, database_password: `Temp!${Date.now()}Db` },
          });
          const dbId = await client.call<number>("sites_database_add", {
            client_id: newClientId,
            params: {
              server_id: serverId,
              database_name: `c${newClientId}_${domain.replace(/\W+/g, "").slice(0, 10)}`,
              database_user_id: dbUserId,
              database_charset: "UTF8",
              remote_access: "n",
              active: "y",
            },
          });
          created.database_user_id = dbUserId;
          created.database_id = dbId;
        }

        await client.call("sites_web_domain_update", { client_id: newClientId, primary_id: websiteId, params: { ssl: "y", ssl_letsencrypt: "y" } });

        return { ok: true, domain, created };
      }),
    },
    {
      name: "isp_client_list",
      description: "List clients with details",
      run: async (_params, context) => withClient(context, "isp_client_list", async (client) => {
        const clients = await client.call<Array<JsonMap>>("client_get_all", {});
        const details: JsonMap[] = [];
        for (const c of clients ?? []) {
          const id = toNumber(c.client_id ?? 0, 0);
          if (id > 0) details.push(await client.call<JsonMap>("client_get", { client_id: id }));
        }
        return { total: clients?.length ?? 0, clients: details };
      }),
    },
    {
      name: "isp_client_add",
      description: "Create a new ISPConfig client",
      run: async (params, context) => withClient(context, "isp_client_add", (client) => client.call("client_add", { reseller_id: 0, params })),
    },
    {
      name: "isp_client_get",
      description: "Get client details by client_id",
      run: async (params, context) => withClient(context, "isp_client_get", (client) => client.call("client_get", { client_id: toNumber(params.client_id ?? params.clientId) })),
    },
    {
      name: "isp_sites_list",
      description: "List web sites with optional filters",
      run: async (params, context) => withClient(context, "isp_sites_list", async (client) => {
        if (Object.keys(params).length > 0) {
          return client.call("sites_web_domain_get", params);
        }
        return fetchSites(client);
      }),
    },
    {
      name: "isp_site_get",
      description: "Get one site by primary_id",
      run: async (params, context) => withClient(context, "isp_site_get", (client) => client.call("sites_web_domain_get", { primary_id: toNumber(params.primary_id ?? params.domain_id ?? params.site_id) })),
    },
    {
      name: "isp_site_add",
      description: "Create web site",
      run: async (params, context) => withClient(context, "isp_site_add", (client) => client.call("sites_web_domain_add", params)),
    },
    {
      name: "isp_domains_list",
      description: "List all web domains",
      run: async (_params, context) => withClient(context, "isp_domains_list", async (client) => {
        const sites = await fetchSites(client);
        return sites.map((s) => ({ domain_id: s.domain_id, domain: s.domain, active: s.active }));
      }),
    },
    {
      name: "isp_domain_add",
      description: "Alias for isp_site_add",
      run: async (params, context) => withClient(context, "isp_domain_add", (client) => client.call("sites_web_domain_add", params)),
    },
    {
      name: "isp_dns_zone_list",
      description: "List DNS zones by user",
      run: async (params, context) => withClient(context, "isp_dns_zone_list", (client) => client.call("dns_zone_get_by_user", params)),
    },
    {
      name: "isp_dns_zone_add",
      description: "Create DNS zone",
      run: async (params, context) => withClient(context, "isp_dns_zone_add", (client) => client.call("dns_zone_add", params)),
    },
    {
      name: "isp_dns_record_list",
      description: "List DNS records by zone_id",
      run: async (params, context) => withClient(context, "isp_dns_record_list", (client) => client.call("dns_rr_get_all_by_zone", { zone_id: toNumber(params.zone_id ?? params.zoneId) })),
    },
    {
      name: "isp_dns_record_add",
      description: "Add DNS record using type-specific method",
      run: async (params, context) => withClient(context, "isp_dns_record_add", (client) => {
        const method = dnsMethodForType(String(params.type ?? ""), "add");
        return client.call(method, params);
      }),
    },
    {
      name: "isp_dns_record_delete",
      description: "Delete DNS record using type-specific method",
      run: async (params, context) => withClient(context, "isp_dns_record_delete", (client) => {
        const method = dnsMethodForType(String(params.type ?? ""), "delete");
        return client.call(method, params);
      }),
    },
    {
      name: "isp_mail_domain_list",
      description: "List mail domains",
      run: async (params, context) => withClient(context, "isp_mail_domain_list", (client) => client.call("mail_domain_get", params)),
    },
    {
      name: "isp_mail_domain_add",
      description: "Create mail domain",
      run: async (params, context) => withClient(context, "isp_mail_domain_add", (client) => client.call("mail_domain_add", params)),
    },
    {
      name: "isp_mail_user_list",
      description: "List mail users",
      run: async (params, context) => withClient(context, "isp_mail_user_list", (client) => client.call("mail_user_get", params)),
    },
    {
      name: "isp_mail_user_add",
      description: "Create mail user",
      run: async (params, context) => withClient(context, "isp_mail_user_add", (client) => client.call("mail_user_add", params)),
    },
    {
      name: "isp_mail_user_delete",
      description: "Delete mail user",
      run: async (params, context) => withClient(context, "isp_mail_user_delete", (client) => client.call("mail_user_delete", params)),
    },
    {
      name: "isp_db_list",
      description: "List databases by user",
      run: async (params, context) => withClient(context, "isp_db_list", (client) => client.call("sites_database_get_all_by_user", params)),
    },
    {
      name: "isp_db_add",
      description: "Create database",
      run: async (params, context) => withClient(context, "isp_db_add", (client) => client.call("sites_database_add", params)),
    },
    {
      name: "isp_db_user_add",
      description: "Create database user",
      run: async (params, context) => withClient(context, "isp_db_user_add", (client) => client.call("sites_database_user_add", params)),
    },
    {
      name: "isp_ssl_status",
      description: "Check SSL and Let's Encrypt status for sites",
      run: async (_params, context) => withClient(context, "isp_ssl_status", async (client) => {
        const sites = await fetchSites(client);
        const status = (sites ?? []).map((site) => ({
          domain: site.domain,
          ssl: site.ssl,
          ssl_letsencrypt: site.ssl_letsencrypt,
          active: site.active,
        }));
        return { total: status.length, status };
      }),
    },
    {
      name: "isp_quota_check",
      description: "Check quota values for a client",
      run: async (params, context) => withClient(context, "isp_quota_check", async (client) => {
        const details = await client.call<JsonMap>("client_get", { client_id: toNumber(params.client_id ?? params.clientId) });
        return {
          client_id: details.client_id,
          company_name: details.company_name,
          web_quota: details.web_quota,
          traffic_quota: details.traffic_quota,
        };
      }),
    },
    {
      name: "isp_backup_list",
      description: "Backup list if API supports backup methods",
      run: async (_params, context) => withClient(context, "isp_backup_list", async () => ({
        skipped: true,
        reason: "No backup list method discovered in ISPConfig API",
      })),
    },
    {
      name: "isp_shell_user_add",
      description: "Create shell user",
      run: async (params, context) => withClient(context, "isp_shell_user_add", (client) => client.call("sites_shell_user_add", params)),
    },
    {
      name: "isp_ftp_user_add",
      description: "Create FTP user",
      run: async (params, context) => withClient(context, "isp_ftp_user_add", (client) => client.call("sites_ftp_user_add", params)),
    },
    {
      name: "isp_cron_list",
      description: "List cron jobs",
      run: async (params, context) => withClient(context, "isp_cron_list", (client) => client.call("sites_cron_get", params)),
    },
    {
      name: "isp_cron_add",
      description: "Create cron job",
      run: async (params, context) => withClient(context, "isp_cron_add", (client) => client.call("sites_cron_add", params)),
    },
  ];

  return raw.map((tool) => ({
    ...tool,
    run: async (params: JsonMap, context: ToolContext) => {
      try {
        validateParams(tool.name, params);
        return await tool.run(params, context);
      } catch (err) {
        throw normalizeError(err);
      }
    },
  }));
}
