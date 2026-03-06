import type { AgentPipedreamState, AgentConnectedApp } from "../views/agents-panel-pipedream.ts";
import { ALL_APPS } from "../views/pipedream.ts";
import type { GatewayClient } from "../gateway.ts";

type SetState = (fn: (prev: AgentPipedreamState) => AgentPipedreamState) => void;

function resolveAppMeta(slug: string): { name: string; icon: string } {
  const app = ALL_APPS.find((a) => a.slug === slug);
  return { name: app?.name ?? slug, icon: app?.icon ?? "🔌" };
}

export async function loadAgentPipedreamState(
  client: GatewayClient,
  agentId: string,
  setState: SetState,
): Promise<void> {
  setState((p) => ({ ...p, loading: true, error: null }));
  try {
    const result = (await client.request("pipedream.agent.status", { agentId })) as {
      configured: boolean;
      globalConfigured: boolean;
      environment: "development" | "production";
      externalUserId: string;
      enabledApps: string[];
      connectedApps: string[] | Array<{ slug: string; name?: string; accountName?: string; toolCount?: number }>;
    };
    // Normalize connectedApps — backend may return slugs or objects
    const connectedApps: AgentConnectedApp[] = (result.connectedApps ?? []).map((app) => {
      if (typeof app === "string") {
        return { slug: app, ...resolveAppMeta(app) };
      }
      return { ...resolveAppMeta(app.slug), ...app };
    });
    setState((p) => ({
      ...p,
      loading: false,
      configured: result.configured,
      globalConfigured: result.globalConfigured,
      environment: result.environment ?? "development",
      externalUserId: result.externalUserId,
      enabledApps: result.enabledApps ?? [],
      connectedApps,
    }));
  } catch (err) {
    setState((p) => ({ ...p, loading: false, error: String(err) }));
  }
}

export async function saveAgentPipedream(
  client: GatewayClient,
  agentId: string,
  externalUserId: string,
  setState: SetState,
): Promise<void> {
  setState((p) => ({ ...p, saving: true, error: null }));
  try {
    await client.request("pipedream.agent.save", { agentId, externalUserId });
    setState((p) => ({ ...p, saving: false, editingUserId: false, configured: true, externalUserId }));
  } catch (err) {
    setState((p) => ({ ...p, saving: false, error: String(err) }));
  }
}

export async function deleteAgentPipedream(
  client: GatewayClient,
  agentId: string,
  setState: SetState,
): Promise<void> {
  setState((p) => ({ ...p, saving: true, error: null }));
  try {
    await client.request("pipedream.agent.delete", { agentId });
    setState((p) => ({ ...p, saving: false, configured: false, externalUserId: "", enabledApps: [], connectedApps: [] }));
  } catch (err) {
    setState((p) => ({ ...p, saving: false, error: String(err) }));
  }
}

export async function connectAgentApp(
  client: GatewayClient,
  agentId: string,
  appSlug: string,
  setState: SetState,
): Promise<void> {
  setState((p) => ({ ...p, connectingApp: appSlug, error: null, success: null }));
  try {
    const result = (await client.request("pipedream.connect", { agentId, appSlug })) as { connectUrl?: string; error?: string };
    if (result.connectUrl) {
      window.open(result.connectUrl, "_blank");
      setState((p) => ({
        ...p,
        connectingApp: null,
        success: `Authorization opened for ${appSlug}. Complete OAuth in the new tab, then refresh.`,
      }));
    } else {
      setState((p) => ({ ...p, connectingApp: null, error: result.error ?? "No connect URL returned" }));
    }
  } catch (err) {
    setState((p) => ({ ...p, connectingApp: null, error: String(err) }));
  }
}

export async function disconnectAgentApp(
  client: GatewayClient,
  agentId: string,
  appSlug: string,
  setState: SetState,
): Promise<void> {
  setState((p) => ({ ...p, disconnectingApp: appSlug, error: null }));
  try {
    await client.request("pipedream.disconnect", { agentId, appSlug });
    setState((p) => ({
      ...p,
      disconnectingApp: null,
      connectedApps: p.connectedApps.filter((a) => a.slug !== appSlug),
      success: `${appSlug} disconnected.`,
    }));
  } catch (err) {
    setState((p) => ({ ...p, disconnectingApp: null, error: String(err) }));
  }
}


export async function activateAgentApp(
  client: GatewayClient,
  agentId: string,
  appSlug: string,
  setState: SetState,
): Promise<void> {
  setState((p) => ({ ...p, activatingApp: appSlug, error: null, success: null }));
  try {
    const result = (await client.request("pipedream.activate", { agentId, appSlug })) as {
      ok?: boolean;
      error?: string;
      serverName?: string;
      toolCount?: number;
      tools?: Array<{ name: string; description?: string }>;
    };
    if (result.ok) {
      setState((p) => ({
        ...p,
        activatingApp: null,
        success: `${appSlug} activated! ${result.toolCount ?? 0} tools loaded.`,
        connectedApps: p.connectedApps.map((a) =>
          a.slug === appSlug
            ? { ...a, active: true, toolCount: result.toolCount, tools: result.tools }
            : a,
        ),
      }));
    } else {
      setState((p) => ({ ...p, activatingApp: null, error: result.error ?? "Activation failed" }));
    }
  } catch (err) {
    setState((p) => ({ ...p, activatingApp: null, error: String(err) }));
  }
}

export async function testAgentApp(
  client: GatewayClient,
  agentId: string,
  appSlug: string,
  setState: SetState,
): Promise<void> {
  setState((p) => ({ ...p, testingApp: appSlug, error: null, success: null }));
  try {
    const result = (await client.request("pipedream.test", { agentId, appSlug })) as {
      ok: boolean; message?: string; toolCount?: number; tools?: Array<{ name: string; description?: string }>;
    };
    const toolSummary = result.ok && result.toolCount != null
      ? ` — ${result.toolCount} tool${result.toolCount === 1 ? "" : "s"} loaded`
      : "";
    setState((p) => ({
      ...p,
      testingApp: null,
      success: result.ok
        ? `${appSlug} connection OK${toolSummary}`
        : `${appSlug} test failed: ${result.message}`,
      // Store tools on the matched connected app
      connectedApps: result.ok && result.tools
        ? p.connectedApps.map((app) =>
            app.slug === appSlug
              ? { ...app, toolCount: result.toolCount ?? app.toolCount, tools: result.tools ?? [] }
              : app
          )
        : p.connectedApps,
    }));
  } catch (err) {
    setState((p) => ({ ...p, testingApp: null, error: String(err) }));
  }
}
