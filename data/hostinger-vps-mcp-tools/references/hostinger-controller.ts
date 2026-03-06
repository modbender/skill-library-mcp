import type { GatewayBrowserClient } from "../gateway";
import type { HostingerState } from "../views/hostinger.ts";

export function initialHostingerState(): HostingerState {
  return {
    loading: false,
    configured: false,
    apiToken: "",
    githubRepo: "",
    showForm: false,
    toolCount: undefined,
    error: null,
    success: null,
    tools: [],
    expandedGroups: new Set<string>(),
  };
}

type SetState = (fn: (prev: HostingerState) => HostingerState) => void;

export async function loadHostingerState(
  client: GatewayBrowserClient,
  setState: SetState
): Promise<void> {
  setState((prev) => ({ ...prev, loading: true, error: null }));

  try {
    const result = await client.request("hostinger.status", {}) as {
      configured?: boolean;
      apiToken?: string;
      githubRepo?: string;
      error?: string;
    };

    if (result.error) {
      setState((prev) => ({ ...prev, loading: false, error: result.error ?? "Unknown error" }));
      return;
    }

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: result.configured ?? false,
      apiToken: result.apiToken ?? "",
      githubRepo: result.githubRepo ?? "",
      showForm: false,
    }));
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({ ...prev, loading: false, error: `Failed to load status: ${message}` }));
  }
}

export async function saveHostingerConfig(
  client: GatewayBrowserClient,
  state: HostingerState,
  setState: SetState
): Promise<void> {
  if (!state.apiToken.trim()) {
    setState((prev) => ({ ...prev, error: "API token is required" }));
    return;
  }

  setState((prev) => ({ ...prev, loading: true, error: null, success: null }));

  try {
    const result = await client.request("hostinger.save", {
      apiToken: state.apiToken,
      githubRepo: state.githubRepo,
    }) as { success?: boolean; message?: string; error?: string };

    if (!result.success) {
      setState((prev) => ({ ...prev, loading: false, error: result.error ?? "Failed to save" }));
      return;
    }

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: true,
      showForm: false,
      success: result.message ?? "Hostinger API configured!",
    }));

    setTimeout(() => setState((prev) => ({ ...prev, success: null })), 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({ ...prev, loading: false, error: `Failed to save: ${message}` }));
  }
}

export async function disconnectHostinger(
  client: GatewayBrowserClient,
  setState: SetState
): Promise<void> {
  setState((prev) => ({ ...prev, loading: true, error: null }));

  try {
    const result = await client.request("hostinger.disconnect", {}) as {
      success?: boolean;
      message?: string;
      error?: string;
    };

    if (!result.success) {
      setState((prev) => ({ ...prev, loading: false, error: result.error ?? "Failed to disconnect" }));
      return;
    }

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: false,
      apiToken: "",
      githubRepo: "",
      tools: [],
      success: result.message ?? "Disconnected",
    }));

    setTimeout(() => setState((prev) => ({ ...prev, success: null })), 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({ ...prev, loading: false, error: `Failed to disconnect: ${message}` }));
  }
}

export async function loadHostingerTools(
  client: GatewayBrowserClient,
  setState: SetState
): Promise<void> {
  try {
    const result = await client.request("hostinger.tools", {}) as {
      success?: boolean;
      tools?: Array<{ name: string; description?: string }>;
      error?: string;
    };

    if (!result.success) return;

    setState((prev) => ({ ...prev, tools: result.tools ?? [] }));
  } catch {
    // Silently fail
  }
}
