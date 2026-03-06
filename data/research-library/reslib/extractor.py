"""
Document Extraction Pipeline for Research Library

Extracts text and metadata from PDFs, images, and code files with
confidence scoring for search quality assessment.

Author: Research Library System
Version: 1.0.0
"""

import ast
import hashlib
import logging
import mimetypes
import os
import re
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# Constants and Configuration
# ============================================================================

EXTRACTION_TIMEOUT_SECONDS = 300  # 5 minutes max per extraction

# File extension mappings
PDF_EXTENSIONS = {'.pdf'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
CODE_EXTENSIONS = {
    '.py': 'python',
    '.pyw': 'python',
    '.cpp': 'cpp',
    '.cxx': 'cpp',
    '.cc': 'cpp',
    '.c': 'c',
    '.h': 'c_header',
    '.hpp': 'cpp_header',
    '.hxx': 'cpp_header',
    '.ino': 'arduino',
    '.gcode': 'gcode',
    '.gnd': 'gcode',
    '.nc': 'gcode',
    '.ngc': 'gcode',
    '.tap': 'gcode',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.rs': 'rust',
    '.go': 'go',
    '.rb': 'ruby',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.sql': 'sql',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.xml': 'xml',
    '.html': 'html',
    '.css': 'css',
    '.md': 'markdown',
    '.txt': 'text',
    '.scad': 'openscad',
    '.kicad_pcb': 'kicad',
    '.kicad_sch': 'kicad',
}

# Confidence score constants
class ConfidenceScores:
    """Standard confidence scores for extraction quality."""
    TEXT_PDF = 1.0
    SCANNED_PDF_CLEAR = 0.85
    SCANNED_PDF_POOR = 0.4
    IMAGE_CLEAR = 0.8
    IMAGE_HANDWRITING = 0.3
    IMAGE_NO_OCR = 0.2  # EXIF only
    CODE_DETECTED = 1.0
    CODE_UNKNOWN = 0.7
    FALLBACK_FILENAME = 0.1
    EXTRACTION_FAILED = 0.05


# ============================================================================
# Data Classes
# ============================================================================

class FileType(Enum):
    """Enumeration of supported file types."""
    PDF = "pdf"
    IMAGE = "image"
    CODE = "code"
    UNKNOWN = "unknown"


@dataclass
class ExtractionResult:
    """Result of document extraction."""
    text: str
    confidence: float
    file_type: FileType
    language: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_time_ms: float = 0.0
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if extraction was successful."""
        return self.error is None and len(self.text) > 0
    
    @property
    def word_count(self) -> int:
        """Count words in extracted text."""
        return len(self.text.split())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'text': self.text,
            'confidence': self.confidence,
            'file_type': self.file_type.value,
            'language': self.language,
            'metadata': self.metadata,
            'extraction_time_ms': self.extraction_time_ms,
            'warnings': self.warnings,
            'error': self.error,
            'word_count': self.word_count,
        }


@dataclass
class PDFPage:
    """Represents a single PDF page extraction result."""
    page_num: int
    text: str
    has_images: bool
    char_count: int
    confidence: float


@dataclass
class CodeFunction:
    """Represents an extracted function from code."""
    name: str
    signature: str
    docstring: Optional[str]
    line_start: int
    line_end: int
    decorators: List[str] = field(default_factory=list)


@dataclass
class CodeClass:
    """Represents an extracted class from code."""
    name: str
    docstring: Optional[str]
    line_start: int
    line_end: int
    methods: List[CodeFunction] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)


# ============================================================================
# Timeout Handler
# ============================================================================

class TimeoutError(Exception):
    """Raised when extraction times out."""
    pass


class TimeoutHandler:
    """Context manager for extraction timeout."""
    
    def __init__(self, seconds: int, operation: str = "extraction"):
        self.seconds = seconds
        self.operation = operation
        self._old_handler = None
    
    def _timeout_handler(self, signum, frame):
        raise TimeoutError(f"{self.operation} timed out after {self.seconds} seconds")
    
    def __enter__(self):
        # Only set alarm on Unix systems
        if hasattr(signal, 'SIGALRM'):
            self._old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(self.seconds)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
            if self._old_handler is not None:
                signal.signal(signal.SIGALRM, self._old_handler)
        return False


# ============================================================================
# PDF Extractor
# ============================================================================

class PDFExtractor:
    """Extract text from PDF documents."""
    
    def __init__(self):
        self._pdfplumber = None
        self._tesseract_available = None
    
    @property
    def pdfplumber(self):
        """Lazy load pdfplumber."""
        if self._pdfplumber is None:
            try:
                import pdfplumber
                self._pdfplumber = pdfplumber
            except ImportError:
                raise ImportError("pdfplumber is required for PDF extraction. Install with: pip install pdfplumber")
        return self._pdfplumber
    
    @property
    def tesseract_available(self) -> bool:
        """Check if tesseract OCR is available."""
        if self._tesseract_available is None:
            try:
                import pytesseract
                # Try to get version to verify it's working
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
            except Exception:
                self._tesseract_available = False
        return self._tesseract_available
    
    def extract(self, path: Union[str, Path]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Extract text from a PDF file.
        
        Args:
            path: Path to the PDF file
            
        Returns:
            Tuple of (text, confidence, metadata)
        """
        path = Path(path)
        metadata = {
            'filename': path.name,
            'file_size': path.stat().st_size if path.exists() else 0,
            'pages': 0,
            'has_images': False,
            'extraction_method': 'text',
        }
        
        all_text = []
        pages_data: List[PDFPage] = []
        total_chars = 0
        total_images = 0
        confidence_scores = []
        
        try:
            with self.pdfplumber.open(str(path)) as pdf:
                metadata['pages'] = len(pdf.pages)
                metadata['pdf_info'] = pdf.metadata or {}
                
                for i, page in enumerate(pdf.pages):
                    page_num = i + 1
                    
                    # Extract text
                    text = page.extract_text() or ""
                    char_count = len(text.strip())
                    
                    # Check for images on this page
                    images = page.images if hasattr(page, 'images') else []
                    has_images = len(images) > 0
                    total_images += len(images)
                    
                    # Determine confidence for this page
                    if char_count > 50:
                        # Good text extraction
                        page_confidence = ConfidenceScores.TEXT_PDF
                    elif has_images and char_count < 20:
                        # Likely scanned page - try OCR if available
                        if self.tesseract_available:
                            ocr_text = self._ocr_page(page)
                            if ocr_text:
                                text = ocr_text
                                char_count = len(text.strip())
                                metadata['extraction_method'] = 'ocr'
                                page_confidence = self._estimate_ocr_confidence(ocr_text)
                            else:
                                page_confidence = ConfidenceScores.SCANNED_PDF_POOR
                        else:
                            page_confidence = ConfidenceScores.SCANNED_PDF_POOR
                    else:
                        page_confidence = ConfidenceScores.TEXT_PDF if char_count > 0 else 0.0
                    
                    pages_data.append(PDFPage(
                        page_num=page_num,
                        text=text,
                        has_images=has_images,
                        char_count=char_count,
                        confidence=page_confidence,
                    ))
                    
                    if text.strip():
                        all_text.append(f"[Page {page_num}]\n{text.strip()}")
                        confidence_scores.append(page_confidence)
                    
                    total_chars += char_count
                
                metadata['has_images'] = total_images > 0
                metadata['total_images'] = total_images
                metadata['total_chars'] = total_chars
        
        except Exception as e:
            logger.error(f"PDF extraction failed for {path}: {e}")
            raise
        
        # Calculate overall confidence (weighted average by char count)
        if confidence_scores:
            confidence = sum(confidence_scores) / len(confidence_scores)
        else:
            confidence = ConfidenceScores.EXTRACTION_FAILED
        
        full_text = "\n\n".join(all_text)
        return full_text, confidence, metadata
    
    def _ocr_page(self, page) -> Optional[str]:
        """Perform OCR on a PDF page image."""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            # Render page to image
            img = page.to_image(resolution=300)
            
            # Convert to PIL Image
            pil_img = img.original
            
            # Run OCR
            text = pytesseract.image_to_string(pil_img)
            return text.strip() if text else None
            
        except Exception as e:
            logger.warning(f"OCR failed for page: {e}")
            return None
    
    def _estimate_ocr_confidence(self, text: str) -> float:
        """
        Estimate OCR confidence based on text quality indicators.
        
        Heuristics:
        - Ratio of alphanumeric to total characters
        - Average word length
        - Presence of common words
        """
        if not text:
            return ConfidenceScores.SCANNED_PDF_POOR
        
        # Calculate alphanumeric ratio
        alpha_count = sum(1 for c in text if c.isalnum())
        total_count = len(text)
        alpha_ratio = alpha_count / total_count if total_count > 0 else 0
        
        # Check word statistics
        words = text.split()
        if not words:
            return ConfidenceScores.SCANNED_PDF_POOR
        
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        # Common English words as quality indicator
        common_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'it', 'on'}
        common_count = sum(1 for w in words if w.lower() in common_words)
        common_ratio = common_count / len(words)
        
        # Score calculation
        score = 0.0
        
        # Alphanumeric ratio (0.3 weight)
        if alpha_ratio > 0.7:
            score += 0.3
        elif alpha_ratio > 0.5:
            score += 0.2
        else:
            score += 0.1
        
        # Word length (0.3 weight)
        if 3 <= avg_word_length <= 8:
            score += 0.3
        elif 2 <= avg_word_length <= 12:
            score += 0.2
        else:
            score += 0.1
        
        # Common words (0.4 weight)
        if common_ratio > 0.1:
            score += 0.4
        elif common_ratio > 0.05:
            score += 0.3
        else:
            score += 0.15
        
        # Map to confidence range [0.4, 0.85]
        return ConfidenceScores.SCANNED_PDF_POOR + score * (ConfidenceScores.SCANNED_PDF_CLEAR - ConfidenceScores.SCANNED_PDF_POOR)


