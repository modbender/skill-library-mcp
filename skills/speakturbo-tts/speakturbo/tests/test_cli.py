"""
TDD Tests for speakturbo CLI

Run with: uv run pytest speakturbo/tests/test_cli.py -v
"""

import os
import subprocess
import tempfile
import time
import wave

import pytest


# Path to CLI
CLI_PATH = os.path.join(os.path.dirname(__file__), "..", "cli.py")


def run_cli(*args, input_text=None, timeout=30):
    """Run the CLI with given arguments."""
    cmd = ["python", CLI_PATH] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=input_text,
        timeout=timeout,
        cwd=os.path.dirname(CLI_PATH),
    )
    return result


class TestCLIBasic:
    """Basic CLI functionality."""
    
    def test_help_works(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "speakturbo" in result.stdout.lower() or "usage" in result.stdout.lower()
    
    def test_version_works(self):
        result = run_cli("--version")
        assert result.returncode == 0
    
    def test_list_voices(self):
        result = run_cli("--list-voices")
        assert result.returncode == 0
        assert "alba" in result.stdout
        assert "marius" in result.stdout


class TestCLIGeneration:
    """Audio generation via CLI."""
    
    def test_generate_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        
        try:
            result = run_cli("Hello world", "-o", output_path)
            assert result.returncode == 0
            assert os.path.exists(output_path)
            
            # Verify it's a valid WAV
            with wave.open(output_path, 'rb') as wav:
                assert wav.getnchannels() == 1
                assert wav.getframerate() == 24000
                assert wav.getnframes() > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_generate_with_voice(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        
        try:
            result = run_cli("Hello", "-v", "marius", "-o", output_path)
            assert result.returncode == 0
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_read_from_stdin(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        
        try:
            result = run_cli("-o", output_path, input_text="Hello from stdin")
            assert result.returncode == 0
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestCLIValidation:
    """Input validation."""
    
    def test_invalid_voice_shows_error(self):
        result = run_cli("Hello", "-v", "nonexistent", "-o", "/tmp/test.wav")
        assert result.returncode != 0
        assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()
    
    def test_empty_text_shows_error(self):
        result = run_cli("", "-o", "/tmp/test.wav")
        assert result.returncode != 0


class TestCLIDaemon:
    """Daemon management."""
    
    def test_daemon_status(self):
        result = run_cli("--daemon-status")
        # Should work whether daemon is running or not
        assert result.returncode == 0


class TestCLIOutputPathAllowlist:
    """Output path allowlist behavior.

    Tests verify the behavioral contract:
    - Default-allowed directories work without --allow-dir
    - Non-allowed directories are blocked with a clear error
    - --allow-dir overrides the block for that invocation
    - ~/.speakturbo/config adds permanent entries
    - Error messages contain actionable fix instructions
    """

    def test_tmp_is_allowed_by_default(self):
        """Writing to /tmp should work without any flags."""
        output_path = "/tmp/speakturbo_test_allowlist.wav"
        try:
            result = run_cli("test", "-o", output_path)
            assert result.returncode == 0
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_system_tempdir_is_allowed_by_default(self):
        """Writing to tempfile.gettempdir() should work (used by NamedTemporaryFile)."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name
        try:
            result = run_cli("test", "-o", output_path)
            assert result.returncode == 0
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_cwd_is_allowed_by_default(self):
        """Writing to a relative path (CWD) should work."""
        result = run_cli("test", "-o", "speakturbo_test_cwd.wav")
        assert result.returncode == 0
        # Clean up — file is in CWD of the CLI process (speakturbo/ dir)
        cwd_file = os.path.join(os.path.dirname(CLI_PATH), "speakturbo_test_cwd.wav")
        if os.path.exists(cwd_file):
            os.unlink(cwd_file)

    def test_speakturbo_dir_is_allowed_by_default(self):
        """Writing to ~/.speakturbo/ should work."""
        output_path = os.path.expanduser("~/.speakturbo/test_allowlist.wav")
        try:
            result = run_cli("test", "-o", output_path)
            assert result.returncode == 0
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_arbitrary_path_is_blocked(self):
        """Writing to a non-allowed path should fail with exit code 1."""
        result = run_cli("test", "-o", "/usr/share/speakturbo_test.wav")
        assert result.returncode != 0

    def test_blocked_path_error_shows_path(self):
        """Error message should show the rejected path."""
        result = run_cli("test", "-o", "/usr/share/speakturbo_test.wav")
        assert "/usr/share/speakturbo_test.wav" in result.stderr

    def test_blocked_path_error_shows_allowed_dirs(self):
        """Error message should list the directories that ARE allowed."""
        result = run_cli("test", "-o", "/usr/share/speakturbo_test.wav")
        assert "Allowed directories" in result.stderr

    def test_blocked_path_error_shows_allow_dir_fix(self):
        """Error message should show the exact --allow-dir command to fix it."""
        result = run_cli("test", "-o", "/usr/share/speakturbo_test.wav")
        assert "--allow-dir" in result.stderr

    def test_blocked_path_error_shows_config_fix(self):
        """Error message should show how to permanently allow via config."""
        result = run_cli("test", "-o", "/usr/share/speakturbo_test.wav")
        assert "~/.speakturbo/config" in result.stderr
        assert "mkdir -p" in result.stderr

    def test_allow_dir_flag_overrides_block(self):
        """--allow-dir should let you write to an otherwise-blocked path."""
        # Use a dir in HOME root — not under /tmp, gettempdir(), or ~/.speakturbo/
        test_dir = os.path.expanduser("~/speakturbo_allow_test_tmp")
        os.makedirs(test_dir, exist_ok=True)
        output_path = os.path.join(test_dir, "test.wav")
        try:
            # Without --allow-dir, this should fail
            result_blocked = run_cli("test", "-o", output_path)
            assert result_blocked.returncode != 0, "Should be blocked without --allow-dir"

            # With --allow-dir, this should work
            result = run_cli("test", "-o", output_path, "--allow-dir", test_dir)
            assert result.returncode == 0
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
            if os.path.exists(test_dir):
                os.rmdir(test_dir)

    def test_config_file_adds_permanent_entry(self):
        """Dirs listed in ~/.speakturbo/config should be allowed without --allow-dir."""
        config_file = os.path.expanduser("~/.speakturbo/config")
        # Use home root dir — not in default allowlist
        test_dir = os.path.expanduser("~/speakturbo_config_test_tmp")
        os.makedirs(test_dir, exist_ok=True)
        output_path = os.path.join(test_dir, "test.wav")

        # Save existing config if any
        had_config = os.path.exists(config_file)
        old_content = open(config_file).read() if had_config else None

        try:
            # Verify it's blocked first
            result_blocked = run_cli("test", "-o", output_path)
            assert result_blocked.returncode != 0, "Should be blocked before config change"

            # Write test dir to config
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "a") as f:
                f.write(f"\n{test_dir}\n")

            # Now it should work
            result = run_cli("test", "-o", output_path)
            assert result.returncode == 0
            assert os.path.exists(output_path)
        finally:
            # Restore original config
            if had_config:
                with open(config_file, "w") as f:
                    f.write(old_content)
            elif os.path.exists(config_file):
                os.unlink(config_file)
            if os.path.exists(output_path):
                os.unlink(output_path)
            if os.path.exists(test_dir):
                os.rmdir(test_dir)

    def test_symlink_escape_is_blocked(self):
        """A symlink in /tmp pointing outside allowed dirs should be blocked."""
        # Create symlink: /tmp/speakturbo_escape_test -> /usr/share/
        link_path = "/tmp/speakturbo_escape_test"
        target_file = link_path + "/evil.wav"

        try:
            if os.path.islink(link_path):
                os.unlink(link_path)
            os.symlink("/usr/share", link_path)

            result = run_cli("test", "-o", target_file)
            assert result.returncode != 0, "Symlink escape should be blocked"
        finally:
            if os.path.islink(link_path):
                os.unlink(link_path)

    def test_path_traversal_is_blocked(self):
        """Path with .. that escapes an allowed dir should be blocked."""
        result = run_cli("test", "-o", "/tmp/../etc/test.wav")
        assert result.returncode != 0

    def test_no_output_flag_skips_validation(self):
        """When -o is not specified, no path validation occurs."""
        # Without -o, the CLI either plays audio or (with --no-play) does nothing.
        # Either way, the allowlist error should never appear.
        result = run_cli("test", "--no-play")
        # May get daemon connection error if daemon isn't running — that's fine.
        # The key assertion: no allowlist error.
        assert "outside allowed directories" not in result.stderr
