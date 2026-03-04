"""Integration tests for email notifications on campaign milestones."""
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import Campaign, Creator


@pytest.mark.asyncio
class TestMilestoneEmailNotifications:
    """Tests for email notifications when campaign reaches funding milestones."""

    @patch("app.services.email.email_service.send_campaign_milestone")
    async def test_25_percent_milestone_sends_email(
        self, mock_send: AsyncMock, test_client: AsyncClient, test_campaign, test_creator, test_db
    ):
        """When campaign reaches 25% of goal, creator receives email."""
        # Set campaign to 25% (goal 100000 cents = $1000, 25% = 25000 cents)
        test_campaign.goal_amount_usd = 100000
        test_campaign.current_total_usd_cents = 25000
        await test_db.commit()
        await test_db.refresh(test_campaign)

        # Trigger milestone check (implementation will call this from balance flow)
        from app.services.notification_service import check_and_send_milestone_notifications
        await check_and_send_milestone_notifications(test_db, test_campaign.id)

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["to_email"] == test_creator.email
        assert call_kwargs["milestone_percent"] == 25
        assert call_kwargs["campaign_title"] == test_campaign.title

    @patch("app.services.email.email_service.send_campaign_milestone")
    async def test_no_duplicate_notifications_for_same_milestone(
        self, mock_send: AsyncMock, test_campaign, test_creator, test_db
    ):
        """No duplicate notifications for same milestone."""
        from app.services.notification_service import check_and_send_milestone_notifications

        test_campaign.goal_amount_usd = 100000
        test_campaign.current_total_usd_cents = 25000
        test_campaign.notification_milestones_sent = [25]  # Already sent
        await test_db.commit()
        await test_db.refresh(test_campaign)

        await check_and_send_milestone_notifications(test_db, test_campaign.id)

        mock_send.assert_not_called()

    @patch("app.services.email.email_service.send_campaign_milestone")
    async def test_email_failure_does_not_crash(
        self, mock_send: AsyncMock, test_campaign, test_creator, test_db
    ):
        """Email failures do not crash the application."""
        from app.services.notification_service import check_and_send_milestone_notifications

        mock_send.side_effect = Exception("Resend API error")
        test_campaign.goal_amount_usd = 100000
        test_campaign.current_total_usd_cents = 25000
        await test_db.commit()
        await test_db.refresh(test_campaign)

        # Should not raise
        await check_and_send_milestone_notifications(test_db, test_campaign.id)


@pytest.mark.asyncio
class TestNewAdvocateEmailNotifications:
    """Tests for email notifications when a new agent advocates."""

    @patch("app.services.email.email_service.send_new_advocate_notification")
    async def test_new_advocate_sends_email(
        self, mock_send: AsyncMock, test_client: AsyncClient, test_campaign, test_agent, test_creator
    ):
        """When a new agent advocates, creator gets notified."""
        agent, api_key = test_agent
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/advocate",
            headers={"X-Agent-API-Key": api_key},
            json={"statement": "I support this campaign."},
        )
        assert response.status_code == 200

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["to_email"] == test_creator.email
        assert call_kwargs["agent_name"] == agent.name
        assert call_kwargs["campaign_title"] == test_campaign.title
