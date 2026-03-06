# Integrator

"""整合輸出模組 - 將各區域的 OCR 結果整合成完整的 Markdown 文件"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

try:
    from .analyzer import PageAnalysis, Region, RegionType
except ImportError:
    from analyzer import PageAnalysis, Region, RegionType


class MarkdownIntegrator:
    """Markdown 整合器 - 將多個頁面/區域的結果整合成 Markdown"""
    
    def __init__(
        self,
        output_dir: str = "./output",
        save_images: bool = True,
        image_dir: str = "images"
    ):
        """
        初始化整合器。
        
        Args:
            output_dir: 輸出目錄
            save_images: 是否保存圖表區域的圖片
            image_dir: 圖片保存目錄
        """
        self.output_dir = Path(output_dir)
        self.save_images = save_images
        self.image_dir = self.output_dir / image_dir
        
        if save_images:
            self.image_dir.mkdir(parents=True, exist_ok=True)
    
    def integrate(
        self,
        analyses: List[PageAnalysis],
        output_path: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        整合所有頁面分析結果，生成完整的 Markdown 文件。
        
        Args:
            analyses: 頁面分析結果列表
            output_path: 輸出的 Markdown 檔案路徑
            metadata: 額外的中繼資料
            
        Returns:
            生成的 Markdown 內容
        """
        lines = []
        
        # 文件頭
        lines.append("# PDF 轉 Markdown 結果\n")
        
        # 中繼資料
        lines.append(f"**總頁數**: {len(analyses)}")
        if metadata:
            if "model" in metadata:
                lines.append(f"**模型**: {metadata['model']}")
            if "mode" in metadata:
                lines.append(f"**模式**: {metadata['mode']}")
            if "source" in metadata:
                lines.append(f"**來源**: {metadata['source']}")
            if "granularity" in metadata:
                lines.append(f"**粒度**: {metadata['granularity']}")
        lines.append(f"**生成時間**: {datetime.now().isoformat()}")
        lines.append("")
        lines.append("---\n")
        
        # 逐頁處理
        for analysis in analyses:
            lines.append(f"## 第 {analysis.page_number} 頁\n")
            
            # 如果有檢測到主要類型，加入標籤
            if analysis.detected_type:
                lines.append(f"*類型：{analysis.detected_type}*\n")
            
            # 處理每個區域
            for i, region in enumerate(analysis.regions):
                if len(analysis.regions) > 1:
                    # 多區域模式：加入區域標題
                    region_label = f"### 區域 {i+1} ({region.region_type.value})\n"
                    lines.append(region_label)
                
                if region.content:
                    lines.append(region.content)
                    lines.append("")
                
                # 如果是圖表區域且需要保存圖片
                if region.region_type == RegionType.FIGURE and self.save_images:
                    if region.image_path or True:  # 有圖片路徑或標記
                        img_name = f"page_{analysis.page_number}_region_{i+1}.png"
                        img_path = self.image_dir / img_name
                        
                        # 標記圖片位置（實際圖片在 OCR 時已保存）
                        lines.append(f"![圖表](./{self.image_dir.name}/{img_name})\n")
            
            lines.append("---\n")
        
        # 組合所有內容
        markdown_content = "\n".join(lines)
        
        # 寫入檔案
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return markdown_content
    
    def integrate_simple(
        self,
        analyses: List[PageAnalysis],
        output_path: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        簡化版整合：只輸出文字內容，不處理圖片。
        """
        lines = []
        
        # 文件頭
        lines.append("# PDF 轉 Markdown 結果\n")
        lines.append(f"**總頁數**: {len(analyses)}\n")
        
        if metadata:
            for key, value in metadata.items():
                lines.append(f"**{key}**: {value}\n")
        
        lines.append(f"**生成時間**: {datetime.now().isoformat()}\n")
        lines.append("")
        lines.append("---\n")
        
        # 逐頁處理
        for analysis in analyses:
            lines.append(f"## 第 {analysis.page_number} 頁\n")
            
            if analysis.detected_type:
                lines.append(f"*類型：{analysis.detected_type}*\n")
            
            for region in analysis.regions:
                if region.content:
                    lines.append(region.content)
                    lines.append("")
            
            lines.append("---\n")
        
        markdown_content = "\n".join(lines)
        
        # 寫入檔案
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return markdown_content


def assemble_markdown(
    analyses: List[PageAnalysis],
    output_path: str,
    metadata: Optional[Dict] = None,
    simple_mode: bool = False
) -> str:
    """
    便捷函數：將頁面分析結果組合成 Markdown 文件。
    
    Args:
        analyses: 頁面分析結果列表
        output_path: 輸出的 Markdown 檔案路徑
        metadata: 額外的中繼資料
        simple_mode: 是否使用簡化模式
        
    Returns:
        生成的 Markdown 內容
    """
    integrator = MarkdownIntegrator(save_images=not simple_mode)
    
    if simple_mode:
        return integrator.integrate_simple(analyses, output_path, metadata)
    else:
        return integrator.integrate(analyses, output_path, metadata)
