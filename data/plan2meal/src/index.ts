/**
 * Plan2Meal ClawdHub Skill - Main Entry Point
 */

import axios from 'axios';
import { ConvexClient } from './convex';
import { Plan2MealCommands } from './commands';
import { isValidUrl, generateState } from './utils';
import type { SkillConfig, CommandPattern, AuthProvider, Session, UserInfo } from './types';

const SESSION_TTL_MS = 1000 * 60 * 60 * 24 * 7; // 7 days
const OAUTH_STATE_TTL_MS = 1000 * 60 * 10; // 10 minutes

interface OAuthState {
  provider: AuthProvider;
  createdAt: number;
}

const DEFAULT_CONVEX_URL = 'https://gallant-bass-875.convex.cloud';
const ALLOW_DEFAULT_BACKEND = process.env.ALLOW_DEFAULT_BACKEND === 'true';

let config: SkillConfig = {
  convexUrl: process.env.CONVEX_URL || DEFAULT_CONVEX_URL,
  githubClientId: process.env.AUTH_GITHUB_ID || process.env.GITHUB_CLIENT_ID || '',
  githubClientSecret: process.env.AUTH_GITHUB_SECRET || process.env.GITHUB_CLIENT_SECRET || '',
  githubCallbackUrl: process.env.GITHUB_CALLBACK_URL || '',
  googleClientId: process.env.AUTH_GOOGLE_ID || process.env.GOOGLE_CLIENT_ID || '',
  googleClientSecret: process.env.AUTH_GOOGLE_SECRET || process.env.GOOGLE_CLIENT_SECRET || '',
  googleCallbackUrl: process.env.GOOGLE_CALLBACK_URL || '',
  appleClientId: process.env.AUTH_APPLE_ID || process.env.APPLE_CLIENT_ID || '',
  appleClientSecret: process.env.AUTH_APPLE_SECRET || process.env.APPLE_CLIENT_SECRET || '',
  appleCallbackUrl: process.env.APPLE_CALLBACK_URL || '',
  clawdbotUrl: process.env.CLAWDBOT_URL || 'http://localhost:3010'
};

const sessionStore = new Map<string, Session>();
const oauthStateStore = new Map<string, OAuthState>();

function initialize(customConfig?: Partial<SkillConfig>): { name: string; version: string; commands: CommandPattern[] } {
  if (customConfig) {
    config = { ...config, ...customConfig };
  }

  return {
    name: 'plan2meal',
    version: '1.2.5',
    commands: getCommandPatterns()
  };
}

function getCommandPatterns(): CommandPattern[] {
  return [
    { pattern: /^plan2meal\s+login$/i, description: 'Login with GitHub, Google, or Apple' },
    { pattern: /^plan2meal\s+login\s+--github$/i, description: 'Login with GitHub' },
    { pattern: /^plan2meal\s+login\s+--google$/i, description: 'Login with Google' },
    { pattern: /^plan2meal\s+login\s+--apple$/i, description: 'Login with Apple' },
    { pattern: /^plan2meal\s+logout$/i, description: 'Logout and clear session' },
    { pattern: /^plan2meal\s+add\s+(.+)$/i, description: 'Add recipe from URL' },
    { pattern: /^plan2meal\s+list$/i, description: 'List your recipes' },
    { pattern: /^plan2meal\s+search\s+(.+)$/i, description: 'Search recipes' },
    { pattern: /^plan2meal\s+show\s+(.+)$/i, description: 'Show recipe details' },
    { pattern: /^plan2meal\s+delete\s+(.+)$/i, description: 'Delete a recipe' },
    { pattern: /^plan2meal\s+lists$/i, description: 'List grocery lists' },
    { pattern: /^plan2meal\s+list-show\s+(.+)$/i, description: 'Show grocery list' },
    { pattern: /^plan2meal\s+list-create\s+(.+)$/i, description: 'Create grocery list' },
    { pattern: /^plan2meal\s+list-add\s+(\S+)\s+(\S+)$/i, description: 'Add recipe to list' },
    { pattern: /^plan2meal\s+help$/i, description: 'Show help' }
  ];
}

