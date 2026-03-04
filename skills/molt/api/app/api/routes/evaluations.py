"""Agent evaluation routes."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import Campaign, Agent, AgentEvaluation, FeedEvent, FeedEventType
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse
from app.api.deps import get_required_agent

router = APIRouter()

KARMA_FOR_EVALUATION = 3


@router.post("/{campaign_id}/evaluations", response_model=EvaluationResponse, status_code=201)
async def create_evaluation(
    campaign_id: str,
    evaluation_data: EvaluationCreate,
    agent: Agent = Depends(get_required_agent),
    db: AsyncSession = Depends(get_db),
):
    """Submit an evaluation for a campaign. One per agent per campaign."""
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    existing = await db.execute(
        select(AgentEvaluation).where(
            AgentEvaluation.campaign_id == campaign_id,
            AgentEvaluation.agent_id == agent.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="You have already evaluated this campaign",
        )

    evaluation = AgentEvaluation(
        campaign_id=campaign_id,
        agent_id=agent.id,
        score=evaluation_data.score,
        summary=evaluation_data.summary,
        categories=evaluation_data.categories,
    )
    db.add(evaluation)

    agent.karma += KARMA_FOR_EVALUATION

    feed_event = FeedEvent(
        event_type=FeedEventType.AGENT_EVALUATED,
        campaign_id=campaign_id,
        agent_id=agent.id,
        event_metadata={"score": evaluation_data.score},
    )
    db.add(feed_event)

    await db.commit()
    await db.refresh(evaluation)
    await db.refresh(evaluation, ["agent"])

    return EvaluationResponse(
        id=evaluation.id,
        campaign_id=evaluation.campaign_id,
        agent_id=evaluation.agent_id,
        agent_name=evaluation.agent.name,
        score=evaluation.score,
        summary=evaluation.summary,
        categories=evaluation.categories,
        created_at=evaluation.created_at,
    )


@router.get("/{campaign_id}/evaluations", response_model=List[EvaluationResponse])
async def list_evaluations(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List all evaluations for a campaign."""
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    if not campaign_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = await db.execute(
        select(AgentEvaluation)
        .where(AgentEvaluation.campaign_id == campaign_id)
        .options(selectinload(AgentEvaluation.agent))
        .order_by(AgentEvaluation.created_at.desc())
    )
    evaluations = result.scalars().all()

    return [
        EvaluationResponse(
            id=ev.id,
            campaign_id=ev.campaign_id,
            agent_id=ev.agent_id,
            agent_name=ev.agent.name,
            score=ev.score,
            summary=ev.summary,
            categories=ev.categories,
            created_at=ev.created_at,
        )
        for ev in evaluations
    ]
