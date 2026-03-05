#!/usr/bin/env python3
"""
Scholar Research - Figure Extraction Module
Extracts graphs, tables, and scientific illustrations from PDFs
"""

import os
import re
from typing import Dict, List, Optional
import subprocess


class FigureExtractor:
    """Extracts figures, tables, and SIs from PDFs"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.supported_formats = [".pdf", ".png", ".jpg", ".jpeg"]
    
    def extract_from_pdf(self, pdf_path: str, output_dir: str = None) -> Dict:
        """Extract all figures from a PDF"""
        
        if not os.path.exists(pdf_path):
            return {"error": "PDF not found"}
        
        if output_dir is None:
            output_dir = os.path.splitext(pdf_path)[0] + "_figures"
        
        os.makedirs(output_dir, exist_ok=True)
        
        result = {
            "pdf_path": pdf_path,
            "output_dir": output_dir,
            "figures": [],
            "tables": [],
            "charts": []
        }
        
        # Use pdftotext to extract text (for captions)
        try:
            text = self._extract_text(pdf_path)
            result["captions"] = self._find_captions(text)
        except Exception as e:
            result["captions"] = []
        
        # Extract images using pdfimages or similar
        try:
            images = self._extract_images(pdf_path, output_dir)
            result["images"] = images
        except Exception as e:
            result["images"] = []
        
        # Classify each figure
        for img in result.get("images", []):
            fig_type = self._classify_figure(img["path"], img.get("caption", ""))
            if fig_type == "chart":
                result["charts"].append(img)
            else:
                result["figures"].append(img)
        
        return result
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            # Use pdftotext if available
            result = subprocess.run(
                ["pdftotext", pdf_path, "-"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout
        except FileNotFoundError:
            # Fallback - would use PyPDF2
            return ""
    
    def _find_captions(self, text: str) -> List[str]:
        """Find figure/table captions in text"""
        captions = []
        
        # Pattern for Figure X.X or Table X.X
        patterns = [
            r"Figure\s+\d+\.\d+[:\.\s]+([^\n]+)",
            r"Table\s+\d+\.\d+[:\.\s]+([^\n]+)",
            r"Fig\.\s*\d+[:\.\s]+([^\n]+)",
            r"Figure\s+\d+[:\.\s]+([^\n]+)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            captions.extend(matches)
        
        return captions[:20]  # Limit
    
    def _extract_images(self, pdf_path: str, output_dir: str) -> List[Dict]:
        """Extract images from PDF"""
        images = []
        
        try:
            # Try using pdfimages (Poppler)
            base_name = os.path.join(output_dir, "fig")
            subprocess.run(
                ["pdfimages", "-list", "-png", pdf_path, base_name],
                capture_output=True,
                timeout=30
            )
            
            # Check what was extracted
            for f in os.listdir(output_dir):
                if f.startswith("fig-") and f.endswith(".png"):
                    images.append({
                        "path": os.path.join(output_dir, f),
                        "type": "unknown",
                        "caption": ""
                    })
        
        except FileNotFoundError:
            # pdfimages not available
            pass
        
        return images
    
    def _classify_figure(self, image_path: str, caption: str = "") -> str:
        """Classify figure type based on caption and image analysis"""
        
        caption_lower = caption.lower()
        
        # Check caption keywords
        if any(kw in caption_lower for kw in ["table", "tab.", "tb."]):
            return "table"
        
        if any(kw in caption_lower for kw in ["figure", "fig.", "fig "]):
            return "figure"
        
        if any(kw in caption_lower for kw in ["graph", "plot", "chart", "bar", "line"]):
            return "chart"
        
        if any(kw in caption_lower for kw in ["photo", "image", "microscope", "fig"]):
            return "photo"
        
        # Would use image analysis in production
        return "figure"
    
    def analyze_figure(self, figure_path: str) -> Dict:
        """Analyze a figure using vision model"""
        
        if not os.path.exists(figure_path):
            return {"error": "Figure not found"}
        
        # Placeholder - would use vision model to describe
        return {
            "path": figure_path,
            "type": "unknown",
            "description": "Figure analysis would be performed by vision model",
            "data_points": [],
            "trends": [],
            "conclusions": []
        }


class PDFDownloader:
    """Downloads PDFs from various sources"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def download_pdf(self, paper: Dict, output_dir: str = None) -> Optional[str]:
        """Download PDF for a paper"""
        
        if output_dir is None:
            output_dir = "./downloads"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Get PDF URL
        pdf_url = paper.get("pdf_url", "")
        
        # Try different sources
        if not pdf_url:
            # Try arXiv
            arxiv_id = paper.get("arxiv_id", "")
            if arxiv_id:
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        if not pdf_url:
            # Try DOI
            doi = paper.get("doi", "")
            if doi:
                pdf_url = f"https://doi.org/{doi}"
        
        if not pdf_url:
            return None
        
        # Download
        try:
            import requests
            
            filename = self._sanitize_filename(paper.get("title", "paper")) + ".pdf"
            filepath = os.path.join(output_dir, filename)
            
            response = requests.get(pdf_url, timeout=60, stream=True)
            
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return filepath
        
        except Exception as e:
            print(f"Download error: {e}")
        
        return None
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename"""
        # Remove invalid characters
        name = re.sub(r'[<>:"/\\|?*]', "", name)
        name = name[:100]  # Limit length
        return name


if __name__ == "__main__":
    # Test
    extractor = FigureExtractor()
    
    # Would test with actual PDF
    print("Figure extraction module ready")
    print("Usage: python figure_extract.py <pdf_path>")
