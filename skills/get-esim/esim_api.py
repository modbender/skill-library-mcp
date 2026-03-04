"""
API client for esimqr.link eSIM procurement.
Handles package search, quotes, and x402 purchase flow on Base Mainnet or Sepolia Testnet.
"""

import requests
from dataclasses import dataclass
from typing import Optional, List, Literal

BASE_URL = "https://esimqr.link"

# Network Configuration
# Note: Payment wallet addresses are returned dynamically by the API - do not hardcode them
NETWORK_CONFIG = {
    "mainnet": {
        "name": "Base Mainnet",
        "chain_id": 8453,
        "caip2": "eip155:8453",
        "usdc_token": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "api_prefix": "/api/agent",  # /api/agent/quote, /api/agent/purchase, etc.
        "real_esim": True,
    },
    "testnet": {
        "name": "Base Sepolia",
        "chain_id": 84532,
        "caip2": "eip155:84532",
        "usdc_token": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
        "api_prefix": "/api/agent-testnet",  # /api/agent-testnet/quote, etc.
        "real_esim": False,
    }
}


@dataclass
class Package:
    """eSIM package details."""
    code: str
    name: str
    data: str
    duration: str
    country: str
    price_usd: Optional[float] = None


@dataclass
class Quote:
    """Price quote for a package."""
    package_code: str
    price_usdc: float
    price_raw: int  # Amount in smallest units
    network: str  # "mainnet" or "testnet"


@dataclass
class PaymentRequired:
    """402 Payment Required response details."""
    nonce: str
    amount_raw: int
    amount_usdc: float
    pay_to: str
    asset: str
    network: str  # CAIP-2 network identifier
    chain_id: int


@dataclass
class PurchaseResult:
    """Successful purchase result."""
    esim_id: str
    iccid: str
    activation_code: str
    esim_page_url: str  # User-friendly page with QR code and install instructions
    status_url: str
    is_testnet: bool


