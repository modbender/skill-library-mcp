#!/usr/bin/env python3
"""Tests for the Code Cache OpenClaw skill."""

import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSkillMetadata(unittest.TestCase):
    """Test SKILL.md metadata and format."""
    
    def setUp(self):
        self.skill_path = Path(__file__).parent.parent / "SKILL.md"
        self.skill_content = self.skill_path.read_text()
    
    def test_skill_file_exists(self):
        """SKILL.md should exist."""
        self.assertTrue(self.skill_path.exists())
    
    def test_has_frontmatter(self):
        """SKILL.md should have YAML frontmatter."""
        self.assertTrue(self.skill_content.startswith("---"))
        self.assertIn("---\n", self.skill_content[3:])
    
    def test_has_required_fields(self):
        """SKILL.md should have required frontmatter fields."""
        self.assertIn("name:", self.skill_content)
        self.assertIn("description:", self.skill_content)
    
    def test_has_metadata(self):
        """SKILL.md should have OpenClaw metadata."""
        self.assertIn("metadata:", self.skill_content)
        self.assertIn("openclaw", self.skill_content)
        self.assertIn("RAYSURFER_API_KEY", self.skill_content)
    
    def test_skill_name(self):
        """Skill name should be 'code-cache'."""
        self.assertIn("name: code-cache", self.skill_content)


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def test_import_without_raysurfer(self):
        """CLI should handle missing raysurfer package gracefully."""
        import code_cache
        # Module should load even without the raysurfer package
        self.assertTrue(hasattr(code_cache, 'main'))
        self.assertTrue(hasattr(code_cache, 'get_client'))
    
    @patch.dict(os.environ, {"RAYSURFER_API_KEY": ""}, clear=True)
    def test_missing_api_key_error(self):
        """Should error when API key is missing."""
        from code_cache import get_client
        with self.assertRaises(SystemExit) as context:
            get_client()
        self.assertEqual(context.exception.code, 1)


