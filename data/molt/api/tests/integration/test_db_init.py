"""Integration tests for database initialization."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, inspect

from app.db.database import Base, init_db
from app.db.models import Campaign, Agent, Creator, Advocacy, WarRoomPost, Upvote, FeedEvent, MagicLink, Donation


@pytest.mark.asyncio
class TestDatabaseInit:
    """Tests for database initialization."""
    
    async def test_init_db_creates_tables(self, test_db: AsyncSession):
        """Should create all tables."""
        # Verify tables exist by trying to query them
        result = await test_db.execute(select(Campaign))
        campaigns = result.scalars().all()
        assert campaigns == []  # Empty but table exists
        
        result = await test_db.execute(select(Agent))
        agents = result.scalars().all()
        assert agents == []
        
        result = await test_db.execute(select(Creator))
        creators = result.scalars().all()
        assert creators == []
        
        result = await test_db.execute(select(Advocacy))
        advocacies = result.scalars().all()
        assert advocacies == []
        
        result = await test_db.execute(select(WarRoomPost))
        posts = result.scalars().all()
        assert posts == []
        
        result = await test_db.execute(select(Upvote))
        upvotes = result.scalars().all()
        assert upvotes == []
        
        result = await test_db.execute(select(FeedEvent))
        events = result.scalars().all()
        assert events == []
        
        result = await test_db.execute(select(MagicLink))
        magic_links = result.scalars().all()
        assert magic_links == []
        
        result = await test_db.execute(select(Donation))
        donations = result.scalars().all()
        assert donations == []
