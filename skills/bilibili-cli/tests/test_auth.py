"""Tests for auth module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from bilibili_api.utils.network import Credential
from bili_cli.auth import (
    _load_saved_credential,
    save_credential,
    clear_credential,
    _validate_credential,
)


def test_load_missing_file(tmp_path):
    with patch("bili_cli.auth.CREDENTIAL_FILE", tmp_path / "nope.json"):
        assert _load_saved_credential() is None


def test_save_and_load(tmp_path):
    cred_file = tmp_path / "cred.json"
    with patch("bili_cli.auth.CREDENTIAL_FILE", cred_file), \
         patch("bili_cli.auth.CONFIG_DIR", tmp_path):
        cred = Credential(sessdata="test_sess", bili_jct="test_jct")
        save_credential(cred)

        # File should exist with correct permissions
        assert cred_file.exists()

        # Load it back
        loaded = _load_saved_credential()
        assert loaded is not None
        assert loaded.sessdata == "test_sess"
        assert loaded.bili_jct == "test_jct"


def test_save_creates_directory(tmp_path):
    new_dir = tmp_path / "new_config"
    cred_file = new_dir / "cred.json"
    with patch("bili_cli.auth.CREDENTIAL_FILE", cred_file), \
         patch("bili_cli.auth.CONFIG_DIR", new_dir):
        cred = Credential(sessdata="s", bili_jct="j")
        save_credential(cred)
        assert new_dir.exists()
        assert cred_file.exists()


def test_load_corrupt_file(tmp_path):
    cred_file = tmp_path / "bad.json"
    cred_file.write_text("not json at all")
    with patch("bili_cli.auth.CREDENTIAL_FILE", cred_file):
        assert _load_saved_credential() is None


def test_load_empty_sessdata(tmp_path):
    cred_file = tmp_path / "empty.json"
    cred_file.write_text(json.dumps({"sessdata": "", "bili_jct": "x"}))
    with patch("bili_cli.auth.CREDENTIAL_FILE", cred_file):
        assert _load_saved_credential() is None


def test_clear_credential(tmp_path):
    cred_file = tmp_path / "cred.json"
    cred_file.write_text("{}")
    with patch("bili_cli.auth.CREDENTIAL_FILE", cred_file):
        clear_credential()
        assert not cred_file.exists()


def test_clear_credential_nonexistent(tmp_path):
    with patch("bili_cli.auth.CREDENTIAL_FILE", tmp_path / "nope.json"):
        # Should not raise
        clear_credential()


def test_validate_valid_credential():
    with patch("bilibili_api.user.get_self_info", new_callable=AsyncMock, return_value={"mid": 1}):
        cred = Credential(sessdata="valid")
        assert _validate_credential(cred) is True


def test_validate_expired_credential():
    with patch("bilibili_api.user.get_self_info", new_callable=AsyncMock, side_effect=Exception("expired")):
        cred = Credential(sessdata="expired")
        assert _validate_credential(cred) is False
