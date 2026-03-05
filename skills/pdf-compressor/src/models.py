from pydantic import BaseModel, Field
from enum import IntEnum

class CompressionLevel(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class CompressionRequest(BaseModel):
    pdf_path: str = Field(..., description="Absolute path to the input PDF file")
    compression_level: CompressionLevel = Field(default=CompressionLevel.MEDIUM, description="Compression level: 1 (Low), 2 (Medium), 3 (High)")

class CompressionResponseData(BaseModel):
    original_size: int = Field(description="Size of the original PDF in bytes")
    compressed_size: int = Field(description="Size of the compressed PDF in bytes")
    output_path: str = Field(description="Absolute path to the newly compressed PDF file")

class JSONResponse(BaseModel):
    status: str = Field(..., description="'success' or 'error'")
    message: str = Field(..., description="Details regarding the operation result")
    data: CompressionResponseData | None = None
