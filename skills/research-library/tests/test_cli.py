#!/usr/bin/env python3
"""
Tests for Research Library CLI.

Run with: pytest tests/test_cli.py -v
"""

import json
import os
import tempfile
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from reslib.cli import cli, init_database


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    tmp = tempfile.mkdtemp(prefix="reslib_test_")
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def runner():
    """Create a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample text file for testing."""
    sample = temp_dir / "sample.txt"
    sample.write_text("This is sample research content about machine learning and neural networks.")
    return sample


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file for testing."""
    sample = temp_dir / "sample.py"
    sample.write_text('''#!/usr/bin/env python3
"""Sample Python module for testing."""

def hello_world():
    """Print hello world."""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
''')
    return sample


@pytest.fixture
def cli_env(temp_dir):
    """Create CLI environment with temp data directory."""
    return ["--data-dir", str(temp_dir)]


# ============================================================================
# Database Initialization Tests
# ============================================================================

class TestDatabaseInit:
    """Test database initialization."""
    
    def test_init_creates_database(self, temp_dir):
        """Test that init_database creates the database file."""
        db_path = temp_dir / "test.db"
        conn = init_database(db_path)
        
        assert db_path.exists()
        
        # Verify tables exist
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in cursor.fetchall()}
        
        assert "documents" in tables
        assert "attachments" in tables
        assert "links" in tables
        assert "extraction_queue" in tables
        assert "projects" in tables
        
        conn.close()
    
    def test_init_creates_parent_dirs(self, temp_dir):
        """Test that init_database creates parent directories."""
        db_path = temp_dir / "subdir" / "nested" / "test.db"
        conn = init_database(db_path)
        
        assert db_path.exists()
        conn.close()


# ============================================================================
# Add Command Tests
# ============================================================================

class TestAddCommand:
    """Tests for the 'add' command."""
    
    def test_add_text_file(self, runner, cli_env, sample_file):
        """Test adding a text file."""
        result = runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test-project",
            "--material-type", "research"
        ])
        
        assert result.exit_code == 0
        assert "Saved as research #" in result.output
    
    def test_add_with_confidence(self, runner, cli_env, sample_file):
        """Test adding with custom confidence."""
        result = runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test-project",
            "--material-type", "reference",
            "--confidence", "0.9"
        ])
        
        assert result.exit_code == 0
        assert "0.90" in result.output or "0.9" in result.output
    
    def test_add_with_title(self, runner, cli_env, sample_file):
        """Test adding with custom title."""
        result = runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test-project",
            "--material-type", "research",
            "--title", "Custom Title"
        ])
        
        assert result.exit_code == 0
        assert "Custom Title" in result.output
    
    def test_add_with_tags(self, runner, cli_env, sample_file):
        """Test adding with tags."""
        result = runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test-project",
            "--material-type", "research",
            "--tags", "ml,python,test"
        ])
        
        assert result.exit_code == 0
    
    def test_add_python_file(self, runner, cli_env, sample_python_file):
        """Test adding a Python file."""
        result = runner.invoke(cli, cli_env + [
            "add", str(sample_python_file),
            "--project", "code-snippets",
            "--material-type", "reference"
        ])
        
        assert result.exit_code == 0
        assert "Saved as research #" in result.output
    
    def test_add_nonexistent_file(self, runner, cli_env):
        """Test adding a file that doesn't exist."""
        result = runner.invoke(cli, cli_env + [
            "add", "/nonexistent/file.txt",
            "--project", "test",
            "--material-type", "research"
        ])
        
        assert result.exit_code != 0
        assert "not found" in result.output.lower()
    
    def test_add_invalid_confidence(self, runner, cli_env, sample_file):
        """Test adding with invalid confidence."""
        result = runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research",
            "--confidence", "1.5"
        ])
        
        assert result.exit_code != 0
        assert "between 0.0 and 1.0" in result.output
    
    def test_add_json_output(self, runner, cli_env, sample_file):
        """Test adding with JSON output."""
        result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "id" in data
        assert data["project"] == "test"
        assert data["material_type"] == "research"


# ============================================================================
# Search Command Tests
# ============================================================================

