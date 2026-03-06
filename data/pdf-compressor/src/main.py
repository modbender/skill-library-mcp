import argparse
import sys
import json
from loguru import logger
from src.models import CompressionRequest, JSONResponse, CompressionResponseData
from src.compressor import PDFCompressorService
from src.utils import get_file_size, generate_output_path
from pydantic import ValidationError

def main():
    parser = argparse.ArgumentParser(description="OpenClaw PDF Compressor Skill")
    parser.add_argument("--pdf_path", type=str, required=True, help="Absolute path to the input PDF.")
    parser.add_argument("--compression_level", type=int, default=2, help="Compression level (1, 2, or 3).")
    
    args = parser.parse_args()
    
    try:
        request_data = CompressionRequest(
            pdf_path=args.pdf_path,
            compression_level=args.compression_level
        )
    except ValidationError as e:
        response = JSONResponse(status="error", message=f"Invalid arguments: {e}")
        print(response.model_dump_json())
        sys.exit(1)
        
    input_path = request_data.pdf_path
    
    if not get_file_size(input_path):
        response = JSONResponse(status="error", message="Input PDF file does not exist or is empty.")
        print(response.model_dump_json())
        sys.exit(1)
        
    output_path = generate_output_path(input_path)
    logger.info(f"Starting compression for {input_path}")
    
    success = PDFCompressorService.compress(
        input_path, 
        output_path, 
        request_data.compression_level.value
    )
    
    if success:
        original_size = get_file_size(input_path)
        compressed_size = get_file_size(output_path)
        
        data = CompressionResponseData(
            original_size=original_size,
            compressed_size=compressed_size,
            output_path=output_path
        )
        response = JSONResponse(status="success", message="Compression completed successfully.", data=data)
    else:
        response = JSONResponse(status="error", message="Compression failed. See skill logs for details.")

    # 打印给 OpenClaw 使用的标准 JSON 载荷
    print(response.model_dump_json(exclude_none=True))

if __name__ == "__main__":
    main()
