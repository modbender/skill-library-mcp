import type { GatewayBrowserClient } from "../gateway";
import type { MatonState, MatonConnection, MatonApp } from "../views/maton";

export function initialMatonState(): MatonState {
  return {
    loading: false,
    configured: false,
    apiKey: "",
    showForm: false,
    connectionCount: 0,
    error: null,
    success: null,
    testing: false,
    connections: [],
    apps: [],
    connectingApp: null,
    deletingConnection: null,
    showAppPicker: false,
  };
}

type SetState = (fn: (prev: MatonState) => MatonState) => void;

export async function loadMatonState(
  client: GatewayBrowserClient,
  setState: SetState,
): Promise<void> {
  setState((prev) => ({ ...prev, loading: true, error: null }));

  try {
    // Load status and connections in parallel
    const [statusResult, connectionsResult, appsResult] = await Promise.all([
      client.request("maton.status", {}) as Promise<{
        configured?: boolean;
        connectionCount?: number;
        testError?: string;
        error?: string;
      }>,
      client.request("maton.connections", {}) as Promise<{
        success?: boolean;
        connections?: MatonConnection[];
        error?: string;
      }>,
      client.request("maton.apps", {}) as Promise<{
        success?: boolean;
        apps?: MatonApp[];
        error?: string;
      }>,
    ]);

    if (statusResult.error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: statusResult.error ?? "Unknown error",
      }));
      return;
    }

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: statusResult.configured ?? false,
      connectionCount: statusResult.connectionCount ?? 0,
      error: statusResult.testError ?? null,
      connections: connectionsResult.connections ?? [],
      apps: appsResult.apps ?? [],
    }));
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      loading: false,
      error: `Failed to load status: ${message}`,
    }));
  }
}

export async function saveMatonApiKey(
  client: GatewayBrowserClient,
  state: MatonState,
  setState: SetState,
): Promise<void> {
  if (!state.apiKey.trim()) {
    setState((prev) => ({ ...prev, error: "API key is required" }));
    return;
  }

  setState((prev) => ({ ...prev, loading: true, error: null, success: null }));

  try {
    const result = (await client.request("maton.save", { apiKey: state.apiKey })) as {
      success?: boolean;
      connectionCount?: number;
      message?: string;
      error?: string;
    };

    if (!result.success) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: result.error ?? "Failed to save",
      }));
      return;
    }

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: true,
      showForm: false,
      connectionCount: result.connectionCount ?? 0,
      success: result.message ?? "Maton configured!",
    }));

    // Clear success after a delay
    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);

    // Reload connections
    await loadMatonConnections(client, setState);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      loading: false,
      error: `Failed to save: ${message}`,
    }));
  }
}

export async function testMaton(
  client: GatewayBrowserClient,
  setState: SetState,
): Promise<void> {
  setState((prev) => ({ ...prev, testing: true, error: null, success: null }));

  try {
    const result = (await client.request("maton.test", {})) as {
      success?: boolean;
      connectionCount?: number;
      error?: string;
    };

    if (!result.success) {
      setState((prev) => ({
        ...prev,
        testing: false,
        error: `Test failed: ${result.error ?? "Unknown error"}`,
      }));
      return;
    }

    setState((prev) => ({
      ...prev,
      testing: false,
      connectionCount: result.connectionCount ?? prev.connectionCount,
      success: `Connection working! ${result.connectionCount} connections.`,
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      testing: false,
      error: `Test failed: ${message}`,
    }));
  }
}

export async function disconnectMaton(
  client: GatewayBrowserClient,
  setState: SetState,
): Promise<void> {
  setState((prev) => ({ ...prev, loading: true, error: null }));

  try {
    const result = (await client.request("maton.disconnect", {})) as {
      success?: boolean;
      message?: string;
      error?: string;
    };

    if (!result.success) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: result.error ?? "Failed to disconnect",
      }));
      return;
    }

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: false,
      apiKey: "",
      connectionCount: 0,
      connections: [],
      success: result.message ?? "Disconnected",
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      loading: false,
      error: `Failed to disconnect: ${message}`,
    }));
  }
}

export async function loadMatonConnections(
  client: GatewayBrowserClient,
  setState: SetState,
): Promise<void> {
  try {
    const result = (await client.request("maton.connections", {})) as {
      success?: boolean;
      connections?: MatonConnection[];
      error?: string;
    };

    if (!result.success) {
      return;
    }

    setState((prev) => ({
      ...prev,
      connections: result.connections ?? [],
      connectionCount: result.connections?.filter((c) => c.status === "ACTIVE").length ?? 0,
    }));
  } catch {
    // Silently fail - connections list is optional
  }
}

export async function connectMatonApp(
  client: GatewayBrowserClient,
  appId: string,
  setState: SetState,
): Promise<void> {
  setState((prev) => ({ ...prev, connectingApp: appId, error: null }));

  try {
    const result = (await client.request("maton.connect", { app: appId })) as {
      success?: boolean;
      connectionId?: string;
      oauthUrl?: string;
      message?: string;
      error?: string;
    };

    if (!result.success) {
      setState((prev) => ({
        ...prev,
        connectingApp: null,
        error: result.error ?? "Failed to create connection",
      }));
      return;
    }

    // If there's an OAuth URL, open it
    if (result.oauthUrl) {
      window.open(result.oauthUrl, "_blank");
      setState((prev) => ({
        ...prev,
        connectingApp: null,
        showAppPicker: false,
        success: "OAuth window opened. Complete the authorization flow.",
      }));
    } else {
      setState((prev) => ({
        ...prev,
        connectingApp: null,
        showAppPicker: false,
        success: result.message ?? "Connection created",
      }));
    }

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 5000);

    // Reload connections after a short delay
    setTimeout(async () => {
      await loadMatonConnections(client, setState);
    }, 1000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      connectingApp: null,
      error: `Failed to connect: ${message}`,
    }));
  }
}

export async function deleteMatonConnection(
  client: GatewayBrowserClient,
  connectionId: string,
  setState: SetState,
): Promise<void> {
  setState((prev) => ({ ...prev, deletingConnection: connectionId, error: null }));

  try {
    const result = (await client.request("maton.delete", { connectionId })) as {
      success?: boolean;
      message?: string;
      error?: string;
    };

    if (!result.success) {
      setState((prev) => ({
        ...prev,
        deletingConnection: null,
        error: result.error ?? "Failed to delete connection",
      }));
      return;
    }

    // Remove the connection from state
    setState((prev) => ({
      ...prev,
      deletingConnection: null,
      connections: prev.connections.filter((c) => c.connection_id !== connectionId),
      connectionCount: prev.connections.filter(
        (c) => c.connection_id !== connectionId && c.status === "ACTIVE",
      ).length,
      success: result.message ?? "Connection deleted",
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      deletingConnection: null,
      error: `Failed to delete: ${message}`,
    }));
  }
}

export async function loadMatonApps(
  client: GatewayBrowserClient,
  setState: SetState,
): Promise<void> {
  try {
    const result = (await client.request("maton.apps", {})) as {
      success?: boolean;
      apps?: MatonApp[];
      error?: string;
    };

    if (!result.success) {
      return;
    }

    setState((prev) => ({
      ...prev,
      apps: result.apps ?? [],
    }));
  } catch {
    // Silently fail
  }
}