class TestSearchCommand:
    """Tests for the 'search' command."""
    
    def test_search_returns_results(self, runner, cli_env, sample_file):
        """Test that search returns added documents."""
        # First add a document
        runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        
        # Then search
        result = runner.invoke(cli, cli_env + [
            "search", "machine learning"
        ])
        
        assert result.exit_code == 0
        assert "results found" in result.output.lower()
    
    def test_search_no_results(self, runner, cli_env, sample_file):
        """Test search with no matching results."""
        # Add a document
        runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        
        # Search for something not in document
        result = runner.invoke(cli, cli_env + [
            "search", "quantum computing blockchain"
        ])
        
        assert result.exit_code == 0
        assert "no results" in result.output.lower()
    
    def test_search_filter_by_project(self, runner, cli_env, sample_file, temp_dir):
        """Test search with project filter."""
        # Add to project A
        runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "project-a",
            "--material-type", "research"
        ])
        
        # Create another file and add to project B
        other_file = temp_dir / "other.txt"
        other_file.write_text("Other content about machine learning")
        runner.invoke(cli, cli_env + [
            "add", str(other_file),
            "--project", "project-b",
            "--material-type", "research"
        ])
        
        # Search only in project A
        result = runner.invoke(cli, cli_env + [
            "search", "machine",
            "--project", "project-a"
        ])
        
        assert result.exit_code == 0
    
    def test_search_filter_by_material_type(self, runner, cli_env, sample_file, temp_dir):
        """Test search with material type filter."""
        # Add as research
        runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        
        # Add another as reference
        ref_file = temp_dir / "reference.txt"
        ref_file.write_text("Reference material about machine learning")
        runner.invoke(cli, cli_env + [
            "add", str(ref_file),
            "--project", "test",
            "--material-type", "reference"
        ])
        
        # Search only references
        result = runner.invoke(cli, cli_env + [
            "search", "machine",
            "--material", "reference"
        ])
        
        assert result.exit_code == 0
        assert "reference" in result.output.lower()
    
    def test_search_json_output(self, runner, cli_env, sample_file):
        """Test search with JSON output."""
        runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        
        result = runner.invoke(cli, cli_env + [
            "--json-output",
            "search", "machine"
        ])
        
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "query" in data
        assert "count" in data
        assert "results" in data


# ============================================================================
# Get Command Tests
# ============================================================================

class TestGetCommand:
    """Tests for the 'get' command."""
    
    def test_get_document(self, runner, cli_env, sample_file):
        """Test getting a document by ID."""
        # Add a document
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc_id = json.loads(add_result.output)["id"]
        
        # Get the document
        result = runner.invoke(cli, cli_env + [
            "get", str(doc_id)
        ])
        
        assert result.exit_code == 0
        assert f"#{doc_id}" in result.output
        assert "test" in result.output  # project
        assert "research" in result.output  # material type
    
    def test_get_nonexistent_document(self, runner, cli_env):
        """Test getting a document that doesn't exist."""
        result = runner.invoke(cli, cli_env + [
            "get", "99999"
        ])
        
        assert result.exit_code != 0
        assert "not found" in result.output.lower()
    
    def test_get_json_output(self, runner, cli_env, sample_file):
        """Test getting document with JSON output."""
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc_id = json.loads(add_result.output)["id"]
        
        result = runner.invoke(cli, cli_env + [
            "--json-output",
            "get", str(doc_id)
        ])
        
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == doc_id
        assert "attachments" in data


# ============================================================================
# Archive/Unarchive Command Tests
# ============================================================================

class TestArchiveCommand:
    """Tests for the 'archive' and 'unarchive' commands."""
    
    def test_archive_document(self, runner, cli_env, sample_file):
        """Test archiving a document."""
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc_id = json.loads(add_result.output)["id"]
        
        result = runner.invoke(cli, cli_env + [
            "archive", str(doc_id), "--force"
        ])
        
        assert result.exit_code == 0
        assert "archived" in result.output.lower()
    
    def test_unarchive_document(self, runner, cli_env, sample_file):
        """Test unarchiving a document."""
        # Add and archive
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc_id = json.loads(add_result.output)["id"]
        runner.invoke(cli, cli_env + ["archive", str(doc_id), "--force"])
        
        # Unarchive
        result = runner.invoke(cli, cli_env + [
            "unarchive", str(doc_id)
        ])
        
        assert result.exit_code == 0
        assert "restored" in result.output.lower()


# ============================================================================
# Export Command Tests
# ============================================================================

