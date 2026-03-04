///////////////////////////////////////////////////////////////////////////////
// Lightweight API client for Circle Gateway
// Docs: https://developers.circle.com/gateway

export class GatewayClient {
  static GATEWAY_API_BASE_URL = "https://gateway-api-testnet.circle.com/v1";

  // Domain identifiers for supported blockchains (same as CCTP domains)
  // See: https://developers.circle.com/cctp/cctp-supported-blockchains#cctp-supported-domains
  static DOMAINS = {
    ethereum: 0,
    mainnet: 0,
    sepolia: 0,
    avalanche: 1,
    avalancheFuji: 1,
    base: 6,
    baseSepolia: 6,
    arc: 26,
    arcTestnet: 26,
  };

  // Human-readable chain names by domain
  static CHAINS = {
    0: "Ethereum",
    1: "Avalanche",
    6: "Base",
    26: "Arc",
  };

  // Get info about supported chains and contracts
  async info() {
    return this.#get("/info");
  }

  // Check unified USDC balance for a given depositor across specified domains
  // If no domains are specified, checks all supported domains
  async balances(token, depositor, domains) {
    if (!domains) {
      domains = Object.keys(GatewayClient.CHAINS).map((d) => parseInt(d));
    }
    return this.#post("/balances", {
      token,
      sources: domains.map((domain) => ({ depositor, domain })),
    });
  }

  // Submit burn intents to receive attestation for crosschain mint
  async transfer(body) {
    return this.#post("/transfer", body);
  }

  async #get(path) {
    const url = GatewayClient.GATEWAY_API_BASE_URL + path;
    const response = await fetch(url);
    return response.json();
  }

  async #post(path, body) {
    const url = GatewayClient.GATEWAY_API_BASE_URL + path;
    const headers = { "Content-Type": "application/json" };
    const response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(body, (_key, value) =>
        typeof value === "bigint" ? value.toString() : value,
      ),
    });
    return response.json();
  }
}
