"""Unit tests for security functions."""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.security import (
    create_api_key,
    hash_api_key,
    verify_api_key,
    create_magic_link_token,
    create_access_token,
    decode_access_token,
)
from app.core.config import settings


class TestCreateAPIKey:
    """Tests for create_api_key()."""
    
    def test_returns_string(self):
        """Should return a string."""
        key = create_api_key()
        assert isinstance(key, str)
    
    def test_returns_urlsafe_token(self):
        """Should return URL-safe token."""
        key = create_api_key()
        # URL-safe base64: alphanumeric, -, _
        assert all(c.isalnum() or c in '-_' for c in key)
    
    def test_returns_unique_keys(self):
        """Should return different keys on each call."""
        key1 = create_api_key()
        key2 = create_api_key()
        assert key1 != key2
    
    def test_returns_32_bytes_encoded(self):
        """Should return approximately 43-44 characters (32 bytes base64url encoded)."""
        key = create_api_key()
        # token_urlsafe(32) produces ~43 chars
        assert 40 <= len(key) <= 45


class TestHashAPIKey:
    """Tests for hash_api_key()."""
    
    def test_returns_hex_string(self):
        """Should return hexadecimal string."""
        key = create_api_key()
        hashed = hash_api_key(key)
        assert isinstance(hashed, str)
        assert all(c in '0123456789abcdef' for c in hashed)
    
    def test_returns_64_char_hash(self):
        """Should return 64-character SHA256 hash."""
        key = create_api_key()
        hashed = hash_api_key(key)
        assert len(hashed) == 64
    
    def test_is_deterministic(self):
        """Same input should produce same hash."""
        key = create_api_key()
        hash1 = hash_api_key(key)
        hash2 = hash_api_key(key)
        assert hash1 == hash2
    
    def test_different_keys_produce_different_hashes(self):
        """Different keys should produce different hashes."""
        key1 = create_api_key()
        key2 = create_api_key()
        hash1 = hash_api_key(key1)
        hash2 = hash_api_key(key2)
        assert hash1 != hash2


class TestVerifyAPIKey:
    """Tests for verify_api_key()."""
    
    def test_verifies_correct_key(self):
        """Should return True for correct key."""
        key = create_api_key()
        hashed = hash_api_key(key)
        assert verify_api_key(key, hashed) is True
    
    def test_rejects_wrong_key(self):
        """Should return False for wrong key."""
        key1 = create_api_key()
        key2 = create_api_key()
        hashed = hash_api_key(key1)
        assert verify_api_key(key2, hashed) is False
    
    def test_rejects_empty_key(self):
        """Should return False for empty key."""
        key = create_api_key()
        hashed = hash_api_key(key)
        assert verify_api_key("", hashed) is False


class TestCreateMagicLinkToken:
    """Tests for create_magic_link_token()."""
    
    def test_returns_string(self):
        """Should return a string."""
        token = create_magic_link_token()
        assert isinstance(token, str)
    
    def test_returns_urlsafe_token(self):
        """Should return URL-safe token."""
        token = create_magic_link_token()
        assert all(c.isalnum() or c in '-_' for c in token)
    
    def test_returns_unique_tokens(self):
        """Should return different tokens on each call."""
        token1 = create_magic_link_token()
        token2 = create_magic_link_token()
        assert token1 != token2


class TestCreateAccessToken:
    """Tests for create_access_token()."""
    
    def test_returns_jwt_string(self):
        """Should return a JWT string."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
    
    def test_includes_data_in_token(self):
        """Should include provided data in token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
    
    def test_includes_expiration(self):
        """Should include expiration claim."""
        data = {"sub": "user123"}
        token = create_access_token(data)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
    
    def test_uses_custom_expiration(self):
        """Should use custom expiration delta if provided."""
        data = {"sub": "user123"}
        custom_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=custom_delta)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        # Should expire in approximately 30 minutes (allow 1 minute tolerance)
        assert 29 * 60 <= (exp_time - now).total_seconds() <= 31 * 60


class TestDecodeAccessToken:
    """Tests for decode_access_token()."""
    
    def test_decodes_valid_token(self):
        """Should decode valid token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
    
    def test_returns_none_for_invalid_token(self):
        """Should return None for invalid token."""
        invalid_token = "invalid.token.here"
        payload = decode_access_token(invalid_token)
        assert payload is None
    
    def test_returns_none_for_expired_token(self):
        """Should return None for expired token."""
        data = {"sub": "user123"}
        # Create token with past expiration
        expired_delta = timedelta(minutes=-1)
        token = create_access_token(data, expires_delta=expired_delta)
        payload = decode_access_token(token)
        assert payload is None
    
    def test_returns_none_for_wrong_secret(self):
        """Should return None for token signed with wrong secret."""
        # Create token with different secret
        wrong_secret = "wrong-secret-key"
        data = {"sub": "user123"}
        token = jwt.encode(
            {**data, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            wrong_secret,
            algorithm=settings.algorithm
        )
        payload = decode_access_token(token)
        assert payload is None