class TestExportCommand:
    """Tests for the 'export' command."""
    
    def test_export_json(self, runner, cli_env, sample_file):
        """Test exporting as JSON."""
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc_id = json.loads(add_result.output)["id"]
        
        result = runner.invoke(cli, cli_env + [
            "export", str(doc_id), "--format", "json"
        ])
        
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == doc_id
        assert "title" in data
    
    def test_export_markdown(self, runner, cli_env, sample_file):
        """Test exporting as Markdown."""
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc_id = json.loads(add_result.output)["id"]
        
        result = runner.invoke(cli, cli_env + [
            "export", str(doc_id), "--format", "markdown"
        ])
        
        assert result.exit_code == 0
        assert "# " in result.output  # Markdown header
        assert "**ID:**" in result.output
    
    def test_export_to_file(self, runner, cli_env, sample_file, temp_dir):
        """Test exporting to a file."""
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc_id = json.loads(add_result.output)["id"]
        
        output_file = temp_dir / "export.json"
        result = runner.invoke(cli, cli_env + [
            "export", str(doc_id), "--format", "json", "-o", str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["id"] == doc_id


# ============================================================================
# Link Command Tests
# ============================================================================

class TestLinkCommand:
    """Tests for the 'link' command."""
    
    def test_link_documents(self, runner, cli_env, sample_file, temp_dir):
        """Test creating a link between documents."""
        # Add two documents
        add_result1 = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc1_id = json.loads(add_result1.output)["id"]
        
        other_file = temp_dir / "other.txt"
        other_file.write_text("Other research content")
        add_result2 = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(other_file),
            "--project", "test",
            "--material-type", "reference"
        ])
        doc2_id = json.loads(add_result2.output)["id"]
        
        # Create link
        result = runner.invoke(cli, cli_env + [
            "link", str(doc1_id), str(doc2_id),
            "--type", "applies_to"
        ])
        
        assert result.exit_code == 0
        assert "linked" in result.output.lower()
    
    def test_link_with_relevance(self, runner, cli_env, sample_file, temp_dir):
        """Test creating a link with custom relevance."""
        # Add two documents
        add_result1 = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc1_id = json.loads(add_result1.output)["id"]
        
        other_file = temp_dir / "other.txt"
        other_file.write_text("Other content")
        add_result2 = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(other_file),
            "--project", "test",
            "--material-type", "reference"
        ])
        doc2_id = json.loads(add_result2.output)["id"]
        
        result = runner.invoke(cli, cli_env + [
            "link", str(doc1_id), str(doc2_id),
            "--type", "related",
            "--relevance", "0.9"
        ])
        
        assert result.exit_code == 0
    
    def test_link_self_error(self, runner, cli_env, sample_file):
        """Test that linking a document to itself fails."""
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        doc_id = json.loads(add_result.output)["id"]
        
        result = runner.invoke(cli, cli_env + [
            "link", str(doc_id), str(doc_id),
            "--type", "related"
        ])
        
        assert result.exit_code != 0
        assert "itself" in result.output.lower()


# ============================================================================
# Status Command Tests
# ============================================================================