function getConvexClient(authToken: string, provider: AuthProvider = 'github'): ConvexClient {
  return new ConvexClient(config.convexUrl, authToken, provider);
}

function getCommands(authToken: string, provider: AuthProvider = 'github'): Plan2MealCommands {
  const convex = getConvexClient(authToken, provider);
  return new Plan2MealCommands(convex, { github: null, google: null, apple: null }, config);
}

function getConfigIssue(): string | null {
  if (!config.convexUrl) {
    return 'Missing `CONVEX_URL`. Configure your Plan2Meal backend URL before using this skill.';
  }

  if (config.convexUrl === DEFAULT_CONVEX_URL && !ALLOW_DEFAULT_BACKEND) {
    return 'Default shared backend is blocked by default. Set `CONVEX_URL` to your own backend, or explicitly opt in with `ALLOW_DEFAULT_BACKEND=true`.';
  }

  return null;
}

function cleanupExpiredData(): void {
  const now = Date.now();

  for (const [sessionId, session] of sessionStore.entries()) {
    if (now - session.createdAt > SESSION_TTL_MS) {
      sessionStore.delete(sessionId);
    }
  }

  for (const [state, data] of oauthStateStore.entries()) {
    if (now - data.createdAt > OAUTH_STATE_TTL_MS) {
      oauthStateStore.delete(state);
    }
  }
}

function getSession(sessionId: string): Session | undefined {
  cleanupExpiredData();
  return sessionStore.get(sessionId);
}

async function handleMessage(message: string, context: { sessionId?: string; userId?: string } = {}): Promise<{ text: string; requiresAuth?: boolean }> {
  const sessionId = context.sessionId || 'default';
  const text = message.trim();

  cleanupExpiredData();

  if (text.startsWith('/oauth/callback') || text.includes('code=')) {
    return handleOAuthCallback(text, sessionId);
  }

  const configIssue = getConfigIssue();
  if (configIssue) {
    return { text: `❌ ${configIssue}` };
  }

  if (/^plan2meal\s+login/i.test(text)) {
    return routeCommand(text, '', 'github', sessionId);
  }

  const session = getSession(sessionId);
  if (!session?.authToken) {
    return showLoginOptions();
  }

  return routeCommand(text, session.authToken, session.provider, sessionId);
}

function createOAuthState(provider: AuthProvider): string {
  const state = `${provider}_${generateState()}`;
  oauthStateStore.set(state, { provider, createdAt: Date.now() });
  return state;
}

function showLoginOptions(): { text: string; requiresAuth: boolean } {
  let text = '🔐 **Plan2Meal Login**\n\nChoose your login method:\n\n';

  if (config.githubClientId && config.githubClientSecret && config.githubCallbackUrl) {
    const state = createOAuthState('github');
    const githubUrl = `https://github.com/login/oauth/authorize?client_id=${config.githubClientId}&redirect_uri=${encodeURIComponent(config.githubCallbackUrl)}&state=${state}&scope=read:user`;
    text += `🐙 **GitHub** - [Login with GitHub](${githubUrl})\n\n`;
  }

  if (config.googleClientId && config.googleClientSecret && config.googleCallbackUrl) {
    const state = createOAuthState('google');
    const googleUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${config.googleClientId}&redirect_uri=${encodeURIComponent(config.googleCallbackUrl)}&state=${state}&scope=openid email profile&response_type=code`;
    text += `🔵 **Google** - [Login with Google](${googleUrl})\n\n`;
  }

  if (config.appleClientId && config.appleClientSecret && config.appleCallbackUrl) {
    const state = createOAuthState('apple');
    const appleUrl = `https://appleid.apple.com/auth/authorize?client_id=${config.appleClientId}&redirect_uri=${encodeURIComponent(config.appleCallbackUrl)}&state=${state}&scope=name email&response_type=code&response_mode=form_post`;
    text += `🍎 **Apple** - [Login with Apple](${appleUrl})\n\n`;
  }

  text += '---\nUse OAuth login links above to authenticate.';

  if (config.convexUrl === DEFAULT_CONVEX_URL) {
    text += '\n\n⚠️ Data routing notice: you are using the shared default backend. For private/self-hosted mode, set `CONVEX_URL`.';
  }

  return { text, requiresAuth: false };
}

