import { html, nothing } from "lit";
import { ALL_APPS, type PipedreamApp } from "./pipedream.js";

export interface AgentPipedreamState {
  loading: boolean;
  error: string | null;
  success: string | null;
  configured: boolean;
  globalConfigured: boolean;
  environment: "development" | "production";
  externalUserId: string;
  enabledApps: string[];
  connectedApps: AgentConnectedApp[];
  saving: boolean;
  editingUserId: boolean;
  draftUserId: string;
  // App browser
  showAppBrowser: boolean;
  appBrowserSearch: string;
  connectingApp: string | null;
  testingApp: string | null;
  disconnectingApp: string | null;
  activatingApp: string | null;
  manualSlug: string;
  expandedApps: Set<string>;
}

export interface AgentConnectedAppTool {
  name: string;
  description?: string;
}

export interface AgentConnectedApp {
  slug: string;
  name: string;
  icon: string;
  accountName?: string;
  active?: boolean;
  toolCount?: number;
  tools?: AgentConnectedAppTool[];
}

export function initialAgentPipedreamState(): AgentPipedreamState {
  return {
    loading: false,
    error: null,
    success: null,
    configured: false,
    globalConfigured: false,
    environment: "development",
    externalUserId: "",
    enabledApps: [],
    connectedApps: [],
    saving: false,
    editingUserId: false,
    draftUserId: "",
    showAppBrowser: false,
    appBrowserSearch: "",
    connectingApp: null,
    testingApp: null,
    disconnectingApp: null,
    activatingApp: null,
    manualSlug: "",
    expandedApps: new Set(),
  };
}

export interface AgentPipedreamProps extends AgentPipedreamState {
  agentId: string;
  onSave: (externalUserId: string) => void;
  onDelete: () => void;
  onEditUserId: (editing: boolean) => void;
  onDraftUserIdChange: (value: string) => void;
  onRefresh: () => void;
  onConnectApp: (slug: string) => void;
  onDisconnectApp: (slug: string) => void;
  onActivateApp: (slug: string) => void;
  onTestApp: (slug: string) => void;
  onToggleExpand: (slug: string) => void;
  onOpenAppBrowser: () => void;
  onCloseAppBrowser: () => void;
  onAppBrowserSearchChange: (value: string) => void;
  onManualSlugChange: (value: string) => void;
  onConnectManualSlug: () => void;
}

const FEATURED_SLUGS = [
  "google-calendar", "google-sheets", "google-drive", "google-docs", "google-tasks",
  "youtube", "youtube-data-api", "slack", "telegram-bot-api", "twilio",
  "sendgrid", "mailgun",
];

