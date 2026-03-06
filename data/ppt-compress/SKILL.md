---
name: ppt-compress
description: Compress PPT/PPTX file size. Decompress PPT, compress large images, repackage and convert to PDF to significantly reduce file size. Suitable for scenarios where large PPT files need to be shared or uploaded.
---

# PPT压缩 / PPT Compression

将大型PPT/PPTX文件压缩为更小的PDF版本。
Compress large PPT/PPTX files into smaller PDF versions.

## Workflow

1. **Decompress PPT** - PPTX is essentially a ZIP, decompress to extract media files
   
2. **Compress Images** - Use sips to compress images larger than 1MB
   
3. **Repackage** - Repackage as PPTX

4. **Convert to PDF** - Use LibreOffice to convert to PDF

## Usage

Run the compression script:

```bash
python3 ~/clawd/skills/ppt-compress/scripts/compress.py <pptx_file_path> [output_directory]
```

## Examples

```bash
# Compress PPT and convert to PDF
python3 ~/clawd/skills/ppt-compress/scripts/compress.py "/path/to/file.pptx"

# Specify output directory
python3 ~/clawd/skills/ppt-compress/scripts/compress.py "/path/to/file.pptx" "/Users/xxx/Downloads"
```

## Dependencies

- Python 3
- sips (built-in to macOS)
- LibreOffice (used for PDF conversion)

Install LibreOffice: `brew install libreoffice`
