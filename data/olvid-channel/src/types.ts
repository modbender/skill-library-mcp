export type OlvidAccountConfig = {
  /** Optional display name for this account (used in CLI/UI lists). */
  name?: string;
  /** If false, do not start this Olvid account. Default: true. */
  enabled?: boolean;
  /** Daemon URL (e.g., "http://locahost:50051"). */
  daemonUrl?: string;
  /** Bot client key */
  clientKey?: string;
  disableActions?: boolean;
};

export type OlvidConfig = {
  /** Optional per-account Olvid configuration (multi-account). */
  accounts?: Record<string, OlvidAccountConfig>;
} & OlvidAccountConfig;

export type CoreConfig = {
  channels?: {
    olvid?: OlvidConfig;
  };
  [key: string]: unknown;
};
