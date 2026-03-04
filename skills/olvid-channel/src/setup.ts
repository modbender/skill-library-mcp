import {
    applyAccountNameToChannelSection,
    ChannelSetupAdapter,
    DEFAULT_ACCOUNT_ID, migrateBaseNameToDefaultAccount,
    normalizeAccountId
} from "openclaw/plugin-sdk";
import {CoreConfig} from "./types";

export let OlvidSetupAdapter: ChannelSetupAdapter = {
    resolveAccountId: ({ accountId }) => normalizeAccountId(accountId),
    applyAccountName: ({ cfg, accountId, name }) =>
    applyAccountNameToChannelSection({
        cfg,
        channelKey: "olvid",
        accountId,
        name,
    }),
    validateInput: ({ accountId, input }) => {
        if (input.useEnv && accountId !== DEFAULT_ACCOUNT_ID) {
            return "Olvid env vars can only be used for the default account.";
        }
        const clientKey = input.botToken ?? input.token;
        const daemonUrl = input.url ?? input.httpUrl;
        if (!input.useEnv && (!clientKey || !daemonUrl)) {
            return "Olvid requires --bot-token and --http-url (or --use-env).";
        }
        if (!daemonUrl?.startsWith("https://") && !daemonUrl?.startsWith("http://")) {
            return "Olvid --url must include a valid base URL.";
        }
        return null;
    },
    applyAccountConfig: ({ cfg, accountId, input }) => {
        const clientKey = input.botToken?.trim() ?? input.token?.trim();
        const daemonUrl = input.url?.trim() ?? input.httpUrl?.trim();
        const namedConfig = applyAccountNameToChannelSection({
            cfg,
            channelKey: "olvid",
            accountId,
            name: input.name,
        });
        const next: CoreConfig =
            (accountId !== DEFAULT_ACCOUNT_ID
                ? migrateBaseNameToDefaultAccount({
                    cfg: namedConfig,
                    channelKey: "olvid",
                })
                : namedConfig) as CoreConfig;
        if (accountId === DEFAULT_ACCOUNT_ID) {
            return {
                ...next,
                channels: {
                    ...next.channels,
                    olvid: {
                        ...next.channels?.olvid,
                        enabled: true,
                        ...(input.useEnv
                            ? {}
                            : {
                                ...(clientKey ? { clientKey } : {}),
                                ...(daemonUrl ? { daemonUrl } : {}),
                            }),
                    },
                },
            };
        }
        return {
            ...next,
            channels: {
                ...next.channels,
                olvid: {
                    ...next.channels?.olvid,
                    enabled: true,
                    accounts: {
                        ...next.channels?.olvid?.accounts,
                        [accountId]: {
                            ...next.channels?.olvid?.accounts?.[accountId],
                            enabled: true,
                            ...(clientKey ? { clientKey } : {}),
                            ...(daemonUrl ? { daemonUrl } : {}),
                        },
                    },
                },
            },
        };
    },
};