"""Tests for KYC routes."""
import pytest
import io
from pathlib import Path
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Creator, KYCSubmission


class TestKYCStatus:
    """Tests for GET /api/kyc/status endpoint."""

    async def test_get_kyc_status_unauthenticated(self, test_client: AsyncClient):
        """Should return 401 when not authenticated."""
        response = await test_client.get("/api/kyc/status")
        assert response.status_code == 401

    async def test_get_kyc_status_none(self, test_client: AsyncClient, test_creator_no_kyc, test_creator_no_kyc_token):
        """Should return status=none for creator without KYC."""
        response = await test_client.get(
            "/api/kyc/status",
            headers={"Authorization": f"Bearer {test_creator_no_kyc_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "none"
        assert data["can_create_campaign"] is False
        assert data["attempts_remaining"] == 3
        assert data["rejection_reason"] is None

    async def test_get_kyc_status_approved(self, test_client: AsyncClient, test_creator, test_creator_token):
        """Should return status=approved for KYC-approved creator."""
        response = await test_client.get(
            "/api/kyc/status",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["can_create_campaign"] is True
        assert data["attempts_remaining"] == 2  # 3 - 1 (already used 1)

    async def test_get_kyc_status_rejected(self, test_client: AsyncClient, test_db: AsyncSession):
        """Should return rejection reason for rejected KYC."""
        from app.core.security import create_access_token
        
        # Create a creator with rejected KYC
        creator = Creator(
            id="rejected-creator-id",
            email="rejected@example.com",
            kyc_status="rejected",
            kyc_attempt_count=1,
            kyc_rejection_reason="ID image was blurry",
        )
        test_db.add(creator)
        await test_db.commit()
        
        token = create_access_token(data={"sub": creator.id, "email": creator.email})
        
        response = await test_client.get(
            "/api/kyc/status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["can_create_campaign"] is False
        assert data["attempts_remaining"] == 2
        assert data["rejection_reason"] == "ID image was blurry"


class TestKYCSubmit:
    """Tests for POST /api/kyc/submit endpoint."""

    def _create_test_image(self, content: bytes = b"fake image content") -> io.BytesIO:
        """Create a fake image file for testing."""
        return io.BytesIO(content)

    async def test_submit_kyc_unauthenticated(self, test_client: AsyncClient):
        """Should return 401 when not authenticated."""
        response = await test_client.post(
            "/api/kyc/submit",
            files={
                "id_photo": ("id.jpg", self._create_test_image(), "image/jpeg"),
                "selfie_photo": ("selfie.jpg", self._create_test_image(), "image/jpeg"),
            },
            data={"submitted_date": "Feb 4, 2026"},
        )
        assert response.status_code == 401

    async def test_submit_kyc_success(
        self, test_client: AsyncClient, test_db: AsyncSession, test_creator_no_kyc, test_creator_no_kyc_token
    ):
        """Should successfully submit KYC and auto-approve."""
        response = await test_client.post(
            "/api/kyc/submit",
            files={
                "id_photo": ("id.jpg", self._create_test_image(), "image/jpeg"),
                "selfie_photo": ("selfie.jpg", self._create_test_image(), "image/jpeg"),
            },
            data={"submitted_date": "Feb 4, 2026"},
            headers={"Authorization": f"Bearer {test_creator_no_kyc_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "approved"
        assert data["submitted_date"] == "Feb 4, 2026"
        assert "id" in data
        assert "created_at" in data

        # Verify creator status was updated
        await test_db.refresh(test_creator_no_kyc)
        assert test_creator_no_kyc.kyc_status == "approved"
        assert test_creator_no_kyc.kyc_attempt_count == 1
        assert test_creator_no_kyc.kyc_flagged_for_review is True

    async def test_submit_kyc_png_format(
        self, test_client: AsyncClient, test_db: AsyncSession
    ):
        """Should accept PNG format."""
        from app.core.security import create_access_token
        
        creator = Creator(
            id="png-creator-id",
            email="png@example.com",
            kyc_status="none",
        )
        test_db.add(creator)
        await test_db.commit()
        
        token = create_access_token(data={"sub": creator.id, "email": creator.email})
        
        response = await test_client.post(
            "/api/kyc/submit",
            files={
                "id_photo": ("id.png", self._create_test_image(), "image/png"),
                "selfie_photo": ("selfie.png", self._create_test_image(), "image/png"),
            },
            data={"submitted_date": "Feb 4, 2026"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

    async def test_submit_kyc_invalid_file_type(
        self, test_client: AsyncClient, test_creator_no_kyc, test_creator_no_kyc_token
    ):
        """Should reject non-image file types."""
        response = await test_client.post(
            "/api/kyc/submit",
            files={
                "id_photo": ("id.pdf", self._create_test_image(), "application/pdf"),
                "selfie_photo": ("selfie.jpg", self._create_test_image(), "image/jpeg"),
            },
            data={"submitted_date": "Feb 4, 2026"},
            headers={"Authorization": f"Bearer {test_creator_no_kyc_token}"},
        )
        assert response.status_code == 400
        assert "JPG and PNG" in response.json()["detail"]

    async def test_submit_kyc_max_attempts_reached(
        self, test_client: AsyncClient, test_db: AsyncSession
    ):
        """Should reject submission when max attempts reached."""
        from app.core.security import create_access_token
        
        creator = Creator(
            id="maxed-creator-id",
            email="maxed@example.com",
            kyc_status="rejected",
            kyc_attempt_count=3,  # Max attempts reached
        )
        test_db.add(creator)
        await test_db.commit()
        
        token = create_access_token(data={"sub": creator.id, "email": creator.email})
        
        response = await test_client.post(
            "/api/kyc/submit",
            files={
                "id_photo": ("id.jpg", self._create_test_image(), "image/jpeg"),
                "selfie_photo": ("selfie.jpg", self._create_test_image(), "image/jpeg"),
            },
            data={"submitted_date": "Feb 4, 2026"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "Maximum KYC attempts" in response.json()["detail"]

    async def test_submit_kyc_creates_submission_record(
        self, test_client: AsyncClient, test_db: AsyncSession
    ):
        """Should create KYCSubmission record in database."""
        from app.core.security import create_access_token
        
        creator = Creator(
            id="submission-creator-id",
            email="submission@example.com",
            kyc_status="none",
        )
        test_db.add(creator)
        await test_db.commit()
        
        token = create_access_token(data={"sub": creator.id, "email": creator.email})
        
        response = await test_client.post(
            "/api/kyc/submit",
            files={
                "id_photo": ("id.jpg", self._create_test_image(), "image/jpeg"),
                "selfie_photo": ("selfie.jpg", self._create_test_image(), "image/jpeg"),
            },
            data={"submitted_date": "Feb 4, 2026"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        
        # Verify submission record was created
        result = await test_db.execute(
            select(KYCSubmission).where(KYCSubmission.creator_id == creator.id)
        )
        submission = result.scalar_one()
        assert submission is not None
        assert submission.submitted_date == "Feb 4, 2026"
        assert submission.status == "approved"


class TestKYCSubmissions:
    """Tests for GET /api/kyc/submissions endpoint."""

    async def test_get_submissions_unauthenticated(self, test_client: AsyncClient):
        """Should return 401 when not authenticated."""
        response = await test_client.get("/api/kyc/submissions")
        assert response.status_code == 401

    async def test_get_submissions_empty(
        self, test_client: AsyncClient, test_creator_no_kyc, test_creator_no_kyc_token
    ):
        """Should return empty list when no submissions."""
        response = await test_client.get(
            "/api/kyc/submissions",
            headers={"Authorization": f"Bearer {test_creator_no_kyc_token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_submissions_with_data(
        self, test_client: AsyncClient, test_db: AsyncSession
    ):
        """Should return list of submissions."""
        from app.core.security import create_access_token
        
        creator = Creator(
            id="list-creator-id",
            email="list@example.com",
            kyc_status="approved",
        )
        test_db.add(creator)
        
        submission = KYCSubmission(
            creator_id=creator.id,
            id_photo_path="list-creator-id/id_photo.jpg",
            selfie_photo_path="list-creator-id/selfie.jpg",
            submitted_date="Feb 4, 2026",
            status="approved",
        )
        test_db.add(submission)
        await test_db.commit()
        
        token = create_access_token(data={"sub": creator.id, "email": creator.email})
        
        response = await test_client.get(
            "/api/kyc/submissions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "approved"
        assert data[0]["submitted_date"] == "Feb 4, 2026"


class TestKYCCampaignGate:
    """Tests for KYC gate on campaign creation."""

    async def test_create_campaign_without_kyc_fails(
        self, test_client: AsyncClient, test_creator_no_kyc, test_creator_no_kyc_token
    ):
        """Should reject campaign creation without KYC approval."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test Campaign",
                "description": "Test description",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator_no_kyc.email,
            },
            headers={"Authorization": f"Bearer {test_creator_no_kyc_token}"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["code"] == "KYC_REQUIRED"
        assert data["detail"]["kyc_status"] == "none"

    async def test_create_campaign_with_kyc_succeeds(
        self, test_client: AsyncClient, test_creator, test_creator_token
    ):
        """Should allow campaign creation with KYC approval."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test Campaign",
                "description": "Test description",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        assert response.status_code == 201

    async def test_create_campaign_pending_kyc_fails(
        self, test_client: AsyncClient, test_db: AsyncSession
    ):
        """Should reject campaign creation with pending KYC."""
        from app.core.security import create_access_token
        
        creator = Creator(
            id="pending-creator-id",
            email="pending@example.com",
            kyc_status="pending",
        )
        test_db.add(creator)
        await test_db.commit()
        
        token = create_access_token(data={"sub": creator.id, "email": creator.email})
        
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test Campaign",
                "description": "Test description",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": creator.email,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["code"] == "KYC_REQUIRED"
        assert data["detail"]["kyc_status"] == "pending"
