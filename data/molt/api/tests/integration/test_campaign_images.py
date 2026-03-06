"""Integration tests for campaign image upload, delete, and serve."""
import io
import pytest
from httpx import AsyncClient

from app.db.models import Campaign, CampaignImage, CampaignCategory


def _create_test_image(content: bytes = b"fake image content") -> io.BytesIO:
    return io.BytesIO(content)


@pytest.mark.asyncio
class TestCampaignImageUpload:
    """Tests for POST /api/campaigns/{campaign_id}/images."""

    async def test_upload_image_returns_201(
        self, test_client: AsyncClient, test_campaign, test_creator_token
    ):
        """Should upload image and return 201 with image data."""
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/images",
            files={"image": ("image.jpg", _create_test_image(), "image/jpeg")},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "image_url" in data
        assert "display_order" in data

    async def test_upload_rejects_non_image(
        self, test_client: AsyncClient, test_campaign, test_creator_token
    ):
        """Should reject non-image files."""
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/images",
            files={"image": ("file.txt", io.BytesIO(b"not image"), "text/plain")},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 400

    async def test_upload_rejects_over_5mb(
        self, test_client: AsyncClient, test_campaign, test_creator_token
    ):
        """Should reject files over 5MB."""
        large = b"x" * (5 * 1024 * 1024 + 1)
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/images",
            files={"image": ("image.jpg", _create_test_image(large), "image/jpeg")},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 400

    async def test_upload_rejects_when_5_images_exist(
        self, test_client: AsyncClient, test_campaign, test_creator_token, test_db
    ):
        """Should reject when campaign already has 5 images."""
        for i in range(5):
            ci = CampaignImage(
                campaign_id=test_campaign.id,
                image_path=f"campaigns/{test_campaign.id}/img_{i}.jpg",
                display_order=i,
            )
            test_db.add(ci)
        await test_db.commit()

        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/images",
            files={"image": ("image.jpg", _create_test_image(), "image/jpeg")},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 400

    async def test_upload_requires_creator_auth(
        self, test_client: AsyncClient, test_campaign
    ):
        """Should return 401/403 without creator auth."""
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/images",
            files={"image": ("image.jpg", _create_test_image(), "image/jpeg")},
        )

        assert response.status_code in (401, 403)

    async def test_only_owner_can_upload(
        self, test_client: AsyncClient, test_db, test_campaign, test_creator_token
    ):
        """Should reject when non-owner tries to upload."""
        from app.db.models import Creator, Campaign
        from app.core.security import create_access_token

        other_creator = Creator(email="other@example.com", kyc_status="approved")
        test_db.add(other_creator)
        await test_db.flush()

        other_campaign = Campaign(
            title="Other Campaign",
            description="Other",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            contact_email=other_creator.email,
            creator_id=other_creator.id,
        )
        test_db.add(other_campaign)
        await test_db.commit()
        await test_db.refresh(other_campaign)

        response = await test_client.post(
            f"/api/campaigns/{other_campaign.id}/images",
            files={"image": ("image.jpg", _create_test_image(), "image/jpeg")},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestCampaignImageDelete:
    """Tests for DELETE /api/campaigns/{campaign_id}/images/{image_id}."""

    async def test_delete_image_returns_204(
        self, test_client: AsyncClient, test_campaign, test_creator_token, test_db
    ):
        """Should delete image and return 204."""
        ci = CampaignImage(
            campaign_id=test_campaign.id,
            image_path=f"campaigns/{test_campaign.id}/img.jpg",
            display_order=0,
        )
        test_db.add(ci)
        await test_db.commit()
        await test_db.refresh(ci)

        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/images/{ci.id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 204

    async def test_only_owner_can_delete(
        self, test_client: AsyncClient, test_db, test_creator_token
    ):
        """Should reject when non-owner tries to delete."""
        from app.db.models import Creator, Campaign, CampaignImage

        other_creator = Creator(email="other2@example.com", kyc_status="approved")
        test_db.add(other_creator)
        await test_db.flush()

        other_campaign = Campaign(
            title="Other Campaign 2",
            description="Other",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            contact_email=other_creator.email,
            creator_id=other_creator.id,
        )
        test_db.add(other_campaign)
        await test_db.flush()

        ci = CampaignImage(
            campaign_id=other_campaign.id,
            image_path="campaigns/other/img.jpg",
            display_order=0,
        )
        test_db.add(ci)
        await test_db.commit()
        await test_db.refresh(ci)

        response = await test_client.delete(
            f"/api/campaigns/{other_campaign.id}/images/{ci.id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestCampaignImagesInResponse:
    """Tests that images are included in campaign GET."""

    async def test_images_included_in_campaign_detail(
        self, test_client: AsyncClient, test_campaign, test_creator_token, test_db
    ):
        """Should include images in campaign GET response."""
        ci = CampaignImage(
            campaign_id=test_campaign.id,
            image_path=f"campaigns/{test_campaign.id}/img.jpg",
            display_order=0,
        )
        test_db.add(ci)
        await test_db.commit()

        response = await test_client.get(f"/api/campaigns/{test_campaign.id}")

        assert response.status_code == 200
        data = response.json()
        assert "images" in data
        assert len(data["images"]) >= 1


@pytest.mark.asyncio
class TestCampaignImageServe:
    """Tests for GET /api/uploads/campaigns/{campaign_id}/{filename}."""

    async def test_serve_returns_file(
        self, test_client: AsyncClient, test_campaign, test_creator_token
    ):
        """Should return the uploaded campaign image."""
        from pathlib import Path

        campaign_dir = Path("data/uploads/campaigns") / test_campaign.id
        campaign_dir.mkdir(parents=True, exist_ok=True)
        (campaign_dir / "test_img.jpg").write_bytes(b"image bytes")

        response = await test_client.get(
            f"/api/uploads/campaigns/{test_campaign.id}/test_img.jpg"
        )

        assert response.status_code == 200
        assert response.content == b"image bytes"
