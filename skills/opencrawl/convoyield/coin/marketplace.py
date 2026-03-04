"""
ConvoCoin Marketplace — Trade playbooks and strategies with CVC.

The marketplace creates a token sink: operators spend CVC to
access premium playbooks, creating demand for the token.
A 2% burn on every transaction makes CVC deflationary.

Listings:
    - Premium playbooks (sold by ConvoYield)
    - Community playbooks (sold by other operators)
    - Custom strategy packs
    - Analytics add-ons
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from convoyield.coin.blockchain import Blockchain, Transaction
from convoyield.coin.wallet import WalletManager
from convoyield.coin.tokenomics import Tokenomics


@dataclass
class MarketListing:
    """A listing on the ConvoCoin marketplace."""

    listing_id: str
    seller_address: str
    item_type: str  # "playbook", "strategy", "analytics", "custom"
    name: str
    description: str
    price_cvc: float
    metadata: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    active: bool = True
    total_sales: int = 0
    total_revenue: float = 0.0

    def to_dict(self) -> dict:
        return {
            "listing_id": self.listing_id,
            "seller_address": self.seller_address,
            "item_type": self.item_type,
            "name": self.name,
            "description": self.description,
            "price_cvc": self.price_cvc,
            "created_at": self.created_at,
            "active": self.active,
            "total_sales": self.total_sales,
            "total_revenue": self.total_revenue,
        }


class Marketplace:
    """
    The ConvoCoin marketplace.

    Handles listing, purchasing, and revenue distribution for
    premium content traded in ConvoCoin.
    """

    # Official ConvoYield treasury address
    TREASURY_ADDRESS = "CVC_TREASURY_OFFICIAL"

    def __init__(
        self,
        blockchain: Blockchain,
        wallet_manager: WalletManager,
        tokenomics: Tokenomics,
    ):
        self.blockchain = blockchain
        self.wallet_manager = wallet_manager
        self.tokenomics = tokenomics
        self.listings: dict[str, MarketListing] = {}
        self.purchase_history: list[dict] = []
        self._next_listing_id = 1

        # Seed with official playbook listings
        self._seed_official_listings()

    def _seed_official_listings(self):
        """Create official ConvoYield playbook listings."""
        official_listings = [
            {
                "name": "SaaS Sales Mastery",
                "description": "25 battle-tested plays for B2B SaaS sales. Trial conversion, expansion revenue, churn prevention.",
                "price_cvc": 50.0,
                "item_type": "playbook",
                "metadata": {"playbook_id": "saas_sales", "plays_count": 25},
            },
            {
                "name": "E-Commerce Revenue Max",
                "description": "22 plays for online retail. Cart recovery, upsell cascades, review harvesting.",
                "price_cvc": 40.0,
                "item_type": "playbook",
                "metadata": {"playbook_id": "ecommerce", "plays_count": 22},
            },
            {
                "name": "Real Estate Closer",
                "description": "20 plays for real estate. Lead qualification, offer negotiation, referral generation.",
                "price_cvc": 80.0,
                "item_type": "playbook",
                "metadata": {"playbook_id": "real_estate", "plays_count": 20},
            },
            {
                "name": "Healthcare Engagement",
                "description": "18 plays for healthcare. Appointment booking, adherence, patient satisfaction.",
                "price_cvc": 100.0,
                "item_type": "playbook",
                "metadata": {"playbook_id": "healthcare", "plays_count": 18},
            },
            {
                "name": "All Playbooks Bundle",
                "description": "All 85 plays across all 4 industry verticals. Best value.",
                "price_cvc": 200.0,
                "item_type": "playbook",
                "metadata": {"playbook_id": "all_bundle", "plays_count": 85},
            },
        ]

        for listing_data in official_listings:
            self.create_listing(
                seller_address=self.TREASURY_ADDRESS,
                **listing_data,
            )

    def create_listing(
        self,
        seller_address: str,
        name: str,
        description: str,
        price_cvc: float,
        item_type: str = "playbook",
        metadata: dict | None = None,
    ) -> MarketListing:
        """Create a new marketplace listing."""
        listing_id = f"LST_{self._next_listing_id:06d}"
        self._next_listing_id += 1

        listing = MarketListing(
            listing_id=listing_id,
            seller_address=seller_address,
            item_type=item_type,
            name=name,
            description=description,
            price_cvc=price_cvc,
            metadata=metadata or {},
        )

        self.listings[listing_id] = listing
        return listing

    def purchase(
        self,
        buyer_address: str,
        listing_id: str,
    ) -> dict | None:
        """
        Purchase an item from the marketplace.

        Flow:
        1. Verify buyer has sufficient balance
        2. Transfer CVC from buyer to seller
        3. Burn 2% of the transaction (deflationary)
        4. Record on the blockchain
        """
        listing = self.listings.get(listing_id)
        if not listing or not listing.active:
            return None

        # Check buyer balance
        buyer_balance = self.blockchain.get_balance(buyer_address)
        if buyer_balance < listing.price_cvc:
            return None

        # Calculate amounts
        burn_amount = self.tokenomics.calculate_burn(listing.price_cvc)
        seller_amount = listing.price_cvc - burn_amount

        # Record transfer transaction
        self.blockchain.add_transaction(Transaction(
            tx_type="purchase",
            sender=buyer_address,
            recipient=listing.seller_address,
            amount=seller_amount,
            metadata={
                "listing_id": listing_id,
                "item_name": listing.name,
                "original_price": listing.price_cvc,
                "burn_amount": burn_amount,
            },
        ))

        # Record burn transaction
        if burn_amount > 0:
            self.blockchain.add_transaction(Transaction(
                tx_type="burn",
                sender=buyer_address,
                recipient="BURN_ADDRESS",
                amount=burn_amount,
                metadata={"reason": "marketplace_fee"},
            ))

        # Update listing stats
        listing.total_sales += 1
        listing.total_revenue += listing.price_cvc

        # Record purchase
        purchase_record = {
            "listing_id": listing_id,
            "buyer": buyer_address,
            "seller": listing.seller_address,
            "item_name": listing.name,
            "price_cvc": listing.price_cvc,
            "seller_received": seller_amount,
            "burned": burn_amount,
            "timestamp": time.time(),
        }
        self.purchase_history.append(purchase_record)

        return purchase_record

    def get_listings(
        self,
        item_type: str | None = None,
        active_only: bool = True,
    ) -> list[dict]:
        """Get marketplace listings."""
        results = []
        for listing in self.listings.values():
            if active_only and not listing.active:
                continue
            if item_type and listing.item_type != item_type:
                continue
            results.append(listing.to_dict())
        return results

    def get_listing(self, listing_id: str) -> dict | None:
        """Get a specific listing."""
        listing = self.listings.get(listing_id)
        return listing.to_dict() if listing else None

    def get_seller_stats(self, seller_address: str) -> dict:
        """Get sales stats for a seller."""
        seller_listings = [
            l for l in self.listings.values()
            if l.seller_address == seller_address
        ]

        return {
            "total_listings": len(seller_listings),
            "active_listings": sum(1 for l in seller_listings if l.active),
            "total_sales": sum(l.total_sales for l in seller_listings),
            "total_revenue_cvc": round(
                sum(l.total_revenue for l in seller_listings), 8
            ),
        }

    def get_marketplace_stats(self) -> dict:
        """Get overall marketplace statistics."""
        active = [l for l in self.listings.values() if l.active]
        total_sales = sum(l.total_sales for l in self.listings.values())
        total_volume = sum(l.total_revenue for l in self.listings.values())

        return {
            "total_listings": len(self.listings),
            "active_listings": len(active),
            "total_sales": total_sales,
            "total_volume_cvc": round(total_volume, 8),
            "total_burned_cvc": round(self.tokenomics.total_burned, 8),
            "avg_price_cvc": round(
                sum(l.price_cvc for l in active) / len(active), 2
            ) if active else 0,
            "recent_purchases": self.purchase_history[-10:],
        }
