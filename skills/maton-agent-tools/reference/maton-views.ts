import { html, nothing } from "lit";

export type MatonConnection = {
  connection_id: string;
  status: "ACTIVE" | "PENDING" | "FAILED";
  creation_time: string;
  last_updated_time: string;
  url: string | null;
  app: string;
  metadata: Record<string, unknown>;
};

export type MatonApp = {
  id: string;
  name: string;
};

export type MatonState = {
  loading: boolean;
  configured: boolean;
  apiKey: string;
  showForm: boolean;
  connectionCount: number;
  error: string | null;
  success: string | null;
  testing: boolean;
  connections: MatonConnection[];
  apps: MatonApp[];
  connectingApp: string | null;
  deletingConnection: string | null;
  showAppPicker: boolean;
};

export type MatonProps = MatonState & {
  onConfigure: () => void;
  onSave: () => void;
  onCancel: () => void;
  onApiKeyChange: (value: string) => void;
  onTest: () => void;
  onDisconnect: () => void;
  onRefresh: () => void;
  onLoadConnections: () => void;
  onShowAppPicker: () => void;
  onHideAppPicker: () => void;
  onConnectApp: (appId: string) => void;
  onDeleteConnection: (connectionId: string) => void;
  onOpenOAuthUrl: (url: string) => void;
};

function formatAppName(app: string): string {
  return app
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateString;
  }
}

function getStatusChipClass(status: string): string {
  switch (status) {
    case "ACTIVE":
      return "chip-ok";
    case "PENDING":
      return "chip-warn";
    case "FAILED":
      return "chip-danger";
    default:
      return "";
  }
}

function getAppEmoji(app: string): string {
  const emojiMap: Record<string, string> = {
    gmail: "📧",
    "google-calendar": "📅",
    "google-docs": "📄",
    "google-sheets": "📊",
    "google-drive": "💾",
    "google-slides": "🎨",
    "google-ads": "📢",
    "google-analytics-admin": "📈",
    "google-analytics-data": "📈",
    "google-search-console": "🔍",
    slack: "💬",
    notion: "📝",
    airtable: "🗂️",
    hubspot: "🎯",
    jira: "🎫",
    youtube: "▶️",
    calendly: "📆",
    outlook: "📬",
    apollo: "🚀",
    chargebee: "💳",
  };
  return emojiMap[app] ?? "🔗";
}

function renderConnectionCard(
  connection: MatonConnection,
  props: MatonProps,
) {
  const { connection_id, status, app, last_updated_time, url } = connection;
  const isDeleting = props.deletingConnection === connection_id;

  return html`
    <div
      class="card"
      style="margin-bottom: 12px; padding: 16px;"
    >
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <span style="font-size: 24px;">${getAppEmoji(app)}</span>
          <div>
            <div style="font-weight: 600; font-size: 14px;">
              ${formatAppName(app)}
            </div>
            <div style="font-size: 12px; opacity: 0.7;">
              Updated ${formatDate(last_updated_time)}
            </div>
          </div>
        </div>
        <span class="chip ${getStatusChipClass(status)}">${status}</span>
      </div>

      ${status === "PENDING" && url
        ? html`
            <div class="callout info" style="margin-top: 12px; font-size: 13px;">
              OAuth flow not completed.
              <a
                href="${url}"
                target="_blank"
                rel="noopener noreferrer"
                @click=${() => props.onOpenOAuthUrl(url)}
              >
                Click here to authorize
              </a>
            </div>
          `
        : nothing}

      <div class="row" style="margin-top: 12px; gap: 8px;">
        ${status === "PENDING" && url
          ? html`
              <button
                class="btn small primary"
                @click=${() => window.open(url, "_blank")}
              >
                Authorize
              </button>
            `
          : nothing}
        <button
          class="btn small danger"
          ?disabled=${isDeleting}
          @click=${() => props.onDeleteConnection(connection_id)}
        >
          ${isDeleting ? "Deleting..." : "Delete"}
        </button>
      </div>
    </div>
  `;
}

function renderAppPicker(props: MatonProps) {
  if (!props.showAppPicker) return nothing;

  const connectedAppIds = new Set(props.connections.map((c) => c.app));

  return html`
    <div
      class="modal-backdrop"
      style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      "
      @click=${(e: Event) => {
        if (e.target === e.currentTarget) props.onHideAppPicker();
      }}
    >
      <div
        class="card"
        style="
          max-width: 500px;
          max-height: 80vh;
          overflow: auto;
          padding: 24px;
        "
      >
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <div class="card-title">Connect an App</div>
          <button class="btn small" @click=${props.onHideAppPicker}>×</button>
        </div>

        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
          ${props.apps.map((app) => {
            const isConnected = connectedAppIds.has(app.id);
            const isConnecting = props.connectingApp === app.id;

            return html`
              <button
                class="btn"
                style="
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  justify-content: flex-start;
                  padding: 12px;
                  ${isConnected ? "opacity: 0.5;" : ""}
                "
                ?disabled=${isConnected || isConnecting}
                @click=${() => props.onConnectApp(app.id)}
              >
                <span style="font-size: 20px;">${getAppEmoji(app.id)}</span>
                <span style="flex: 1; text-align: left;">
                  ${app.name}
                  ${isConnected ? html`<span style="font-size: 11px; opacity: 0.7;"> (connected)</span>` : nothing}
                </span>
                ${isConnecting ? html`<span style="font-size: 11px;">...</span>` : nothing}
              </button>
            `;
          })}
        </div>
      </div>
    </div>
  `;
}

