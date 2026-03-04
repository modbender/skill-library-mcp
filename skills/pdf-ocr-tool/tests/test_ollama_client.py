"""
測試 Ollama 客戶端模組
"""

import pytest
import sys
from pathlib import Path

# 加入上層目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ollama_client import OllamaClient


class TestOllamaClient:
    """測試 OllamaClient 類別"""
    
    def test_init_default(self):
        """測試預設初始化"""
        client = OllamaClient()
        assert client.host == "localhost"
        assert client.port == "11434"
        assert client.model == "glm-ocr:q8_0"
        assert client.base_url == "http://localhost:11434"
    
    def test_init_custom(self):
        """測試自訂初始化"""
        client = OllamaClient(
            host="192.168.1.100",
            port="11435",
            model="test-model",
            timeout=60,
            max_retries=5
        )
        assert client.host == "192.168.1.100"
        assert client.port == "11435"
        assert client.model == "test-model"
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.base_url == "http://192.168.1.100:11435"
    
    def test_check_status(self):
        """測試服務狀態檢查（需要 Ollama 服務運行）"""
        client = OllamaClient()
        ok, errors = client.check_status()
        
        # 如果有 Ollama 服務運行，應該成功
        if ok:
            assert len(errors) == 0
        else:
            assert len(errors) > 0
    
    def test_encode_image_to_base64(self, tmp_path):
        """測試圖片編碼"""
        # 建立測試圖片
        test_img = tmp_path / "test.png"
        test_img.write_bytes(b"fake_image_data")
        
        result = OllamaClient.encode_image_to_base64(str(test_img))
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_no_image(self):
        """測試不含圖片的生成（需要 Ollama 服務）"""
        client = OllamaClient()
        # 測試基本生成（不含圖片）
        result = client.generate(
            prompt="Say hello",
            stream=False
        )
        # 如果有服務，應該有回應
        # 如果沒服務，會是錯誤訊息
        assert isinstance(result, (str, type(None)))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