async function routeCommand(text: string, authToken: string, authProvider: AuthProvider, sessionId: string): Promise<{ text: string }> {
  if (/^plan2meal\s+logout$/i.test(text)) {
    clearSession(sessionId);
    return { text: '✅ You have been logged out. Use `plan2meal login` to authenticate again.' };
  }

  if (/^plan2meal\s+login$/i.test(text)) {
    return showLoginOptions();
  }

  if (/^plan2meal\s+login\s+--github$/i.test(text)) {
    if (!config.githubClientId || !config.githubClientSecret || !config.githubCallbackUrl) return { text: '❌ GitHub OAuth is not fully configured.' };
    const state = createOAuthState('github');
    const githubUrl = `https://github.com/login/oauth/authorize?client_id=${config.githubClientId}&redirect_uri=${encodeURIComponent(config.githubCallbackUrl)}&state=${state}&scope=read:user`;
    return { text: `🐙 **Login with GitHub**\n\n[Click here to authorize](${githubUrl})` };
  }

  if (/^plan2meal\s+login\s+--google$/i.test(text)) {
    if (!config.googleClientId || !config.googleClientSecret || !config.googleCallbackUrl) return { text: '❌ Google OAuth is not fully configured.' };
    const state = createOAuthState('google');
    const googleUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${config.googleClientId}&redirect_uri=${encodeURIComponent(config.googleCallbackUrl)}&state=${state}&scope=openid email profile&response_type=code`;
    return { text: `🔵 **Login with Google**\n\n[Click here to authorize](${googleUrl})` };
  }

  if (/^plan2meal\s+login\s+--apple$/i.test(text)) {
    if (!config.appleClientId || !config.appleClientSecret || !config.appleCallbackUrl) return { text: '❌ Apple OAuth is not fully configured.' };
    const state = createOAuthState('apple');
    const appleUrl = `https://appleid.apple.com/auth/authorize?client_id=${config.appleClientId}&redirect_uri=${encodeURIComponent(config.appleCallbackUrl)}&state=${state}&scope=name email&response_type=code&response_mode=form_post`;
    return { text: `🍎 **Login with Apple**\n\n[Click here to authorize](${appleUrl})` };
  }

  if (!authToken) {
    return showLoginOptions();
  }

  const cmd = getCommands(authToken, authProvider);

  const addMatch = text.match(/^plan2meal\s+add\s+(.+)$/i);
  if (addMatch) {
    const url = addMatch[1].trim();
    if (!isValidUrl(url)) return { text: '❌ Invalid URL. Please provide a valid recipe URL.' };
    return cmd.addRecipe(url);
  }

  if (/^plan2meal\s+list$/i.test(text)) return cmd.listRecipes();

  const searchMatch = text.match(/^plan2meal\s+search\s+(.+)$/i);
  if (searchMatch) return cmd.searchRecipes(searchMatch[1].trim());

  const showMatch = text.match(/^plan2meal\s+show\s+(.+)$/i);
  if (showMatch) return cmd.showRecipe(showMatch[1].trim());

  const deleteMatch = text.match(/^plan2meal\s+delete\s+(.+)$/i);
  if (deleteMatch) return cmd.deleteRecipe(deleteMatch[1].trim());

  if (/^plan2meal\s+lists$/i.test(text)) return cmd.lists();

  const listShowMatch = text.match(/^plan2meal\s+list-show\s+(.+)$/i);
  if (listShowMatch) return cmd.showList(listShowMatch[1].trim());

  const listCreateMatch = text.match(/^plan2meal\s+list-create\s+(.+)$/i);
  if (listCreateMatch) return cmd.createList(listCreateMatch[1].trim());

  const listAddMatch = text.match(/^plan2meal\s+list-add\s+(\S+)\s+(\S+)$/i);
  if (listAddMatch) return cmd.addRecipeToList(listAddMatch[1].trim(), listAddMatch[2].trim());

  if (/^plan2meal\s+help$/i.test(text)) return cmd.help();

  return { text: '❌ Unknown command. Type `plan2meal help` for available commands.' };
}

