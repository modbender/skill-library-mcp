/**
 * Discord Connect UI views for OpenClaw Dashboard.
 * Lit-based templates for the Discord tab.
 *
 * Add to: ui/src/ui/views/discord.ts
 * Import in: ui/src/ui/app-render.ts
 */

import { html, css, LitElement } from "lit";
import { customElement, state } from "lit/decorators.js";
import { rpc } from "../rpc.js";

interface DiscordUser {
  id: string;
  username: string;
  discriminator: string;
  avatar: string | null;
}

interface DiscordGuild {
  id: string;
  name: string;
  icon: string | null;
  memberCount?: number;
}

interface HealthCheck {
  check: string;
  status: "pass" | "fail" | "warn";
  message: string;
}

interface DiscordStatus {
  connected: boolean;
  configured: boolean;
  token?: string;
  user?: DiscordUser;
  error?: string;
}

@customElement("discord-connect-view")
export class DiscordConnectView extends LitElement {
  static styles = css`
    :host {
      display: block;
      padding: 24px;
      max-width: 900px;
    }

    h1 {
      font-size: 24px;
      font-weight: 600;
      margin: 0 0 8px 0;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .subtitle {
      color: var(--text-secondary, #666);
      margin-bottom: 24px;
    }

    .card {
      background: var(--surface, #fff);
      border: 1px solid var(--border, #e0e0e0);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
    }

    .card-title {
      font-size: 16px;
      font-weight: 600;
      margin: 0 0 16px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 16px;
      font-size: 13px;
      font-weight: 500;
    }

    .status-connected {
      background: #dcfce7;
      color: #166534;
    }

    .status-disconnected {
      background: #fee2e2;
      color: #991b1b;
    }

    .status-unconfigured {
      background: #f3f4f6;
      color: #6b7280;
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 12px;
    }

    .avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--surface-secondary, #f0f0f0);
    }

    .username {
      font-weight: 600;
      font-size: 16px;
    }

    .user-id {
      font-size: 13px;
      color: var(--text-secondary, #666);
    }

    .setup-steps {
      counter-reset: step;
    }

    .setup-step {
      display: flex;
      gap: 16px;
      margin-bottom: 20px;
    }

    .step-number {
      counter-increment: step;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--primary, #5865f2);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 14px;
      flex-shrink: 0;
    }

    .step-number::before {
      content: counter(step);
    }

    .step-content h3 {
      margin: 0 0 4px 0;
      font-size: 15px;
      font-weight: 600;
    }

    .step-content p {
      margin: 0;
      color: var(--text-secondary, #666);
      font-size: 14px;
    }

    .step-content a {
      color: var(--primary, #5865f2);
      text-decoration: none;
    }

    .step-content a:hover {
      text-decoration: underline;
    }

    .token-input {
      display: flex;
      gap: 8px;
      margin-top: 12px;
    }

    .token-input input {
      flex: 1;
      padding: 10px 14px;
      border: 1px solid var(--border, #e0e0e0);
      border-radius: 8px;
      font-size: 14px;
      font-family: monospace;
    }

    .token-input input:focus {
      outline: none;
      border-color: var(--primary, #5865f2);
    }

    button {
      padding: 10px 20px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;
    }

    .btn-primary {
      background: var(--primary, #5865f2);
      color: white;
    }

    .btn-primary:hover {
      background: var(--primary-hover, #4752c4);
    }

    .btn-primary:disabled {
      background: var(--disabled, #ccc);
      cursor: not-allowed;
    }

    .btn-secondary {
      background: var(--surface-secondary, #f0f0f0);
      color: var(--text, #333);
    }

    .btn-secondary:hover {
      background: var(--surface-secondary-hover, #e0e0e0);
    }

    .health-checks {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .health-check {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      background: var(--surface-secondary, #f8f8f8);
      border-radius: 8px;
    }

    .health-icon {
      font-size: 16px;
    }

    .health-pass { color: #16a34a; }
    .health-fail { color: #dc2626; }
    .health-warn { color: #ca8a04; }

    .guilds-list {
      display: grid;
      gap: 12px;
    }

    .guild-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: var(--surface-secondary, #f8f8f8);
      border-radius: 8px;
    }

    .guild-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--surface, #e0e0e0);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      color: var(--text-secondary, #666);
    }

    .guild-icon img {
      width: 100%;
      height: 100%;
      border-radius: 50%;
    }

    .guild-name {
      font-weight: 500;
    }

    .guild-members {
      font-size: 13px;
      color: var(--text-secondary, #666);
    }

    .error-message {
      background: #fee2e2;
      color: #991b1b;
      padding: 12px 16px;
      border-radius: 8px;
      margin-top: 12px;
    }

    .success-message {
      background: #dcfce7;
      color: #166534;
      padding: 12px 16px;
      border-radius: 8px;
      margin-top: 12px;
    }

    .invite-url {
      background: var(--surface-secondary, #f8f8f8);
      padding: 12px;
      border-radius: 8px;
      font-family: monospace;
      font-size: 13px;
      word-break: break-all;
      margin-top: 12px;
    }

    .copy-btn {
      margin-top: 8px;
      font-size: 13px;
      padding: 6px 12px;
    }

    .loading {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-secondary, #666);
    }

    .spinner {
      width: 16px;
      height: 16px;
      border: 2px solid var(--border, #e0e0e0);
      border-top-color: var(--primary, #5865f2);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `;

