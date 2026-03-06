import type { GatewayBrowserClient } from "../gateway";
import type { ZapierState } from "../views/zapier";

export function initialZapierState(): ZapierState {
  return {
    loading: false,
    configured: false,
    mcpUrl: "",
    showForm: false,
    toolCount: undefined,
    error: null,
    success: null,
    testing: false,
    tools: [],
  };
}

type SetState = (fn: (prev: ZapierState) => ZapierState) => void;

export async function loadZapierState(
  client: GatewayBrowserClient,
  setState: SetState
): Promise<void> {
  setState((prev) => ({ ...prev, loading: true, error: null }));

  try {
    const result = await client.request("zapier.status", {}) as {
      configured?: boolean;
      mcpUrl?: string;
      toolCount?: number;
      testError?: string;
      error?: string;
    };

    if (result.error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: result.error ?? "Unknown error",
      }));
      return;
    }

    setState((prev) => ({
      ...prev,
      loading: false,
      configured: result.configured ?? false,
      mcpUrl: result.mcpUrl ?? "",
      toolCount: result.toolCount,
      error: result.testError ?? null,
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

export async function saveZapierUrl(
  client: GatewayBrowserClient,
  state: ZapierState,
  setState: SetState
): Promise<void> {
  if (!state.mcpUrl.trim()) {
    setState((prev) => ({ ...prev, error: "MCP URL is required" }));
    return;
  }

  setState((prev) => ({ ...prev, loading: true, error: null, success: null }));

  try {
    const result = await client.request("zapier.save", { mcpUrl: state.mcpUrl }) as {
      success?: boolean;
      toolCount?: number;
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
      toolCount: result.toolCount,
      success: result.message ?? "Zapier connected!",
    }));

    setTimeout(() => {
      setState((prev) => ({ ...prev, success: null }));
    }, 3000);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    setState((prev) => ({
      ...prev,
      loading: false,
      error: `Failed to save: ${message}`,
    }));
  }
}

export async function testZapier(
  client: GatewayBrowserClient,
  state: ZapierState,
  setState: SetState
): Promise<void> {
  setState((prev) => ({ ...prev, testing: true, error: null, success: null }));

  try {
    const result = await client.request("zapier.test", { mcpUrl: state.mcpUrl }) as {
      success?: boolean;
      toolCount?: number;
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
      toolCount: result.toolCount,
      success: `Connection working! ${result.toolCount} tools available.`,
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

export async function disconnectZapier(
  client: GatewayBrowserClient,
  setState: SetState
): Promise<void> {
  setState((prev) => ({ ...prev, loading: true, error: null }));

  try {
    const result = await client.request("zapier.disconnect", {}) as {
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
      mcpUrl: "",
      toolCount: undefined,
      tools: [],
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

export async function loadZapierTools(
  client: GatewayBrowserClient,
  setState: SetState
): Promise<void> {
  try {
    const result = await client.request("zapier.tools", {}) as {
      success?: boolean;
      tools?: Array<{ name: string; description?: string }>;
      error?: string;
    };

    if (!result.success) {
      return;
    }

    setState((prev) => ({
      ...prev,
      tools: result.tools ?? [],
    }));
  } catch {
    // Silently fail - tools list is optional
  }
}