class ESIMApiError(Exception):
    """API error with status code."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ESIMApi:
    """Client for esimqr.link API. Supports Base Mainnet (production) and Base Sepolia (testing)."""

    def __init__(self, network: Literal["mainnet", "testnet"] = "mainnet"):
        """
        Initialize API client.

        Args:
            network: "mainnet" for real eSIMs (default), "testnet" for mock/testing eSIMs
        """
        self.network = network
        self.config = NETWORK_CONFIG[network]
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ESIMAgent/1.0",
            "Accept": "application/json",
        })

    def _get_api_url(self, endpoint: str) -> str:
        """Build full API URL based on network."""
        prefix = self.config["api_prefix"]
        # endpoint should start with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return f"{BASE_URL}{prefix}{endpoint}"

    def search_packages(self, country: str) -> List[Package]:
        """
        Search for eSIM packages by country.
        Works for both mainnet and testnet (packages are the same).

        Args:
            country: Country name or code (e.g., "US", "USA", "United States")

        Returns:
            List of available packages
        """
        url = f"{BASE_URL}/api/web3/packages"
        response = self.session.get(url, params={"q": country})

        if response.status_code != 200:
            raise ESIMApiError(
                f"Failed to search packages: {response.text}",
                status_code=response.status_code
            )

        data = response.json()
        packages = []

        for pkg in data.get("packages", data if isinstance(data, list) else []):
            packages.append(Package(
                code=pkg.get("packageCode", pkg.get("code", "")),
                name=pkg.get("name", ""),
                data=pkg.get("data", pkg.get("dataAmount", "")),
                duration=pkg.get("duration", pkg.get("validity", "")),
                country=pkg.get("country", country),
                price_usd=pkg.get("price", pkg.get("priceUsd")),
            ))

        return packages

    def get_quote(self, package_code: str) -> Quote:
        """
        Get price quote for a package on the configured network.

        Args:
            package_code: Package code (e.g., "US_1_7")

        Returns:
            Quote with price details
        """
        url = self._get_api_url("/quote")
        response = self.session.get(url, params={"packageCode": package_code})

        if response.status_code != 200:
            raise ESIMApiError(
                f"Failed to get quote: {response.text}",
                status_code=response.status_code
            )

        data = response.json()

        # Handle different response formats
        usdc_amount = data.get("usdcAmount", data.get("priceUsdc", data.get("price", "0")))
        if isinstance(usdc_amount, str):
            price_usdc = float(usdc_amount)
        else:
            price_usdc = float(usdc_amount)

        # Calculate raw amount (multiply by 10^6 for USDC decimals)
        price_raw = int(price_usdc * 1_000_000)

        # Detect network from response if available
        detected_network = self.network
        if data.get("isTestnet") or data.get("network") == "eip155:84532":
            detected_network = "testnet"

        return Quote(
            package_code=data.get("packageCode", package_code),
            price_usdc=price_usdc,
            price_raw=price_raw,
            network=detected_network,
        )

    def initiate_purchase(self, package_code: str) -> PaymentRequired:
        """
        Initiate purchase on the configured network - expects 402 Payment Required response.

        Args:
            package_code: Package code to purchase

        Returns:
            PaymentRequired with payment details
        """
        url = self._get_api_url("/purchase")
        response = self.session.post(url, json={"packageCode": package_code})

        if response.status_code != 402:
            if response.status_code == 200:
                # Might be free or already paid
                raise ESIMApiError(
                    "Unexpected success - expected 402",
                    status_code=200,
                    response=response.json()
                )
            raise ESIMApiError(
                f"Unexpected response: {response.text}",
                status_code=response.status_code
            )

        data = response.json()

        # Parse x402 response - find the "transfer" scheme
        accepts_list = data.get("accepts", [])
        accepts = None
        for scheme in accepts_list:
            if scheme.get("scheme") == "transfer":
                accepts = scheme
                break

        # Fallback to first scheme if transfer not found
        if accepts is None:
            accepts = accepts_list[0] if accepts_list else {}

        extra = accepts.get("extra", {})

        amount_raw = accepts.get("amount", 0)
        if isinstance(amount_raw, str):
            amount_raw = int(amount_raw)

        # Get network info from response
        network = accepts.get("network", self.config["caip2"])
        chain_id = accepts.get("extra", {}).get("chainId", self.config["chain_id"])

        return PaymentRequired(
            nonce=extra.get("nonce", ""),
            amount_raw=amount_raw,
            amount_usdc=amount_raw / 1_000_000,
            pay_to=accepts.get("payTo", ""),
            asset=accepts.get("asset", ""),
            network=network,
            chain_id=chain_id,
        )

    def complete_purchase(self, package_code: str, tx_hash: str, nonce: str) -> PurchaseResult:
        """
        Complete purchase with payment proof on the configured network.

        Args:
            package_code: Package code being purchased
            tx_hash: Transaction hash of USDC payment
            nonce: Nonce from 402 response

        Returns:
            PurchaseResult with eSIM details
        """
        url = self._get_api_url("/purchase")

        # Ensure tx_hash has 0x prefix
        if not tx_hash.startswith("0x"):
            tx_hash = f"0x{tx_hash}"

        headers = {
            "X-PAYMENT": f"txHash={tx_hash},nonce={nonce}"
        }

        response = self.session.post(
            url,
            json={"packageCode": package_code},
            headers=headers
        )

        if response.status_code != 200:
            raise ESIMApiError(
                f"Purchase failed: {response.text}",
                status_code=response.status_code,
                response=response.json() if response.text else None
            )

        data = response.json()

        esim_id = data.get("esimId", "")
        esim_details = data.get("esimDetails", {})

        # Detect if this is testnet from response
        is_testnet = data.get("isTestnet", False) or self.network == "testnet"

        return PurchaseResult(
            esim_id=esim_id,
            iccid=esim_details.get("iccid", ""),
            activation_code=esim_details.get("activationCode", ""),
            esim_page_url=data.get("esimPageUrl", f"{BASE_URL}/web3/esim/{esim_id}"),
            status_url=data.get("statusUrl", f"{self.config['api_prefix']}/esim/{esim_id}"),
            is_testnet=is_testnet,
        )

    def get_esim_status(self, esim_id: str) -> dict:
        """
        Get status of an eSIM on the configured network.

        Args:
            esim_id: eSIM ID from purchase

        Returns:
            Status dictionary
        """
        url = self._get_api_url(f"/esim/{esim_id}")
        response = self.session.get(url)

        if response.status_code != 200:
            raise ESIMApiError(
                f"Failed to get eSIM status: {response.text}",
                status_code=response.status_code
            )

        return response.json()

    def get_network_info(self) -> dict:
        """Get information about the configured network."""
        return {
            "network": self.network,
            **self.config
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python esim_api.py search <country> [mainnet|testnet]  - Search packages")
        print("  python esim_api.py quote <code> [mainnet|testnet]      - Get price quote")
        print("  python esim_api.py network [mainnet|testnet]           - Show network config")
        print("")
        print("Examples:")
        print("  python esim_api.py search US mainnet     # Search on mainnet (default)")
        print("  python esim_api.py search US testnet     # Search on testnet")
        print("  python esim_api.py quote US_1_7 mainnet  # Get quote on mainnet")
        sys.exit(1)

    command = sys.argv[1]

    # Determine network from args (default to mainnet)
    network = "mainnet"
    if len(sys.argv) > 3:
        network_arg = sys.argv[-1].lower()
        if network_arg in ("mainnet", "testnet"):
            network = network_arg

    api = ESIMApi(network=network)

    if command == "search" and len(sys.argv) > 2:
        country = sys.argv[2]
        print(f"Searching packages for: {country} on {network}")
        packages = api.search_packages(country)
        for pkg in packages:
            price_str = f"${pkg.price_usd:.2f}" if pkg.price_usd else "Quote required"
            esim_type = "(test)" if network == "testnet" else ""
            print(f"  {pkg.code}: {pkg.name} - {pkg.data} / {pkg.duration} - {price_str} {esim_type}")

    elif command == "quote" and len(sys.argv) > 2:
        code = sys.argv[2]
        print(f"Getting quote for: {code} on {network}")
        quote = api.get_quote(code)
        network_label = "Mainnet" if quote.network == "mainnet" else "Testnet"
        print(f"  Price: ${quote.price_usdc:.2f} USDC ({network_label})")
        print(f"  Raw amount: {quote.price_raw}")

    elif command == "network":
        info = api.get_network_info()
        print(f"Network Configuration: {info['name']}")
        print(f"  Chain ID: {info['chain_id']}")
        print(f"  CAIP-2: {info['caip2']}")
        print(f"  USDC Token: {info['usdc_token']}")
        print(f"  API Prefix: {info['api_prefix']}")
        print(f"  Real eSIM: {info['real_esim']}")
        print(f"  Payment Wallet: (returned by API in quote/402 response)")

    else:
        print(f"Unknown command: {command}")