export function renderMaton(props: MatonProps) {
  const statusLabel = props.configured ? "Active" : "Not Configured";
  const statusClass = props.configured ? "chip-ok" : "chip-warn";

  const activeConnections = props.connections.filter((c) => c.status === "ACTIVE").length;
  const pendingConnections = props.connections.filter((c) => c.status === "PENDING").length;

  return html`
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start;">
      <div>
        <h1>Maton</h1>
        <p class="muted">Connect to your SaaS tools via Maton AI.</p>
      </div>
      <button
        class="btn"
        ?disabled=${props.loading}
        @click=${props.onRefresh}
        title="Refresh status"
      >
        ${props.loading ? "Loading..." : "↻ Refresh"}
      </button>
    </div>

    ${props.error
      ? html`<div class="callout danger" style="margin-bottom: 16px;">${props.error}</div>`
      : nothing}

    ${props.success
      ? html`<div class="callout success" style="margin-bottom: 16px;">${props.success}</div>`
      : nothing}

    <section class="card">
      <div class="row" style="justify-content: space-between; align-items: flex-start;">
        <div>
          <div class="card-title">
            🔗 Connection Status
            <span class="chip ${statusClass}" style="margin-left: 8px;">${statusLabel}</span>
          </div>
          <div class="card-sub">
            ${props.configured
              ? html`
                  ${activeConnections} active connection${activeConnections !== 1 ? "s" : ""}
                  ${pendingConnections > 0
                    ? html`, ${pendingConnections} pending`
                    : nothing}
                `
              : "Configure your Maton API key to get started."}
          </div>
        </div>
      </div>
    </section>

    <section class="card" style="margin-top: 16px;">
      <div class="row" style="justify-content: space-between; align-items: center;">
        <div class="card-title">🔑 API Key</div>
        ${!props.showForm
          ? html`
              <button class="btn" @click=${props.onConfigure}>
                ${props.configured ? "Edit" : "Configure"}
              </button>
            `
          : nothing}
      </div>

      ${props.showForm
        ? html`
            <div style="margin-top: 12px; padding: 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-secondary);">
              <div class="callout info" style="margin-bottom: 16px; font-size: 13px;">
                Get your API key from your
                <a href="https://maton.ai" target="_blank">Maton dashboard</a>
              </div>

              <label class="field">
                <span>Maton API Key</span>
                <input
                  type="password"
                  .value=${props.apiKey}
                  @input=${(e: Event) => props.onApiKeyChange((e.target as HTMLInputElement).value)}
                  placeholder="maton_..."
                />
              </label>

              <div class="row" style="margin-top: 16px; gap: 8px;">
                <button class="btn primary" ?disabled=${props.loading} @click=${props.onSave}>
                  ${props.loading ? "Saving..." : "Save"}
                </button>
                <button class="btn" @click=${props.onCancel}>Cancel</button>
              </div>
            </div>
          `
        : html`
            <div class="card-sub" style="margin-top: 8px;">
              ${props.configured
                ? html`
                    <div style="margin-top: 12px;">
                      <code>••••••••••••••••</code>
                    </div>
                    <div class="row" style="margin-top: 16px; gap: 8px;">
                      <button
                        class="btn small"
                        ?disabled=${props.testing}
                        @click=${props.onTest}
                      >
                        ${props.testing ? "Testing..." : "Test Connection"}
                      </button>
                      <button class="btn small danger" @click=${props.onDisconnect}>
                        Disconnect
                      </button>
                    </div>
                  `
                : html`<p class="muted">No API key configured. Click "Configure" to get started.</p>`}
            </div>
          `}
    </section>

    ${props.configured
      ? html`
          <section class="card" style="margin-top: 16px;">
            <div class="row" style="justify-content: space-between; align-items: center;">
              <div class="card-title">📱 Connected Apps</div>
              <div class="row" style="gap: 8px;">
                <button class="btn small" @click=${props.onLoadConnections}>
                  Refresh
                </button>
                <button class="btn small primary" @click=${props.onShowAppPicker}>
                  + Connect App
                </button>
              </div>
            </div>

            ${props.connections.length > 0
              ? html`
                  <div style="margin-top: 16px;">
                    ${props.connections.map((conn) => renderConnectionCard(conn, props))}
                  </div>
                `
              : html`
                  <div class="card-sub" style="margin-top: 12px;">
                    <p class="muted">No apps connected yet. Click "Connect App" to get started.</p>
                  </div>
                `}
          </section>
        `
      : nothing}

    <section class="card" style="margin-top: 16px;">
      <div class="card-title">📚 Setup Guide</div>
      <div class="card-sub" style="margin-top: 8px;">
        <ol style="margin: 12px 0; padding-left: 20px; line-height: 1.8;">
          <li>
            <strong>Get your API key</strong> — Sign up at
            <a href="https://maton.ai" target="_blank">maton.ai</a>
            and create an API key
          </li>
          <li><strong>Enter key above</strong> — Paste your API key in the form above</li>
          <li>
            <strong>Connect apps</strong> — Click "Connect App" and complete the OAuth flow
          </li>
          <li>
            <strong>Use naturally</strong> — Your agent can now interact with connected apps
          </li>
        </ol>
      </div>
    </section>

    <section class="card" style="margin-top: 16px;">
      <div class="card-title">🔧 Supported Apps</div>
      <div class="card-sub" style="margin-top: 8px;">
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">
          ${["gmail", "google-calendar", "slack", "notion", "hubspot", "jira", "airtable", "youtube"].map(
            (app) => html`
              <span class="chip">
                ${getAppEmoji(app)} ${formatAppName(app)}
              </span>
            `,
          )}
          <span class="chip">+ many more</span>
        </div>
      </div>
    </section>

    ${renderAppPicker(props)}
  `;
}
