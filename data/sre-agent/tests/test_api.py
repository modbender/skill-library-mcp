"""
Tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app, raise_server_exceptions=False)

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_readiness_check(self, client):
        """Test readiness endpoint."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True

    def test_liveness_check(self, client):
        """Test liveness endpoint."""
        response = client.get("/live")

        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True


class TestAnomalyEndpoints:
    """Tests for anomaly endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app, raise_server_exceptions=False)

    def test_list_anomalies(self, client):
        """Test listing anomalies."""
        # Note: This test may fail without a running agent
        # In a real test setup, you'd mock the agent
        response = client.get("/api/v1/anomalies")

        # Either 200 (if agent running) or 503 (if not)
        assert response.status_code in (200, 503)

    def test_get_nonexistent_anomaly(self, client):
        """Test getting a nonexistent anomaly."""
        response = client.get("/api/v1/anomalies/ANO-nonexistent")

        # Either 404 (not found) or 503 (agent not running)
        assert response.status_code in (404, 503)
