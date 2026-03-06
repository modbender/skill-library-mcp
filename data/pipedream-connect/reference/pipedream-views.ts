import { html, nothing } from "lit";

export type PipedreamApp = {
  slug: string;
  name: string;
  icon: string;
  connected: boolean;
  toolCount?: number;
  accountName?: string;
  serverName?: string;
};

export type PipedreamCredentials = {
  clientId: string;
  clientSecret: string;
  projectId: string;
  environment: "development" | "production";
};

export type PipedreamState = {
  loading: boolean;
  configured: boolean;
  credentials: PipedreamCredentials;
  showCredentialsForm: boolean;
  connectedApps: PipedreamApp[];
  availableApps: PipedreamApp[];
  error: string | null;
  success: string | null;
  testingApp: string | null;
  connectingApp: string | null;
  refreshingApp: string | null;
  externalUserId: string;
  showAppBrowser: boolean;
  appBrowserSearch: string;
  allApps: PipedreamApp[];
  loadingApps: boolean;
  manualSlug: string;
  agentSummaries: Array<{ agentId: string; configured: boolean; externalUserId: string; appCount: number }>;
};

export type PipedreamProps = PipedreamState & {
  onConfigure: () => void;
  onSaveCredentials: () => void;
  onCancelCredentials: () => void;
  onCredentialChange: (field: keyof PipedreamCredentials, value: string) => void;
  onConnectApp: (appSlug: string) => void;
  onDisconnectApp: (appSlug: string) => void;
  onTestApp: (appSlug: string) => void;
  onRefreshToken: (appSlug: string) => void;
  onExternalUserIdChange: (value: string) => void;
  onOpenAppBrowser: () => void;
  onCloseAppBrowser: () => void;
  onAppBrowserSearchChange: (value: string) => void;
  onManualSlugChange: (value: string) => void;
  onConnectManualSlug: () => void;
};

export function renderPipedream(props: PipedreamProps) {
  const statusLabel = props.configured ? "Active" : "Not Configured";
  const statusClass = props.configured ? "chip-ok" : "chip-warn";

  return html`
    <div class="page-header">
      <h1>Pipedream</h1>
      <p class="muted">Pipedream platform credentials. App connections are managed per-agent under Agents → Tools → Pipedream.</p>
    </div>

    ${props.error ? html`<div class="callout danger" style="margin-bottom: 16px;">${props.error}</div>` : nothing}
    ${props.success ? html`<div class="callout success" style="margin-bottom: 16px;">${props.success}</div>` : nothing}

    <section class="card">
      <div class="card-title">
        🔗 Connection Status
        <span class="chip ${statusClass}" style="margin-left: 8px;">${statusLabel}</span>
      </div>
      <div class="card-sub">
        ${props.configured
          ? "Platform credentials configured. Go to an agent's Tools → Pipedream tab to connect apps."
          : "Enter your Pipedream credentials below to enable OAuth app connections for your agents."}
      </div>
    </section>

    <section class="card" style="margin-top: 16px;">
      <div class="row" style="justify-content: space-between; align-items: center;">
        <div class="card-title">🔑 Credentials</div>
        ${!props.showCredentialsForm
          ? html`<button class="btn" @click=${props.onConfigure}>${props.configured ? "Edit" : "Configure"}</button>`
          : nothing}
      </div>
      ${props.showCredentialsForm
        ? renderCredentialsForm(props)
        : html`
          <div class="card-sub" style="margin-top: 8px;">
            ${props.configured
              ? html`
                <div class="row" style="gap: 24px; margin-top: 12px; flex-wrap: wrap;">
                  <div><span class="muted">Project ID:</span> <code style="margin-left: 8px;">${props.credentials.projectId}</code></div>
                  <div><span class="muted">Environment:</span> <span style="margin-left: 8px;">${props.credentials.environment}</span></div>
                </div>`
              : html`<p class="muted">No credentials configured. Click "Configure" to get started.</p>`}
          </div>`}
    </section>

    ${props.configured && props.agentSummaries?.length > 0 ? html`
      <section class="card" style="margin-top: 16px;">
        <div class="card-title">👥 Agent Connections</div>
        <div class="card-sub">Each agent manages its own app connections. Configure in Agents → [Agent] → Tools → Pipedream.</div>
        <table style="width: 100%; margin-top: 12px; border-collapse: collapse;">
          <thead>
            <tr style="text-align: left; border-bottom: 1px solid var(--border);">
              <th style="padding: 8px 12px; font-size: 13px;">Agent</th>
              <th style="padding: 8px 12px; font-size: 13px;">External User ID</th>
              <th style="padding: 8px 12px; font-size: 13px;">Status</th>
              <th style="padding: 8px 12px; font-size: 13px;"></th>
            </tr>
          </thead>
          <tbody>
            ${props.agentSummaries.map((agent) => html`
              <tr style="border-bottom: 1px solid var(--border);">
                <td style="padding: 8px 12px;"><span class="mono" style="font-size: 13px;">${agent.agentId}</span></td>
                <td style="padding: 8px 12px;"><code style="font-size: 12px;">${agent.externalUserId || agent.agentId}</code></td>
                <td style="padding: 8px 12px;">
                  <span class="chip ${agent.configured ? "chip-ok" : "chip-muted"}">${agent.configured ? "Configured" : "Global"}</span>
                </td>
                <td style="padding: 8px 12px; text-align: right;">
                  <a href="#" style="font-size: 12px; color: var(--accent);" @click=${(e: Event) => {
                    e.preventDefault();
                    window.dispatchEvent(new CustomEvent("openclaw-navigate", {
                      detail: { tab: "agents", agentId: agent.agentId, panel: "tools", subTab: "pipedream" }
                    }));
                  }}>Configure →</a>
                </td>
              </tr>`)}
          </tbody>
        </table>
      </section>` : nothing}

    <section class="card" style="margin-top: 16px;">
      <div class="card-title">📚 Setup Guide</div>
      <div class="card-sub" style="margin-top: 8px;">
        <ol style="margin: 12px 0; padding-left: 20px; line-height: 1.8;">
          <li><strong>Create OAuth Client</strong> — Go to <a href="https://pipedream.com/settings/api" target="_blank">pipedream.com/settings/api</a> and create a new OAuth client</li>
          <li><strong>Create Project</strong> — Go to <a href="https://pipedream.com/projects" target="_blank">pipedream.com/projects</a> and create a project</li>
          <li><strong>Enter Credentials</strong> — Paste your Client ID, Secret, and Project ID above</li>
          <li><strong>Connect Apps per Agent</strong> — Go to Agents → [Agent] → Tools → Pipedream and connect apps for each agent</li>
        </ol>
      </div>
    </section>
  `;
}

