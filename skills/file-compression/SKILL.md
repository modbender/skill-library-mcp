---
name: file-compression
description: Compress files to reduce storage and transfer size. Use this skill when users ask to shrink PDFs or images, optimize upload/share size, or balance quality and size. Supports PDF compression and image compression with Python-first workflows plus Node.js fallback when Python dependencies are unavailable.
metadata:
  {
    "clawdbot":
      {
        "requires":
          {
            "bins": ["python3", "node", "gs"],
            "packages": ["pikepdf", "pillow", "sharp"],
          },
        "primaryEnv": "python",
      },
  }
---

# File Compression

Compress files with Python-first workflows and Node.js fallback workflows.

## Supported File Types

- PDF: `.pdf`
- Image: `.jpg`, `.jpeg`, `.png`, `.webp`

## What This Skill Can Do

- Compress PDF with preset quality levels.
- Compress image with quality/resize/format controls.
- Switch backend automatically when dependencies are missing.
- Detect bad compression results and retry with better strategy.

## Installation Spec (Before Running)

Required binaries:

- `python3` (recommended `>= 3.8`)
- `node`
- `gs` (Ghostscript, required for PDF Ghostscript paths)

Python install spec:

```bash
python3 -m pip install -r {baseDir}/requirements.txt
```

Node install spec:

```bash
cd {baseDir}
npm install
```

Ghostscript install examples:

- macOS: `brew install ghostscript`
- Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ghostscript`

Safety note:

- Explain to the user before each install command that third-party packages are being installed.
- If installation fails, report the failing command and switch to available fallback backend.

## CLI Options Cheat Sheet

PDF (`scripts/compress_pdf.py`):

- `--preset screen|ebook|printer|prepress`
- `--strategy auto|ghostscript|pikepdf`
- `--remove-metadata`
- `--no-linearize`
- `--overwrite`

PDF Node (`scripts/compress_pdf_node.mjs`):

- `--preset screen|ebook|printer|prepress`

Image (`scripts/compress_image.py`):

- `--quality <1-100>`
- `--format keep|jpeg|png|webp`
- `--max-width <n>`
- `--max-height <n>`
- `--strategy auto|pillow|node`
- `--overwrite`

Image Node (`scripts/compress_image_node.mjs`):

- `--quality <1-100>`
- `--format keep|jpeg|png|webp`
- `--max-width <n>`
- `--max-height <n>`

## Example Set (Python + Node)

PDF default:

```bash
python {baseDir}/scripts/compress_pdf.py in.pdf out.pdf
```

PDF aggressive:

```bash
python {baseDir}/scripts/compress_pdf.py in.pdf out.pdf --preset screen --strategy ghostscript
```

PDF with pikepdf:

```bash
python {baseDir}/scripts/compress_pdf.py in.pdf out.pdf --strategy pikepdf --remove-metadata
```

PDF via Node:

```bash
node {baseDir}/scripts/compress_pdf_node.mjs in.pdf out.pdf --preset ebook
```

Image default:

```bash
python {baseDir}/scripts/compress_image.py in.jpg out.jpg --quality 75
```

Image convert + resize:

```bash
python {baseDir}/scripts/compress_image.py in.png out.webp --format webp --quality 72 --max-width 1920
```

Image force Node backend:

```bash
python {baseDir}/scripts/compress_image.py in.jpg out.jpg --strategy node --quality 70
```

Image direct Node:

```bash
node {baseDir}/scripts/compress_image_node.mjs in.jpg out.jpg --quality 70 --max-width 1600
```

## Environment and Fallback

Check and install in this order:

1. Python: `python3 --version` (fallback: `python --version`)
2. Node: `node --version`
3. Ghostscript: `gs --version` (required for PDF Ghostscript paths)
4. Python deps when needed:
   - `pip install pikepdf`
   - `pip install pillow`
5. Node deps when needed:
   - `npm install`

Fallback policy:

- PDF: `ghostscript` -> `pikepdf` -> `node-ghostscript`
- Image: `pillow` -> `node-sharp`

If `python3.8+` is unavailable, try `python3.11/3.10/3.9/3.8`; if still blocked, use Node flow when possible.

## Execution Transparency

Always communicate each step:

1. Tell user what you are checking or running.
2. Show the exact command before execution.
3. For slow steps (`pip install`, `npm install`, large Ghostscript jobs), say you are waiting.
4. After each step, report result and next action.

## Bad Result Recovery

When `output_size >= input_size`, do not stop:

1. Report exact from/to numbers and compression ratio.
2. Explain likely cause:
   - PDF: already optimized, scanned-image content, metadata overhead, unsuitable preset.
   - Image: unsuitable format conversion, quality too high, small-file overhead.
3. Retry with alternate strategy:
   - PDF: `ebook -> screen`, then switch backend.
   - Image: lower quality, switch backend, convert to `webp`, optionally resize.
4. Return the best attempt and state which command produced it.

## Agent Response Contract

After every compression task, always return:

1. Output absolute path.
2. `from <before_size> to <after_size>`.
3. `saved <delta_size> (<ratio>%)`.
4. Backend used.
