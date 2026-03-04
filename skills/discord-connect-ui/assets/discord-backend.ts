/**
 * Discord Connect backend handlers for OpenClaw Gateway.
 * Provides RPC methods for Discord bot management and health checks.
 *
 * Add to: src/gateway/server-methods/discord-connect.ts
 * Register in: src/gateway/server-methods.ts
 */

import type { ServerMethodContext } from "./types.js";
import { loadConfig, readConfigFileSnapshot, writeConfigFile } from "../../config/config.js";
import { createSubsystemLogger } from "../../logging/subsystem.js";
import { scheduleGatewaySigusr1Restart } from "../../infra/restart.js";

const log = createSubsystemLogger("discord-connect");

// Discord API base URL
const DISCORD_API = "https://discord.com/api/v10";

// Required bot permissions for basic functionality
const REQUIRED_PERMISSIONS = {
  SEND_MESSAGES: 1n << 11n,
  READ_MESSAGE_HISTORY: 1n << 16n,
  ADD_REACTIONS: 1n << 6n,
  EMBED_LINKS: 1n << 14n,
  ATTACH_FILES: 1n << 15n,
  USE_SLASH_COMMANDS: 1n << 31n,
};

const DEFAULT_PERMISSIONS = Object.values(REQUIRED_PERMISSIONS).reduce((a, b) => a | b, 0n);

interface DiscordUser {
  id: string;
  username: string;
  discriminator: string;
  avatar: string | null;
  bot?: boolean;
}

interface DiscordGuild {
  id: string;
  name: string;
  icon: string | null;
  owner_id: string;
  member_count?: number;
  permissions?: string;
}

interface DiscordChannel {
  id: string;
  name: string;
  type: number;
  guild_id?: string;
  position?: number;
  parent_id?: string | null;
}

interface HealthCheckResult {
  check: string;
  status: "pass" | "fail" | "warn";
  message: string;
  details?: unknown;
}

/**
 * Make a Discord API request.
 */
async function discordRequest<T>(
  endpoint: string,
  token: string,
  method: string = "GET",
  body?: unknown,
): Promise<T> {
  const url = `${DISCORD_API}${endpoint}`;
  const headers: Record<string, string> = {
    Authorization: `Bot ${token}`,
    "Content-Type": "application/json",
  };

  const response = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      `Discord API error: ${response.status} ${response.statusText} - ${JSON.stringify(error)}`,
    );
  }

  return response.json();
}

/**
 * Get the current Discord bot token from config.
 */
function getToken(ctx: ServerMethodContext): string | undefined {
  const config = ctx.serverState.config;
  return config.channels?.discord?.botToken;
}

/**
 * Mask a token for display (show last 4 chars).
 */
function maskToken(token: string): string {
  if (token.length <= 8) return "****";
  return "****" + token.slice(-4);
}

/**
 * Get Discord connection status.
 */