class TestSearchCommand(unittest.TestCase):
    """Test the search command."""
    
    def _create_mock_code_block(self, id="test-id", name="test_code", language="python", 
                                 description="Test description", source="print('hello')"):
        """Create a mock CodeBlock."""
        mock_cb = MagicMock()
        mock_cb.id = id
        mock_cb.name = name
        mock_cb.language = language
        mock_cb.description = description
        mock_cb.source = source
        return mock_cb
    
    def _create_mock_match(self, code_block=None, combined_score=0.85, vector_score=0.9,
                           verdict_score=0.8, thumbs_up=10, thumbs_down=2):
        """Create a mock SearchMatch."""
        mock_match = MagicMock()
        mock_match.code_block = code_block or self._create_mock_code_block()
        mock_match.combined_score = combined_score
        mock_match.vector_score = vector_score
        mock_match.verdict_score = verdict_score
        mock_match.thumbs_up = thumbs_up
        mock_match.thumbs_down = thumbs_down
        return mock_match
    
    @patch("code_cache.get_client")
    def test_search_with_results(self, mock_get_client):
        """Search should format results nicely."""
        from code_cache import cmd_search
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_result = MagicMock()
        mock_result.matches = [self._create_mock_match()]
        mock_result.total_found = 1
        mock_client.search.return_value = mock_result
        
        args = MagicMock()
        args.task = ["test", "task"]
        args.top_k = 5
        args.min_score = 0.3
        args.show_code = False
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        cmd_search(args)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        self.assertIn("Found 1 matches", output)
        self.assertIn("test_code", output)
        self.assertIn("test-id", output)
        self.assertIn("python", output)
        self.assertIn("0.85", output)  # combined_score
        self.assertIn("👍 10", output)
        self.assertIn("👎 2", output)
        
        # Verify API was called correctly
        mock_client.search.assert_called_once_with(
            task="test task",
            top_k=5,
            min_verdict_score=0.3,
        )
    
    @patch("code_cache.get_client")
    def test_search_no_results(self, mock_get_client):
        """Search should handle no results gracefully."""
        from code_cache import cmd_search
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_result = MagicMock()
        mock_result.matches = []
        mock_result.total_found = 0
        mock_client.search.return_value = mock_result
        
        args = MagicMock()
        args.task = ["test", "task"]
        args.top_k = 5
        args.min_score = 0.3
        args.show_code = False
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        cmd_search(args)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        self.assertIn("No cached code found", output)
        self.assertIn("Tip:", output)
    
    @patch("code_cache.get_client")
    def test_search_with_show_code(self, mock_get_client):
        """Search with --show-code should display code."""
        from code_cache import cmd_search
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        code_block = self._create_mock_code_block(source="def hello():\n    print('hello')")
        mock_result = MagicMock()
        mock_result.matches = [self._create_mock_match(code_block=code_block)]
        mock_result.total_found = 1
        mock_client.search.return_value = mock_result
        
        args = MagicMock()
        args.task = ["test"]
        args.top_k = 5
        args.min_score = 0.3
        args.show_code = True
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        cmd_search(args)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        self.assertIn("Code from top match", output)
        self.assertIn("def hello()", output)
    
    @patch("code_cache.get_client")
    def test_search_long_description_truncated(self, mock_get_client):
        """Long descriptions should be truncated to 100 chars."""
        from code_cache import cmd_search
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        long_desc = "A" * 150  # 150 character description
        code_block = self._create_mock_code_block(description=long_desc)
        mock_result = MagicMock()
        mock_result.matches = [self._create_mock_match(code_block=code_block)]
        mock_result.total_found = 1
        mock_client.search.return_value = mock_result
        
        args = MagicMock()
        args.task = ["test"]
        args.top_k = 5
        args.min_score = 0.3
        args.show_code = False
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        cmd_search(args)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # Should have "..." indicating truncation
        self.assertIn("...", output)
        # Should not have full 150 A's
        self.assertNotIn("A" * 150, output)


class TestFilesCommand(unittest.TestCase):
    """Test the files command."""
    
    @patch("code_cache.get_client")
    def test_files_writes_to_disk(self, mock_get_client):
        """Files command should write files to cache directory."""
        from code_cache import cmd_files
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_file = MagicMock()
        mock_file.filename = "test_script.py"
        mock_file.source = "print('hello world')"
        
        mock_result = MagicMock()
        mock_result.files = [mock_file]
        mock_result.add_to_llm_prompt = "Test LLM prompt"
        mock_client.get_code_files.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            args = MagicMock()
            args.task = ["test", "task"]
            args.top_k = 5
            args.cache_dir = tmpdir
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            cmd_files(args)
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Verify file was written
            written_file = Path(tmpdir) / "test_script.py"
            self.assertTrue(written_file.exists())
            self.assertEqual(written_file.read_text(), "print('hello world')")
            
            # Verify output
            self.assertIn("Retrieved 1 files", output)
            self.assertIn("test_script.py", output)
            self.assertIn("Test LLM prompt", output)
            
            # Verify API was called
            mock_client.get_code_files.assert_called_once_with(
                task="test task",
                top_k=5,
                cache_dir=tmpdir,
            )
    
    @patch("code_cache.get_client")
    def test_files_multiple(self, mock_get_client):
        """Files command should handle multiple files."""
        from code_cache import cmd_files
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_file1 = MagicMock()
        mock_file1.filename = "script1.py"
        mock_file1.source = "# Script 1"
        
        mock_file2 = MagicMock()
        mock_file2.filename = "script2.py"
        mock_file2.source = "# Script 2"
        
        mock_result = MagicMock()
        mock_result.files = [mock_file1, mock_file2]
        mock_result.add_to_llm_prompt = ""
        mock_client.get_code_files.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            args = MagicMock()
            args.task = ["test"]
            args.top_k = 5
            args.cache_dir = tmpdir
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            cmd_files(args)
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Verify both files were written
            self.assertTrue((Path(tmpdir) / "script1.py").exists())
            self.assertTrue((Path(tmpdir) / "script2.py").exists())
            self.assertIn("Retrieved 2 files", output)
    
    @patch("code_cache.get_client")
    def test_files_no_results(self, mock_get_client):
        """Files command should handle no results."""
        from code_cache import cmd_files
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_result = MagicMock()
        mock_result.files = []
        mock_client.get_code_files.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            args = MagicMock()
            args.task = ["test"]
            args.top_k = 5
            args.cache_dir = tmpdir
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            cmd_files(args)
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            self.assertIn("No code files found", output)
    
    @patch("code_cache.get_client")
    def test_files_creates_cache_dir(self, mock_get_client):
        """Files command should create cache directory if it doesn't exist."""
        from code_cache import cmd_files
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_file = MagicMock()
        mock_file.filename = "script.py"
        mock_file.source = "# code"
        
        mock_result = MagicMock()
        mock_result.files = [mock_file]
        mock_result.add_to_llm_prompt = ""
        mock_client.get_code_files.return_value = mock_result
        
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = Path(tmpdir) / "nested" / "cache"
            args = MagicMock()
            args.task = ["test"]
            args.top_k = 5
            args.cache_dir = str(nested_dir)
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            cmd_files(args)
            
            sys.stdout = sys.__stdout__
            
            # Verify nested directory was created
            self.assertTrue(nested_dir.exists())
            self.assertTrue((nested_dir / "script.py").exists())


