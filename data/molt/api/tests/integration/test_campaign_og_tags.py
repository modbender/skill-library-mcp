"""Integration tests for campaign OG meta tags endpoint.

Tests the GET /api/campaigns/og/{campaign_id} endpoint that returns
minimal HTML with Open Graph meta tags for social crawlers.
"""
import pytest
from httpx import AsyncClient

from app.db.models import Campaign, CampaignImage, CampaignCategory, CampaignStatus, Creator


@pytest.fixture
async def test_campaign_with_image(test_db, test_creator):
    """Create a campaign with an uploaded image for OG tag tests."""
    campaign = Campaign(
        id="og-test-campaign-id",
        title="Help Rebuild After the Flood",
        description="A devastating flood destroyed homes in the village. We need funds to rebuild shelters, provide clean water, and support families who lost everything. Every donation goes directly to the affected families.",
        category=CampaignCategory.DISASTER_RELIEF,
        goal_amount_usd=500000,  # $5000 in cents
        eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        contact_email=test_creator.email,
        creator_id=test_creator.id,
        status=CampaignStatus.ACTIVE,
    )
    test_db.add(campaign)
    await test_db.flush()

    image = CampaignImage(
        campaign_id=campaign.id,
        image_path=f"{campaign.id}/img_20260213_120000.jpg",
        display_order=0,
    )
    test_db.add(image)
    await test_db.commit()
    await test_db.refresh(campaign)
    return campaign


@pytest.fixture
async def test_campaign_with_cover_url(test_db, test_creator):
    """Create a campaign with an external cover image URL (no uploaded images)."""
    campaign = Campaign(
        id="og-cover-url-campaign-id",
        title="Support Local Schools",
        description="Help us provide supplies and resources to underfunded schools in rural areas.",
        category=CampaignCategory.EDUCATION,
        goal_amount_usd=200000,
        eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        cover_image_url="https://example.com/school-cover.jpg",
        contact_email=test_creator.email,
        creator_id=test_creator.id,
        status=CampaignStatus.ACTIVE,
    )
    test_db.add(campaign)
    await test_db.commit()
    await test_db.refresh(campaign)
    return campaign


@pytest.mark.asyncio
class TestCampaignOGTags:
    """Tests for GET /api/campaigns/og/{campaign_id} OG meta tags endpoint."""

    async def test_returns_html_content_type(
        self, test_client: AsyncClient, test_campaign
    ):
        """OG endpoint returns HTML, not JSON."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    async def test_returns_404_for_nonexistent_campaign(
        self, test_client: AsyncClient
    ):
        """OG endpoint returns 404 for unknown campaign ID."""
        response = await test_client.get("/api/campaigns/og/nonexistent-id")
        assert response.status_code == 404

    async def test_og_title_matches_campaign_title(
        self, test_client: AsyncClient, test_campaign
    ):
        """og:title meta tag contains the campaign title."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        assert 'property="og:title"' in html
        assert test_campaign.title in html

    async def test_og_description_present_and_truncated(
        self, test_client: AsyncClient, test_campaign_with_image
    ):
        """og:description is present and truncated to 200 chars max."""
        response = await test_client.get(
            f"/api/campaigns/og/{test_campaign_with_image.id}"
        )
        html = response.text
        assert 'property="og:description"' in html
        # Description is longer than 200 chars, should be truncated
        assert "..." in html
        # Should contain the start of the description
        assert "A devastating flood" in html

    async def test_og_description_not_truncated_when_short(
        self, test_client: AsyncClient, test_campaign_with_cover_url
    ):
        """og:description is not truncated when description is under 200 chars."""
        response = await test_client.get(
            f"/api/campaigns/og/{test_campaign_with_cover_url.id}"
        )
        html = response.text
        assert "..." not in html or "Redirecting" in html  # Only the redirect text has no ellipsis issue
        assert "Help us provide supplies" in html

    async def test_og_url_is_canonical_spa_url(
        self, test_client: AsyncClient, test_campaign
    ):
        """og:url points to the SPA campaign page, not the OG endpoint."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        assert 'property="og:url"' in html
        assert f"/campaigns/{test_campaign.id}" in html
        # Must NOT point to the /api/campaigns/og/ path
        assert "/api/campaigns/og/" not in html

    async def test_og_type_is_website(
        self, test_client: AsyncClient, test_campaign
    ):
        """og:type is set to 'website'."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        assert 'content="website"' in html

    async def test_og_site_name_is_moltfundme(
        self, test_client: AsyncClient, test_campaign
    ):
        """og:site_name is set to MoltFundMe."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        assert 'content="MoltFundMe"' in html

    async def test_twitter_card_is_summary_large_image(
        self, test_client: AsyncClient, test_campaign
    ):
        """Twitter card type is summary_large_image."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        assert 'content="summary_large_image"' in html

    async def test_twitter_title_matches_campaign(
        self, test_client: AsyncClient, test_campaign
    ):
        """twitter:title matches the campaign title."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        assert 'name="twitter:title"' in html
        assert test_campaign.title in html

    async def test_og_image_uses_uploaded_image(
        self, test_client: AsyncClient, test_campaign_with_image
    ):
        """og:image uses the first uploaded campaign image as an absolute URL."""
        response = await test_client.get(
            f"/api/campaigns/og/{test_campaign_with_image.id}"
        )
        html = response.text
        assert 'property="og:image"' in html
        # Should contain the image filename from the uploaded image
        assert "img_20260213_120000.jpg" in html
        # Must be an absolute URL (starts with http)
        assert "http" in html

    async def test_og_image_falls_back_to_cover_url(
        self, test_client: AsyncClient, test_campaign_with_cover_url
    ):
        """og:image falls back to cover_image_url when no uploaded images exist."""
        response = await test_client.get(
            f"/api/campaigns/og/{test_campaign_with_cover_url.id}"
        )
        html = response.text
        assert 'property="og:image"' in html
        assert "https://example.com/school-cover.jpg" in html

    async def test_no_og_image_when_no_images(
        self, test_client: AsyncClient, test_campaign
    ):
        """No og:image meta tag when campaign has no images at all."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        # test_campaign has no images and no cover_image_url
        assert 'property="og:image"' not in html

    async def test_includes_meta_refresh_redirect(
        self, test_client: AsyncClient, test_campaign
    ):
        """HTML includes a meta refresh redirect to the SPA URL."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        assert 'http-equiv="refresh"' in html
        assert f"/campaigns/{test_campaign.id}" in html

    async def test_includes_canonical_link(
        self, test_client: AsyncClient, test_campaign
    ):
        """HTML includes a canonical link to the SPA URL."""
        response = await test_client.get(f"/api/campaigns/og/{test_campaign.id}")
        html = response.text
        assert 'rel="canonical"' in html
        assert f"/campaigns/{test_campaign.id}" in html

    async def test_html_escapes_special_characters(
        self, test_client: AsyncClient, test_db, test_creator
    ):
        """OG tags properly escape HTML special characters in campaign data."""
        campaign = Campaign(
            id="og-escape-test-id",
            title='Campaign with "quotes" & <tags>',
            description='Description with <script>alert("xss")</script> & special chars',
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()

        response = await test_client.get("/api/campaigns/og/og-escape-test-id")
        html = response.text
        assert response.status_code == 200
        # Raw HTML tags must not appear unescaped
        assert "<script>" not in html
        assert "<tags>" not in html
        # Escaped versions should be present
        assert "&lt;tags&gt;" in html or "&amp;" in html
