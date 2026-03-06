import { createTools } from "../src";
import * as dotenv from "dotenv";
dotenv.config();

const SUPPORTED_NETWORKS = ["eip155:8453", "solana:5eykt4UsFv8P8NJdTREpY1vzqAQZSSfL"] as const;
type SupportedNetwork = (typeof SUPPORTED_NETWORKS)[number];

function getNetwork(): SupportedNetwork {
  const raw = process.env.PROVISION_NETWORK ?? "eip155:8453";
  if (SUPPORTED_NETWORKS.includes(raw as SupportedNetwork)) return raw as SupportedNetwork;
  throw new Error(
    `PROVISION_NETWORK must be one of: ${SUPPORTED_NETWORKS.join(", ")}. Got: ${raw}`
  );
}

async function main() {
  const privateKey = process.env.AGENT_PRIVATE_KEY;
  if (!privateKey) throw new Error("AGENT_PRIVATE_KEY required");

  const network = getNetwork();
  const originUrl =
    process.env.ORIGIN_URL ?? "https://example.com";

  let storedToken: string | null = null;
  const tools = createTools({
    getWalletPrivateKey: async () => privateKey,
    getManagementToken: async () => storedToken ?? "",
    storeManagementToken: (token) => {
      storedToken = token;
    },
  });

  console.log("🚀 Starting Agent API Provisioning...", { network, origin_url: originUrl });

  try {
    const result = await tools.provision_api({
      api_name: "Autonomous Agent API",
      network,
      origin_url: originUrl,
      routes: [
        {
          path_pattern: "/v1/inference",
          method: "POST",
          price_usdc: 0.005,
        },
      ],
    });
    console.log("✅ API Provisioned successfully!");
    console.log("Response (agent-safe):", result);
    if (storedToken) {
      console.log("Management token stored by runtime; use for get_earnings and withdraw_funds.");
    }
  } catch (error) {
    console.error("❌ Provisioning failed:", (error as Error).message);
  }
}

main();
