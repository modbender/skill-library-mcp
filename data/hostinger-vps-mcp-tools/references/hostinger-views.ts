import { html, nothing } from "lit";

export type HostingerTool = { name: string; description?: string };

export type HostingerState = {
  loading: boolean;
  configured: boolean;
  apiToken: string;
  githubRepo: string;
  showForm: boolean;
  toolCount?: number;
  error: string | null;
  success: string | null;
  tools?: Array<HostingerTool>;
  expandedGroups?: Set<string>;
};

export type HostingerProps = HostingerState & {
  onRefresh: () => void;
  onConfigure: () => void;
  onSave: () => void;
  onCancel: () => void;
  onApiTokenChange: (value: string) => void;
  onGithubRepoChange: (value: string) => void;
  onDisconnect: () => void;
  onLoadTools: () => void;
  onToggleGroup: (groupName: string) => void;
};

function getToolGroup(toolName: string): string {
  if (toolName.startsWith("vps_")) return "VPS Management";
  if (toolName.startsWith("billing_")) return "Billing";
  if (toolName.startsWith("dns_") || toolName.startsWith("DNS_")) return "DNS";
  if (toolName.startsWith("domains_")) return "Domains";
  if (toolName.startsWith("hosting_")) return "Hosting";
  return "Other";
}

type ToolGroup = { name: string; tools: HostingerTool[] };

function renderGroupedTools(props: HostingerProps) {
  const tools = props.tools || [];
  const expandedGroups = props.expandedGroups || new Set<string>();

  const groupMap = new Map<string, HostingerTool[]>();
  for (const tool of tools) {
    const groupName = getToolGroup(tool.name);
    if (!groupMap.has(groupName)) groupMap.set(groupName, []);
    groupMap.get(groupName)!.push(tool);
  }

  const groups: ToolGroup[] = Array.from(groupMap.entries())
    .map(([name, toolList]) => ({ name, tools: toolList }))
    .sort((a, b) => {
      if (a.name === "Other") return 1;
      if (b.name === "Other") return -1;
      return a.name.localeCompare(b.name);
    });

  return html`
    <div style="margin-top: 12px; max-height: 400px; overflow-y: auto;">
      ${groups.map((group) => {
        const isExpanded = expandedGroups.has(group.name);
        return html`
          <div style="border: 1px solid var(--border); border-radius: 8px; margin-bottom: 8px; overflow: hidden;">
            <div
              style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--bg-secondary); cursor: pointer; user-select: none;"
              @click=${() => props.onToggleGroup(group.name)}
            >
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 12px; opacity: 0.6;">${isExpanded ? "▼" : "▶"}</span>
                <span style="font-weight: 600;">${group.name}</span>
                <span class="chip" style="font-size: 11px;">${group.tools.length} tools</span>
              </div>
            </div>
            ${isExpanded
              ? html`
                  <div style="border-top: 1px solid var(--border);">
                    ${group.tools.map((tool) => html`
                      <div style="padding: 10px 16px; border-bottom: 1px solid var(--border);">
                        <div style="font-family: monospace; font-size: 13px; color: var(--text-primary);">${tool.name}</div>
                        ${tool.description
                          ? html`<div style="font-size: 12px; opacity: 0.7; margin-top: 4px;">${tool.description}</div>`
                          : nothing}
                      </div>
                    `)}
                  </div>
                `
              : nothing}
          </div>
        `;
      })}
    </div>
  `;
}