# ============================================================================
# Image Extractor
# ============================================================================

class ImageExtractor:
    """Extract text and metadata from images."""
    
    def __init__(self):
        self._tesseract_available = None
        self._pil_available = None
    
    @property
    def pil_available(self) -> bool:
        """Check if PIL is available."""
        if self._pil_available is None:
            try:
                from PIL import Image, ExifTags
                self._pil_available = True
            except ImportError:
                self._pil_available = False
        return self._pil_available
    
    @property
    def tesseract_available(self) -> bool:
        """Check if tesseract OCR is available."""
        if self._tesseract_available is None:
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
            except Exception:
                self._tesseract_available = False
        return self._tesseract_available
    
    def extract(self, path: Union[str, Path]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Extract text and metadata from an image file.
        
        Args:
            path: Path to the image file
            
        Returns:
            Tuple of (text, confidence, metadata)
        """
        path = Path(path)
        metadata = {
            'filename': path.name,
            'file_size': path.stat().st_size if path.exists() else 0,
            'extraction_method': 'none',
        }
        
        text_parts = []
        confidence = ConfidenceScores.IMAGE_NO_OCR
        
        # Always try to extract EXIF data
        exif_data = self._extract_exif(path)
        if exif_data:
            metadata['exif'] = exif_data
            
            # Add EXIF text content
            exif_text = self._exif_to_text(exif_data)
            if exif_text:
                text_parts.append(f"[Image Metadata]\n{exif_text}")
        
        # Get image dimensions
        if self.pil_available:
            try:
                from PIL import Image
                with Image.open(path) as img:
                    metadata['width'] = img.width
                    metadata['height'] = img.height
                    metadata['mode'] = img.mode
                    metadata['format'] = img.format
            except Exception as e:
                logger.warning(f"Could not read image info: {e}")
        
        # Try OCR if available
        if self.tesseract_available:
            try:
                ocr_text, ocr_confidence = self._ocr_image(path)
                if ocr_text:
                    text_parts.append(f"[OCR Text]\n{ocr_text}")
                    confidence = ocr_confidence
                    metadata['extraction_method'] = 'ocr'
            except Exception as e:
                logger.warning(f"OCR failed for {path}: {e}")
                metadata['ocr_error'] = str(e)
        else:
            metadata['extraction_method'] = 'exif_only'
        
        # Always include filename as fallback context
        text_parts.insert(0, f"[File: {path.name}]")
        
        full_text = "\n\n".join(text_parts)
        return full_text, confidence, metadata
    
    def _extract_exif(self, path: Path) -> Dict[str, Any]:
        """Extract EXIF metadata from image."""
        exif_data = {}
        
        if not self.pil_available:
            return exif_data
        
        try:
            from PIL import Image, ExifTags
            
            with Image.open(path) as img:
                exif_raw = img._getexif()
                if exif_raw:
                    for tag_id, value in exif_raw.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        
                        # Convert bytes to string if needed
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except Exception:
                                value = str(value)
                        
                        # Skip very long values
                        if isinstance(value, str) and len(value) > 500:
                            continue
                        
                        exif_data[tag] = value
        
        except Exception as e:
            logger.debug(f"EXIF extraction failed: {e}")
        
        return exif_data
    
    def _exif_to_text(self, exif_data: Dict[str, Any]) -> str:
        """Convert EXIF data to searchable text."""
        interesting_tags = [
            'ImageDescription', 'Make', 'Model', 'Software',
            'DateTime', 'DateTimeOriginal', 'Artist', 'Copyright',
            'GPSInfo', 'LensModel', 'CameraOwnerName', 'BodySerialNumber',
            'XPTitle', 'XPComment', 'XPAuthor', 'XPKeywords', 'XPSubject',
        ]
        
        text_parts = []
        for tag in interesting_tags:
            if tag in exif_data:
                value = exif_data[tag]
                if value:
                    text_parts.append(f"{tag}: {value}")
        
        return "\n".join(text_parts)
    
    def _ocr_image(self, path: Path) -> Tuple[str, float]:
        """Perform OCR on an image and estimate confidence."""
        import pytesseract
        from PIL import Image
        
        with Image.open(path) as img:
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            # Extract text
            text = pytesseract.image_to_string(img)
            
            # Calculate confidence from OCR data
            confidences = [
                int(c) for c in ocr_data['conf'] 
                if c != '-1' and str(c).isdigit()
            ]
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences) / 100.0
            else:
                avg_confidence = 0.5
            
            # Adjust based on text characteristics
            confidence = self._adjust_ocr_confidence(text, avg_confidence)
            
            return text.strip(), confidence
    
    def _adjust_ocr_confidence(self, text: str, base_confidence: float) -> float:
        """
        Adjust OCR confidence based on text quality.
        
        Detects potential handwriting or low-quality scans.
        """
        if not text:
            return ConfidenceScores.EXTRACTION_FAILED
        
        # Check for gibberish indicators
        words = text.split()
        if not words:
            return ConfidenceScores.EXTRACTION_FAILED
        
        # Calculate metrics
        avg_word_len = sum(len(w) for w in words) / len(words)
        
        # Too many very short or very long "words" = likely noise
        short_words = sum(1 for w in words if len(w) <= 1)
        long_words = sum(1 for w in words if len(w) > 20)
        noise_ratio = (short_words + long_words) / len(words)
        
        # Special character ratio
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        special_ratio = special_chars / len(text) if text else 0
        
        # Adjust confidence
        adjusted = base_confidence
        
        if noise_ratio > 0.5:
            adjusted *= 0.5  # Lots of noise
        elif noise_ratio > 0.3:
            adjusted *= 0.7
        
        if special_ratio > 0.3:
            adjusted *= 0.6  # Too many special characters
        
        # Map to our confidence ranges
        if adjusted > 0.7:
            return ConfidenceScores.IMAGE_CLEAR
        elif adjusted > 0.4:
            return (ConfidenceScores.IMAGE_CLEAR + ConfidenceScores.IMAGE_HANDWRITING) / 2
        else:
            return ConfidenceScores.IMAGE_HANDWRITING


# ============================================================================
# Code Extractor
# ============================================================================

class CodeExtractor:
    """Extract structured information from source code files."""
    
    # Language-specific comment patterns
    COMMENT_PATTERNS = {
        'python': (r'#\s*(.+)$', r'"""([\s\S]*?)"""', r"'''([\s\S]*?)'''"),
        'cpp': (r'//\s*(.+)$', r'/\*[\s\S]*?\*/'),
        'c': (r'//\s*(.+)$', r'/\*[\s\S]*?\*/'),
        'javascript': (r'//\s*(.+)$', r'/\*[\s\S]*?\*/'),
        'java': (r'//\s*(.+)$', r'/\*[\s\S]*?\*/'),
        'rust': (r'//\s*(.+)$', r'/\*[\s\S]*?\*/'),
        'go': (r'//\s*(.+)$', r'/\*[\s\S]*?\*/'),
        'shell': (r'#\s*(.+)$',),
        'ruby': (r'#\s*(.+)$', r'=begin([\s\S]*?)=end'),
        'gcode': (r';\s*(.+)$', r'\(([^)]+)\)'),
    }
    
    # Function/method patterns for different languages
    FUNCTION_PATTERNS = {
        'cpp': r'(?:[\w:]+\s+)*(\w+)\s*\([^)]*\)\s*(?:const\s*)?(?:override\s*)?(?:final\s*)?[{;]',
        'c': r'(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*[{;]',
        'javascript': r'(?:function\s+(\w+)|(\w+)\s*[:=]\s*(?:async\s+)?function|\bconst\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)',
        'java': r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+)?\s*{',
        'rust': r'fn\s+(\w+)',
        'go': r'func\s+(?:\([^)]+\)\s*)?(\w+)',
    }
    
    # G-code command descriptions
    GCODE_COMMANDS = {
        'G0': 'Rapid positioning',
        'G1': 'Linear interpolation',
        'G2': 'Circular interpolation CW',
        'G3': 'Circular interpolation CCW',
        'G4': 'Dwell',
        'G17': 'XY plane selection',
        'G18': 'XZ plane selection',
        'G19': 'YZ plane selection',
        'G20': 'Inch units',
        'G21': 'Millimeter units',
        'G28': 'Return to home',
        'G90': 'Absolute positioning',
        'G91': 'Relative positioning',
        'M0': 'Program stop',
        'M1': 'Optional stop',
        'M2': 'Program end',
        'M3': 'Spindle on CW',
        'M4': 'Spindle on CCW',
        'M5': 'Spindle off',
        'M6': 'Tool change',
        'M8': 'Coolant on',
        'M9': 'Coolant off',
        'M30': 'Program end and reset',
    }
    
    def extract(self, path: Union[str, Path]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Extract structured information from a code file.
        
        Args:
            path: Path to the code file
            
        Returns:
            Tuple of (text, confidence, metadata)
        """
        path = Path(path)
        
        # Detect language
        ext = path.suffix.lower()
        language = CODE_EXTENSIONS.get(ext, 'unknown')
        
        metadata = {
            'filename': path.name,
            'file_size': path.stat().st_size if path.exists() else 0,
            'language': language,
            'extension': ext,
        }
        
        try:
            content = path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            logger.error(f"Failed to read code file {path}: {e}")
            return f"[File: {path.name}]", ConfidenceScores.FALLBACK_FILENAME, metadata
        
        metadata['line_count'] = content.count('\n') + 1
        metadata['char_count'] = len(content)
        
        # Route to appropriate extractor
        if language == 'python':
            text, confidence, extra_meta = self._extract_python(content, path)
        elif language == 'gcode':
            text, confidence, extra_meta = self._extract_gcode(content, path)
        elif language in ('cpp', 'c', 'c_header', 'cpp_header', 'arduino'):
            text, confidence, extra_meta = self._extract_cpp(content, path, language)
        elif language in self.FUNCTION_PATTERNS:
            text, confidence, extra_meta = self._extract_generic(content, path, language)
        else:
            text, confidence, extra_meta = self._extract_plain(content, path)
        
        metadata.update(extra_meta)
        return text, confidence, metadata
    
    def _extract_python(self, content: str, path: Path) -> Tuple[str, float, Dict[str, Any]]:
        """Extract structured information from Python code using AST."""
        metadata = {'extraction_method': 'ast'}
        text_parts = [f"[Python File: {path.name}]"]
        
        try:
            tree = ast.parse(content)
            
            # Extract module docstring
            module_doc = ast.get_docstring(tree)
            if module_doc:
                text_parts.append(f"\n[Module Docstring]\n{module_doc}")
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            if imports:
                metadata['imports'] = imports
                text_parts.append(f"\n[Imports]\n" + "\n".join(f"- {imp}" for imp in imports[:20]))
            
            # Extract classes
            classes = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    cls = self._extract_python_class(node)
                    classes.append(cls)
            
            if classes:
                metadata['classes'] = [c.name for c in classes]
                text_parts.append("\n[Classes]")
                for cls in classes:
                    cls_text = f"\nclass {cls.name}"
                    if cls.bases:
                        cls_text += f"({', '.join(cls.bases)})"
                    if cls.docstring:
                        cls_text += f"\n  \"\"\"{cls.docstring}\"\"\""
                    for method in cls.methods:
                        cls_text += f"\n  def {method.signature}"
                        if method.docstring:
                            cls_text += f"\n    \"\"\"{method.docstring}\"\"\""
                    text_parts.append(cls_text)
            
            # Extract top-level functions
            functions = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func = self._extract_python_function(node)
                    functions.append(func)
            
            if functions:
                metadata['functions'] = [f.name for f in functions]
                text_parts.append("\n[Functions]")
                for func in functions:
                    func_text = f"\ndef {func.signature}"
                    if func.decorators:
                        func_text = "\n".join(f"@{d}" for d in func.decorators) + "\n" + func_text
                    if func.docstring:
                        func_text += f"\n  \"\"\"{func.docstring}\"\"\""
                    text_parts.append(func_text)
            
            # Extract comments (not captured by AST)
            comments = self._extract_comments(content, 'python')
            if comments:
                text_parts.append(f"\n[Comments]\n" + "\n".join(comments[:30]))
            
            confidence = ConfidenceScores.CODE_DETECTED
            
        except SyntaxError as e:
            logger.warning(f"Python syntax error in {path}: {e}")
            metadata['extraction_method'] = 'fallback'
            metadata['syntax_error'] = str(e)
            
            # Fall back to regex extraction
            text_parts.append("\n[Note: Syntax error, using fallback extraction]")
            functions = self._extract_functions_regex(content, 'python')
            if functions:
                text_parts.append("\n[Functions (regex)]\n" + "\n".join(functions))
            
            comments = self._extract_comments(content, 'python')
            if comments:
                text_parts.append(f"\n[Comments]\n" + "\n".join(comments[:30]))
            
            text_parts.append(f"\n[Raw Content]\n{content[:5000]}")
            confidence = ConfidenceScores.CODE_UNKNOWN
        
        return "\n".join(text_parts), confidence, metadata
    
    def _extract_python_function(self, node: ast.FunctionDef) -> CodeFunction:
        """Extract function information from AST node."""
        # Build signature
        args = []
        
        # Regular arguments
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        
        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        
        signature = f"{node.name}({', '.join(args)})"
        
        # Return type
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"
        
        # Decorators
        decorators = [ast.unparse(d) for d in node.decorator_list]
        
        return CodeFunction(
            name=node.name,
            signature=signature,
            docstring=ast.get_docstring(node),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            decorators=decorators,
        )
    
    def _extract_python_class(self, node: ast.ClassDef) -> CodeClass:
        """Extract class information from AST node."""
        bases = [ast.unparse(b) for b in node.bases]
        
        methods = []
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_python_function(child))
        
        return CodeClass(
            name=node.name,
            docstring=ast.get_docstring(node),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods=methods,
            bases=bases,
        )
    
    def _extract_gcode(self, content: str, path: Path) -> Tuple[str, float, Dict[str, Any]]:
        """Extract information from G-code files."""
        metadata = {'extraction_method': 'gcode_parser'}
        text_parts = [f"[G-Code File: {path.name}]"]
        
        lines = content.split('\n')
        
        # Extract commands used
        commands_used = {}
        coordinates = {'X': [], 'Y': [], 'Z': []}
        feedrates = []
        spindle_speeds = []
        comments = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract comments
            if line.startswith(';'):
                comments.append(line[1:].strip())
                continue
            
            # Extract inline comments
            if '(' in line:
                comment_match = re.search(r'\(([^)]+)\)', line)
                if comment_match:
                    comments.append(comment_match.group(1))
            
            # Extract G/M codes
            for match in re.finditer(r'([GM])(\d+)', line, re.IGNORECASE):
                code = f"{match.group(1).upper()}{match.group(2)}"
                commands_used[code] = commands_used.get(code, 0) + 1
            
            # Extract coordinates
            for axis in ['X', 'Y', 'Z']:
                match = re.search(rf'{axis}([-\d.]+)', line, re.IGNORECASE)
                if match:
                    try:
                        coordinates[axis].append(float(match.group(1)))
                    except ValueError:
                        pass
            
            # Extract feedrate
            f_match = re.search(r'F([\d.]+)', line, re.IGNORECASE)
            if f_match:
                try:
                    feedrates.append(float(f_match.group(1)))
                except ValueError:
                    pass
            
            # Extract spindle speed
            s_match = re.search(r'S([\d.]+)', line, re.IGNORECASE)
            if s_match:
                try:
                    spindle_speeds.append(float(s_match.group(1)))
                except ValueError:
                    pass
        
        # Build summary
        metadata['commands'] = commands_used
        metadata['command_count'] = sum(commands_used.values())
        
        # Commands summary
        text_parts.append("\n[Commands Used]")
        for code, count in sorted(commands_used.items()):
            desc = self.GCODE_COMMANDS.get(code, 'Unknown')
            text_parts.append(f"  {code}: {desc} (×{count})")
        
        # Work envelope
        if any(coordinates.values()):
            text_parts.append("\n[Work Envelope]")
            for axis, values in coordinates.items():
                if values:
                    text_parts.append(f"  {axis}: {min(values):.3f} to {max(values):.3f}")
                    metadata[f'{axis.lower()}_min'] = min(values)
                    metadata[f'{axis.lower()}_max'] = max(values)
        
        # Feed/Speed info
        if feedrates:
            text_parts.append(f"\n[Feed Rates]\n  Range: {min(feedrates):.1f} - {max(feedrates):.1f}")
            metadata['feedrate_range'] = (min(feedrates), max(feedrates))
        
        if spindle_speeds:
            text_parts.append(f"\n[Spindle Speeds]\n  Range: {min(spindle_speeds):.0f} - {max(spindle_speeds):.0f} RPM")
            metadata['spindle_range'] = (min(spindle_speeds), max(spindle_speeds))
        
        # Comments
        if comments:
            text_parts.append(f"\n[Comments]\n" + "\n".join(f"  {c}" for c in comments[:30]))
        
        return "\n".join(text_parts), ConfidenceScores.CODE_DETECTED, metadata
    
    def _extract_cpp(self, content: str, path: Path, language: str) -> Tuple[str, float, Dict[str, Any]]:
        """Extract information from C/C++/Arduino code."""
        metadata = {'extraction_method': 'regex'}
        text_parts = [f"[{language.upper()} File: {path.name}]"]
        
        # Extract includes
        includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
        if includes:
            metadata['includes'] = includes
            text_parts.append("\n[Includes]\n" + "\n".join(f"  {inc}" for inc in includes))
        
        # Extract defines
        defines = re.findall(r'#define\s+(\w+)(?:\s+(.+))?', content)
        if defines:
            metadata['defines'] = [d[0] for d in defines]
            text_parts.append("\n[Defines]")
            for name, value in defines[:20]:
                text_parts.append(f"  {name}" + (f" = {value}" if value else ""))
        
        # Extract classes/structs
        classes = re.findall(r'(?:class|struct)\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+(\w+))?', content)
        if classes:
            metadata['classes'] = [c[0] for c in classes]
            text_parts.append("\n[Classes/Structs]")
            for name, base in classes:
                text_parts.append(f"  {name}" + (f" : {base}" if base else ""))
        
        # Extract function signatures
        func_pattern = r'(?:(?:static|virtual|inline|const|unsigned|signed|void|int|float|double|char|bool|long|short|auto)\s+)+(\w+)\s*\([^)]*\)\s*(?:const\s*)?(?:override\s*)?(?:final\s*)?[{;]'
        functions = re.findall(func_pattern, content)
        
        # Also catch constructor/destructor patterns
        if classes:
            for cls_name, _ in classes:
                ctor_pattern = rf'{cls_name}\s*\([^)]*\)\s*[{{:]'
                ctors = re.findall(ctor_pattern, content)
                functions.extend([cls_name] * len(ctors))
                
                dtor_pattern = rf'~{cls_name}\s*\([^)]*\)'
                dtors = re.findall(dtor_pattern, content)
                functions.extend([f'~{cls_name}'] * len(dtors))
        
        if functions:
            unique_funcs = list(dict.fromkeys(functions))  # Preserve order, remove dupes
            metadata['functions'] = unique_funcs
            text_parts.append("\n[Functions]\n" + "\n".join(f"  {f}()" for f in unique_funcs[:30]))
        
        # Extract comments
        comments = self._extract_comments(content, 'cpp')
        if comments:
            text_parts.append(f"\n[Comments]\n" + "\n".join(f"  {c}" for c in comments[:30]))
        
        # For Arduino, look for setup() and loop()
        if language == 'arduino':
            has_setup = 'void setup()' in content or 'void setup ()' in content
            has_loop = 'void loop()' in content or 'void loop ()' in content
            metadata['arduino_standard'] = has_setup and has_loop
            if has_setup or has_loop:
                text_parts.append(f"\n[Arduino Structure]")
                text_parts.append(f"  setup(): {'✓' if has_setup else '✗'}")
                text_parts.append(f"  loop(): {'✓' if has_loop else '✗'}")
        
        return "\n".join(text_parts), ConfidenceScores.CODE_DETECTED, metadata
    
    def _extract_generic(self, content: str, path: Path, language: str) -> Tuple[str, float, Dict[str, Any]]:
        """Extract information from code using regex patterns."""
        metadata = {'extraction_method': 'regex'}
        text_parts = [f"[{language.upper()} File: {path.name}]"]
        
        # Extract functions
        if language in self.FUNCTION_PATTERNS:
            pattern = self.FUNCTION_PATTERNS[language]
            matches = re.findall(pattern, content)
            functions = [m if isinstance(m, str) else next(x for x in m if x) for m in matches if m]
            
            if functions:
                metadata['functions'] = functions
                text_parts.append("\n[Functions]\n" + "\n".join(f"  {f}" for f in functions[:30]))
        
        # Extract comments
        comments = self._extract_comments(content, language)
        if comments:
            text_parts.append(f"\n[Comments]\n" + "\n".join(f"  {c}" for c in comments[:30]))
        
        return "\n".join(text_parts), ConfidenceScores.CODE_DETECTED, metadata
    
    def _extract_plain(self, content: str, path: Path) -> Tuple[str, float, Dict[str, Any]]:
        """Extract plain text with line numbers."""
        metadata = {'extraction_method': 'plain'}
        
        lines = content.split('\n')
        
        # Add line numbers for reference
        numbered_lines = [f"{i+1:4d} | {line}" for i, line in enumerate(lines[:500])]
        
        text = f"[File: {path.name}]\n\n" + "\n".join(numbered_lines)
        
        if len(lines) > 500:
            text += f"\n\n... ({len(lines) - 500} more lines)"
        
        return text, ConfidenceScores.CODE_UNKNOWN, metadata
    
    def _extract_comments(self, content: str, language: str) -> List[str]:
        """Extract comments from code."""
        comments = []
        
        patterns = self.COMMENT_PATTERNS.get(language, self.COMMENT_PATTERNS.get('python'))
        if not patterns:
            return comments
        
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    match = match.strip()
                    if match and len(match) > 3:  # Skip very short comments
                        comments.append(match[:200])  # Limit length
            except Exception:
                pass
        
        return comments[:50]  # Limit total comments
    
    def _extract_functions_regex(self, content: str, language: str) -> List[str]:
        """Fallback function extraction using regex."""
        patterns = {
            'python': r'def\s+(\w+)\s*\([^)]*\)',
            'cpp': r'(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*[{;]',
        }
        
        pattern = patterns.get(language)
        if not pattern:
            return []
        
        matches = re.findall(pattern, content)
        return [f"{m}()" for m in matches if m]


