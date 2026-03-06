"""Balance tracking service for updating campaign balances and recording donations."""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Campaign, Donation, CampaignStatus
from app.services.blockchain import BlockchainService, BlockchainAPIError
from app.services.price_service import PriceService
from app.services.notification_service import check_and_send_milestone_notifications

logger = logging.getLogger(__name__)


class BalanceTracker:
    """Service for tracking campaign balances and recording donations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.blockchain_service = BlockchainService()
    
    async def update_campaign_balances(self, campaign_id: str) -> None:
        """Update balances for a single campaign."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            return
        
        # Update BTC balance
        if campaign.btc_wallet_address:
            try:
                balance = await self.blockchain_service.get_btc_balance(campaign.btc_wallet_address)
                campaign.current_btc_satoshi = balance
            except BlockchainAPIError as e:
                logger.warning(f"Failed to update BTC balance for campaign {campaign_id}: {e}")
        
        # Update ETH balance
        if campaign.eth_wallet_address:
            try:
                balance = await self.blockchain_service.get_eth_balance(campaign.eth_wallet_address)
                campaign.current_eth_wei = balance
            except BlockchainAPIError as e:
                logger.warning(f"Failed to update ETH balance for campaign {campaign_id}: {e}")
        
        # Update USDC on Base balance
        if campaign.usdc_base_wallet_address:
            try:
                balance = await self.blockchain_service.get_usdc_base_balance(campaign.usdc_base_wallet_address)
                campaign.current_usdc_base = balance
            except BlockchainAPIError as e:
                logger.warning(f"Failed to update USDC Base balance for campaign {campaign_id}: {e}")
        
        # Update SOL balance
        if campaign.sol_wallet_address:
            try:
                balance = await self.blockchain_service.get_sol_balance(campaign.sol_wallet_address)
                campaign.current_sol_lamports = balance
            except BlockchainAPIError as e:
                logger.warning(f"Failed to update SOL balance for campaign {campaign_id}: {e}")
        
        campaign.last_balance_check = datetime.now(timezone.utc)
        await self.db.commit()
    
    async def record_new_donations(
        self,
        campaign_id: str,
        chain: str,
        transactions: List[Dict[str, Any]]
    ) -> int:
        """Record new donations from transactions. Returns count of new donations."""
        # Fetch campaign to get wallet addresses
        campaign_result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            return 0
        
        # Get existing donation tx hashes to avoid duplicates
        result = await self.db.execute(
            select(Donation.tx_hash).where(
                Donation.campaign_id == campaign_id,
                Donation.chain == chain
            )
        )
        existing_hashes = set(result.scalars().all())
        
        new_donations = []
        for tx in transactions:
            tx_hash = tx.get("hash") or tx.get("tx_hash") or tx.get("signature")
            if not tx_hash or tx_hash in existing_hashes:
                continue
            
            # Extract amount and from_address based on chain
            amount = 0
            from_address = None
            
            if chain == "btc":
                # BlockCypher BTC format
                outputs = tx.get("outputs", [])
                for output in outputs:
                    addresses = output.get("addresses", [])
                    if campaign.btc_wallet_address in addresses:
                        amount += output.get("value", 0)
                inputs = tx.get("inputs", [])
                if inputs:
                    from_address = inputs[0].get("addresses", [None])[0]
            
            elif chain == "eth":
                # BlockCypher ETH format
                outputs = tx.get("outputs", [])
                for output in outputs:
                    addresses = output.get("addresses", [])
                    if campaign.eth_wallet_address in addresses:
                        amount += output.get("value", 0)
                inputs = tx.get("inputs", [])
                if inputs:
                    from_address = inputs[0].get("addresses", [None])[0]
            
            elif chain == "usdc_base":
                # Normalized format from get_usdc_base_transactions: hash, from, value, block_num
                amount = tx.get("value", 0)
                from_address = tx.get("from")
            
            elif chain == "sol":
                # Helius SOL format
                native_transfers = tx.get("nativeTransfers", [])
                for transfer in native_transfers:
                    if transfer.get("toUserAccount") == campaign.sol_wallet_address:
                        amount += transfer.get("amount", 0)
                from_address = tx.get("fromUserAccount")
            
            if amount > 0:
                block_num = tx.get("block_height") or tx.get("slot") or tx.get("block_num")
                if isinstance(block_num, str) and str(block_num).startswith("0x"):
                    block_number = int(block_num, 16)
                else:
                    block_number = block_num
                donation = Donation(
                    campaign_id=campaign_id,
                    chain=chain,
                    tx_hash=tx_hash,
                    amount_smallest_unit=amount,
                    from_address=from_address,
                    confirmed_at=datetime.now(timezone.utc),
                    block_number=block_number,
                )
                new_donations.append(donation)
        
        if new_donations:
            self.db.add_all(new_donations)
            await self.db.commit()
        
        return len(new_donations)
    
    async def poll_all_active_campaigns(self) -> None:
        """Poll balances for all active campaigns and update USD totals."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
        )
        campaigns = result.scalars().all()

        price_service = PriceService()
        try:
            prices = await price_service.get_prices()
        except Exception as e:
            logger.warning(f"Failed to fetch prices for poll: {e}")
            prices = None

        for campaign in campaigns:
            try:
                await self.update_campaign_balances(campaign.id)

                # Also check for new transactions and record donations
                if campaign.btc_wallet_address:
                    txs = await self.blockchain_service.get_btc_transactions(campaign.btc_wallet_address, limit=10)
                    await self.record_new_donations(campaign.id, "btc", txs)

                if campaign.eth_wallet_address:
                    txs = await self.blockchain_service.get_eth_transactions(campaign.eth_wallet_address, limit=10)
                    await self.record_new_donations(campaign.id, "eth", txs)

                if campaign.usdc_base_wallet_address:
                    txs = await self.blockchain_service.get_usdc_base_transactions(campaign.usdc_base_wallet_address, limit=10)
                    await self.record_new_donations(campaign.id, "usdc_base", txs)

                if campaign.sol_wallet_address:
                    txs = await self.blockchain_service.get_sol_transactions(campaign.sol_wallet_address, limit=10)
                    await self.record_new_donations(campaign.id, "sol", txs)

                # Update USD total with current prices (monotonic)
                if prices:
                    await self.db.refresh(campaign)
                    btc_amount = campaign.current_btc_satoshi / 100_000_000
                    eth_amount = campaign.current_eth_wei / 10**18
                    sol_amount = campaign.current_sol_lamports / 10**9
                    usdc_amount = campaign.current_usdc_base / 1_000_000
                    new_total_usd = (
                        btc_amount * prices["btc"]
                        + eth_amount * prices["eth"]
                        + sol_amount * prices["sol"]
                        + usdc_amount * prices["usdc_base"]
                    )
                    new_total_cents = int(new_total_usd * 100)
                    if new_total_cents > campaign.current_total_usd_cents:
                        campaign.current_total_usd_cents = new_total_cents
                    await self.db.commit()
                    await check_and_send_milestone_notifications(self.db, campaign.id)
            except Exception as e:
                logger.error(f"Error polling campaign {campaign.id}: {e}", exc_info=True)
