"""Unit tests for balance tracker service."""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from app.services.balance_tracker import BalanceTracker
from app.db.models import Campaign, CampaignStatus, CampaignCategory
from app.services.blockchain import BlockchainAPIError


@pytest.mark.asyncio
class TestBalanceTracker:
    """Tests for BalanceTracker."""
    
    @pytest.fixture
    async def tracker(self, test_db):
        return BalanceTracker(test_db)
    
    @pytest.fixture
    async def test_campaign(self, test_db, test_creator):
        campaign = Campaign(
            id="test-campaign-id",
            title="Test Campaign",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0xtest",
            btc_wallet_address="bc1qtest",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        return campaign

    @pytest.fixture
    async def test_campaign_usdc(self, test_db, test_creator):
        """Campaign with USDC Base wallet for USDC donation tests."""
        campaign = Campaign(
            id="test-campaign-usdc-id",
            title="USDC Campaign",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            usdc_base_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        return campaign
    
    async def test_update_campaign_balances_btc(self, tracker, test_campaign):
        """Should update BTC balance."""
        with patch.object(tracker.blockchain_service, "get_btc_balance", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = 100000000  # 1 BTC
            
            await tracker.update_campaign_balances(test_campaign.id)
            
            await tracker.db.refresh(test_campaign)
            assert test_campaign.current_btc_satoshi == 100000000
    
    async def test_update_campaign_balances_eth(self, tracker, test_campaign):
        """Should update ETH balance."""
        with patch.object(tracker.blockchain_service, "get_eth_balance", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = 1000000000000000000  # 1 ETH
            
            await tracker.update_campaign_balances(test_campaign.id)
            
            await tracker.db.refresh(test_campaign)
            assert test_campaign.current_eth_wei == 1000000000000000000
    
    async def test_update_campaign_balances_handles_error(self, tracker, test_campaign):
        """Should handle blockchain API errors gracefully."""
        original_balance = test_campaign.current_btc_satoshi
        with patch.object(tracker.blockchain_service, "get_btc_balance", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = BlockchainAPIError("API error")
            
            # Should not raise exception
            await tracker.update_campaign_balances(test_campaign.id)
            
            # Balance should remain unchanged (not updated)
            await tracker.db.refresh(test_campaign)
            assert test_campaign.current_btc_satoshi == original_balance
    
    async def test_record_new_donations(self, tracker, test_campaign):
        """Should record new donations from transactions."""
        transactions = [{
            "hash": "tx123",
            "outputs": [{
                "addresses": ["bc1qtest"],
                "value": 50000000  # 0.5 BTC
            }],
            "inputs": [{
                "addresses": ["bc1qfrom"]
            }],
            "block_height": 12345
        }]
        
        count = await tracker.record_new_donations(test_campaign.id, "btc", transactions)
        
        assert count == 1
        
        # Verify donation was created
        from sqlalchemy import select
        from app.db.models import Donation
        result = await tracker.db.execute(
            select(Donation).where(Donation.campaign_id == test_campaign.id)
        )
        donations = result.scalars().all()
        assert len(donations) == 1
        assert donations[0].tx_hash == "tx123"
        assert donations[0].amount_smallest_unit == 50000000
    
    async def test_record_new_donations_skips_duplicates(self, tracker, test_campaign):
        """Should skip duplicate transactions."""
        from app.db.models import Donation
        from datetime import datetime, timezone
        
        # Create existing donation
        existing = Donation(
            campaign_id=test_campaign.id,
            chain="btc",
            tx_hash="tx123",
            amount_smallest_unit=1000000,
            confirmed_at=datetime.now(timezone.utc),
        )
        tracker.db.add(existing)
        await tracker.db.commit()
        
        transactions = [{
            "hash": "tx123",  # Duplicate
            "outputs": [],
        }]
        
        count = await tracker.record_new_donations(test_campaign.id, "btc", transactions)
        
        assert count == 0

    async def test_record_new_donations_usdc_base(self, tracker, test_campaign_usdc):
        """Should record new USDC Base donations from normalized transfer data."""
        # Normalized format from get_usdc_base_transactions (hash, from, value, block_num)
        transactions = [
            {
                "hash": "0xusdc123",
                "from": "0xfrom123",
                "value": 1000000,  # 1 USDC in smallest unit (6 decimals)
                "block_num": "0x12345",
            },
        ]

        count = await tracker.record_new_donations(
            test_campaign_usdc.id, "usdc_base", transactions
        )

        assert count == 1

        from sqlalchemy import select
        from app.db.models import Donation
        result = await tracker.db.execute(
            select(Donation).where(Donation.campaign_id == test_campaign_usdc.id)
        )
        donations = result.scalars().all()
        assert len(donations) == 1
        assert donations[0].tx_hash == "0xusdc123"
        assert donations[0].amount_smallest_unit == 1000000
        assert donations[0].from_address == "0xfrom123"

    async def test_update_campaign_balances_usdc_base(self, tracker, test_campaign_usdc):
        """Should update USDC Base balance."""
        with patch.object(
            tracker.blockchain_service,
            "get_usdc_base_balance",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = 5000000  # 5 USDC (6 decimals)

            await tracker.update_campaign_balances(test_campaign_usdc.id)

            await tracker.db.refresh(test_campaign_usdc)
            assert test_campaign_usdc.current_usdc_base == 5000000

    async def test_update_campaign_balances_sol(self, tracker, test_db, test_creator):
        """Should update SOL balance."""
        campaign = Campaign(
            id="test-campaign-sol-id",
            title="SOL Campaign",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            sol_wallet_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()

        with patch.object(
            tracker.blockchain_service,
            "get_sol_balance",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = 2000000000  # 2 SOL in lamports

            await tracker.update_campaign_balances(campaign.id)

            await tracker.db.refresh(campaign)
            assert campaign.current_sol_lamports == 2000000000

    async def test_poll_all_active_campaigns_updates_usd_totals(
        self, tracker, test_db, test_creator
    ):
        """Should update current_total_usd_cents when polling campaigns."""
        campaign = Campaign(
            id="poll-usd-campaign",
            title="Poll USD Campaign",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            btc_wallet_address="bc1qtest",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
            current_btc_satoshi=100000000,  # 1 BTC
            current_eth_wei=1000000000000000000,  # 1 ETH
            current_sol_lamports=0,
            current_usdc_base=0,
        )
        test_db.add(campaign)
        await test_db.commit()

        with patch.object(
            tracker.blockchain_service,
            "get_btc_balance",
            new_callable=AsyncMock,
            return_value=100000000,
        ), patch.object(
            tracker.blockchain_service,
            "get_eth_balance",
            new_callable=AsyncMock,
            return_value=1000000000000000000,
        ), patch.object(
            tracker.blockchain_service,
            "get_btc_transactions",
            new_callable=AsyncMock,
            return_value=[],
        ), patch.object(
            tracker.blockchain_service,
            "get_eth_transactions",
            new_callable=AsyncMock,
            return_value=[],
        ), patch(
            "app.services.balance_tracker.PriceService"
        ) as mock_price_cls:
            mock_price_service = AsyncMock()
            mock_price_service.get_prices = AsyncMock(
                return_value={
                    "btc": 95000.0,
                    "eth": 2700.0,
                    "sol": 200.0,
                    "usdc_base": 1.0,
                }
            )
            mock_price_cls.return_value = mock_price_service

            await tracker.poll_all_active_campaigns()

        await tracker.db.refresh(campaign)
        # 1 BTC * 95000 + 1 ETH * 2700 = 95000 + 2700 = 97700 USD = 9770000 cents
        assert campaign.current_total_usd_cents == 9770000

    async def test_poll_usd_totals_monotonic(self, tracker, test_db, test_creator):
        """Should only increase current_total_usd_cents, never decrease."""
        campaign = Campaign(
            id="poll-monotonic-campaign",
            title="Poll Monotonic Campaign",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
            current_eth_wei=1000000000000000000,
            current_total_usd_cents=500000,  # Already has $5000
        )
        test_db.add(campaign)
        await test_db.commit()

        with patch.object(
            tracker.blockchain_service,
            "get_eth_balance",
            new_callable=AsyncMock,
            return_value=1000000000000000000,
        ), patch.object(
            tracker.blockchain_service,
            "get_eth_transactions",
            new_callable=AsyncMock,
            return_value=[],
        ), patch(
            "app.services.balance_tracker.PriceService"
        ) as mock_price_cls:
            mock_price_service = AsyncMock()
            # Price drop would result in lower total - should keep old value
            mock_price_service.get_prices = AsyncMock(
                return_value={
                    "btc": 1.0,
                    "eth": 1.0,  # Very low = ~100 USD total
                    "sol": 1.0,
                    "usdc_base": 1.0,
                }
            )
            mock_price_cls.return_value = mock_price_service

            await tracker.poll_all_active_campaigns()

        await tracker.db.refresh(campaign)
        # Should keep 500000 (monotonic) not drop to ~10000
        assert campaign.current_total_usd_cents == 500000
