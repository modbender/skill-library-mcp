import { html, nothing } from "lit";

export type ZapierTool = { name: string; description?: string };

export type ZapierState = {
  loading: boolean;
  configured: boolean;
  mcpUrl: string;
  showForm: boolean;
  toolCount?: number;
  error: string | null;
  success: string | null;
  testing: boolean;
  tools?: Array<ZapierTool>;
  expandedGroups?: Set<string>;
};

export type ZapierProps = ZapierState & {
  onConfigure: () => void;
  onSave: () => void;
  onCancel: () => void;
  onUrlChange: (value: string) => void;
  onTest: () => void;
  onDisconnect: () => void;
  onRefresh: () => void;
  onLoadTools: () => void;
  onToggleGroup: (groupName: string) => void;
};

/**
 * Extract a friendly group name from a tool name.
 * e.g., "quickbooks_online_find_customer" -> "QuickBooks Online"
 * e.g., "get_configuration_url" -> "Configuration"
 */
function getToolGroup(toolName: string): string {
  // Common prefixes to group by
  const prefixMappings: Record<string, string> = {
    "quickbooks_online": "QuickBooks Online",
    "google_sheets": "Google Sheets",
    "google_calendar": "Google Calendar",
    "google_docs": "Google Docs",
    "google_drive": "Google Drive",
    "slack": "Slack",
    "gmail": "Gmail",
    "notion": "Notion",
    "airtable": "Airtable",
    "hubspot": "HubSpot",
    "salesforce": "Salesforce",
    "trello": "Trello",
    "asana": "Asana",
    "jira": "Jira",
    "github": "GitHub",
    "discord": "Discord",
    "twitter": "Twitter",
    "linkedin": "LinkedIn",
    "stripe": "Stripe",
    "shopify": "Shopify",
    "mailchimp": "Mailchimp",
    "zendesk": "Zendesk",
    "intercom": "Intercom",
    "twilio": "Twilio",
    "dropbox": "Dropbox",
    "zoom": "Zoom",
    "calendly": "Calendly",
  };

  // Check known prefixes
  for (const [prefix, friendlyName] of Object.entries(prefixMappings)) {
    if (toolName.startsWith(prefix + "_")) {
      return friendlyName;
    }
  }

  // Fall back to extracting prefix before first action word
  const actionWords = ["find", "create", "update", "delete", "send", "get", "list", "add", "remove", "void", "attach"];
  for (const action of actionWords) {
    const idx = toolName.indexOf("_" + action);
    if (idx > 0) {
      const prefix = toolName.substring(0, idx);
      // Convert snake_case to Title Case
      return prefix.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
    }
  }

  // If no pattern matches, use "Other"
  return "Other";
}

/**
 * Get a short action name from the full tool name.
 * e.g., "quickbooks_online_find_customer" -> "find_customer"
 */
function getToolShortName(toolName: string, groupPrefix: string): string {
  // Find the prefix in the tool name and strip it
  const lowerGroup = groupPrefix.toLowerCase().replace(/ /g, "_");
  if (toolName.startsWith(lowerGroup + "_")) {
    return toolName.substring(lowerGroup.length + 1);
  }
  return toolName;
}

type ToolGroup = {
  name: string;
  tools: ZapierTool[];
};

/**
 * Group tools by their app/service prefix and render as expandable sections.
 */