class TestUploadCommand(unittest.TestCase):
    """Test the upload command."""
    
    @patch("code_cache.get_client")
    def test_upload_single_file(self, mock_get_client):
        """Upload should send files to API."""
        from code_cache import cmd_upload
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('test')")
            temp_path = f.name
        
        try:
            args = MagicMock()
            args.task = "test task"
            args.files = [temp_path]
            args.succeeded = True
            args.no_auto_vote = False
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            cmd_upload(args)
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Verify API was called
            mock_client.upload_new_code_snip.assert_called_once()
            call_kwargs = mock_client.upload_new_code_snip.call_args.kwargs
            self.assertEqual(call_kwargs['task'], "test task")
            self.assertEqual(call_kwargs['succeeded'], True)
            self.assertEqual(call_kwargs['use_raysurfer_ai_voting'], True)
            self.assertEqual(call_kwargs['file_written'].path, temp_path)
            
            self.assertIn("Uploaded 1 file(s)", output)
            self.assertIn("Succeeded: True", output)
        finally:
            os.unlink(temp_path)
    
    @patch("code_cache.get_client")
    def test_upload_multiple_files(self, mock_get_client):
        """Upload should handle multiple files."""
        from code_cache import cmd_upload
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        temp_files = []
        try:
            for i in range(3):
                f = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
                f.write(f"# File {i}")
                f.close()
                temp_files.append(f.name)
            
            args = MagicMock()
            args.task = "multi file task"
            args.files = temp_files
            args.succeeded = True
            args.no_auto_vote = False
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            cmd_upload(args)
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            self.assertEqual(mock_client.upload_new_code_snip.call_count, 3)
            self.assertIn("Uploaded 3 file(s)", output)
        finally:
            for f in temp_files:
                os.unlink(f)
    
    @patch("code_cache.get_client")
    def test_upload_failed_execution(self, mock_get_client):
        """Upload with --failed should mark as failed."""
        from code_cache import cmd_upload
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# broken")
            temp_path = f.name
        
        try:
            args = MagicMock()
            args.task = "failed task"
            args.files = [temp_path]
            args.succeeded = False
            args.no_auto_vote = False
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            cmd_upload(args)
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            call_kwargs = mock_client.upload_new_code_snip.call_args.kwargs
            self.assertEqual(call_kwargs['succeeded'], False)
            self.assertIn("Succeeded: False", output)
        finally:
            os.unlink(temp_path)
    
    @patch("code_cache.get_client")
    def test_upload_no_auto_vote(self, mock_get_client):
        """Upload with --no-auto-vote should disable auto voting."""
        from code_cache import cmd_upload
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# code")
            temp_path = f.name
        
        try:
            args = MagicMock()
            args.task = "test"
            args.files = [temp_path]
            args.succeeded = True
            args.no_auto_vote = True
            
            captured_output = StringIO()
            sys.stdout = captured_output
            
            cmd_upload(args)
            
            sys.stdout = sys.__stdout__
            
            call_kwargs = mock_client.upload_new_code_snip.call_args.kwargs
            self.assertEqual(call_kwargs['use_raysurfer_ai_voting'], False)
        finally:
            os.unlink(temp_path)
    
    def test_upload_file_not_found(self):
        """Upload should error on missing file."""
        from code_cache import cmd_upload
        
        args = MagicMock()
        args.task = "test"
        args.files = ["/nonexistent/file.py"]
        args.succeeded = True
        args.no_auto_vote = False
        
        with self.assertRaises(SystemExit) as context:
            cmd_upload(args)
        
        self.assertEqual(context.exception.code, 1)


