/**
 * 1Password UI - Settings/Loading Logic
 * 
 * Add this function to ui/src/ui/app-settings.ts
 * And import GatewayBrowserClient from "./gateway"
 */

import type { GatewayBrowserClient } from "./gateway";

// 1Password status loading
type OnePasswordHost = {
  onePasswordLoading: boolean;
  onePasswordMode: "cli" | "connect" | "unknown";
  onePasswordStatus: {
    installed?: boolean;
    signedIn?: boolean;
    connected?: boolean;
    account?: string;
    email?: string;
    host?: string;
    error?: string;
  };
  onePasswordError: string | null;
  client: GatewayBrowserClient | null;
};

export async function load1PasswordStatus(host: OnePasswordHost): Promise<void> {
  if (!host.client) return;

  host.onePasswordLoading = true;
  host.onePasswordError = null;

  try {
    const result = (await host.client.call("1password.status")) as {
      mode: string;
      installed?: boolean;
      signedIn?: boolean;
      connected?: boolean;
      account?: string;
      email?: string;
      host?: string;
      error?: string;
    };

    host.onePasswordMode = result.mode as "cli" | "connect" | "unknown";
    host.onePasswordStatus = {
      installed: result.installed,
      signedIn: result.signedIn,
      connected: result.connected,
      account: result.account,
      email: result.email,
      host: result.host,
      error: result.error,
    };
  } catch (e) {
    host.onePasswordError = e instanceof Error ? e.message : String(e);
  } finally {
    host.onePasswordLoading = false;
  }
}
