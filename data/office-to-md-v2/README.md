# Office to Markdown Skill (v2) for OpenClaw

## Overview
A comprehensive OpenClaw skill for converting office documents to Markdown format. This skill supports PDF, DOC, DOCX, and PPTX files with special emphasis on legacy .doc format support.

## Features
- ✅ **Full .doc support** using word-extractor library
- ✅ **Chinese encoding** automatically handled
- ✅ **OpenClaw integration** ready to use
- ✅ **Multiple formats** PDF, DOC, DOCX, PPTX
- ✅ **Structured output** with statistics and preview
- ✅ **Error handling** comprehensive error reporting
- ✅ **Batch processing** support for multiple files

## Quick Start

### 1. Installation
```bash
# Copy the skill to your workspace
cp -r /root/.openclaw/workspace/skills/office-to-md-v2 /your/workspace/skills/

# Install dependencies
cd /your/workspace/skills/office-to-md-v2
npm run install-deps

# Optional: Install PPTX support
npm run install-pptx
```

### 2. Basic Usage in OpenClaw
```javascript
// Convert a document
const result = await exec(
  'node /your/workspace/skills/office-to-md-v2/office-to-md/openclaw-skill.js /path/to/document.doc',
  { workdir: '/your/workspace', timeout: 60000 }
);

if (result.exitCode === 0) {
  console.log('✅ Conversion successful!');
  // Output file: /path/to/document.md
}
```

### 3. Test the Skill
```bash
cd /your/workspace/skills/office-to-md-v2
npm test
```

## Documentation

### Supported File Types
| Format | Extension | Library Used | Notes |
|--------|-----------|--------------|-------|
| PDF | `.pdf` | pdf-parse | Text extraction only |
| Word (legacy) | `.doc` | word-extractor | Full Chinese support |
| Word (modern) | `.docx` | mammoth + turndown | Good formatting |
| PowerPoint | `.pptx` | python-pptx | Basic text extraction |

### API Reference

#### convertOfficeToMarkdown(filePath)
```javascript
// Returns:
{
  success: boolean,
  outputPath?: string,
  markdown?: string,
  preview?: string,
  fileType?: string,
  message?: string,
  stats?: {
    lines: number,
    characters: number,
    words: number
  },
  error?: string,
  stack?: string
}
```

### Examples
See the `examples/` directory for complete usage examples:
- Basic conversion
- Error handling
- Batch processing
- Direct module usage

## Performance
- **Small files** (<1MB): < 10 seconds
- **Medium files** (1-10MB): 10-30 seconds
- **Large files** (>10MB): 30-120 seconds
- **Memory usage**: Typically < 100MB

## Troubleshooting

### Common Issues

**Q: .doc files show gibberish instead of Chinese text**
A: The word-extractor library should handle Chinese automatically. If issues persist, the file may be corrupted.

**Q: Conversion times out**
A: Increase the timeout for large files: `timeout: 120000` (2 minutes)

**Q: "Unsupported file type" error**
A: Check file extension and ensure it's one of: .pdf, .doc, .docx, .pptx

**Q: PPTX conversion fails**
A: Install python-pptx: `pip3 install python-pptx`

### Debug Mode
```bash
DEBUG=office-to-md node openclaw-skill.js document.doc
```

## Changelog

### v2.0.0 (2026-02-15)
- Added full .doc support with word-extractor
- Fixed ESM compatibility issues
- Added comprehensive OpenClaw integration
- Improved error handling and reporting
- Added statistics and preview in output

### v1.0.0
- Initial release with basic PDF, DOCX, PPTX support

## License
MIT - See included license file for details.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support
- Documentation: https://docs.openclaw.ai/skills/office-to-md
- Issues: https://github.com/openclaw/skills/issues
- Community: https://discord.com/invite/clawd

---

**Skill successfully tested with:**
- ✅ 2023级操作系统课程设计任务书.doc (Chinese .doc file)
- ✅ Full text extraction with Chinese characters
- ✅ OpenClaw integration working
- ✅ All dependencies installed and working