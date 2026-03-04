"""Tests for generate_dev_token.py — Apple Music JWT token generation."""

import sys
from unittest.mock import patch, MagicMock, mock_open

import pytest

import generate_dev_token as gdt


class TestMain:
    def test_missing_pyjwt_exits(self, monkeypatch):
        """When PyJWT is not installed, should exit with error."""
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "jwt":
                raise ImportError("No module named 'jwt'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        with pytest.raises(SystemExit):
            gdt.main()

    def test_missing_env_vars_exits(self, monkeypatch):
        """Should exit when required env vars are missing."""
        monkeypatch.delenv("APPLE_KEY_ID", raising=False)
        monkeypatch.delenv("APPLE_TEAM_ID", raising=False)
        monkeypatch.delenv("APPLE_PRIVATE_KEY_PATH", raising=False)

        # Mock jwt import
        mock_jwt = MagicMock()
        monkeypatch.setitem(sys.modules, "jwt", mock_jwt)

        with pytest.raises(SystemExit):
            gdt.main()

    def test_missing_key_file_exits(self, monkeypatch, tmp_path):
        """Should exit when key file doesn't exist."""
        monkeypatch.setenv("APPLE_KEY_ID", "KEY123")
        monkeypatch.setenv("APPLE_TEAM_ID", "TEAM456")
        monkeypatch.setenv("APPLE_PRIVATE_KEY_PATH", str(tmp_path / "nonexistent.p8"))

        mock_jwt = MagicMock()
        monkeypatch.setitem(sys.modules, "jwt", mock_jwt)

        with pytest.raises(SystemExit):
            gdt.main()

    def test_invalid_expiry_exits(self, monkeypatch, tmp_path):
        """Should exit when APPLE_TOKEN_EXPIRY is not a number."""
        key_file = tmp_path / "key.p8"
        key_file.write_text("fake-key")
        monkeypatch.setenv("APPLE_KEY_ID", "KEY123")
        monkeypatch.setenv("APPLE_TEAM_ID", "TEAM456")
        monkeypatch.setenv("APPLE_PRIVATE_KEY_PATH", str(key_file))
        monkeypatch.setenv("APPLE_TOKEN_EXPIRY", "not-a-number")

        mock_jwt = MagicMock()
        monkeypatch.setitem(sys.modules, "jwt", mock_jwt)

        with pytest.raises(SystemExit):
            gdt.main()

    def test_successful_token_generation(self, monkeypatch, tmp_path, capsys):
        """Should generate and print token on success."""
        key_file = tmp_path / "key.p8"
        key_file.write_text("-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----")
        monkeypatch.setenv("APPLE_KEY_ID", "KEY123")
        monkeypatch.setenv("APPLE_TEAM_ID", "TEAM456")
        monkeypatch.setenv("APPLE_PRIVATE_KEY_PATH", str(key_file))
        monkeypatch.delenv("APPLE_TOKEN_EXPIRY", raising=False)

        mock_jwt = MagicMock()
        mock_jwt.encode.return_value = "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.test.sig"
        monkeypatch.setitem(sys.modules, "jwt", mock_jwt)

        gdt.main()

        captured = capsys.readouterr()
        assert "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.test.sig" in captured.out
        assert "Token generated" in captured.err

    def test_token_bytes_decoded(self, monkeypatch, tmp_path, capsys):
        """When jwt.encode returns bytes, should decode to string."""
        key_file = tmp_path / "key.p8"
        key_file.write_text("fake-key")
        monkeypatch.setenv("APPLE_KEY_ID", "KEY123")
        monkeypatch.setenv("APPLE_TEAM_ID", "TEAM456")
        monkeypatch.setenv("APPLE_PRIVATE_KEY_PATH", str(key_file))

        mock_jwt = MagicMock()
        mock_jwt.encode.return_value = b"token-as-bytes"
        monkeypatch.setitem(sys.modules, "jwt", mock_jwt)

        gdt.main()

        captured = capsys.readouterr()
        assert "token-as-bytes" in captured.out

    def test_custom_expiry(self, monkeypatch, tmp_path, capsys):
        """Should use custom expiry from env var."""
        key_file = tmp_path / "key.p8"
        key_file.write_text("fake-key")
        monkeypatch.setenv("APPLE_KEY_ID", "KEY123")
        monkeypatch.setenv("APPLE_TEAM_ID", "TEAM456")
        monkeypatch.setenv("APPLE_PRIVATE_KEY_PATH", str(key_file))
        monkeypatch.setenv("APPLE_TOKEN_EXPIRY", "86400")  # 1 day

        mock_jwt = MagicMock()
        mock_jwt.encode.return_value = "token"
        monkeypatch.setitem(sys.modules, "jwt", mock_jwt)

        gdt.main()

        # Verify the encode call used the right expiry
        call_args = mock_jwt.encode.call_args
        payload = call_args[0][0]
        assert payload["exp"] - payload["iat"] == 86400

        captured = capsys.readouterr()
        assert "1 days" in captured.err

    def test_jwt_encode_error_exits(self, monkeypatch, tmp_path):
        """Should exit when jwt.encode raises an exception."""
        key_file = tmp_path / "key.p8"
        key_file.write_text("fake-key")
        monkeypatch.setenv("APPLE_KEY_ID", "KEY123")
        monkeypatch.setenv("APPLE_TEAM_ID", "TEAM456")
        monkeypatch.setenv("APPLE_PRIVATE_KEY_PATH", str(key_file))

        mock_jwt = MagicMock()
        mock_jwt.encode.side_effect = Exception("Invalid key")
        monkeypatch.setitem(sys.modules, "jwt", mock_jwt)

        with pytest.raises(SystemExit):
            gdt.main()

    def test_partial_env_vars_reports_missing(self, monkeypatch, capsys):
        """Should report which specific vars are missing."""
        monkeypatch.setenv("APPLE_KEY_ID", "KEY123")
        monkeypatch.delenv("APPLE_TEAM_ID", raising=False)
        monkeypatch.delenv("APPLE_PRIVATE_KEY_PATH", raising=False)

        mock_jwt = MagicMock()
        monkeypatch.setitem(sys.modules, "jwt", mock_jwt)

        with pytest.raises(SystemExit):
            gdt.main()

        captured = capsys.readouterr()
        assert "APPLE_TEAM_ID" in captured.err
        assert "APPLE_PRIVATE_KEY_PATH" in captured.err
