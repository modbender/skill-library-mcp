"use strict";

const { z } = require("zod");

// ─── Network Constants ────────────────────────────────────────────────
const NETWORKS = Object.freeze({
  BASE_SEPOLIA: { chainId: 84532, name: "Base Sepolia", isTestnet: true },
  BASE_MAINNET: { chainId: 8453, name: "Base Mainnet", isTestnet: false },
});

const CHAIN_ID_MAP = Object.freeze({
  [NETWORKS.BASE_SEPOLIA.chainId]: NETWORKS.BASE_SEPOLIA,
  [NETWORKS.BASE_MAINNET.chainId]: NETWORKS.BASE_MAINNET,
});

// ─── Contract addresses (per-network) ─────────────────────────────────
const CONTRACT_ADDRESSES = Object.freeze({
  [NETWORKS.BASE_SEPOLIA.chainId]: {
    creditor: "0x1867a19816f38ec31ec3af1be15fd7104f161978",
    borrowerManager: "0x76e51158015e869ab2875fa17b87383d8886e93c",
    usdc: "0x55b8ff660d4f0f176de84f325d39a773a7a3bda7",
  },
  [NETWORKS.BASE_MAINNET.chainId]: {
    creditor: null,
    borrowerManager: null,
    usdc: null,
  },
});

const USDC_DECIMALS = 6;

// ─── Wallet Signer Providers ──────────────────────────────────────────
// The wallet signer is ALWAYS owned/controlled by the user or agent
// operator — never by SoHo. SoHo is a credit layer only; it does not
// custody keys, hold key shards, or produce signatures.
const SignerProvider = Object.freeze({
  WALLET_SIGNER_REMOTE: "WALLET_SIGNER_REMOTE",
  LOCAL_PRIVATE_KEY: "LOCAL_PRIVATE_KEY",
});

// ─── Zod Schema ───────────────────────────────────────────────────────
const envSchema = z
  .object({
    RPC_URL: z.string().url("RPC_URL must be a valid URL"),
    CHAIN_ID: z.coerce.number().int().positive(),
    SIGNER_PROVIDER: z.nativeEnum(SignerProvider),

    // Wallet signer service (user/operator-controlled MPC / HSM)
    WALLET_SIGNER_SERVICE_URL: z.string().url().optional(),
    SIGNER_SERVICE_AUTH_TOKEN: z.string().min(1).optional(),

    // SoHo credit-layer API (credit checks, just-in-time funding)
    SOHO_API_URL: z.string().url().optional(),

    // Dev-only local key
    SOHO_DEV_PRIVATE_KEY: z.string().min(1).optional(),
    DEV_ALLOW_LOCAL_KEY: z.literal("YES").optional(),

    // Mainnet safety gate
    SOHO_MAINNET_CONFIRM: z.literal("YES").optional(),
  })
  .superRefine((val, ctx) => {
    const network = CHAIN_ID_MAP[val.CHAIN_ID];
    if (!network) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `Unsupported CHAIN_ID ${val.CHAIN_ID}. Allowed: ${Object.keys(CHAIN_ID_MAP).join(", ")}`,
        path: ["CHAIN_ID"],
      });
      return;
    }

    if (!network.isTestnet && val.SOHO_MAINNET_CONFIRM !== "YES") {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message:
          "SOHO_MAINNET_CONFIRM=YES is required to transact on mainnet. This is a safety gate.",
        path: ["SOHO_MAINNET_CONFIRM"],
      });
    }

    if (val.SIGNER_PROVIDER === SignerProvider.WALLET_SIGNER_REMOTE) {
      if (!val.WALLET_SIGNER_SERVICE_URL) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message:
            "WALLET_SIGNER_SERVICE_URL is required when SIGNER_PROVIDER=WALLET_SIGNER_REMOTE",
          path: ["WALLET_SIGNER_SERVICE_URL"],
        });
      }
    }

    if (val.SIGNER_PROVIDER === SignerProvider.LOCAL_PRIVATE_KEY) {
      const isTestnet = network && network.isTestnet;
      const devOverride = val.DEV_ALLOW_LOCAL_KEY === "YES";
      if (!isTestnet && !devOverride) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message:
            "LOCAL_PRIVATE_KEY signer is only allowed on testnets. " +
            "Set DEV_ALLOW_LOCAL_KEY=YES to override (NOT recommended for mainnet).",
          path: ["SIGNER_PROVIDER"],
        });
      }
      if (!val.SOHO_DEV_PRIVATE_KEY) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message:
            "SOHO_DEV_PRIVATE_KEY is required when SIGNER_PROVIDER=LOCAL_PRIVATE_KEY",
          path: ["SOHO_DEV_PRIVATE_KEY"],
        });
      }
    }
  });

// ─── Loader ───────────────────────────────────────────────────────────
function loadConfig() {
  require("dotenv").config();

  const result = envSchema.safeParse(process.env);
  if (!result.success) {
    const messages = result.error.issues
      .map((i) => `  • ${i.path.join(".")}: ${i.message}`)
      .join("\n");
    console.error(`\n❌ Configuration error(s):\n${messages}\n`);
    process.exit(1);
  }

  const env = result.data;
  const network = CHAIN_ID_MAP[env.CHAIN_ID];
  const addresses = CONTRACT_ADDRESSES[env.CHAIN_ID];

  if (!network.isTestnet && (!addresses.creditor || !addresses.usdc)) {
    console.error(
      "❌ Mainnet contract addresses are not yet configured. Deploy contracts first.",
    );
    process.exit(1);
  }

  return Object.freeze({
    rpcUrl: env.RPC_URL,
    chainId: env.CHAIN_ID,
    network,
    addresses,
    signerProvider: env.SIGNER_PROVIDER,
    walletSignerServiceUrl: env.WALLET_SIGNER_SERVICE_URL || null,
    signerServiceAuthToken: env.SIGNER_SERVICE_AUTH_TOKEN || null,
    sohoApiUrl: env.SOHO_API_URL || null,
    devPrivateKey: env.SOHO_DEV_PRIVATE_KEY || null,
    usdcDecimals: USDC_DECIMALS,
  });
}

module.exports = {
  NETWORKS,
  CHAIN_ID_MAP,
  CONTRACT_ADDRESSES,
  USDC_DECIMALS,
  SignerProvider,
  loadConfig,
};
