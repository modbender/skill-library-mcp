import { html, nothing, type TemplateResult } from "lit";

interface OnePasswordViewState {
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
  onePasswordSigningIn: boolean;
  gatewayClient: { call: (method: string, params?: unknown) => Promise<unknown> } | null;
}

export function renderOnePassword(state: OnePasswordViewState): TemplateResult {
  return html`
    <div class="page-content">
      <div class="section-header">
        <div class="header-info">
          <h2>🔐 1Password</h2>
          <span
            class="status-badge ${state.onePasswordStatus.signedIn || state.onePasswordStatus.connected ? "connected" : "disconnected"}"
          >
            ${state.onePasswordStatus.signedIn || state.onePasswordStatus.connected ? "Connected" : "Not Connected"}
          </span>
          ${state.onePasswordMode === "connect"
            ? html`<span class="mode-badge">Docker/Connect</span>`
            : state.onePasswordMode === "cli"
              ? html`<span class="mode-badge">CLI</span>`
              : nothing}
        </div>
        <div class="header-actions">
          <button @click=${() => loadOnePasswordStatus(state)} ?disabled=${state.onePasswordLoading}>
            Refresh
          </button>
        </div>
      </div>

      ${state.onePasswordLoading
        ? html`<div class="loading">Loading...</div>`
        : renderContent(state)}

      ${state.onePasswordError ? html`<div class="error-banner">${state.onePasswordError}</div>` : nothing}
    </div>
  `;
}

function renderContent(state: OnePasswordViewState): TemplateResult {
  if (state.onePasswordMode === "cli" && state.onePasswordStatus.installed === false) {
    return html`
      <div class="setup-panel">
        <h3>1Password CLI Not Found</h3>
        <p>Install the 1Password CLI to continue:</p>
        <pre><code>brew install 1password-cli</code></pre>
        <p>
          Or download from
          <a href="https://1password.com/downloads/command-line/" target="_blank">1password.com</a>
        </p>
        <button @click=${() => loadOnePasswordStatus(state)}>Check Again</button>
      </div>
    `;
  }

  if (!state.onePasswordStatus.signedIn && !state.onePasswordStatus.connected) {
    return html`
      <div class="setup-panel">
        <h3>Sign In to 1Password</h3>
        <p>Connect your 1Password account to securely manage credentials.</p>

        ${state.onePasswordStatus.error
          ? html`
              <div class="error-message">
                ${state.onePasswordStatus.error}
                ${state.onePasswordStatus.error.includes("authorization")
                  ? html`<p class="hint">Make sure the 1Password app is unlocked and CLI integration is enabled.</p>`
                  : nothing}
              </div>
            `
          : nothing}

        <div class="signin-form">
          <button
            @click=${() => signInOnePassword(state)}
            ?disabled=${state.onePasswordSigningIn}
            class="btn btn--primary"
          >
            ${state.onePasswordSigningIn ? "Signing in..." : "Sign In with 1Password"}
          </button>
        </div>

        <div class="help-text">
          <h4>Requirements</h4>
          <ul>
            <li>1Password desktop app installed and running</li>
            <li>CLI integration enabled: Settings → Developer → "Integrate with 1Password CLI"</li>
          </ul>
        </div>
      </div>
    `;
  }

  return html`
    <div class="connected-content">
      <div class="account-info">
        ${state.onePasswordMode === "connect"
          ? html`
              <span class="label">Connect Server:</span>
              <span class="value">${state.onePasswordStatus.host}</span>
            `
          : html`
              <span class="label">Account:</span>
              <span class="value">${state.onePasswordStatus.account || "Unknown"}</span>
              ${state.onePasswordStatus.email
                ? html`<span class="email">(${state.onePasswordStatus.email})</span>`
                : nothing}
            `}
      </div>

      <div class="section">
        <h3>Credential Mappings</h3>
        <p>Map 1Password items to skill configurations.</p>
        <p class="text-muted">
          Mapping UI coming soon. For now, use the CLI:
          <code>python3 ~/clawd/skills/1password-ui/scripts/op-helper.py status</code>
        </p>
      </div>
    </div>
  `;
}

async function loadOnePasswordStatus(state: OnePasswordViewState): Promise<void> {
  if (!state.gatewayClient) return;

  state.onePasswordLoading = true;
  state.onePasswordError = null;

  try {
    const result = (await state.gatewayClient.call("1password.status")) as {
      mode: string;
      installed?: boolean;
      signedIn?: boolean;
      connected?: boolean;
      account?: string;
      email?: string;
      host?: string;
      error?: string;
    };

    state.onePasswordMode = result.mode as "cli" | "connect" | "unknown";
    state.onePasswordStatus = {
      installed: result.installed,
      signedIn: result.signedIn,
      connected: result.connected,
      account: result.account,
      email: result.email,
      host: result.host,
      error: result.error,
    };
  } catch (e) {
    state.onePasswordError = e instanceof Error ? e.message : String(e);
  } finally {
    state.onePasswordLoading = false;
  }
}

async function signInOnePassword(state: OnePasswordViewState): Promise<void> {
  if (!state.gatewayClient) return;

  state.onePasswordSigningIn = true;
  state.onePasswordError = null;

  try {
    const result = (await state.gatewayClient.call("1password.signin")) as {
      success: boolean;
      error?: string;
    };

    if (result.success) {
      await loadOnePasswordStatus(state);
    } else {
      state.onePasswordError = result.error || "Sign-in failed";
    }
  } catch (e) {
    state.onePasswordError = e instanceof Error ? e.message : String(e);
  } finally {
    state.onePasswordSigningIn = false;
  }
}

export { loadOnePasswordStatus };