export function renderHostinger(props: HostingerProps) {
  const statusLabel = props.configured ? "Active" : "Not Configured";
  const statusClass = props.configured ? "chip-ok" : "chip-warn";

  return html`
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start;">
      <div>
        <h1>Hostinger VPS</h1>
        <p class="muted">Deploy and manage VPS instances via Hostinger API.</p>
      </div>
      <button class="btn" ?disabled=${props.loading} @click=${props.onRefresh} title="Refresh status">
        ${props.loading ? "Loading..." : "↻ Refresh"}
      </button>
    </div>

    ${props.error ? html`<div class="callout danger" style="margin-bottom: 16px;">${props.error}</div>` : nothing}
    ${props.success ? html`<div class="callout success" style="margin-bottom: 16px;">${props.success}</div>` : nothing}

    <section class="card">
      <div class="row" style="justify-content: space-between; align-items: flex-start;">
        <div>
          <div class="card-title">
            🖥️ Connection Status
            <span class="chip ${statusClass}" style="margin-left: 8px;">${statusLabel}</span>
          </div>
          <div class="card-sub">
            ${props.configured
              ? `Connected to Hostinger API${props.toolCount ? ` · ${props.toolCount} tools` : ""}.`
              : "Configure your Hostinger API token to get started."}
          </div>
        </div>
      </div>
    </section>

    <section class="card" style="margin-top: 16px;">
      <div class="row" style="justify-content: space-between; align-items: center;">
        <div class="card-title">🔑 API Configuration</div>
        ${!props.showForm
          ? html`<button class="btn" @click=${props.onConfigure}>${props.configured ? "Edit" : "Configure"}</button>`
          : nothing}
      </div>

      ${props.showForm
        ? html`
            <div style="margin-top: 12px; padding: 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-secondary);">
              <div class="callout info" style="margin-bottom: 16px; font-size: 13px;">
                Get your API token from
                <a href="https://hpanel.hostinger.com/api-tokens" target="_blank">hPanel → API Tokens</a>.
                Docs: <a href="https://developers.hostinger.com/" target="_blank">developers.hostinger.com</a>
              </div>

              <label class="field">
                <span>Hostinger API Token</span>
                <input
                  type="password"
                  .value=${props.apiToken}
                  @input=${(e: Event) => props.onApiTokenChange((e.target as HTMLInputElement).value)}
                  placeholder="Your Hostinger API token"
                />
              </label>

              <label class="field" style="margin-top: 12px;">
                <span>GitHub Repo URL (OpenClaw fork to install on VPS)</span>
                <input
                  type="text"
                  .value=${props.githubRepo}
                  @input=${(e: Event) => props.onGithubRepoChange((e.target as HTMLInputElement).value)}
                  placeholder="https://github.com/your-org/openclaw"
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
                    <div style="margin-top: 8px;">
                      <strong>API Token:</strong> <code>${props.apiToken}</code>
                    </div>
                    ${props.githubRepo
                      ? html`<div style="margin-top: 6px;"><strong>GitHub Repo:</strong> <code>${props.githubRepo}</code></div>`
                      : html`<div style="margin-top: 6px; opacity: 0.6;">No GitHub repo configured.</div>`}
                    <div class="row" style="margin-top: 16px; gap: 8px;">
                      <button class="btn small danger" @click=${props.onDisconnect}>Disconnect</button>
                    </div>
                  `
                : html`<p class="muted">No API token configured. Click "Configure" to get started.</p>`}
            </div>
          `}
    </section>

    ${props.configured
      ? html`
          <section class="card" style="margin-top: 16px;">
            <div class="row" style="justify-content: space-between; align-items: center;">
              <div class="card-title">🔧 Available MCP Tools</div>
              <button class="btn small" @click=${props.onLoadTools}>
                ${props.tools && props.tools.length > 0 ? "Refresh" : "Load Tools"}
              </button>
            </div>
            ${props.tools && props.tools.length > 0
              ? renderGroupedTools(props)
              : html`<div class="card-sub" style="margin-top: 8px;"><p class="muted">Click "Load Tools" to see available Hostinger API tools.</p></div>`}
          </section>

          <section class="card" style="margin-top: 16px;">
            <div class="card-title">⚡ Key VPS Tools</div>
            <div class="card-sub" style="margin-top: 8px;">
              <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                  <tr style="border-bottom: 1px solid var(--border);">
                    <th style="text-align: left; padding: 6px 8px; opacity: 0.7;">Tool</th>
                    <th style="text-align: left; padding: 6px 8px; opacity: 0.7;">Purpose</th>
                  </tr>
                </thead>
                <tbody>
                  ${[
                    ["vps_getVirtualMachineListV1", "List all VPS instances"],
                    ["vps_createVirtualMachineV1", "Deploy a new VPS"],
                    ["vps_getDataCenterListV1", "List available data centers"],
                    ["vps_getOsListV1", "List available OS options (Ubuntu, etc.)"],
                    ["vps_startVirtualMachineV1", "Start a stopped VPS"],
                    ["vps_stopVirtualMachineV1", "Stop a running VPS"],
                    ["vps_restartVirtualMachineV1", "Restart a VPS"],
                    ["vps_resetPasswordV1", "Reset root password"],
                    ["vps_getMetricsV1", "Get VPS resource metrics"],
                    ["billing_getCatalogItemListV1", "Browse VPS plans and pricing"],
                    ["billing_getPaymentMethodListV1", "List payment methods"],
                  ].map(([name, desc]) => html`
                    <tr style="border-bottom: 1px solid var(--border);">
                      <td style="padding: 8px; font-family: monospace; font-size: 12px;">${name}</td>
                      <td style="padding: 8px; opacity: 0.8;">${desc}</td>
                    </tr>
                  `)}
                </tbody>
              </table>
              <pre style="margin-top: 16px; padding: 12px; background: var(--bg-secondary); border-radius: 6px; overflow-x: auto; font-size: 12px;"><code># List VPS instances
mcporter call hostinger-api.vps_getVirtualMachineListV1

# View available plans
mcporter call hostinger-api.billing_getCatalogItemListV1 category=VPS

# Deploy a new VPS (requires plan ID, OS, datacenter)
mcporter call hostinger-api.vps_createVirtualMachineV1 ...</code></pre>
            </div>
          </section>
        `
      : nothing}

    <section class="card" style="margin-top: 16px;">
      <div class="card-title">📚 Setup Guide</div>
      <div class="card-sub" style="margin-top: 8px;">
        <ol style="margin: 12px 0; padding-left: 20px; line-height: 1.8;">
          <li><strong>Get API Token</strong> — Go to <a href="https://hpanel.hostinger.com/api-tokens" target="_blank">hPanel → API Tokens</a> and create a token</li>
          <li><strong>Enter Token Above</strong> — Paste your token in the Configuration section</li>
          <li><strong>Add GitHub Repo</strong> — Enter your OpenClaw fork URL to auto-install on new VPS instances</li>
          <li><strong>Deploy VPS</strong> — Ask Koda: "Deploy a new Hostinger VPS with Ubuntu 24.04"</li>
          <li><strong>Auto-install</strong> — Koda will SSH into the VPS and clone your repo automatically</li>
        </ol>
        <div style="margin-top: 12px;">
          <strong>Resources:</strong>
          <ul style="margin: 8px 0; padding-left: 20px; line-height: 1.8;">
            <li><a href="https://developers.hostinger.com/" target="_blank">Hostinger API Reference</a></li>
            <li><a href="https://developers.hostinger.com/#description/authentication" target="_blank">Authentication Guide</a></li>
            <li><a href="https://github.com/hostinger/api-mcp-server" target="_blank">Hostinger API MCP Server (GitHub)</a></li>
            <li><a href="https://hpanel.hostinger.com/api-tokens" target="_blank">hPanel API Token Manager</a></li>
          </ul>
        </div>
      </div>
    </section>
  `;
}