export async function discordStatus(
  _params: Record<string, never>,
  ctx: ServerMethodContext,
): Promise<{
  connected: boolean;
  configured: boolean;
  token?: string;
  user?: { id: string; username: string; discriminator: string; avatar: string | null };
  error?: string;
}> {
  const token = getToken(ctx);

  if (!token) {
    return { connected: false, configured: false };
  }

  try {
    const user = await discordRequest<DiscordUser>("/users/@me", token);
    return {
      connected: true,
      configured: true,
      token: maskToken(token),
      user: {
        id: user.id,
        username: user.username,
        discriminator: user.discriminator,
        avatar: user.avatar,
      },
    };
  } catch (err) {
    return {
      connected: false,
      configured: true,
      token: maskToken(token),
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

/**
 * Run health checks on the Discord bot.
 */
export async function discordHealth(
  _params: Record<string, never>,
  ctx: ServerMethodContext,
): Promise<{ checks: HealthCheckResult[]; healthy: boolean }> {
  const checks: HealthCheckResult[] = [];
  const token = getToken(ctx);

  // Check 1: Token configured
  if (!token) {
    checks.push({
      check: "token_configured",
      status: "fail",
      message: "Bot token not configured",
    });
    return { checks, healthy: false };
  }
  checks.push({
    check: "token_configured",
    status: "pass",
    message: "Bot token is configured",
  });

  // Check 2: Token valid (can fetch bot user)
  let user: DiscordUser;
  try {
    user = await discordRequest<DiscordUser>("/users/@me", token);
    checks.push({
      check: "token_valid",
      status: "pass",
      message: `Authenticated as ${user.username}`,
      details: { userId: user.id, username: user.username },
    });
  } catch (err) {
    checks.push({
      check: "token_valid",
      status: "fail",
      message: `Invalid token: ${err instanceof Error ? err.message : String(err)}`,
    });
    return { checks, healthy: false };
  }

  // Check 3: Gateway connection (check websocket state)
  // This would need access to the Discord client instance
  // For now, we check if we can fetch gateway info
  try {
    const gateway = await discordRequest<{ url: string }>("/gateway/bot", token);
    checks.push({
      check: "gateway_accessible",
      status: "pass",
      message: "Discord gateway is accessible",
      details: { url: gateway.url },
    });
  } catch (err) {
    checks.push({
      check: "gateway_accessible",
      status: "warn",
      message: `Gateway check failed: ${err instanceof Error ? err.message : String(err)}`,
    });
  }

  // Check 4: Application info (for intent verification)
  try {
    const app = await discordRequest<{ id: string; name: string; flags: number }>(
      "/oauth2/applications/@me",
      token,
    );
    checks.push({
      check: "application_info",
      status: "pass",
      message: `Application: ${app.name}`,
      details: { appId: app.id, name: app.name },
    });
  } catch (err) {
    checks.push({
      check: "application_info",
      status: "warn",
      message: "Could not fetch application info",
    });
  }

  // Check 5: Bot is in at least one guild
  try {
    const guilds = await discordRequest<DiscordGuild[]>("/users/@me/guilds", token);
    if (guilds.length === 0) {
      checks.push({
        check: "guilds",
        status: "warn",
        message: "Bot is not in any servers",
      });
    } else {
      checks.push({
        check: "guilds",
        status: "pass",
        message: `Bot is in ${guilds.length} server(s)`,
        details: { count: guilds.length },
      });
    }
  } catch (err) {
    checks.push({
      check: "guilds",
      status: "fail",
      message: `Failed to fetch guilds: ${err instanceof Error ? err.message : String(err)}`,
    });
  }

  const healthy = checks.every((c) => c.status !== "fail");
  return { checks, healthy };
}

/**
 * List guilds (servers) the bot is in.
 */
export async function discordGuilds(
  _params: Record<string, never>,
  ctx: ServerMethodContext,
): Promise<{ guilds: Array<{ id: string; name: string; icon: string | null; memberCount?: number }> }> {
  const token = getToken(ctx);
  if (!token) {
    throw new Error("Discord bot token not configured");
  }

  const guilds = await discordRequest<DiscordGuild[]>("/users/@me/guilds", token);
  return {
    guilds: guilds.map((g) => ({
      id: g.id,
      name: g.name,
      icon: g.icon,
      memberCount: g.member_count,
    })),
  };
}

/**
 * Get details for a specific guild.
 */
export async function discordGuild(
  params: { guildId: string },
  ctx: ServerMethodContext,
): Promise<{ guild: DiscordGuild; channels: DiscordChannel[] }> {
  const token = getToken(ctx);
  if (!token) {
    throw new Error("Discord bot token not configured");
  }

  const [guild, channels] = await Promise.all([
    discordRequest<DiscordGuild>(`/guilds/${params.guildId}?with_counts=true`, token),
    discordRequest<DiscordChannel[]>(`/guilds/${params.guildId}/channels`, token),
  ]);

  return { guild, channels };
}

/**
 * List channels in a guild.
 */
export async function discordChannels(
  params: { guildId: string },
  ctx: ServerMethodContext,
): Promise<{ channels: DiscordChannel[] }> {
  const token = getToken(ctx);
  if (!token) {
    throw new Error("Discord bot token not configured");
  }

  const channels = await discordRequest<DiscordChannel[]>(
    `/guilds/${params.guildId}/channels`,
    token,
  );

  // Filter to text channels (type 0) and sort by position
  const textChannels = channels
    .filter((c) => c.type === 0)
    .sort((a, b) => (a.position ?? 0) - (b.position ?? 0));

  return { channels: textChannels };
}

/**
 * Generate a bot invite URL.
 */
export async function discordInvite(
  params: { permissions?: string; scopes?: string[] },
  ctx: ServerMethodContext,
): Promise<{ url: string; permissions: string }> {
  const token = getToken(ctx);
  if (!token) {
    throw new Error("Discord bot token not configured");
  }

  // Get application ID
  const user = await discordRequest<DiscordUser>("/users/@me", token);
  const appId = user.id;

  const permissions = params.permissions ?? DEFAULT_PERMISSIONS.toString();
  const scopes = params.scopes ?? ["bot", "applications.commands"];

  const url = new URL("https://discord.com/api/oauth2/authorize");
  url.searchParams.set("client_id", appId);
  url.searchParams.set("permissions", permissions);
  url.searchParams.set("scope", scopes.join(" "));

  return { url: url.toString(), permissions };
}

/**
 * Test a bot token without saving it.
 */
export async function discordTestToken(
  params: { token: string },
  _ctx: ServerMethodContext,
): Promise<{ valid: boolean; user?: DiscordUser; error?: string }> {
  try {
    const user = await discordRequest<DiscordUser>("/users/@me", params.token);
    if (!user.bot) {
      return { valid: false, error: "Token is not a bot token" };
    }
    return { valid: true, user };
  } catch (err) {
    return {
      valid: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

/**
 * Set the Discord bot token (validates, saves to config, and triggers restart).
 */
export async function discordSetToken(
  params: { token: string },
  ctx: ServerMethodContext,
): Promise<{ success: boolean; user?: DiscordUser; restart?: unknown; message?: string; error?: string }> {
  // First validate the token
  const testResult = await discordTestToken(params, ctx);
  if (!testResult.valid) {
    return { success: false, error: testResult.error };
  }

  // Read current config
  const snapshot = await readConfigFileSnapshot();
  if (!snapshot.valid) {
    return { success: false, error: "Current config is invalid; fix before updating" };
  }

  // Merge in the new token
  const updatedConfig = {
    ...snapshot.config,
    channels: {
      ...snapshot.config.channels,
      discord: {
        ...snapshot.config.channels?.discord,
        token: params.token,
      },
    },
  };

  // Write the updated config
  await writeConfigFile(updatedConfig);
  log.info(`Discord token saved for user: ${testResult.user?.username}`);

  // Schedule a restart so the new token takes effect
  const restart = scheduleGatewaySigusr1Restart({
    delayMs: 2000,
    reason: "discord.setToken",
  });

  return {
    success: true,
    user: testResult.user,
    restart,
    message: "Token saved to config. Gateway restarting...",
  };
}

/**
 * Get required permissions info.
 */
export async function discordPermissions(
  _params: Record<string, never>,
  _ctx: ServerMethodContext,
): Promise<{
  required: Array<{ name: string; value: string; description: string }>;
  recommended: string;
}> {
  return {
    required: [
      { name: "Send Messages", value: REQUIRED_PERMISSIONS.SEND_MESSAGES.toString(), description: "Send messages in channels" },
      { name: "Read Message History", value: REQUIRED_PERMISSIONS.READ_MESSAGE_HISTORY.toString(), description: "Read previous messages for context" },
      { name: "Add Reactions", value: REQUIRED_PERMISSIONS.ADD_REACTIONS.toString(), description: "React to messages" },
      { name: "Embed Links", value: REQUIRED_PERMISSIONS.EMBED_LINKS.toString(), description: "Send rich embeds" },
      { name: "Attach Files", value: REQUIRED_PERMISSIONS.ATTACH_FILES.toString(), description: "Upload files and images" },
      { name: "Use Slash Commands", value: REQUIRED_PERMISSIONS.USE_SLASH_COMMANDS.toString(), description: "Register and use slash commands" },
    ],
    recommended: DEFAULT_PERMISSIONS.toString(),
  };
}

/**
 * Register all Discord Connect handlers.
 */
export function registerDiscordConnectHandlers(
  registerMethod: (name: string, handler: (params: unknown, ctx: ServerMethodContext) => Promise<unknown>) => void,
): void {
  registerMethod("discord.status", discordStatus as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
  registerMethod("discord.health", discordHealth as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
  registerMethod("discord.guilds", discordGuilds as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
  registerMethod("discord.guild", discordGuild as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
  registerMethod("discord.channels", discordChannels as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
  registerMethod("discord.invite", discordInvite as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
  registerMethod("discord.testToken", discordTestToken as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
  registerMethod("discord.setToken", discordSetToken as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
  registerMethod("discord.permissions", discordPermissions as (params: unknown, ctx: ServerMethodContext) => Promise<unknown>);
}
