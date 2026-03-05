---
name: Office to Markdown
description: Converts PDF, DOCX, and PPTX files to Markdown format.
---

# Office to Markdown Skill

This skill allows you to convert various office document formats into Markdown.

## Supported Formats
- **PDF** (.pdf): Extracts text from PDF files.
- **Word** (.docx): Converts Word documents to Markdown, preserving basic formatting.
- **Legacy Word** (.doc): Extracts text from legacy Word files (Office 97-2003).
- **PowerPoint** (.pptx): Extracts text from PowerPoint presentations.

## Dependencies
- `pdf-parse`
- `mammoth`
- `turndown`
- `office-text-extractor`
- `word-extractor`

## Usage

To use this skill, run the `convert.js` script with the path to the file you want to convert.

```bash
node convert.js <path-to-file>
```

### Example

```bash
node convert.js ./documents/report.pdf
```

The script will generate a new file with the same name but with a `.md` extension in the same directory (e.g., `./documents/report.md`).

## Notes
- **PDF Conversion**: Extracts raw text. Formatting preservation is limited.
- **DOCX Conversion**: Uses `mammoth` to convert to HTML first, then `turndown` to Markdown. Layout preservation is generally good for simple documents.
- **PPTX Conversion**: Currently extracts text content. Slide structure might not be fully preserved in the Markdown output.