class TestVoteCommand(unittest.TestCase):
    """Test the vote command."""
    
    @patch("code_cache.get_client")
    def test_upvote(self, mock_get_client):
        """Should send upvote correctly."""
        from code_cache import cmd_vote
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        args = MagicMock()
        args.code_block_id = "abc123"
        args.up = True
        args.task = "test task"
        args.name = "test_code"
        args.description = "Test description"
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        cmd_vote(args)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        mock_client.vote_code_snip.assert_called_once_with(
            task="test task",
            code_block_id="abc123",
            code_block_name="test_code",
            code_block_description="Test description",
            succeeded=True,
        )
        
        self.assertIn("👍", output)
        self.assertIn("abc123", output)
    
    @patch("code_cache.get_client")
    def test_downvote(self, mock_get_client):
        """Should send downvote correctly."""
        from code_cache import cmd_vote
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        args = MagicMock()
        args.code_block_id = "xyz789"
        args.up = False
        args.task = None
        args.name = None
        args.description = None
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        cmd_vote(args)
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        mock_client.vote_code_snip.assert_called_once_with(
            task="",
            code_block_id="xyz789",
            code_block_name="",
            code_block_description="",
            succeeded=False,
        )
        
        self.assertIn("👎", output)
        self.assertIn("xyz789", output)
    
    @patch("code_cache.get_client")
    def test_vote_minimal_args(self, mock_get_client):
        """Vote should work with just code_block_id."""
        from code_cache import cmd_vote
        
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        args = MagicMock()
        args.code_block_id = "simple123"
        args.up = True
        args.task = None
        args.name = None
        args.description = None
        
        cmd_vote(args)
        
        mock_client.vote_code_snip.assert_called_once()


class TestMainEntrypoint(unittest.TestCase):
    """Test main CLI entrypoint."""
    
    def test_help_output(self):
        """--help should show usage."""
        from code_cache import main
        
        with self.assertRaises(SystemExit) as context:
            sys.argv = ["code-cache", "--help"]
            main()
        
        self.assertEqual(context.exception.code, 0)
    
    def test_missing_command(self):
        """Should error without command."""
        from code_cache import main
        
        with self.assertRaises(SystemExit) as context:
            sys.argv = ["code-cache"]
            main()
        
        self.assertNotEqual(context.exception.code, 0)
    
    def test_search_subcommand_help(self):
        """search --help should show search-specific options."""
        from code_cache import main
        
        captured_stderr = StringIO()
        sys.stderr = captured_stderr
        
        with self.assertRaises(SystemExit) as context:
            sys.argv = ["code-cache", "search", "--help"]
            main()
        
        sys.stderr = sys.__stderr__
        self.assertEqual(context.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