export function renderAgentPipedream(props: AgentPipedreamProps) {
  if (props.loading) {
    return html`
      <section class="card">
        <div class="card-title">Pipedream</div>
        <div class="card-sub">Loading…</div>
      </section>`;
  }

  if (!props.globalConfigured) {
    return html`
      <section class="card">
        <div class="card-title">Pipedream</div>
        <div class="card-sub" style="color: var(--warning, #f59e0b);">
          ⚠️ Global Pipedream credentials not configured. Set them up in the
          <strong>Pipedream</strong> tab first.
        </div>
      </section>`;
  }

  const userId = props.editingUserId ? props.draftUserId : (props.externalUserId || props.agentId);
  const connectedSlugs = new Set(props.connectedApps.map((a) => a.slug));
  const featured = ALL_APPS.filter((a) => FEATURED_SLUGS.includes(a.slug) && !connectedSlugs.has(a.slug));

  return html`
    <!-- Header -->
    <section class="card">
      <div class="row" style="justify-content: space-between; align-items: center;">
        <div>
          <div class="card-title">Pipedream</div>
          <div class="card-sub">Per-agent OAuth app connections via Pipedream Connect.</div>
        </div>
        <button class="btn btn--sm" @click=${props.onRefresh} ?disabled=${props.saving}>↻ Refresh</button>
      </div>

      ${props.error ? html`<div class="callout danger" style="margin-top: 12px;">${props.error}</div>` : nothing}
      ${props.success ? html`<div class="callout success" style="margin-top: 12px;">${props.success}</div>` : nothing}

      ${props.environment === "development" ? html`
        <div class="callout" style="margin-top: 12px; font-size: 13px; background: rgba(245,158,11,0.1); border-color: #f59e0b; color: #f59e0b;">
          ⚠️ Using <strong>development</strong> environment. To use production, go to the
          <strong>Pipedream</strong> tab → Edit credentials → set Environment to Production.
        </div>` : html`
        <div style="margin-top: 10px; font-size: 12px; color: var(--muted);">
          🟢 Production environment
        </div>`}

      <!-- External User ID -->
      <div style="margin-top: 16px;">
        <label class="field-label">External User ID</label>
        <div class="card-sub" style="margin-bottom: 8px;">Isolates this agent's OAuth tokens from other agents.</div>
        <div class="row" style="gap: 8px;">
          ${props.editingUserId
            ? html`
              <input class="input" style="flex: 1;" .value=${props.draftUserId}
                @input=${(e: Event) => props.onDraftUserIdChange((e.target as HTMLInputElement).value)}
                placeholder=${props.agentId} />
              <button class="btn btn--sm btn--primary" ?disabled=${props.saving || !props.draftUserId.trim()}
                @click=${() => props.onSave(props.draftUserId.trim())}>
                ${props.saving ? "Saving…" : "Save"}
              </button>
              <button class="btn btn--sm" @click=${() => props.onEditUserId(false)} ?disabled=${props.saving}>Cancel</button>`
            : html`
              <code class="mono" style="padding: 6px 12px; background: var(--surface-alt, var(--surface)); border-radius: 6px; flex: 1;">${userId}</code>
              <button class="btn btn--sm" @click=${() => { props.onDraftUserIdChange(userId); props.onEditUserId(true); }}>Edit</button>`}
        </div>
      </div>
    </section>

    <!-- Connected Apps -->
    <section class="card" style="margin-top: 16px;">
      <div class="card-title">✅ Connected Apps</div>
      <div class="card-sub">Apps this agent can use. Tokens refresh automatically.</div>

      ${props.connectedApps.length === 0
        ? html`
          <div style="padding: 20px; text-align: center; border: 1px dashed var(--border); border-radius: 8px; margin-top: 12px;">
            <div style="font-size: 32px; margin-bottom: 8px;">🔌</div>
            <div class="card-sub">No apps connected yet. Browse available apps below to get started.</div>
          </div>`
        : html`
          <div class="list" style="margin-top: 12px;">
            ${props.connectedApps.map((app) => {
              const isTesting = props.testingApp === app.slug;
              const isDisconnecting = props.disconnectingApp === app.slug;
              const isExpanded = props.expandedApps.has(app.slug);
              const hasTools = app.tools && app.tools.length > 0;
              return html`
                <div class="list-item" style="flex-direction: column; align-items: stretch; gap: 0;">
                  <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                    <div class="list-main" style="flex: 1; min-width: 0;">
                      <div class="list-title" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <span style="font-size: 20px;">${app.icon}</span>
                        <span>${app.name}</span>
                        ${app.toolCount != null ? html`<span style="font-size: 11px; font-weight: 500; color: var(--muted); background: var(--secondary); border: 1px solid var(--border); border-radius: 10px; padding: 1px 7px;">${app.toolCount} tools</span>` : nothing}
                      </div>
                      <div class="list-sub">
                        ${app.active === false
                          ? html`<span style="color: var(--warning, #f59e0b);">⚠ OAuth complete — needs activation</span>`
                          : app.accountName ? `Connected as ${app.accountName}` : "Connected"}
                      </div>
                    </div>
                    <div class="list-actions">
                      ${app.active === false ? html`
                        <button class="btn small" style="background: var(--accent); color: var(--bg); font-weight: 600;" ?disabled=${props.activatingApp === app.slug} @click=${() => props.onActivateApp(app.slug)}>
                          ${props.activatingApp === app.slug ? "Activating..." : "⚡ Activate"}
                        </button>
                      ` : html`
                        ${hasTools ? html`<button class="btn small" @click=${() => props.onToggleExpand(app.slug)} title="${isExpanded ? "Hide tools" : "Show tools"}">${isExpanded ? "▲ Hide" : "▼ Tools"}</button>` : nothing}
                        <button class="btn small" ?disabled=${isTesting} @click=${() => props.onTestApp(app.slug)}>
                          ${isTesting ? "Testing..." : "Test"}
                        </button>
                      `}
                      <button class="btn small danger" ?disabled=${isDisconnecting} @click=${() => props.onDisconnectApp(app.slug)}>
                        ${isDisconnecting ? "..." : "Disconnect"}
                      </button>
                    </div>
                  </div>
                  ${isExpanded && hasTools ? html`
                    <div style="margin-top: 10px; border-top: 1px solid var(--border); padding-top: 10px; width: 100%;">
                      <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <thead>
                          <tr style="color: var(--muted); text-align: left;">
                            <th style="padding: 4px 8px; font-weight: 500; width: 35%;">Tool</th>
                            <th style="padding: 4px 8px; font-weight: 500;">Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          ${app.tools!.map((tool, i) => html`
                            <tr style="border-top: 1px solid var(--border); ${i % 2 === 1 ? "background: rgba(255,255,255,0.02);" : ""}">
                              <td style="padding: 5px 8px; font-family: monospace; font-size: 11px; color: var(--accent); white-space: nowrap;">${tool.name}</td>
                              <td style="padding: 5px 8px; color: var(--muted); line-height: 1.4;">${tool.description ?? "—"}</td>
                            </tr>
                          `)}
                        </tbody>
                      </table>
                    </div>
                  ` : nothing}
                </div>`;
            })}
          </div>`}
    </section>

    <!-- Available Apps -->
    <section class="card" style="margin-top: 16px;">
      <div class="row" style="justify-content: space-between; align-items: flex-start;">
        <div>
          <div class="card-title">➕ Available Apps</div>
          <div class="card-sub">Connect apps to expand this agent's capabilities.</div>
        </div>
        <button class="btn" @click=${props.onOpenAppBrowser}>Browse All Apps</button>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px; margin-top: 16px;">
        ${featured.slice(0, 12).map((app) => renderAvailableApp(app, props))}
      </div>

      <!-- Manual slug -->
      <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border);">
        <div class="muted" style="font-size: 13px; margin-bottom: 8px;">Know the app slug? Connect directly:</div>
        <div class="row" style="gap: 8px;">
          <input type="text" .value=${props.manualSlug}
            @input=${(e: Event) => props.onManualSlugChange((e.target as HTMLInputElement).value)}
            @keydown=${(e: KeyboardEvent) => { if (e.key === "Enter" && props.manualSlug.trim()) props.onConnectManualSlug(); }}
            placeholder="e.g., spotify, notion, stripe..."
            style="flex: 1; max-width: 300px;" />
          <button class="btn primary small"
            ?disabled=${!props.manualSlug.trim() || props.connectingApp === props.manualSlug}
            @click=${props.onConnectManualSlug}>
            ${props.connectingApp === props.manualSlug ? "Connecting..." : "Connect"}
          </button>
        </div>
        <div class="muted" style="font-size: 12px; margin-top: 6px;">
          Find app slugs at <a href="https://mcp.pipedream.com" target="_blank">mcp.pipedream.com</a>
        </div>
      </div>
    </section>

    <!-- Remove config -->
    ${props.configured ? html`
      <section class="card" style="margin-top: 16px;">
        <div class="row" style="align-items: center; gap: 12px;">
          <button class="btn btn--sm btn--danger" @click=${props.onDelete} ?disabled=${props.saving}>Remove Agent Config</button>
          <span class="card-sub">Removes per-agent overrides. Falls back to global credentials.</span>
        </div>
      </section>` : nothing}

    <!-- App Browser Modal -->
    ${props.showAppBrowser ? renderAppBrowserModal(props) : nothing}
  `;
}

