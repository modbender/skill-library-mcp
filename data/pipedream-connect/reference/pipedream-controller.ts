import type { GatewayBrowserClient } from "../gateway";
import type { PipedreamState, PipedreamCredentials, PipedreamApp } from "../views/pipedream";

export function initialPipedreamState(): PipedreamState {
  return {
    loading: false,
    configured: false,
    credentials: {
      clientId: "",
      clientSecret: "",
      projectId: "",
      environment: "development",
    },
    showCredentialsForm: false,
    connectedApps: [],
    availableApps: [],
    error: null,
    success: null,
    testingApp: null,
    connectingApp: null,
    refreshingApp: null,
    externalUserId: "clawdbot",
    // App browser modal
    showAppBrowser: false,
    appBrowserSearch: "",
    allApps: [],
    loadingApps: false,
    manualSlug: "",
  };
}

type SetState = (fn: (prev: PipedreamState) => PipedreamState) => void;

async function getPipedreamAccessToken(clientId: string, clientSecret: string): Promise<string> {
  const response = await fetch("https://api.pipedream.com/v1/oauth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      grant_type: "client_credentials",
      client_id: clientId,
      client_secret: clientSecret,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get Pipedream token: ${error}`);
  }

  const data = await response.json();
  if (!data.access_token) {
    throw new Error("No access_token in Pipedream response");
  }

  return data.access_token;
}

export async function loadPipedreamState(
  client: GatewayBrowserClient,
  setState: SetState,
): Promise<void> {
  setState((prev) => ({ ...prev, loading: true, error: null }));

  try {
    const result = await client.request<{
      configured: boolean;
      credentials: {
        clientId: string;
        hasSecret: boolean;
        projectId: string;
        environment: string;
        externalUserId: string;
      } | null;
      apps: Array<{ slug: string; name: string; serverName: string }>;
      error?: string;
    }>("pipedream.status", {});

    if (result.error) {
      setState((prev) => ({ ...prev, loading: false, error: result.error }));
      return;
    }

    const connectedApps: PipedreamApp[] = result.apps.map((app) => ({
      slug: app.slug,
      name: app.name,
      icon: appSlugToIcon(app.slug),
      connected: true,
      serverName: app.serverName,
    }));

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: result.configured,
      credentials: result.credentials
        ? {
            clientId: result.credentials.clientId,
            clientSecret: result.credentials.hasSecret ? "••••••••" : "", // Placeholder dots if secret is saved
            projectId: result.credentials.projectId,
            environment: result.credentials.environment as "development" | "production",
          }
        : prev.credentials,
      externalUserId: result.credentials?.externalUserId || "clawdbot",
      connectedApps,
    }));
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      loading: false,
      error: `Failed to load Pipedream state: ${message}`,
    }));
  }
}

export async function savePipedreamCredentials(
  client: GatewayBrowserClient,
  state: PipedreamState,
  setState: SetState,
): Promise<void> {
  const { credentials, externalUserId } = state;

  if (!credentials.clientId.trim() || !credentials.clientSecret.trim()) {
    setState((prev) => ({ ...prev, error: "Client ID and Secret are required" }));
    return;
  }

  if (!credentials.projectId.trim()) {
    setState((prev) => ({ ...prev, error: "Project ID is required" }));
    return;
  }

  setState((prev) => ({ ...prev, loading: true, error: null, success: null }));

  try {
    // Validate credentials via backend (avoids CORS issues with direct Pipedream API calls)
    const result = await client.request<{ success: boolean; error?: string; accessToken?: string }>(
      "pipedream.saveCredentials",
      {
        clientId: credentials.clientId,
        clientSecret: credentials.clientSecret,
        projectId: credentials.projectId,
        environment: credentials.environment,
        externalUserId,
      },
    );

    if (!result.success) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: result.error || "Failed to validate credentials",
      }));
      return;
    }

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: true,
      showCredentialsForm: false,
      success: "Credentials validated! You can now connect apps.",
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      loading: false,
      error: `Failed to save credentials: ${message}`,
    }));
  }
}

export async function connectPipedreamApp(
  client: GatewayBrowserClient,
  appSlug: string,
  _state: PipedreamState,
  setState: SetState,
): Promise<void> {
  console.log("[Pipedream] connectPipedreamApp called for:", appSlug);

  setState((prev) => ({ ...prev, connectingApp: appSlug, error: null, success: null }));

  try {
    // Get access token and credentials from backend
    const tokenResult = await client.request<{
      success: boolean;
      error?: string;
      accessToken?: string;
      credentials?: {
        clientId: string;
        projectId: string;
        environment: string;
        externalUserId: string;
      };
    }>("pipedream.getToken", {});

    if (!tokenResult.success || !tokenResult.accessToken || !tokenResult.credentials) {
      setState((prev) => ({
        ...prev,
        error: tokenResult.error || "Please configure credentials first.",
        connectingApp: null,
      }));
      return;
    }

    const { accessToken, credentials } = tokenResult;

    // Try to list tools - this checks if OAuth is already completed
    // Note: MCP endpoint uses underscores (google_calendar) not hyphens (google-calendar)
    const mcpAppSlug = appSlug.replace(/-/g, "_");
    const response = await fetch("https://remote.mcp.pipedream.net", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "x-pd-project-id": credentials.projectId,
        "x-pd-environment": credentials.environment,
        "x-pd-external-user-id": credentials.externalUserId,
        "x-pd-app-slug": mcpAppSlug,
        "Content-Type": "application/json",
        Accept: "application/json, text/event-stream",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "tools/list",
      }),
    });

    // Handle SSE or JSON response
    const contentType = response.headers.get("content-type") || "";
    let data: unknown;
    if (contentType.includes("text/event-stream")) {
      // Parse SSE response - extract JSON from event data
      const text = await response.text();
      const lines = text.split("\n");
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            data = JSON.parse(line.slice(6));
            break;
          } catch {
            // continue to next line
          }
        }
      }
      if (!data) {
        throw new Error("No valid JSON found in SSE response");
      }
    } else {
      data = await response.json();
    }

    // Type the response for proper access
    const jsonRpcResponse = data as {
      error?: { message?: string };
      result?: { tools?: unknown[] };
    };

    console.log("[Pipedream] MCP response:", JSON.stringify(jsonRpcResponse, null, 2));

    // Check for errors
    if (jsonRpcResponse.error) {
      throw new Error(jsonRpcResponse.error.message || JSON.stringify(jsonRpcResponse.error));
    }

    const toolCount = jsonRpcResponse.result?.tools?.length || 0;

    // If no tools, OAuth wasn't completed - open the connect popup
    if (toolCount === 0) {
      console.log("[Pipedream] No tools available, opening OAuth flow");

      // Get the connect URL from Pipedream's Connect API
      const connectResult = await client.request<{
        success: boolean;
        error?: string;
        connectUrl?: string;
      }>("pipedream.getConnectUrl", { appSlug });

      if (!connectResult.success || !connectResult.connectUrl) {
        setState((prev) => ({
          ...prev,
          error: connectResult.error || "Failed to get connect URL",
          connectingApp: null,
        }));
        return;
      }

      console.log("[Pipedream] Got connect URL:", connectResult.connectUrl);

      // Open OAuth popup
      const popup = window.open(
        connectResult.connectUrl,
        "pipedream_oauth",
        "width=600,height=700,scrollbars=yes,resizable=yes",
      );

      if (!popup) {
        setState((prev) => ({
          ...prev,
          connectingApp: null,
          error: `Popup blocked. Please allow popups or open this URL manually: ${connectResult.connectUrl}`,
        }));
        return;
      }

      // Show pending state - user needs to complete OAuth
      setState((prev) => ({
        ...prev,
        success: `Authorizing ${appSlugToName(appSlug)}... Complete the OAuth flow in the popup window, then click Connect again to finish setup.`,
        connectingApp: null,
      }));

      return;
    }

    // Save to mcporter config via gateway RPC (backend reads stored credentials)
    const saveResult = await client.request<{
      success: boolean;
      serverName?: string;
      error?: string;
    }>("pipedream.connectApp", {
      appSlug,
      accessToken,
    });

    if (!saveResult.success) {
      throw new Error(saveResult.error || "Failed to save config");
    }

    const newApp: PipedreamApp = {
      slug: appSlug,
      name: appSlugToName(appSlug),
      icon: appSlugToIcon(appSlug),
      connected: true,
      toolCount,
      serverName: saveResult.serverName,
    };

    setState((prev) => ({
      ...prev,
      connectingApp: null,
      connectedApps: [...prev.connectedApps.filter((a) => a.slug !== appSlug), newApp],
      success: `${newApp.name} connected! ${toolCount} tools available.`,
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      connectingApp: null,
      error: `Failed to connect ${appSlug}: ${message}`,
    }));
  }
}

export async function disconnectPipedreamApp(
  client: GatewayBrowserClient,
  appSlug: string,
  state: PipedreamState,
  setState: SetState,
): Promise<void> {
  const app = state.connectedApps.find((a) => a.slug === appSlug);
  const serverName = (app)?.serverName;

  if (!serverName) {
    setState((prev) => ({
      ...prev,
      connectedApps: prev.connectedApps.filter((a) => a.slug !== appSlug),
      success: `${appSlugToName(appSlug)} disconnected.`,
    }));
    return;
  }

  try {
    await client.request("pipedream.disconnectApp", { serverName });

    setState((prev) => ({
      ...prev,
      connectedApps: prev.connectedApps.filter((a) => a.slug !== appSlug),
      success: `${appSlugToName(appSlug)} disconnected.`,
      error: null,
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      error: `Failed to disconnect: ${message}`,
    }));
  }
}

export async function testPipedreamApp(
  client: GatewayBrowserClient,
  appSlug: string,
  _state: PipedreamState,
  setState: SetState,
): Promise<void> {
  setState((prev) => ({ ...prev, testingApp: appSlug, error: null, success: null }));

  try {
    // Get token and credentials from backend
    const tokenResult = await client.request<{
      success: boolean;
      error?: string;
      accessToken?: string;
      credentials?: {
        clientId: string;
        projectId: string;
        environment: string;
        externalUserId: string;
      };
    }>("pipedream.getToken", {});

    if (!tokenResult.success || !tokenResult.accessToken || !tokenResult.credentials) {
      throw new Error(tokenResult.error || "No credentials configured");
    }

    const { accessToken, credentials } = tokenResult;

    const response = await fetch("https://remote.mcp.pipedream.net", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "x-pd-project-id": credentials.projectId,
        "x-pd-environment": credentials.environment,
        "x-pd-external-user-id": credentials.externalUserId,
        "x-pd-app-slug": appSlug.replace(/-/g, "_"),
        "Content-Type": "application/json",
        Accept: "application/json, text/event-stream",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "tools/list",
      }),
    });

    // Handle SSE or JSON response
    const contentType = response.headers.get("content-type") || "";
    let data: unknown;
    if (contentType.includes("text/event-stream")) {
      const text = await response.text();
      const lines = text.split("\n");
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            data = JSON.parse(line.slice(6));
            break;
          } catch {
            // continue
          }
        }
      }
      if (!data) {
        throw new Error("No valid JSON found in SSE response");
      }
    } else {
      data = await response.json();
    }

    const jsonRpcResponse = data as {
      error?: { message?: string };
      result?: { tools?: unknown[] };
    };

    if (jsonRpcResponse.error) {
      throw new Error(jsonRpcResponse.error.message || "API error");
    }

    const toolCount = jsonRpcResponse.result?.tools?.length || 0;

    setState((prev) => ({
      ...prev,
      testingApp: null,
      connectedApps: prev.connectedApps.map((a) => (a.slug === appSlug ? { ...a, toolCount } : a)),
      success: `${appSlugToName(appSlug)} is working! ${toolCount} tools available.`,
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      testingApp: null,
      error: `Test failed for ${appSlug}: ${message}`,
    }));
  }
}

export async function refreshPipedreamAppToken(
  client: GatewayBrowserClient,
  appSlug: string,
  state: PipedreamState,
  setState: SetState,
): Promise<void> {
  const app = state.connectedApps.find((a) => a.slug === appSlug);
  const serverName = (app)?.serverName;

  setState((prev) => ({ ...prev, refreshingApp: appSlug, error: null, success: null }));

  try {
    // Get token from backend
    const tokenResult = await client.request<{
      success: boolean;
      error?: string;
      accessToken?: string;
    }>("pipedream.getToken", {});

    if (!tokenResult.success || !tokenResult.accessToken) {
      throw new Error(tokenResult.error || "No credentials configured");
    }

    if (serverName) {
      await client.request("pipedream.refreshToken", {
        serverName,
        accessToken: tokenResult.accessToken,
      });
    }

    setState((prev) => ({
      ...prev,
      refreshingApp: null,
      success: `Token refreshed for ${appSlugToName(appSlug)}.`,
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      refreshingApp: null,
      error: `Failed to refresh token: ${message}`,
    }));
  }
}

function appSlugToName(slug: string): string {
  const names: Record<string, string> = {
    gmail: "Gmail",
    "google-calendar": "Google Calendar",
    "google-sheets": "Google Sheets",
    "google-drive": "Google Drive",
    slack: "Slack",
    notion: "Notion",
    github: "GitHub",
    linear: "Linear",
    discord: "Discord",
    twitter: "Twitter/X",
    airtable: "Airtable",
    hubspot: "HubSpot",
    asana: "Asana",
    trello: "Trello",
    dropbox: "Dropbox",
    openai: "OpenAI",
  };
  return (
    names[slug] ||
    slug
      .split("-")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ")
  );
}

function appSlugToIcon(slug: string): string {
  const icons: Record<string, string> = {
    gmail: "📧",
    "google-calendar": "📅",
    "google-sheets": "📊",
    "google-drive": "📁",
    slack: "💬",
    notion: "📝",
    github: "🐙",
    linear: "📋",
    discord: "🎮",
    twitter: "🐦",
    airtable: "📑",
    hubspot: "🧲",
    asana: "✅",
    trello: "📌",
    dropbox: "📦",
    openai: "🤖",
  };
  return icons[slug] || "🔌";
}

// App Browser functions
export function openAppBrowser(setState: SetState): void {
  setState((prev) => ({
    ...prev,
    showAppBrowser: true,
    appBrowserSearch: "",
    error: null,
    success: null,
  }));
}

export function closeAppBrowser(setState: SetState): void {
  setState((prev) => ({
    ...prev,
    showAppBrowser: false,
    appBrowserSearch: "",
  }));
}

export function setAppBrowserSearch(search: string, setState: SetState): void {
  setState((prev) => ({ ...prev, appBrowserSearch: search }));
}

export function setManualSlug(slug: string, setState: SetState): void {
  setState((prev) => ({ ...prev, manualSlug: slug }));
}

export async function connectManualSlug(
  client: GatewayBrowserClient,
  state: PipedreamState,
  setState: SetState,
): Promise<void> {
  const slug = state.manualSlug.trim().toLowerCase();
  if (!slug) {return;}

  // Use existing connectPipedreamApp with the manual slug
  await connectPipedreamApp(client, slug, state, setState);

  // Clear the manual slug input on success
  setState((prev) => ({
    ...prev,
    manualSlug: "",
  }));
}


// Load per-agent Pipedream summaries for the global tab
export async function loadPipedreamAgentSummaries(
  client: GatewayBrowserClient,
  setState: SetState,
): Promise<void> {
  try {
    // Get agent list
    const agentsResult = await client.request<{
      agents?: Array<{ id: string }>;
    }>("agents.list", {});
    const agents = agentsResult?.agents ?? [];
    if (agents.length === 0) {return;}

    // Fetch per-agent status in parallel
    const summaries = await Promise.all(
      agents.map(async (agent) => {
        try {
          const status = await client.request<{
            configured: boolean;
            externalUserId: string;
            connectedApps: string[];
          }>("pipedream.agent.status", { agentId: agent.id });
          return {
            agentId: agent.id,
            configured: status.configured,
            externalUserId: status.externalUserId || agent.id,
            appCount: status.connectedApps?.length ?? 0,
          };
        } catch {
          return { agentId: agent.id, configured: false, externalUserId: agent.id, appCount: 0 };
        }
      }),
    );

    setState((prev) => ({ ...prev, agentSummaries: summaries }));
  } catch {
    // Non-fatal — just don't show agent summaries
  }
}
