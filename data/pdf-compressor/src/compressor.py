import os
import fitz  # PyMuPDF
from loguru import logger

class PDFCompressorService:
    @staticmethod
    def compress(input_path: str, output_path: str, compression_level: int) -> bool:
        """
        压缩指定的 PDF 文件，支持简单的内部参数控制。
        由于这是大纲级的框架脚手架，我们使用 fitz 执行标准压缩。

        :param input_path: 输入文件路径
        :param output_path: 输出文件路径
        :param compression_level: 压缩级别
        :return: bool 是否成功
        """
        try:
            doc = fitz.open(input_path)
            
            garbage_level = 3 if compression_level == 1 else 4
            
            if compression_level >= 2:
                # 去除隐藏的元数据和无用信息
                if hasattr(doc, "scrub"):
                    doc.scrub()
                
                # 裁剪仅使用到的字体集
                if hasattr(doc, "subset_fonts"):
                    try:
                        doc.subset_fonts()
                    except Exception as e:
                        logger.warning(f"Font subsetting skipped: {e}")
                
                # 图片重采样降质以大幅度压缩文件
                if hasattr(doc, "rewrite_images"):
                    # Level 2 适中压缩; Level 3极限压缩
                    dpi = 150 if compression_level == 2 else 72
                    quality = 75 if compression_level == 2 else 50
                    try:
                        doc.rewrite_images(dpi_threshold=dpi + 10, dpi_target=dpi, quality=quality)
                    except Exception as e:
                        logger.warning(f"Image rewriting skipped: {e}")
            
            doc.save(
                output_path, 
                garbage=garbage_level, 
                deflate=True, 
                clean=True
            )
            doc.close()
            return True
        except Exception as e:
            logger.error(f"Compression failed: {str(e)}")
            return False