function renderCredentialsForm(props: PipedreamProps) {
  return html`
    <div style="margin-top: 12px; padding: 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-secondary);">
      <div class="callout info" style="margin-bottom: 16px; font-size: 13px;">
        Get your credentials from <a href="https://pipedream.com/settings/api" target="_blank">pipedream.com/settings/api</a>
      </div>
      <label class="field">
        <span>Client ID</span>
        <input type="text" .value=${props.credentials.clientId}
          @input=${(e: Event) => props.onCredentialChange("clientId", (e.target as HTMLInputElement).value)}
          placeholder="Your OAuth Client ID" />
      </label>
      <label class="field" style="margin-top: 12px;">
        <span>Client Secret</span>
        <input type="password" .value=${props.credentials.clientSecret}
          @input=${(e: Event) => props.onCredentialChange("clientSecret", (e.target as HTMLInputElement).value)}
          placeholder="Your OAuth Client Secret" />
      </label>
      <label class="field" style="margin-top: 12px;">
        <span>Project ID</span>
        <input type="text" .value=${props.credentials.projectId}
          @input=${(e: Event) => props.onCredentialChange("projectId", (e.target as HTMLInputElement).value)}
          placeholder="proj_..." />
      </label>
      <label class="field" style="margin-top: 12px;">
        <span>Environment</span>
        <select .value=${props.credentials.environment}
          @change=${(e: Event) => props.onCredentialChange("environment", (e.target as HTMLSelectElement).value)}>
          <option value="development">Development</option>
          <option value="production">Production</option>
        </select>
      </label>
      <div class="row" style="margin-top: 16px; gap: 8px;">
        <button class="btn primary" ?disabled=${props.loading} @click=${props.onSaveCredentials}>
          ${props.loading ? "Saving..." : "Save Credentials"}
        </button>
        <button class="btn" @click=${props.onCancelCredentials}>Cancel</button>
      </div>
    </div>
  `;
}

