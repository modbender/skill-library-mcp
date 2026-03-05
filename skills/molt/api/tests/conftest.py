"""Pytest configuration and shared fixtures."""
import os
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

# Set TESTING environment variable before importing app
os.environ["TESTING"] = "true"

from app.db.database import Base, get_db
from app.db.models import Creator, Agent, Campaign, CampaignCategory, CampaignStatus
from app.main import app
from app.core.security import create_access_token, create_api_key, hash_api_key

# Import all models to ensure they're registered with Base
from app.db import models  # noqa: F401


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(autouse=True)
def clear_rate_limits():
    """Clear rate limit store before each test for isolation."""
    from app.core.rate_limit import clear_rate_limit_store
    clear_rate_limit_store()
    yield


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Cleanup: drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for API calls."""
    from httpx import ASGITransport
    
    # Override get_db dependency
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Use true async client with ASGI transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
async def test_creator(test_db: AsyncSession) -> Creator:
    """Create a test creator with KYC approved (for campaign creation tests)."""
    creator = Creator(
        id="test-creator-id",
        email="test@example.com",
        kyc_status="approved",  # Pre-approved for tests that need to create campaigns
        kyc_attempt_count=1,
    )
    test_db.add(creator)
    await test_db.commit()
    await test_db.refresh(creator)
    return creator


@pytest.fixture
async def test_creator_no_kyc(test_db: AsyncSession) -> Creator:
    """Create a test creator without KYC (for KYC flow tests)."""
    creator = Creator(
        id="test-creator-no-kyc-id",
        email="nokyc@example.com",
        kyc_status="none",
        kyc_attempt_count=0,
    )
    test_db.add(creator)
    await test_db.commit()
    await test_db.refresh(creator)
    return creator


@pytest.fixture
def test_creator_no_kyc_token(test_creator_no_kyc: Creator) -> str:
    """Create a JWT token for test creator without KYC."""
    return create_access_token(data={"sub": test_creator_no_kyc.id, "email": test_creator_no_kyc.email})


@pytest.fixture
def test_creator_token(test_creator: Creator) -> str:
    """Create a JWT token for test creator."""
    return create_access_token(data={"sub": test_creator.id, "email": test_creator.email})


@pytest.fixture
async def test_agent(test_db: AsyncSession) -> tuple[Agent, str]:
    """Create a test agent and return (agent, api_key)."""
    api_key = create_api_key()
    api_key_hash = hash_api_key(api_key)
    
    agent = Agent(
        id="test-agent-id",
        name="test-agent",
        description="Test agent",
        api_key_hash=api_key_hash,
        karma=10,
    )
    test_db.add(agent)
    await test_db.commit()
    await test_db.refresh(agent)
    return agent, api_key


@pytest.fixture
async def test_campaign(test_db: AsyncSession, test_creator: Creator) -> Campaign:
    """Create a test campaign."""
    campaign = Campaign(
        id="test-campaign-id",
        title="Test Campaign",
        description="Test description",
        category=CampaignCategory.MEDICAL,
        goal_amount_usd=100000,  # $1000 in cents
        eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        contact_email=test_creator.email,
        creator_id=test_creator.id,
        status=CampaignStatus.ACTIVE,
    )
    test_db.add(campaign)
    await test_db.commit()
    await test_db.refresh(campaign)
    return campaign


# Pytest asyncio configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
