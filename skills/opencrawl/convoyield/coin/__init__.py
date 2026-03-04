"""
ConvoCoin — The world's first Proof-of-Yield cryptocurrency.

Traditional crypto mines blocks by burning electricity.
ConvoCoin mines blocks by capturing conversational yield.

The more value your bot extracts from conversations,
the more ConvoCoin you earn. Real work. Real value. Real tokens.

Modules:
    blockchain  — Block/chain data structures with SHA-256 integrity
    wallet      — Wallet creation, balances, and key management
    miner       — Proof-of-Yield mining tied to ConvoYield captures
    tokenomics  — Supply curves, halvings, and reward schedules
    marketplace — Buy/sell playbooks and strategies with ConvoCoin
    ledger      — Persistent transaction ledger
"""

from convoyield.coin.blockchain import Block, Blockchain
from convoyield.coin.wallet import Wallet, WalletManager
from convoyield.coin.miner import ProofOfYieldMiner
from convoyield.coin.tokenomics import Tokenomics
from convoyield.coin.marketplace import Marketplace
from convoyield.coin.ledger import Ledger

__all__ = [
    "Block",
    "Blockchain",
    "Wallet",
    "WalletManager",
    "ProofOfYieldMiner",
    "Tokenomics",
    "Marketplace",
    "Ledger",
]
