import type { ResolvedOneBotAccount, OneBotAccountConfig } from "./types.js";

const DEFAULT_ACCOUNT_ID = "default";

interface OpenClawConfig {
  channels?: {
    onebot?: OneBotChannelConfig;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

interface OneBotChannelConfig extends OneBotAccountConfig {
  accounts?: Record<string, OneBotAccountConfig>;
}

/**
 * List all configured OneBot account IDs.
 */
export function listOneBotAccountIds(cfg: OpenClawConfig): string[] {
  const ids = new Set<string>();
  const onebot = cfg.channels?.onebot;

  if (onebot?.wsUrl || onebot?.httpUrl) {
    ids.add(DEFAULT_ACCOUNT_ID);
  }

  if (onebot?.accounts) {
    for (const accountId of Object.keys(onebot.accounts)) {
      const acct = onebot.accounts[accountId];
      if (acct?.wsUrl || acct?.httpUrl) {
        ids.add(accountId);
      }
    }
  }

  return Array.from(ids);
}

/**
 * Resolve a OneBot account from config.
 */
export function resolveOneBotAccount(
  cfg: OpenClawConfig,
  accountId?: string | null,
): ResolvedOneBotAccount {
  const resolvedAccountId = accountId ?? DEFAULT_ACCOUNT_ID;
  const onebot = cfg.channels?.onebot;

  let accountConfig: OneBotAccountConfig = {};

  if (resolvedAccountId === DEFAULT_ACCOUNT_ID) {
    accountConfig = {
      enabled: onebot?.enabled,
      name: onebot?.name,
      wsUrl: onebot?.wsUrl,
      httpUrl: onebot?.httpUrl,
      accessToken: onebot?.accessToken,
      allowFrom: onebot?.allowFrom,
    };
  } else {
    const account = onebot?.accounts?.[resolvedAccountId];
    accountConfig = account ?? {};
  }

  // Environment variable fallbacks for default account
  let wsUrl = accountConfig.wsUrl ?? "";
  let httpUrl = accountConfig.httpUrl ?? "";
  let accessToken = accountConfig.accessToken;

  if (resolvedAccountId === DEFAULT_ACCOUNT_ID) {
    if (!wsUrl && process.env.ONEBOT_WS_URL) {
      wsUrl = process.env.ONEBOT_WS_URL;
    }
    if (!httpUrl && process.env.ONEBOT_HTTP_URL) {
      httpUrl = process.env.ONEBOT_HTTP_URL;
    }
    if (!accessToken && process.env.ONEBOT_ACCESS_TOKEN) {
      accessToken = process.env.ONEBOT_ACCESS_TOKEN;
    }
  }

  const allowFrom = accountConfig.allowFrom;

  return {
    accountId: resolvedAccountId,
    name: accountConfig.name,
    enabled: accountConfig.enabled !== false,
    wsUrl,
    httpUrl,
    accessToken,
    allowFrom,
    config: accountConfig,
  };
}

/**
 * Apply account configuration changes.
 */
export function applyOneBotAccountConfig(
  cfg: OpenClawConfig,
  accountId: string,
  input: { wsUrl?: string; httpUrl?: string; accessToken?: string; name?: string },
): OpenClawConfig {
  const next = { ...cfg };

  if (accountId === DEFAULT_ACCOUNT_ID) {
    next.channels = {
      ...next.channels,
      onebot: {
        ...next.channels?.onebot,
        enabled: true,
        ...(input.wsUrl ? { wsUrl: input.wsUrl } : {}),
        ...(input.httpUrl ? { httpUrl: input.httpUrl } : {}),
        ...(input.accessToken ? { accessToken: input.accessToken } : {}),
        ...(input.name ? { name: input.name } : {}),
      },
    };
  } else {
    next.channels = {
      ...next.channels,
      onebot: {
        ...next.channels?.onebot,
        enabled: true,
        accounts: {
          ...(next.channels?.onebot as OneBotChannelConfig)?.accounts,
          [accountId]: {
            ...(next.channels?.onebot as OneBotChannelConfig)?.accounts?.[accountId],
            enabled: true,
            ...(input.wsUrl ? { wsUrl: input.wsUrl } : {}),
            ...(input.httpUrl ? { httpUrl: input.httpUrl } : {}),
            ...(input.accessToken ? { accessToken: input.accessToken } : {}),
            ...(input.name ? { name: input.name } : {}),
          },
        },
      },
    };
  }

  return next;
}