function renderGroupedTools(props: ZapierProps) {
  const tools = props.tools || [];
  const expandedGroups = props.expandedGroups || new Set<string>();

  // Group tools by their prefix
  const groupMap = new Map<string, ZapierTool[]>();
  for (const tool of tools) {
    const groupName = getToolGroup(tool.name);
    if (!groupMap.has(groupName)) {
      groupMap.set(groupName, []);
    }
    groupMap.get(groupName)!.push(tool);
  }

  // Convert to array and sort by group name
  const groups: ToolGroup[] = Array.from(groupMap.entries())
    .map(([name, tools]) => ({ name, tools }))
    .sort((a, b) => {
      // Put "Other" at the end
      if (a.name === "Other") return 1;
      if (b.name === "Other") return -1;
      return a.name.localeCompare(b.name);
    });

  return html`
    <div style="margin-top: 12px; max-height: 400px; overflow-y: auto;">
      ${groups.map((group) => {
        const isExpanded = expandedGroups.has(group.name);
        const groupPrefix = group.name.toLowerCase().replace(/ /g, "_");
        
        return html`
          <div style="border: 1px solid var(--border); border-radius: 8px; margin-bottom: 8px; overflow: hidden;">
            <div
              style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background: var(--bg-secondary);
                cursor: pointer;
                user-select: none;
              "
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
                    ${group.tools.map((tool) => {
                      const shortName = getToolShortName(tool.name, group.name);
                      return html`
                        <div style="padding: 10px 16px; border-bottom: 1px solid var(--border);">
                          <div style="font-family: monospace; font-size: 13px; color: var(--text-primary);">
                            ${shortName}
                          </div>
                          ${tool.description
                            ? html`<div style="font-size: 12px; opacity: 0.7; margin-top: 4px;">${tool.description}</div>`
                            : nothing}
                        </div>
                      `;
                    })}
                  </div>
                `
              : nothing}
          </div>
        `;
      })}
    </div>
  `;
}

export function renderZapier(props: ZapierProps) {
  const statusLabel = props.configured ? "Active" : "Not Configured";
  const statusClass = props.configured ? "chip-ok" : "chip-warn";

  return html`
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start;">
      <div>
        <h1>Zapier</h1>
        <p class="muted">Connect to 8,000+ apps via Zapier MCP.</p>
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
            ⚡ Connection Status
            <span class="chip ${statusClass}" style="margin-left: 8px;">${statusLabel}</span>
          </div>
          <div class="card-sub">
            ${props.configured
              ? `Connected${props.toolCount ? ` with ${props.toolCount} tools available.` : "."}`
              : "Configure your Zapier MCP URL to get started."}
          </div>
        </div>
      </div>
    </section>

    <section class="card" style="margin-top: 16px;">
      <div class="row" style="justify-content: space-between; align-items: center;">
        <div class="card-title">🔗 MCP URL</div>
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
                Get your MCP URL from
                <a href="https://zapier.com/mcp" target="_blank">zapier.com/mcp</a>
              </div>

              <label class="field">
                <span>Zapier MCP URL</span>
                <input
                  type="text"
                  .value=${props.mcpUrl}
                  @input=${(e: Event) => props.onUrlChange((e.target as HTMLInputElement).value)}
                  placeholder="https://actions.zapier.com/mcp/..."
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
                      <code style="word-break: break-all;">${props.mcpUrl}</code>
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
                : html`<p class="muted">No URL configured. Click "Configure" to get started.</p>`}
            </div>
          `}
    </section>

    ${props.configured
      ? html`
          <section class="card" style="margin-top: 16px;">
            <div class="row" style="justify-content: space-between; align-items: center;">
              <div class="card-title">🔧 Available Tools</div>
              <button class="btn small" @click=${props.onLoadTools}>
                ${props.tools && props.tools.length > 0 ? "Refresh" : "Load Tools"}
              </button>
            </div>
            ${props.tools && props.tools.length > 0
              ? renderGroupedTools(props)
              : html`
                  <div class="card-sub" style="margin-top: 8px;">
                    <p class="muted">Click "Load Tools" to see available Zapier actions.</p>
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
            <strong>Get your MCP URL</strong> — Go to
            <a href="https://zapier.com/mcp" target="_blank">zapier.com/mcp</a>
            and sign in
          </li>
          <li>
            <strong>Configure actions</strong> — Choose which apps and actions to expose to your agent
          </li>
          <li><strong>Copy URL</strong> — Copy your personalized MCP URL</li>
          <li><strong>Paste above</strong> — Enter the URL in the form above</li>
          <li>
            <strong>Use naturally</strong> — Just ask your agent to "Send a Slack message" or
            "Add a row to my spreadsheet"
          </li>
        </ol>
      </div>
    </section>

    <section class="card" style="margin-top: 16px;">
      <div class="card-title">🤖 Using with MCPorter</div>
      <div class="card-sub" style="margin-top: 8px;">
        <p>Once connected, your Zapier tools are available via MCPorter:</p>
        <pre style="margin-top: 12px; padding: 12px; background: var(--bg-secondary); border-radius: 6px; overflow-x: auto; font-size: 12px;"><code># List available Zapier tools
mcporter list zapier-mcp --schema

# Call a specific tool
mcporter call zapier-mcp.&lt;tool_name&gt; param=value</code></pre>
      </div>
    </section>
  `;
}