// Comprehensive app list — used by agent panel
export const ALL_APPS: PipedreamApp[] = [
  { slug: "gmail", name: "Gmail", icon: "📧", connected: false },
  { slug: "google-calendar", name: "Google Calendar", icon: "📅", connected: false },
  { slug: "google-sheets", name: "Google Sheets", icon: "📊", connected: false },
  { slug: "google-drive", name: "Google Drive", icon: "📁", connected: false },
  { slug: "google-docs", name: "Google Docs", icon: "📄", connected: false },
  { slug: "google-tasks", name: "Google Tasks", icon: "✔️", connected: false },
  { slug: "youtube", name: "YouTube", icon: "▶️", connected: false },
  { slug: "youtube-data-api", name: "YouTube Data API", icon: "📺", connected: false },
  { slug: "slack", name: "Slack", icon: "💬", connected: false },
  { slug: "discord", name: "Discord", icon: "🎮", connected: false },
  { slug: "telegram-bot-api", name: "Telegram", icon: "📱", connected: false },
  { slug: "twilio", name: "Twilio", icon: "📞", connected: false },
  { slug: "sendgrid", name: "SendGrid", icon: "✉️", connected: false },
  { slug: "mailgun", name: "Mailgun", icon: "📬", connected: false },
  { slug: "mailchimp", name: "Mailchimp", icon: "🐵", connected: false },
  { slug: "zoom", name: "Zoom", icon: "📹", connected: false },
  { slug: "microsoft_teams", name: "Microsoft Teams", icon: "👥", connected: false },
  { slug: "notion", name: "Notion", icon: "📝", connected: false },
  { slug: "linear", name: "Linear", icon: "📋", connected: false },
  { slug: "asana", name: "Asana", icon: "✅", connected: false },
  { slug: "trello", name: "Trello", icon: "📌", connected: false },
  { slug: "monday", name: "Monday.com", icon: "📆", connected: false },
  { slug: "clickup", name: "ClickUp", icon: "🎯", connected: false },
  { slug: "jira", name: "Jira", icon: "🔷", connected: false },
  { slug: "todoist", name: "Todoist", icon: "☑️", connected: false },
  { slug: "github", name: "GitHub", icon: "🐙", connected: false },
  { slug: "gitlab", name: "GitLab", icon: "🦊", connected: false },
  { slug: "vercel", name: "Vercel", icon: "▲", connected: false },
  { slug: "netlify", name: "Netlify", icon: "🌐", connected: false },
  { slug: "sentry", name: "Sentry", icon: "🐛", connected: false },
  { slug: "datadog", name: "Datadog", icon: "🐕", connected: false },
  { slug: "hubspot", name: "HubSpot", icon: "🧲", connected: false },
  { slug: "salesforce_rest_api", name: "Salesforce", icon: "☁️", connected: false },
  { slug: "pipedrive", name: "Pipedrive", icon: "🔀", connected: false },
  { slug: "dropbox", name: "Dropbox", icon: "📦", connected: false },
  { slug: "aws", name: "AWS", icon: "🟠", connected: false },
  { slug: "supabase", name: "Supabase", icon: "⚡", connected: false },
  { slug: "airtable", name: "Airtable", icon: "📑", connected: false },
  { slug: "mongodb", name: "MongoDB", icon: "🍃", connected: false },
  { slug: "postgresql", name: "PostgreSQL", icon: "🐘", connected: false },
  { slug: "openai", name: "OpenAI", icon: "🤖", connected: false },
  { slug: "anthropic", name: "Anthropic", icon: "🧠", connected: false },
  { slug: "replicate", name: "Replicate", icon: "🔄", connected: false },
  { slug: "eleven-labs", name: "ElevenLabs", icon: "🔊", connected: false },
  { slug: "twitter", name: "Twitter/X", icon: "🐦", connected: false },
  { slug: "linkedin", name: "LinkedIn", icon: "💼", connected: false },
  { slug: "instagram_business", name: "Instagram", icon: "📸", connected: false },
  { slug: "stripe", name: "Stripe", icon: "💳", connected: false },
  { slug: "shopify", name: "Shopify", icon: "🛍️", connected: false },
  { slug: "typeform", name: "Typeform", icon: "📋", connected: false },
  { slug: "google_analytics", name: "Google Analytics", icon: "📈", connected: false },
  { slug: "mixpanel", name: "Mixpanel", icon: "📊", connected: false },
  { slug: "posthog", name: "PostHog", icon: "🦔", connected: false },
  { slug: "zendesk", name: "Zendesk", icon: "🎫", connected: false },
  { slug: "freshdesk", name: "Freshdesk", icon: "🍃", connected: false },
  { slug: "webhook", name: "Webhook", icon: "🪝", connected: false },
  { slug: "rss", name: "RSS", icon: "📡", connected: false },
  { slug: "spotify", name: "Spotify", icon: "🎵", connected: false },
];