  @state() private status: DiscordStatus | null = null;
  @state() private healthChecks: HealthCheck[] = [];
  @state() private guilds: DiscordGuild[] = [];
  @state() private loading = true;
  @state() private tokenInput = "";
  @state() private saving = false;
  @state() private saveError = "";
  @state() private saveSuccess = false;
  @state() private inviteUrl = "";
  @state() private showSetup = false;

  connectedCallback() {
    super.connectedCallback();
    this.loadStatus();
  }

  private async loadStatus() {
    this.loading = true;
    try {
      const [statusResult, healthResult, guildsResult] = await Promise.all([
        rpc("discord.status", {}),
        rpc("discord.health", {}).catch(() => ({ checks: [], healthy: false })),
        rpc("discord.guilds", {}).catch(() => ({ guilds: [] })),
      ]);
      
      this.status = statusResult as DiscordStatus;
      this.healthChecks = (healthResult as { checks: HealthCheck[] }).checks;
      this.guilds = (guildsResult as { guilds: DiscordGuild[] }).guilds;
      this.showSetup = !this.status.configured;
    } catch (err) {
      console.error("Failed to load Discord status:", err);
      this.status = { connected: false, configured: false };
      this.showSetup = true;
    }
    this.loading = false;
  }

  private async saveToken() {
    if (!this.tokenInput.trim()) return;
    
    this.saving = true;
    this.saveError = "";
    this.saveSuccess = false;
    
    try {
      // Validate first
      const testResult = await rpc("discord.testToken", { token: this.tokenInput }) as { valid: boolean; error?: string };
      
      if (!testResult.valid) {
        this.saveError = testResult.error || "Invalid token";
        this.saving = false;
        return;
      }
      
      // Save the token
      await rpc("discord.setToken", { token: this.tokenInput });
      this.saveSuccess = true;
      this.tokenInput = "";
      
      // Reload status after a short delay to let connection establish
      setTimeout(() => this.loadStatus(), 1500);
    } catch (err) {
      this.saveError = String(err);
    }
    
    this.saving = false;
  }

  private async generateInvite() {
    try {
      const result = await rpc("discord.invite", {}) as { url: string };
      this.inviteUrl = result.url;
    } catch (err) {
      console.error("Failed to generate invite:", err);
    }
  }

  private copyInvite() {
    navigator.clipboard.writeText(this.inviteUrl);
  }

  private getAvatarUrl(user: DiscordUser): string {
    if (!user.avatar) {
      const defaultIndex = Number(BigInt(user.id) >> 22n) % 6;
      return `https://cdn.discordapp.com/embed/avatars/${defaultIndex}.png`;
    }
    return `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=96`;
  }

  private getGuildIcon(guild: DiscordGuild): string | null {
    if (!guild.icon) return null;
    return `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=80`;
  }

