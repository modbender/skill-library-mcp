import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Creator, KYCSubmission, utc_now
from app.schemas.kyc import KYCStatusResponse, KYCSubmissionResponse
from app.api.deps import get_required_creator

router = APIRouter()

# Base upload directory
UPLOAD_BASE_DIR = Path("data/uploads/kyc")


def ensure_upload_directory(creator_id: str) -> Path:
    """Ensure upload directory exists for a creator."""
    creator_dir = UPLOAD_BASE_DIR / creator_id
    creator_dir.mkdir(parents=True, exist_ok=True)
    return creator_dir


async def save_upload_file(file: UploadFile, save_path: Path) -> str:
    """Save uploaded file and return relative path."""
    # Ensure parent directory exists
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read file content
    content = await file.read()
    
    # Write to file
    with open(save_path, "wb") as f:
        f.write(content)
    
    # Return relative path from data/uploads/kyc/ (e.g., "creator_id/filename.jpg")
    return str(save_path.relative_to(UPLOAD_BASE_DIR))


@router.get("/status", response_model=KYCStatusResponse)
async def get_kyc_status(
    creator: Creator = Depends(get_required_creator),
):
    """Get current creator's KYC status."""
    attempts_remaining = max(0, 3 - creator.kyc_attempt_count)
    
    return KYCStatusResponse(
        status=creator.kyc_status,
        can_create_campaign=creator.kyc_status == "approved",
        attempts_remaining=attempts_remaining,
        rejection_reason=creator.kyc_rejection_reason,
    )


@router.post("/submit", response_model=KYCSubmissionResponse, status_code=201)
async def submit_kyc(
    id_photo: UploadFile = File(...),
    selfie_photo: UploadFile = File(...),
    submitted_date: str = Form(...),
    creator: Creator = Depends(get_required_creator),
    db: AsyncSession = Depends(get_db),
):
    """Submit KYC documents for verification."""
    # Check attempt limit (max 3)
    if creator.kyc_attempt_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum KYC attempts reached. Please contact support."
        )
    
    # Validate file types (jpg, png only)
    allowed_extensions = {".jpg", ".jpeg", ".png"}
    id_ext = Path(id_photo.filename).suffix.lower()
    selfie_ext = Path(selfie_photo.filename).suffix.lower()
    
    if id_ext not in allowed_extensions or selfie_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG and PNG images are allowed"
        )
    
    # Validate file sizes (max 10MB each)
    # Read content to check size (UploadFile.seek doesn't support whence parameter)
    id_content = await id_photo.read()
    selfie_content = await selfie_photo.read()
    
    max_size = 10 * 1024 * 1024  # 10MB
    if len(id_content) > max_size or len(selfie_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB"
        )
    
    # Reset file position for later reading
    await id_photo.seek(0)
    await selfie_photo.seek(0)
    
    try:
        # Ensure upload directory exists
        creator_dir = ensure_upload_directory(creator.id)
        
        # Generate filenames with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        id_filename = f"id_photo_{timestamp}{id_ext}"
        selfie_filename = f"selfie_{timestamp}{selfie_ext}"
        
        id_path = creator_dir / id_filename
        selfie_path = creator_dir / selfie_filename
        
        # Save files
        id_relative_path = await save_upload_file(id_photo, id_path)
        selfie_relative_path = await save_upload_file(selfie_photo, selfie_path)
        
        # Create KYCSubmission record
        submission = KYCSubmission(
            creator_id=creator.id,
            id_photo_path=id_relative_path,
            selfie_photo_path=selfie_relative_path,
            submitted_date=submitted_date,
            status="approved",  # Auto-approve initially
        )
        
        db.add(submission)
        
        # Update creator KYC status
        creator.kyc_status = "approved"  # Auto-approve
        creator.kyc_flagged_for_review = True  # Flag for manual review
        creator.kyc_submitted_at = utc_now()
        creator.kyc_attempt_count += 1
        
        await db.commit()
        await db.refresh(submission)
        
        return KYCSubmissionResponse(
            id=submission.id,
            status=submission.status,
            submitted_date=submission.submitted_date,
            created_at=submission.created_at,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit KYC: {str(e)}"
        )


@router.get("/submissions", response_model=List[KYCSubmissionResponse])
async def get_kyc_submissions(
    creator: Creator = Depends(get_required_creator),
    db: AsyncSession = Depends(get_db),
):
    """List creator's KYC submissions."""
    result = await db.execute(
        select(KYCSubmission)
        .where(KYCSubmission.creator_id == creator.id)
        .order_by(KYCSubmission.created_at.desc())
    )
    submissions = result.scalars().all()
    
    return [
        KYCSubmissionResponse(
            id=sub.id,
            status=sub.status,
            submitted_date=sub.submitted_date,
            created_at=sub.created_at,
        )
        for sub in submissions
    ]
