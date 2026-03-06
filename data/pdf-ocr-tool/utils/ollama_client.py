# Ollama Client

"""Ollama API 客戶端，提供 OCR 識別功能。"""

import base64
import requests
import time
from typing import Optional, List
from pathlib import Path


class OllamaClient:
    """Ollama API 客戶端，支援超時、重試機制。"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: str = "11434",
        model: str = "glm-ocr:q8_0",
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        初始化 Ollama 客戶端。
        
        Args:
            host: Ollama 主機位置
            port: Ollama 端口
            model: 預設使用的模型
            timeout: 請求超時時間（秒）
            max_retries: 最大重試次數
            retry_delay: 重試延遲時間（秒）
        """
        self.host = host
        self.port = port
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.base_url = f"http://{host}:{port}"
    
    def check_status(self) -> tuple[bool, List[str]]:
        """
        檢查 Ollama 服務狀態。
        
        Returns:
            (是否成功，錯誤訊息列表)
        """
        errors = []
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                model_names = [m["name"] for m in models]
                
                if not any(self.model.split(":")[0] in m for m in model_names):
                    errors.append(f"⚠️ 模型 {self.model} 未安裝")
                    errors.append(f"   執行：ollama pull {self.model}")
                
                return True, errors
            else:
                errors.append(f"❌ Ollama 服務異常：{resp.status_code}")
                return False, errors
        except Exception as e:
            errors.append(f"❌ 無法連接 Ollama 服務 ({self.base_url}): {e}")
            return False, errors
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """
        將圖片編碼為 base64。
        
        Args:
            image_path: 圖片路徑
            
        Returns:
            base64 編碼的字串
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def generate(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        model: Optional[str] = None,
        stream: bool = False
    ) -> Optional[str]:
        """
        調用 Ollama API 生成回應。
        
        Args:
            prompt: 提示詞
            image_path: 圖片路徑（可選）
            model: 使用的模型（可選，預設為實例模型）
            stream: 是否使用流式傳輸
            
        Returns:
            生成的文字內容，失敗時返回 None
        """
        model = model or self.model
        
        # 準備請求負載
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        
        # 如果有圖片，加入圖片數據
        if image_path:
            try:
                image_base64 = self.encode_image_to_base64(image_path)
                payload["images"] = [image_base64]
            except Exception as e:
                return f"❌ 無法讀取圖片：{e}"
        
        # 發送請求（含重試機制）
        last_error = None
        for attempt in range(self.max_retries):
            try:
                resp = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("done"):
                        return result.get("response", "")
                    else:
                        return "❌ OCR 未完成"
                else:
                    last_error = f"API 錯誤：{resp.status_code} - {resp.text[:200]}"
                    
            except requests.exceptions.Timeout:
                last_error = f"請求超時（第 {attempt + 1}/{self.max_retries} 次）"
            except requests.exceptions.RequestException as e:
                last_error = f"請求失敗：{e}"
            except Exception as e:
                last_error = f"發生意外錯誤：{e}"
            
            # 重試延遲
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return f"❌ {last_error}"
    
    def ocr_image(
        self,
        image_path: str,
        prompt: str,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        對圖片進行 OCR 識別。
        
        Args:
            image_path: 圖片路徑
            prompt: 提示詞
            model: 使用的模型（可選）
            
        Returns:
            OCR 識別結果
        """
        return self.generate(prompt=prompt, image_path=image_path, model=model)