class TestStatusCommand:
    """Tests for the 'status' command."""
    
    def test_status_empty(self, runner, cli_env):
        """Test status with empty database."""
        result = runner.invoke(cli, cli_env + ["status"])
        
        assert result.exit_code == 0
        assert "Research Library Status" in result.output
        assert "Documents:" in result.output
        assert "Storage:" in result.output
    
    def test_status_with_documents(self, runner, cli_env, sample_file):
        """Test status after adding documents."""
        runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        
        result = runner.invoke(cli, cli_env + ["status"])
        
        assert result.exit_code == 0
        # Should show at least 1 document
        assert "Total:" in result.output
    
    def test_status_json_output(self, runner, cli_env):
        """Test status with JSON output."""
        result = runner.invoke(cli, cli_env + [
            "--json-output",
            "status"
        ])
        
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "total_documents" in data
        assert "db_size" in data


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow(self, runner, cli_env, sample_file, temp_dir):
        """Test: add → search → get → archive workflow."""
        # 1. Add document
        add_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "integration-test",
            "--material-type", "research",
            "--tags", "test,integration"
        ])
        assert add_result.exit_code == 0
        doc_id = json.loads(add_result.output)["id"]
        
        # 2. Search for it
        search_result = runner.invoke(cli, cli_env + [
            "search", "machine learning"
        ])
        assert search_result.exit_code == 0
        assert f"#{doc_id}" in search_result.output
        
        # 3. Get details
        get_result = runner.invoke(cli, cli_env + [
            "get", str(doc_id)
        ])
        assert get_result.exit_code == 0
        assert "integration-test" in get_result.output
        
        # 4. Export
        export_result = runner.invoke(cli, cli_env + [
            "export", str(doc_id), "--format", "json"
        ])
        assert export_result.exit_code == 0
        export_data = json.loads(export_result.output)
        assert export_data["id"] == doc_id
        
        # 5. Archive
        archive_result = runner.invoke(cli, cli_env + [
            "archive", str(doc_id), "--force"
        ])
        assert archive_result.exit_code == 0
        
        # 6. Verify not in regular search
        search_after = runner.invoke(cli, cli_env + [
            "search", "machine learning"
        ])
        assert f"#{doc_id}" not in search_after.output
        
        # 7. Unarchive
        unarchive_result = runner.invoke(cli, cli_env + [
            "unarchive", str(doc_id)
        ])
        assert unarchive_result.exit_code == 0
        
        # 8. Verify back in search
        search_restored = runner.invoke(cli, cli_env + [
            "search", "machine learning"
        ])
        assert f"#{doc_id}" in search_restored.output
    
    def test_multi_project_workflow(self, runner, cli_env, sample_file, temp_dir):
        """Test working with multiple projects."""
        # Create files for different projects
        file_a = sample_file
        file_b = temp_dir / "project_b.txt"
        file_b.write_text("Python programming best practices")
        
        # Add to project A
        runner.invoke(cli, cli_env + [
            "add", str(file_a),
            "--project", "project-a",
            "--material-type", "reference"
        ])
        
        # Add to project B
        runner.invoke(cli, cli_env + [
            "add", str(file_b),
            "--project", "project-b",
            "--material-type", "research"
        ])
        
        # Search across all projects
        all_search = runner.invoke(cli, cli_env + [
            "search", "python OR machine",
            "--all-projects"
        ])
        assert all_search.exit_code == 0
        
        # Check status shows multiple projects
        status = runner.invoke(cli, cli_env + [
            "--json-output",
            "status"
        ])
        data = json.loads(status.output)
        assert data["project_count"] >= 2
    
    def test_linking_workflow(self, runner, cli_env, temp_dir):
        """Test document linking workflow."""
        # Create related documents
        paper = temp_dir / "paper.txt"
        paper.write_text("Research paper on deep learning")
        
        implementation = temp_dir / "impl.py"
        implementation.write_text("# Implementation of paper\ndef train(): pass")
        
        critique = temp_dir / "critique.txt"
        critique.write_text("Critical analysis of the research paper")
        
        # Add all documents
        paper_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(paper),
            "--project", "ml-research",
            "--material-type", "reference"
        ])
        paper_id = json.loads(paper_result.output)["id"]
        
        impl_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(implementation),
            "--project", "ml-research",
            "--material-type", "research"
        ])
        impl_id = json.loads(impl_result.output)["id"]
        
        critique_result = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(critique),
            "--project", "ml-research",
            "--material-type", "research"
        ])
        critique_id = json.loads(critique_result.output)["id"]
        
        # Create links
        # Implementation applies to paper
        runner.invoke(cli, cli_env + [
            "link", str(impl_id), str(paper_id),
            "--type", "applies_to",
            "--relevance", "0.9"
        ])
        
        # Critique relates to paper
        runner.invoke(cli, cli_env + [
            "link", str(critique_id), str(paper_id),
            "--type", "related"
        ])
        
        # Get paper and verify links are shown
        get_result = runner.invoke(cli, cli_env + [
            "get", str(paper_id)
        ])
        assert "Links" in get_result.output
        assert str(impl_id) in get_result.output or str(critique_id) in get_result.output


# ============================================================================
# Output Format Tests
# ============================================================================

class TestOutputFormat:
    """Tests for output formatting."""
    
    def test_search_table_format(self, runner, cli_env, sample_file):
        """Test that search output is properly formatted as a table."""
        runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "reference"
        ])
        
        result = runner.invoke(cli, cli_env + [
            "search", "machine"
        ])
        
        # Should have table headers
        assert "ID" in result.output
        assert "Title" in result.output
        assert "Material" in result.output
        assert "Conf" in result.output
    
    def test_status_sections(self, runner, cli_env):
        """Test that status shows all sections."""
        result = runner.invoke(cli, cli_env + ["status"])
        
        assert "Documents:" in result.output
        assert "Organization:" in result.output
        assert "Storage:" in result.output
        assert "Extraction Queue:" in result.output
        assert "Backups:" in result.output


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for error handling."""
    
    def test_missing_required_option(self, runner, cli_env, sample_file):
        """Test error when required option is missing."""
        result = runner.invoke(cli, cli_env + [
            "add", str(sample_file)
            # Missing --project and --material-type
        ])
        
        assert result.exit_code != 0
    
    def test_invalid_material_type(self, runner, cli_env, sample_file):
        """Test error with invalid material type."""
        result = runner.invoke(cli, cli_env + [
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "invalid"
        ])
        
        assert result.exit_code != 0
    
    def test_invalid_link_type(self, runner, cli_env, sample_file, temp_dir):
        """Test error with invalid link type."""
        add1 = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(sample_file),
            "--project", "test",
            "--material-type", "research"
        ])
        id1 = json.loads(add1.output)["id"]
        
        other = temp_dir / "other.txt"
        other.write_text("Other")
        add2 = runner.invoke(cli, cli_env + [
            "--json-output",
            "add", str(other),
            "--project", "test",
            "--material-type", "research"
        ])
        id2 = json.loads(add2.output)["id"]
        
        result = runner.invoke(cli, cli_env + [
            "link", str(id1), str(id2),
            "--type", "invalid_type"
        ])
        
        assert result.exit_code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