  render() {
    if (this.loading) {
      return html`
        <h1>🎮 Discord</h1>
        <div class="loading">
          <div class="spinner"></div>
          Loading...
        </div>
      `;
    }

    return html`
      <h1>🎮 Discord</h1>
      <p class="subtitle">Connect and manage your Discord bot</p>

      <!-- Connection Status -->
      <div class="card">
        <h2 class="card-title">
          Connection Status
          ${this.status?.connected
            ? html`<span class="status-badge status-connected">🟢 Connected</span>`
            : this.status?.configured
              ? html`<span class="status-badge status-disconnected">🔴 Disconnected</span>`
              : html`<span class="status-badge status-unconfigured">⚪ Not Configured</span>`}
        </h2>

        ${this.status?.user ? html`
          <div class="user-info">
            <img class="avatar" src="${this.getAvatarUrl(this.status.user)}" alt="Bot avatar">
            <div>
              <div class="username">${this.status.user.username}</div>
              <div class="user-id">ID: ${this.status.user.id}</div>
            </div>
          </div>
        ` : ""}

        ${this.status?.error ? html`
          <div class="error-message">${this.status.error}</div>
        ` : ""}

        <div style="margin-top: 16px">
          <button class="btn-secondary" @click=${() => this.showSetup = !this.showSetup}>
            ${this.showSetup ? "Hide Setup" : "Show Setup Guide"}
          </button>
          <button class="btn-secondary" style="margin-left: 8px" @click=${this.loadStatus}>
            Refresh
          </button>
        </div>
      </div>

      <!-- Setup Guide -->
      ${this.showSetup ? html`
        <div class="card">
          <h2 class="card-title">📋 Setup Guide</h2>
          <div class="setup-steps">
            <div class="setup-step">
              <div class="step-number"></div>
              <div class="step-content">
                <h3>Create Discord Application</h3>
                <p>Go to <a href="https://discord.com/developers/applications" target="_blank">Discord Developer Portal</a> and create a new application.</p>
              </div>
            </div>
            <div class="setup-step">
              <div class="step-number"></div>
              <div class="step-content">
                <h3>Get Bot Token</h3>
                <p>In your app, go to <strong>Bot</strong> tab → <strong>Reset Token</strong> → Copy the token.</p>
              </div>
            </div>
            <div class="setup-step">
              <div class="step-number"></div>
              <div class="step-content">
                <h3>Enable Intents</h3>
                <p>In Bot settings, enable <strong>Message Content Intent</strong> (required).</p>
              </div>
            </div>
            <div class="setup-step">
              <div class="step-number"></div>
              <div class="step-content">
                <h3>Enter Token Below</h3>
                <p>Paste your bot token and click Test to verify it works.</p>
              </div>
            </div>
          </div>

          <div class="token-input">
            <input 
              type="password" 
              placeholder="Paste your bot token here..."
              .value=${this.tokenInput}
              @input=${(e: InputEvent) => this.tokenInput = (e.target as HTMLInputElement).value}
            >
            <button class="btn-primary" @click=${this.saveToken} ?disabled=${this.saving || !this.tokenInput}>
              ${this.saving ? "Saving..." : "Save"}
            </button>
          </div>

          ${this.saveError ? html`
            <div class="error-message">
              ❌ ${this.saveError}
            </div>
          ` : ""}
          
          ${this.saveSuccess ? html`
            <div class="success-message">
              ✅ Token saved! Connecting...
            </div>
          ` : ""}
        </div>
      ` : ""}

      <!-- Health Checks -->
      ${this.status?.configured && this.healthChecks.length > 0 ? html`
        <div class="card">
          <h2 class="card-title">🏥 Health Checks</h2>
          <div class="health-checks">
            ${this.healthChecks.map(check => html`
              <div class="health-check">
                <span class="health-icon health-${check.status}">
                  ${check.status === "pass" ? "✓" : check.status === "fail" ? "✗" : "⚠"}
                </span>
                <span>${check.message}</span>
              </div>
            `)}
          </div>
        </div>
      ` : ""}

      <!-- Servers -->
      ${this.guilds.length > 0 ? html`
        <div class="card">
          <h2 class="card-title">🏠 Servers (${this.guilds.length})</h2>
          <div class="guilds-list">
            ${this.guilds.map(guild => html`
              <div class="guild-item">
                <div class="guild-icon">
                  ${this.getGuildIcon(guild) 
                    ? html`<img src="${this.getGuildIcon(guild)}" alt="${guild.name}">`
                    : guild.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div class="guild-name">${guild.name}</div>
                  ${guild.memberCount ? html`
                    <div class="guild-members">${guild.memberCount.toLocaleString()} members</div>
                  ` : ""}
                </div>
              </div>
            `)}
          </div>
        </div>
      ` : ""}

      <!-- Invite Generator -->
      ${this.status?.configured ? html`
        <div class="card">
          <h2 class="card-title">🔗 Invite Bot to Server</h2>
          <p style="color: var(--text-secondary); margin: 0 0 12px">Generate an invite link with required permissions.</p>
          <button class="btn-primary" @click=${this.generateInvite}>Generate Invite URL</button>
          ${this.inviteUrl ? html`
            <div class="invite-url">${this.inviteUrl}</div>
            <button class="btn-secondary copy-btn" @click=${this.copyInvite}>📋 Copy URL</button>
          ` : ""}
        </div>
      ` : ""}
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "discord-connect-view": DiscordConnectView;
  }
}