function renderAvailableApp(app: PipedreamApp, props: AgentPipedreamProps) {
  const isConnecting = props.connectingApp === app.slug;
  return html`
    <div style="padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-secondary); display: flex; align-items: center; justify-content: space-between; gap: 8px;">
      <div style="display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1;">
        <span style="font-size: 18px; flex-shrink: 0;">${app.icon}</span>
        <span style="font-weight: 500; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${app.name}">${app.name}</span>
      </div>
      <button class="btn small primary" style="flex-shrink: 0;" ?disabled=${isConnecting} @click=${() => props.onConnectApp(app.slug)}>
        ${isConnecting ? "..." : "Connect"}
      </button>
    </div>`;
}

function renderAppBrowserModal(props: AgentPipedreamProps) {
  const connectedSlugs = new Set(props.connectedApps.map((a) => a.slug));
  const search = props.appBrowserSearch.toLowerCase().trim();
  const filtered = ALL_APPS.filter((app) => {
    if (connectedSlugs.has(app.slug)) return false;
    if (!search) return true;
    return app.name.toLowerCase().includes(search) || app.slug.toLowerCase().includes(search);
  });

  return html`
    <div class="modal-backdrop" @click=${props.onCloseAppBrowser}>
      <div class="modal" style="width: 90%; max-width: 900px; max-height: 85vh; display: flex; flex-direction: column;"
        @click=${(e: Event) => e.stopPropagation()}>
        <div class="modal-header" style="flex-shrink: 0;">
          <h2 style="margin: 0;">Browse Apps</h2>
          <button class="btn small" @click=${props.onCloseAppBrowser}>✕</button>
        </div>

        <div style="padding: 16px; border-bottom: 1px solid var(--border); flex-shrink: 0;">
          <input type="text" .value=${props.appBrowserSearch}
            @input=${(e: Event) => props.onAppBrowserSearchChange((e.target as HTMLInputElement).value)}
            placeholder="Search apps by name or slug..."
            style="width: 100%; font-size: 16px;" autofocus />
          <div class="muted" style="margin-top: 8px; font-size: 13px;">${filtered.length} apps available</div>
        </div>

        <div style="flex: 1; overflow-y: auto; padding: 16px;">
          ${filtered.length === 0
            ? html`<div style="text-align: center; padding: 40px; color: var(--muted);">No apps found matching "${props.appBrowserSearch}"</div>`
            : html`
              <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px;">
                ${filtered.map((app) => renderAvailableApp(app, props))}
              </div>`}
        </div>

        <div style="padding: 16px; border-top: 1px solid var(--border); flex-shrink: 0;">
          <div class="muted" style="font-size: 13px; margin-bottom: 8px;">Can't find your app? Enter the slug directly:</div>
          <div class="row" style="gap: 8px;">
            <input type="text" .value=${props.manualSlug}
              @input=${(e: Event) => props.onManualSlugChange((e.target as HTMLInputElement).value)}
              @keydown=${(e: KeyboardEvent) => { if (e.key === "Enter" && props.manualSlug.trim()) props.onConnectManualSlug(); }}
              placeholder="e.g., spotify, notion, stripe..."
              style="flex: 1;" />
            <button class="btn primary"
              ?disabled=${!props.manualSlug.trim() || props.connectingApp === props.manualSlug}
              @click=${props.onConnectManualSlug}>
              ${props.connectingApp === props.manualSlug ? "Connecting..." : "Connect by Slug"}
            </button>
          </div>
          <div class="muted" style="font-size: 12px; margin-top: 6px;">
            Find all slugs at <a href="https://mcp.pipedream.com" target="_blank">mcp.pipedream.com</a>
          </div>
        </div>
      </div>
    </div>`;
}
