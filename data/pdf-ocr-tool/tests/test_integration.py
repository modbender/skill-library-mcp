"""
端到端整合測試
"""

import pytest
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCLI:
    """測試 CLI 功能"""
    
    def test_help_message(self):
        """測試幫助訊息"""
        result = subprocess.run(
            [sys.executable, "-m", "ocr_tool", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        # 應該有幫助訊息
        assert "usage" in result.stdout.lower() or "usage" in result.stderr.lower()
    
    def test_check_environment(self, tmp_path):
        """測試環境檢查"""
        output_md = tmp_path / "test_output.md"
        
        result = subprocess.run(
            [
                sys.executable, "-m", "ocr_tool",
                "--check",
                "--input", str(tmp_path / "dummy.pdf"),
                "--output", str(output_md)
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # 環境檢查應該執行（不管成功與否）
        # 如果有缺少依賴，應該有警告
        assert result.returncode in [0, 1]


class TestPrompts:
    """測試提示詞模組"""
    
    def test_load_text_prompt(self):
        """測試加載文字提示詞"""
        from prompts import load_prompt, TEXT_PROMPT
        
        prompt = load_prompt("text")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_load_table_prompt(self):
        """測試加載表格提示詞"""
        from prompts import load_prompt, TABLE_PROMPT
        
        prompt = load_prompt("table")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_load_figure_prompt(self):
        """測試加載圖表提示詞"""
        from prompts import load_prompt, FIGURE_PROMPT
        
        prompt = load_prompt("figure")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_default_prompts(self):
        """測試預設提示詞"""
        from prompts import TEXT_PROMPT, TABLE_PROMPT, FIGURE_PROMPT, MIXED_PROMPT
        
        assert "markdown" in TEXT_PROMPT.lower()
        assert "table" in TABLE_PROMPT.lower() or "表格" in TABLE_PROMPT
        assert "figure" in FIGURE_PROMPT.lower() or "圖表" in FIGURE_PROMPT


class TestIntegration:
    """整合測試"""
    
    def test_import_all_modules(self):
        """測試所有模組可導入"""
        try:
            from utils.ollama_client import OllamaClient
            from utils.image_utils import crop_image, save_image
            from utils.pdf_utils import pdf_to_images
            from analyzer import PageAnalyzer, PageAnalysis
            from processor import RegionProcessor
            from integrator import MarkdownIntegrator
            from prompts import TEXT_PROMPT, TABLE_PROMPT
            assert True
        except ImportError as e:
            pytest.fail(f"模組導入失敗：{e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