async function exchangeCodeForAccessToken(provider: AuthProvider, code: string): Promise<string> {
  if (provider === 'github') {
    const response = await axios.post(
      'https://github.com/login/oauth/access_token',
      {
        client_id: config.githubClientId,
        client_secret: config.githubClientSecret,
        code,
        redirect_uri: config.githubCallbackUrl
      },
      { headers: { Accept: 'application/json' } }
    );

    const token = response.data?.access_token;
    if (!token) throw new Error(response.data?.error_description || 'GitHub token exchange failed');
    return token;
  }

  if (provider === 'google') {
    const params = new URLSearchParams({
      code,
      client_id: config.googleClientId,
      client_secret: config.googleClientSecret,
      redirect_uri: config.googleCallbackUrl,
      grant_type: 'authorization_code'
    });

    const response = await axios.post('https://oauth2.googleapis.com/token', params.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    const token = response.data?.access_token;
    if (!token) throw new Error('Google token exchange failed');
    return token;
  }

  const params = new URLSearchParams({
    client_id: config.appleClientId,
    client_secret: config.appleClientSecret,
    code,
    grant_type: 'authorization_code',
    redirect_uri: config.appleCallbackUrl
  });

  const response = await axios.post('https://appleid.apple.com/auth/token', params.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });

  const token = response.data?.access_token;
  if (!token) throw new Error('Apple token exchange failed');
  return token;
}

async function fetchUserInfo(provider: AuthProvider, token: string): Promise<UserInfo | null> {
  try {
    if (provider === 'github') {
      const r = await axios.get('https://api.github.com/user', {
        headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' }
      });
      return {
        id: String(r.data.id),
        name: r.data.name || r.data.login,
        email: r.data.email || undefined,
        login: r.data.login,
        avatarUrl: r.data.avatar_url || undefined
      };
    }
  } catch {
    return null;
  }

  return null;
}

async function handleOAuthCallback(text: string, sessionId: string): Promise<{ text: string }> {
  let callbackUrl: URL;

  try {
    callbackUrl = new URL(text.startsWith('http') ? text : `http://localhost${text}`);
  } catch {
    return { text: '❌ Invalid callback URL.' };
  }

  const code = callbackUrl.searchParams.get('code');
  const state = callbackUrl.searchParams.get('state') || '';

  if (!code) return { text: '❌ No authorization code found.' };

  const stateEntry = oauthStateStore.get(state);
  if (!stateEntry) return { text: '❌ Invalid or expired OAuth state. Please run `plan2meal login` again.' };

  oauthStateStore.delete(state);

  if (Date.now() - stateEntry.createdAt > OAUTH_STATE_TTL_MS) {
    return { text: '❌ OAuth session expired. Please run `plan2meal login` again.' };
  }

  try {
    const accessToken = await exchangeCodeForAccessToken(stateEntry.provider, code);
    const userInfo = await fetchUserInfo(stateEntry.provider, accessToken);

    sessionStore.set(sessionId, {
      authToken: accessToken,
      provider: stateEntry.provider,
      userInfo,
      createdAt: Date.now()
    });

    const providerName = stateEntry.provider.charAt(0).toUpperCase() + stateEntry.provider.slice(1);
    const userLabel = userInfo?.name || userInfo?.email || 'Authenticated user';

    return {
      text: `✅ Successfully authenticated with **${providerName}** as **${userLabel}**!\n\nYou can now use Plan2Meal commands. Type \`plan2meal help\` to get started.`
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return { text: `❌ Authentication failed: ${message}` };
  }
}

function clearSession(sessionId: string): void {
  sessionStore.delete(sessionId);
}

module.exports = {
  initialize,
  handleMessage,
  clearSession,
  getSession,
  getCommandPatterns
};
