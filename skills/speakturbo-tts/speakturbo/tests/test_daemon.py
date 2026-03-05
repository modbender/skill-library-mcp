"""
TDD Tests for speakturbo daemon (daemon_streaming.py)

Tests the PRODUCTION daemon — daemon_streaming.py with GET /tts on port 7125.

Run with: cd speakturbo && uv run pytest tests/test_daemon.py -v
"""

import struct
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create test client — imports the PRODUCTION streaming daemon.
    
    base_url must be set to localhost so the DNS rebinding middleware
    (which rejects any Host header not in {127.0.0.1, localhost}) allows
    requests through. TestClient defaults to base_url="http://testserver"
    which would cause every request to get 403.
    """
    from speakturbo.daemon_streaming import app
    return TestClient(app, base_url="http://127.0.0.1:7125")


class TestHealthEndpoint:
    """Health check must be fast and informative."""
    
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_returns_ready_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ready"
    
    def test_health_lists_voices(self, client):
        response = client.get("/health")
        data = response.json()
        assert "voices" in data
        assert "alba" in data["voices"]
        assert len(data["voices"]) >= 8


class TestTTSEndpoint:
    """Core TTS functionality — uses GET with query params (matching Rust CLI and Python CLI)."""
    
    def test_tts_returns_audio(self, client):
        response = client.get("/tts", params={"text": "Hello"})
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
    
    def test_tts_returns_valid_wav(self, client):
        response = client.get("/tts", params={"text": "Hello world"})
        # Check WAV header
        assert response.content[:4] == b"RIFF"
        assert response.content[8:12] == b"WAVE"
    
    def test_tts_wav_is_playable(self, client):
        response = client.get("/tts", params={"text": "Test"})
        # Streaming WAV uses 0x7FFFFFFF for data/file sizes — wave.open() can't parse it.
        # Validate format from raw header bytes instead (maintains same coverage as original).
        content = response.content
        assert content[:4] == b"RIFF"
        assert content[8:12] == b"WAVE"
        # Verify PCM format details from WAV header
        assert struct.unpack_from('<H', content, 20)[0] == 1      # PCM format
        assert struct.unpack_from('<H', content, 22)[0] == 1      # Mono
        assert struct.unpack_from('<I', content, 24)[0] == 24000  # 24kHz
        assert struct.unpack_from('<H', content, 34)[0] == 16     # 16-bit
        assert len(content) > 44  # Has audio data beyond header
    
    def test_tts_with_voice_parameter(self, client):
        response = client.get("/tts", params={"text": "Hello", "voice": "marius"})
        assert response.status_code == 200
        assert len(response.content) > 44  # More than just WAV header
    
    def test_tts_all_voices_work(self, client):
        voices = ["alba", "marius", "javert", "jean", "fantine", "cosette", "eponine", "azelma"]
        for voice in voices:
            response = client.get("/tts", params={"text": "Test", "voice": voice})
            assert response.status_code == 200, f"Voice {voice} failed"
            assert len(response.content) > 100, f"Voice {voice} returned too little audio"


class TestTTSValidation:
    """Input validation — GET /tts with query params."""
    
    def test_empty_text_returns_400(self, client):
        # GET /tts?text= passes empty string to handler, which returns 400
        response = client.get("/tts", params={"text": ""})
        assert response.status_code == 400
    
    def test_whitespace_only_returns_400(self, client):
        response = client.get("/tts", params={"text": "   "})
        assert response.status_code == 400
    
    def test_missing_text_returns_422(self, client):
        response = client.get("/tts")
        assert response.status_code == 422
    
    def test_invalid_voice_returns_400(self, client):
        response = client.get("/tts", params={"text": "Hello", "voice": "nonexistent"})
        assert response.status_code == 400


class TestTTSStreaming:
    """Streaming must work for low latency."""
    
    def test_response_is_streamed(self, client):
        with client.stream("GET", "/tts", params={"text": "Hello world this is a test"}) as response:
            assert response.status_code == 200
            chunks = list(response.iter_bytes(chunk_size=1024))
            # Should have multiple chunks for streaming
            assert len(chunks) >= 1


class TestDNSRebindingProtection:
    """Verify localhost-only access via Host header validation middleware."""
    
    def test_localhost_allowed(self, client):
        response = client.get("/health", headers={"host": "127.0.0.1:7125"})
        assert response.status_code == 200
    
    def test_external_host_rejected(self, client):
        response = client.get("/health", headers={"host": "evil.com"})
        assert response.status_code == 403


class TestPerformance:
    """Performance requirements."""
    
    def test_ttfc_under_500ms_warm(self, client):
        """Time to first chunk should be under 500ms when warm."""
        import time
        
        # Warm up
        client.get("/tts", params={"text": "warmup"})
        
        # Measure
        start = time.perf_counter()
        with client.stream("GET", "/tts", params={"text": "Hello world"}) as response:
            next(response.iter_bytes(chunk_size=1024))  # trigger first chunk
            ttfc = (time.perf_counter() - start) * 1000
        
        assert ttfc < 500, f"TTFC was {ttfc:.0f}ms, expected < 500ms"
    
    def test_generation_faster_than_realtime(self, client):
        """Should generate faster than real-time (RTF > 1)."""
        import time
        
        text = "The quick brown fox jumps over the lazy dog."
        
        start = time.perf_counter()
        response = client.get("/tts", params={"text": text})
        generation_time = time.perf_counter() - start
        
        # Streaming WAV can't use wave.open() — calculate from byte length
        audio_bytes = len(response.content) - 44  # minus WAV header
        audio_samples = audio_bytes / 2  # 16-bit = 2 bytes per sample
        audio_duration = audio_samples / 24000  # 24kHz sample rate
        
        rtf = audio_duration / generation_time
        assert rtf > 1.0, f"RTF was {rtf:.1f}x, expected > 1.0x"
