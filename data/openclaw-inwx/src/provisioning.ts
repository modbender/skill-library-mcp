import { JsonMap } from "./types";

/**
 * Minimal interface matching BoundTool from both openclaw-inwx and
 * openclaw-ispconfig. Avoids a hard npm dependency on either package.
 */
export interface ExternalBoundTool {
  name: string;
  run: (params: JsonMap) => Promise<unknown>;
}

// ---------------------------------------------------------------------------
// Provisioning parameters
// ---------------------------------------------------------------------------

export interface ProvisionDomainHostingParams {
  /** Domain to register and provision (e.g. "example.com") */
  domain: string;
  /** Nameservers to set on the registered domain */
  nameservers: string[];
  /** IP address of the hosting server (used by ISPConfig for the A record) */
  serverIp: string;
  /** Client display name for ISPConfig client creation */
  clientName: string;
  /** Client email for ISPConfig client creation */
  clientEmail: string;
  /** Create mail domain and mailboxes in ISPConfig (default true) */
  createMail?: boolean;
  /** Create database and user in ISPConfig (default true) */
  createDb?: boolean;
  /** ISPConfig server ID override */
  serverId?: number;
  /** INWX registration period in years (default 1) */
  registrationPeriod?: number;
  /** INWX contact handle IDs for domain registration */
  contacts?: JsonMap;
  /** Skip domain registration if already owned (default false) */
  skipRegistration?: boolean;
}

// ---------------------------------------------------------------------------
// Step tracking
// ---------------------------------------------------------------------------

export interface ProvisioningStep {
  step: string;
  status: "ok" | "error" | "skipped";
  data?: unknown;
  error?: string;
}

export interface ProvisioningResult {
  ok: boolean;
  domain: string;
  steps: ProvisioningStep[];
  created: {
    domainRegistered?: boolean;
    nameserversConfigured?: boolean;
    hostingProvisioned?: boolean;
    ispProvisionResult?: unknown;
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function findTool(tools: ExternalBoundTool[], name: string): ExternalBoundTool {
  const tool = tools.find((t) => t.name === name);
  if (!tool) {
    throw new Error(`Required tool "${name}" not found in provided toolset`);
  }
  return tool;
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

// ---------------------------------------------------------------------------
// Main workflow
// ---------------------------------------------------------------------------

/**
 * End-to-end domain-to-hosting provisioning.
 *
 * Orchestrates openclaw-inwx tools (domain registration, nameserver
 * configuration) and openclaw-ispconfig tools (site, DNS zone, mail,
 * database provisioning) into a single composable workflow.
 *
 * Both toolsets are injected at call time so neither plugin carries a
 * hard npm dependency on the other.
 *
 * Workflow steps:
 *  1. Check domain availability via `inwx_domain_check`
 *  2. Register domain via `inwx_domain_register` (unless skipped)
 *  3. Set nameservers via `inwx_nameserver_set`
 *  4. Provision hosting via `isp_provision_site`
 */
export async function provisionDomainWithHosting(
  inwxTools: ExternalBoundTool[],
  ispTools: ExternalBoundTool[],
  params: ProvisionDomainHostingParams,
): Promise<ProvisioningResult> {
  const steps: ProvisioningStep[] = [];
  const created: ProvisioningResult["created"] = {};
  const domain = params.domain.trim();

  if (!domain) {
    return {
      ok: false,
      domain: "",
      steps: [{ step: "validate", status: "error", error: "domain is required" }],
      created,
    };
  }

  // Step 1 - Check domain availability
  let domainAvailable = false;
  try {
    const checkTool = findTool(inwxTools, "inwx_domain_check");
    const raw = await checkTool.run({ domain });
    const checkResult = Array.isArray(raw) ? (raw[0] as JsonMap) : (raw as JsonMap);
    domainAvailable = Boolean(checkResult?.avail);
    steps.push({ step: "domain_check", status: "ok", data: { domain, available: domainAvailable } });
  } catch (err) {
    steps.push({ step: "domain_check", status: "error", error: errorMessage(err) });
    return { ok: false, domain, steps, created };
  }

  // Step 2 - Register domain
  if (params.skipRegistration) {
    steps.push({ step: "domain_register", status: "skipped", data: { reason: "skipRegistration=true" } });
    created.domainRegistered = false;
  } else if (domainAvailable) {
    try {
      const registerTool = findTool(inwxTools, "inwx_domain_register");
      const regResult = await registerTool.run({
        domain,
        period: params.registrationPeriod ?? 1,
        ns: params.nameservers,
        contacts: params.contacts,
      });
      steps.push({ step: "domain_register", status: "ok", data: regResult });
      created.domainRegistered = true;
    } catch (err) {
      steps.push({ step: "domain_register", status: "error", error: errorMessage(err) });
      return { ok: false, domain, steps, created };
    }
  } else {
    steps.push({ step: "domain_register", status: "skipped", data: { reason: "domain not available" } });
    created.domainRegistered = false;
  }

  // Step 3 - Set nameservers
  if (params.nameservers.length > 0) {
    try {
      const nsTool = findTool(inwxTools, "inwx_nameserver_set");
      const nsResult = await nsTool.run({ domain, ns: params.nameservers });
      steps.push({ step: "nameserver_set", status: "ok", data: nsResult });
      created.nameserversConfigured = true;
    } catch (err) {
      steps.push({ step: "nameserver_set", status: "error", error: errorMessage(err) });
      return { ok: false, domain, steps, created };
    }
  } else {
    steps.push({ step: "nameserver_set", status: "skipped", data: { reason: "no nameservers provided" } });
  }

  // Step 4 - Provision hosting via ISPConfig
  try {
    const provisionTool = findTool(ispTools, "isp_provision_site");
    const ispResult = await provisionTool.run({
      domain,
      clientName: params.clientName,
      clientEmail: params.clientEmail,
      serverIp: params.serverIp,
      createMail: params.createMail ?? true,
      createDb: params.createDb ?? true,
      ...(params.serverId != null ? { serverId: params.serverId } : {}),
    });
    steps.push({ step: "isp_provision", status: "ok", data: ispResult });
    created.hostingProvisioned = true;
    created.ispProvisionResult = ispResult;
  } catch (err) {
    steps.push({ step: "isp_provision", status: "error", error: errorMessage(err) });
    return { ok: false, domain, steps, created };
  }

  return { ok: true, domain, steps, created };
}