# ============================================================================
# Main Document Extractor
# ============================================================================

class DocumentExtractor:
    """
    Main extraction orchestrator that auto-detects file types
    and routes to appropriate extractors.
    """
    
    def __init__(self, timeout_seconds: int = EXTRACTION_TIMEOUT_SECONDS):
        """
        Initialize the document extractor.
        
        Args:
            timeout_seconds: Maximum time allowed for extraction (default 5 minutes)
        """
        self.timeout_seconds = timeout_seconds
        self.pdf_extractor = PDFExtractor()
        self.image_extractor = ImageExtractor()
        self.code_extractor = CodeExtractor()
        
        # Statistics
        self._extraction_count = 0
        self._total_time_ms = 0.0
        self._failures = 0
    
    def detect_file_type(self, path: Union[str, Path]) -> FileType:
        """
        Detect the type of a file.
        
        Args:
            path: Path to the file
            
        Returns:
            FileType enumeration value
        """
        path = Path(path)
        ext = path.suffix.lower()
        
        if ext in PDF_EXTENSIONS:
            return FileType.PDF
        elif ext in IMAGE_EXTENSIONS:
            return FileType.IMAGE
        elif ext in CODE_EXTENSIONS:
            return FileType.CODE
        else:
            # Try mime type detection
            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type:
                if mime_type == 'application/pdf':
                    return FileType.PDF
                elif mime_type.startswith('image/'):
                    return FileType.IMAGE
                elif mime_type.startswith('text/'):
                    return FileType.CODE  # Treat text as code for extraction
            
            return FileType.UNKNOWN
    
    def extract(self, path: Union[str, Path]) -> ExtractionResult:
        """
        Extract text and metadata from a file.
        
        Auto-detects file type and routes to appropriate extractor.
        
        Args:
            path: Path to the file to extract
            
        Returns:
            ExtractionResult with text, confidence, and metadata
        """
        path = Path(path)
        start_time = time.perf_counter()
        
        # Validate file exists
        if not path.exists():
            return ExtractionResult(
                text=f"[File not found: {path.name}]",
                confidence=ConfidenceScores.EXTRACTION_FAILED,
                file_type=FileType.UNKNOWN,
                error=f"File not found: {path}",
            )
        
        # Detect file type
        file_type = self.detect_file_type(path)
        
        # Calculate file hash for deduplication
        file_hash = self._calculate_hash(path)
        
        result = ExtractionResult(
            text="",
            confidence=0.0,
            file_type=file_type,
            metadata={'file_hash': file_hash, 'path': str(path)},
        )
        
        try:
            with TimeoutHandler(self.timeout_seconds, f"extraction of {path.name}"):
                if file_type == FileType.PDF:
                    text, confidence, metadata = self.extract_pdf(path)
                elif file_type == FileType.IMAGE:
                    text, confidence, metadata = self.extract_image(path)
                elif file_type == FileType.CODE:
                    text, confidence, metadata = self.extract_code(path)
                else:
                    # Unknown file type - try as text
                    text, confidence, metadata = self._extract_unknown(path)
                
                result.text = text
                result.confidence = confidence
                result.language = metadata.get('language')
                result.metadata.update(metadata)
        
        except TimeoutError as e:
            logger.error(f"Extraction timeout for {path}: {e}")
            result.error = str(e)
            result.text = f"[Extraction timeout: {path.name}]"
            result.confidence = ConfidenceScores.EXTRACTION_FAILED
            result.warnings.append(f"Extraction timed out after {self.timeout_seconds}s")
            self._failures += 1
        
        except Exception as e:
            logger.error(f"Extraction failed for {path}: {e}")
            result.error = str(e)
            result.text = f"[Extraction failed: {path.name}]\nError: {e}"
            result.confidence = ConfidenceScores.FALLBACK_FILENAME
            result.warnings.append(f"Extraction failed: {e}")
            self._failures += 1
        
        # Record timing
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        result.extraction_time_ms = elapsed_ms
        result.metadata['extraction_time_ms'] = elapsed_ms
        
        # Update statistics
        self._extraction_count += 1
        self._total_time_ms += elapsed_ms
        
        return result
    
    def extract_pdf(self, path: Union[str, Path]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Extract text from a PDF file.
        
        Args:
            path: Path to the PDF file
            
        Returns:
            Tuple of (text, confidence, metadata)
        """
        return self.pdf_extractor.extract(path)
    
    def extract_image(self, path: Union[str, Path]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Extract text and metadata from an image file.
        
        Args:
            path: Path to the image file
            
        Returns:
            Tuple of (text, confidence, metadata)
        """
        return self.image_extractor.extract(path)
    
    def extract_code(self, path: Union[str, Path]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Extract structured information from a code file.
        
        Args:
            path: Path to the code file
            
        Returns:
            Tuple of (text, confidence, metadata)
        """
        return self.code_extractor.extract(path)
    
    def _extract_unknown(self, path: Path) -> Tuple[str, float, Dict[str, Any]]:
        """Handle unknown file types."""
        metadata = {
            'filename': path.name,
            'file_size': path.stat().st_size,
            'extraction_method': 'fallback',
        }
        
        # Try to read as text
        try:
            content = path.read_text(encoding='utf-8', errors='replace')
            
            # Check if it looks like code/text
            if len(content) > 0:
                # Check for binary content
                binary_chars = sum(1 for c in content[:1000] if ord(c) < 32 and c not in '\n\r\t')
                if binary_chars > 50:
                    # Likely binary
                    return (
                        f"[Binary file: {path.name}]",
                        ConfidenceScores.FALLBACK_FILENAME,
                        metadata
                    )
                
                # Treat as plain text
                return (
                    f"[File: {path.name}]\n\n{content[:10000]}",
                    ConfidenceScores.CODE_UNKNOWN,
                    metadata
                )
        
        except Exception as e:
            logger.warning(f"Could not read {path} as text: {e}")
        
        return (
            f"[Unknown file: {path.name}]",
            ConfidenceScores.FALLBACK_FILENAME,
            metadata
        )
    
    def _calculate_hash(self, path: Path) -> str:
        """Calculate SHA-256 hash of file for deduplication."""
        hasher = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()[:16]  # First 16 chars is enough
        except Exception:
            return ""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        return {
            'total_extractions': self._extraction_count,
            'total_time_ms': self._total_time_ms,
            'average_time_ms': self._total_time_ms / self._extraction_count if self._extraction_count > 0 else 0,
            'failures': self._failures,
            'success_rate': (self._extraction_count - self._failures) / self._extraction_count if self._extraction_count > 0 else 0,
        }
    
    def reset_statistics(self):
        """Reset extraction statistics."""
        self._extraction_count = 0
        self._total_time_ms = 0.0
        self._failures = 0


# ============================================================================
# Batch Processing
# ============================================================================

class BatchExtractor:
    """Process multiple files in batch with progress tracking."""
    
    def __init__(self, extractor: Optional[DocumentExtractor] = None):
        """
        Initialize batch extractor.
        
        Args:
            extractor: DocumentExtractor instance (creates new if not provided)
        """
        self.extractor = extractor or DocumentExtractor()
    
    def extract_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        extensions: Optional[set] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[ExtractionResult]:
        """
        Extract all supported files from a directory.
        
        Args:
            directory: Directory path to process
            recursive: Whether to process subdirectories
            extensions: Optional set of extensions to filter (e.g., {'.pdf', '.py'})
            progress_callback: Optional callback(current, total, filename)
            
        Returns:
            List of ExtractionResult objects
        """
        directory = Path(directory)
        
        # Collect files
        if recursive:
            files = list(directory.rglob('*'))
        else:
            files = list(directory.glob('*'))
        
        # Filter to supported files
        supported_extensions = extensions or (PDF_EXTENSIONS | IMAGE_EXTENSIONS | set(CODE_EXTENSIONS.keys()))
        files = [f for f in files if f.is_file() and f.suffix.lower() in supported_extensions]
        
        results = []
        total = len(files)
        
        for i, file_path in enumerate(files):
            if progress_callback:
                progress_callback(i + 1, total, file_path.name)
            
            result = self.extractor.extract(file_path)
            results.append(result)
        
        return results
    
    def extract_files(
        self,
        files: List[Union[str, Path]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[ExtractionResult]:
        """
        Extract a list of specific files.
        
        Args:
            files: List of file paths to process
            progress_callback: Optional callback(current, total, filename)
            
        Returns:
            List of ExtractionResult objects
        """
        results = []
        total = len(files)
        
        for i, file_path in enumerate(files):
            file_path = Path(file_path)
            
            if progress_callback:
                progress_callback(i + 1, total, file_path.name)
            
            result = self.extractor.extract(file_path)
            results.append(result)
        
        return results


# ============================================================================
# Convenience Functions
# ============================================================================

def extract_file(path: Union[str, Path]) -> ExtractionResult:
    """
    Convenience function to extract a single file.
    
    Args:
        path: Path to the file
        
    Returns:
        ExtractionResult
    """
    extractor = DocumentExtractor()
    return extractor.extract(path)


def extract_text(path: Union[str, Path]) -> str:
    """
    Convenience function to extract just the text from a file.
    
    Args:
        path: Path to the file
        
    Returns:
        Extracted text string
    """
    result = extract_file(path)
    return result.text


def get_supported_extensions() -> Dict[str, set]:
    """
    Get all supported file extensions by category.
    
    Returns:
        Dictionary with 'pdf', 'image', and 'code' keys
    """
    return {
        'pdf': PDF_EXTENSIONS,
        'image': IMAGE_EXTENSIONS,
        'code': set(CODE_EXTENSIONS.keys()),
    }


# ============================================================================
# Module Initialization
# ============================================================================

# Configure default logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


if __name__ == '__main__':
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extractor.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = extract_file(file_path)
    
    print(f"File Type: {result.file_type.value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Time: {result.extraction_time_ms:.2f}ms")
    print(f"Language: {result.language or 'N/A'}")
    print(f"Words: {result.word_count}")
    print("-" * 50)
    print(result.text[:2000])
    if len(result.text) > 2000:
        print(f"\n... ({len(result.text) - 2000} more characters)")
