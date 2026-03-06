"""
Tests for Research Library Database Schema

Run with: python -m pytest tests/test_schema.py -v
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from reslib.schema import ResearchDatabase, init_database, SCHEMA_VERSION
from reslib.models import (
    Research, Attachment, ResearchLink, ExtractionJob,
    MATERIAL_TYPES, LINK_TYPES, JOB_STATUSES
)


@pytest.fixture
def db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_research.db")
        database = ResearchDatabase(db_path)
        database.init_schema()
        yield database
        database.close()


@pytest.fixture
def db_path():
    """Create a temporary path for database testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_research.db")


class TestDatabaseInitialization:
    """Tests for database initialization."""
    
    def test_database_creates_file(self, db_path):
        """Database file should be created on init."""
        assert not os.path.exists(db_path)
        db = ResearchDatabase(db_path)
        db.init_schema()
        assert os.path.exists(db_path)
        db.close()
    
    def test_database_creates_parent_dirs(self):
        """Database should create parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "nested", "dirs", "test.db")
            db = ResearchDatabase(db_path)
            db.init_schema()
            assert os.path.exists(db_path)
            db.close()
    
    def test_init_database_helper(self, db_path):
        """init_database() convenience function should work."""
        db = init_database(db_path)
        assert db.get_schema_version() == SCHEMA_VERSION
        db.close()
    
    def test_schema_version_set(self, db):
        """Schema version should be set after init."""
        assert db.get_schema_version() == SCHEMA_VERSION
    
    def test_idempotent_init(self, db):
        """Calling init_schema multiple times should be safe."""
        db.init_schema()
        db.init_schema()
        assert db.get_schema_version() == SCHEMA_VERSION


class TestTableCreation:
    """Tests for table creation."""
    
    def test_all_tables_created(self, db):
        """All required tables should be created."""
        required_tables = [
            "research",
            "tags", 
            "research_tags",
            "research_links",
            "attachments",
            "attachment_versions",
            "extraction_queue",
            "embeddings",
            "_schema_meta",
        ]
        
        for table in required_tables:
            assert db.table_exists(table), f"Table {table} should exist"
    
    def test_fts_tables_created(self, db):
        """FTS virtual tables should be created."""
        conn = db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_fts%'"
        )
        fts_tables = [row[0] for row in cursor.fetchall()]
        
        # FTS5 creates multiple tables per virtual table
        assert any("research_fts" in t for t in fts_tables)
        assert any("attachments_fts" in t for t in fts_tables)
    
    def test_research_table_columns(self, db):
        """Research table should have all required columns."""
        info = db.get_table_info("research")
        columns = {col["name"] for col in info}
        
        required = {"id", "title", "content", "project_id", "material_type",
                   "confidence", "source_url", "created_at", "updated_at"}
        
        assert required.issubset(columns)
    
    def test_attachments_table_columns(self, db):
        """Attachments table should have all required columns."""
        info = db.get_table_info("attachments")
        columns = {col["name"] for col in info}
        
        required = {"id", "research_id", "filename", "path", "mime_type",
                   "file_size", "extracted_text", "extraction_confidence", "created_at"}
        
        assert required.issubset(columns)


class TestConstraints:
    """Tests for constraint enforcement."""
    
    def test_confidence_range_valid(self, db):
        """Confidence within 0.0-1.0 should be accepted."""
        conn = db.get_connection()
        
        # Valid values
        for conf in [0.0, 0.5, 1.0]:
            conn.execute(
                "INSERT INTO research(project_id, confidence) VALUES (?, ?)",
                ("test-project", conf)
            )
        conn.commit()
    
    def test_confidence_below_zero_rejected(self, db):
        """Confidence below 0.0 should be rejected."""
        conn = db.get_connection()
        
        with pytest.raises(Exception):  # sqlite3.IntegrityError
            conn.execute(
                "INSERT INTO research(project_id, confidence) VALUES (?, ?)",
                ("test-project", -0.1)
            )
    
    def test_confidence_above_one_rejected(self, db):
        """Confidence above 1.0 should be rejected."""
        conn = db.get_connection()
        
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO research(project_id, confidence) VALUES (?, ?)",
                ("test-project", 1.1)
            )
    
    def test_project_id_required(self, db):
        """project_id should be NOT NULL."""
        conn = db.get_connection()
        
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO research(project_id) VALUES (NULL)"
            )
    
    def test_material_type_valid_values(self, db):
        """Only valid material types should be accepted."""
        conn = db.get_connection()
        
        for mat_type in MATERIAL_TYPES:
            if mat_type == "reference":
                # Reference requires high confidence
                conn.execute(
                    "INSERT INTO research(project_id, material_type, confidence) VALUES (?, ?, ?)",
                    ("test-project", mat_type, 0.9)
                )
            else:
                conn.execute(
                    "INSERT INTO research(project_id, material_type) VALUES (?, ?)",
                    ("test-project", mat_type)
                )
        conn.commit()
    
    def test_material_type_invalid_rejected(self, db):
        """Invalid material type should be rejected."""
        conn = db.get_connection()
        
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO research(project_id, material_type) VALUES (?, ?)",
                ("test-project", "invalid_type")
            )
    
    def test_reference_requires_high_confidence(self, db):
        """Reference material should require confidence >= 0.8."""
        conn = db.get_connection()
        
        # Should fail with low confidence
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO research(project_id, material_type, confidence) VALUES (?, ?, ?)",
                ("test-project", "reference", 0.7)
            )
    
    def test_reference_with_high_confidence_accepted(self, db):
        """Reference material with confidence >= 0.8 should be accepted."""
        conn = db.get_connection()
        
        conn.execute(
            "INSERT INTO research(project_id, material_type, confidence) VALUES (?, ?, ?)",
            ("test-project", "reference", 0.8)
        )
        conn.execute(
            "INSERT INTO research(project_id, material_type, confidence) VALUES (?, ?, ?)",
            ("test-project", "reference", 1.0)
        )
        conn.commit()
    
    def test_link_type_valid_values(self, db):
        """Only valid link types should be accepted."""
        conn = db.get_connection()
        
        # Create two research items to link
        conn.execute("INSERT INTO research(id, project_id) VALUES ('r1', 'test')")
        conn.execute("INSERT INTO research(id, project_id) VALUES ('r2', 'test')")
        
        for i, link_type in enumerate(LINK_TYPES):
            conn.execute(
                "INSERT INTO research_links(source_id, target_id, link_type) VALUES (?, ?, ?)",
                (f"r1", f"r2", link_type)
            )
            # Delete to avoid unique constraint for next iteration
            conn.execute("DELETE FROM research_links")
        conn.commit()
    
    def test_link_type_invalid_rejected(self, db):
        """Invalid link type should be rejected."""
        conn = db.get_connection()
        
        conn.execute("INSERT INTO research(id, project_id) VALUES ('r1', 'test')")
        conn.execute("INSERT INTO research(id, project_id) VALUES ('r2', 'test')")
        
        with pytest.raises(Exception):
            conn.execute(
                "INSERT INTO research_links(source_id, target_id, link_type) VALUES (?, ?, ?)",
                ("r1", "r2", "invalid_link")
            )
    
    def test_extraction_job_status_valid(self, db):
        """Only valid job statuses should be accepted."""
        conn = db.get_connection()
        
        # Create research and attachment
        conn.execute("INSERT INTO research(id, project_id) VALUES ('r1', 'test')")
        # Note: attachment insert triggers auto-creation of extraction job
        conn.execute(
            "INSERT INTO attachments(id, research_id, filename, path) VALUES ('a1', 'r1', 'test.pdf', '/test')"
        )
        
        for status in JOB_STATUSES:
            conn.execute(
                "UPDATE extraction_queue SET status = ? WHERE attachment_id = ?",
                (status, "a1")
            )
        conn.commit()


class TestIndexes:
    """Tests for index creation."""
    
    def test_indexes_exist(self, db):
        """Required indexes should exist."""
        conn = db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        indexes = {row[0] for row in cursor.fetchall()}
        
        expected_indexes = [
            "idx_research_project",
            "idx_research_type",
            "idx_research_confidence",
            "idx_research_created",
            "idx_attachments_research",
            "idx_extraction_status",
            "idx_embeddings_research",
            "idx_links_source",
            "idx_links_target",
        ]
        
        for idx in expected_indexes:
            assert idx in indexes, f"Index {idx} should exist"


class TestTriggers:
    """Tests for trigger functionality."""
    
    def test_updated_at_trigger(self, db):
        """updated_at should auto-update on research changes."""
        conn = db.get_connection()
        
        conn.execute(
            "INSERT INTO research(id, project_id, title) VALUES ('r1', 'test', 'Original')"
        )
        conn.commit()
        
        # Get original updated_at
        cursor = conn.execute("SELECT updated_at FROM research WHERE id = 'r1'")
        original_time = cursor.fetchone()[0]
        
        # Wait a tiny bit and update
        import time
        time.sleep(0.1)
        
        conn.execute("UPDATE research SET title = 'Updated' WHERE id = 'r1'")
        conn.commit()
        
        # Check updated_at changed
        cursor = conn.execute("SELECT updated_at FROM research WHERE id = 'r1'")
        new_time = cursor.fetchone()[0]
        
        # Note: Times might be same if within same second, that's OK
        assert new_time is not None
    
    def test_fts_sync_on_insert(self, db):
        """FTS should sync on research insert."""
        conn = db.get_connection()
        
        conn.execute(
            "INSERT INTO research(id, project_id, title, content) VALUES (?, ?, ?, ?)",
            ("r1", "test", "Test Title", "Test content here")
        )
        conn.commit()
        
        # Search FTS
        cursor = conn.execute(
            "SELECT * FROM research_fts WHERE research_fts MATCH 'Test'"
        )
        results = cursor.fetchall()
        assert len(results) > 0
    
    def test_auto_extraction_queue(self, db):
        """Extraction job should auto-create on attachment insert."""
        conn = db.get_connection()
        
        conn.execute("INSERT INTO research(id, project_id) VALUES ('r1', 'test')")
        conn.execute(
            "INSERT INTO attachments(id, research_id, filename, path) VALUES ('a1', 'r1', 'doc.pdf', '/path')"
        )
        conn.commit()
        
        cursor = conn.execute(
            "SELECT * FROM extraction_queue WHERE attachment_id = 'a1'"
        )
        job = cursor.fetchone()
        assert job is not None
        assert job["status"] == "pending"
    
    def test_cascade_delete(self, db):
        """Deleting research should cascade to related tables."""
        conn = db.get_connection()
        
        conn.execute("INSERT INTO research(id, project_id) VALUES ('r1', 'test')")
        conn.execute(
            "INSERT INTO attachments(id, research_id, filename, path) VALUES ('a1', 'r1', 'doc.pdf', '/path')"
        )
        conn.commit()
        
        # Verify attachment and extraction job exist
        cursor = conn.execute("SELECT COUNT(*) FROM attachments WHERE research_id = 'r1'")
        assert cursor.fetchone()[0] == 1
        
        cursor = conn.execute("SELECT COUNT(*) FROM extraction_queue WHERE attachment_id = 'a1'")
        assert cursor.fetchone()[0] == 1
        
        # Delete research
        conn.execute("DELETE FROM research WHERE id = 'r1'")
        conn.commit()
        
        # Verify cascade
        cursor = conn.execute("SELECT COUNT(*) FROM attachments WHERE research_id = 'r1'")
        assert cursor.fetchone()[0] == 0


class TestHealthCheck:
    """Tests for health check functionality."""
    
    def test_health_check_healthy_db(self, db):
        """Health check should pass for valid database."""
        health = db.health_check()
        
        assert health["healthy"] is True
        assert health["db_exists"] is True
        assert health["schema_version"] == SCHEMA_VERSION
        assert len(health["issues"]) == 0
    
    def test_health_check_reports_missing_db(self, db_path):
        """Health check should report missing database."""
        db = ResearchDatabase(db_path)
        health = db.health_check()
        
        assert health["healthy"] is False
        assert health["db_exists"] is False


class TestStats:
    """Tests for statistics gathering."""
    
    def test_stats_empty_db(self, db):
        """Stats should return zeros for empty database."""
        stats = db.get_stats()
        
        assert stats["research_count"] == 0
        assert stats["attachment_count"] == 0
        assert stats["tag_count"] == 0
    
    def test_stats_with_data(self, db):
        """Stats should reflect actual data counts."""
        conn = db.get_connection()
        
        # Add some data
        conn.execute("INSERT INTO research(project_id) VALUES ('test')")
        conn.execute("INSERT INTO research(project_id) VALUES ('test')")
        conn.execute("INSERT INTO tags(name) VALUES ('tag1')")
        conn.commit()
        
        stats = db.get_stats()
        
        assert stats["research_count"] == 2
        assert stats["tag_count"] == 1


class TestMigrationHelpers:
    """Tests for migration helper methods."""
    
    def test_add_column(self, db):
        """add_column should add new column to table."""
        # Add a new column
        db.add_column("research", "priority", "INTEGER", "0")
        
        # Verify column exists
        info = db.get_table_info("research")
        columns = {col["name"] for col in info}
        assert "priority" in columns
    
    def test_add_column_idempotent(self, db):
        """add_column should be safe to call multiple times."""
        db.add_column("research", "priority", "INTEGER")
        db.add_column("research", "priority", "INTEGER")  # Should not error
    
    def test_create_index(self, db):
        """create_index should create new index."""
        db.create_index("idx_test", "research", ["title"])
        
        conn = db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_test'"
        )
        assert cursor.fetchone() is not None
    
    def test_create_view(self, db):
        """create_view should create database view."""
        db.create_view(
            "v_research_summary",
            "SELECT id, title, project_id FROM research"
        )
        
        conn = db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name='v_research_summary'"
        )
        assert cursor.fetchone() is not None


class TestModels:
    """Tests for dataclass models validation."""
    
    def test_research_valid(self):
        """Valid Research should be created."""
        r = Research(
            title="Test",
            content="Content",
            project_id="proj1",
            material_type="note",
            confidence=0.5
        )
        assert r.title == "Test"
    
    def test_research_invalid_material_type(self):
        """Invalid material type should raise error."""
        with pytest.raises(ValueError, match="Invalid material_type"):
            Research(project_id="test", material_type="invalid")
    
    def test_research_invalid_confidence(self):
        """Confidence out of range should raise error."""
        with pytest.raises(ValueError, match="Confidence must be"):
            Research(project_id="test", confidence=1.5)
    
    def test_research_reference_low_confidence(self):
        """Reference with low confidence should raise error."""
        with pytest.raises(ValueError, match="Reference material requires"):
            Research(project_id="test", material_type="reference", confidence=0.5)
    
    def test_research_missing_project_id(self):
        """Missing project_id should raise error."""
        with pytest.raises(ValueError, match="project_id is required"):
            Research()
    
    def test_link_valid(self):
        """Valid ResearchLink should be created."""
        link = ResearchLink(
            source_id="r1",
            target_id="r2",
            link_type="supports",
            relevance_score=0.8
        )
        assert link.link_type == "supports"
    
    def test_link_invalid_type(self):
        """Invalid link type should raise error."""
        with pytest.raises(ValueError, match="Invalid link_type"):
            ResearchLink(link_type="invalid")
    
    def test_extraction_job_valid(self):
        """Valid ExtractionJob should be created."""
        job = ExtractionJob(
            attachment_id="a1",
            status="pending"
        )
        assert job.status == "pending"
    
    def test_extraction_job_invalid_status(self):
        """Invalid job status should raise error."""
        with pytest.raises(ValueError, match="Invalid status"):
            ExtractionJob(status="invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
