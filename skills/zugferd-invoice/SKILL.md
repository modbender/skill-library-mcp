# zugferd-invoice

Create ZUGFeRD 2.1 / Factur-X compliant e-invoices with **visible merged pages**. German B2B / Gov-ready.

🇩🇪 **Germany/EU only** - This skill implements the German ZUGFeRD standard for electronic invoicing.

## Features

- ✅ **Visible pages**: Merge invoice + time report into a single multi-page PDF
- ✅ **ZUGFeRD 2.1 compliant**: PDF/A-3b with embedded XML
- ✅ **EN16931 valid**: Ready for B2B portals and government submission
- ✅ **No paid APIs**: Uses MustangProject (open source) + GhostScript
- ✅ **Two workflows**: Visible pages (recommended) or attachment-only fallback

## Requirements

| Dependency | Install | Notes |
|------------|---------|-------|
| **Java 11+** | `brew install openjdk@21` | Required by MustangProject |
| **GhostScript** | `brew install ghostscript` | PDF/A-3 conversion |
| **mustang.jar** | Manual download | ZUGFeRD processor |

### Install mustang.jar

```bash
mkdir -p ~/.openclaw/tools/mustang
curl -L https://github.com/ZUGFeRD/mustangproject/releases/download/core-2.22.0/mustang.jar \
     -o ~/.openclaw/tools/mustang/mustang.jar
```

## Usage

### Recommended: GhostScript Workflow (Visible Pages)

```bash
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
cd ~/.openclaw/workspace/skills/zugferd-invoice

python3 scripts/zugferd_pages_workflow.py \
  --invoice Rechnung.pdf \
  --attachment Zeitnachweis.pdf \
  --output Rechnung_komplett.pdf
```

**Output:**
- Multi-page PDF (both documents visible)
- PDF/A-3b compliant
- ZUGFeRD 2.1 XML embedded
- Valid for B2B/Gov portals

### Fallback: Attachment-Only Workflow

```bash
python3 scripts/zugferd_workflow.py \
  --invoice Rechnung.pdf \
  --attachment Zeitnachweis.pdf \
  --output Rechnung_komplett.pdf
```

**Output:**
- Invoice visible, time report as file attachment
- Use when GhostScript is unavailable

## Arguments

| Flag | Description | Required |
|------|-------------|----------|
| `--invoice` | Original ZUGFeRD e-invoice PDF | ✅ Yes |
| `--attachment` | Time report / additional document | ✅ Yes |
| `--output` | Output path for merged PDF | ✅ Yes |
| `--keep-temp` | Keep temporary files (debug) | ❌ No |

## Workflows Compared

| Feature | GhostScript (Recommended) | Attachment-Only (Fallback) |
|---------|---------------------------|----------------------------|
| Visible pages | ✅ Both documents | ⚠️ Only invoice |
| Time report visibility | ✅ Page 2+ | ❌ File attachment only |
| PDF/A-3 compliance | ✅ Full | ✅ Full |
| Requires GhostScript | ✅ Yes | ❌ No |
| Complexity | Medium | Low |

## Technical Details

### GhostScript Workflow Steps

1. **Extract XML** from original e-invoice
2. **Merge PDFs** with GhostScript (visible pages)
3. **Convert to PDF/A-3** with GhostScript
4. **Embed XML** with MustangProject combine
5. **Validate** final PDF

### Why This Works

Standard PDF merging breaks PDF/A-3 compliance. The trick:
1. Merge first (any PDFs allowed)
2. Then convert the **merged** result to PDF/A-3
3. Finally embed the ZUGFeRD XML

This preserves visible pages while achieving full compliance.

### Why Attachment-Only?

If your time report cannot be converted to PDF/A (e.g., Lexware exports with broken ICC profiles), use `--attachments` flag which embeds files without visible merging.

## Troubleshooting

### "gs not found"
```bash
brew install ghostscript
```

### "java not found"
```bash
brew install openjdk@21
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
```

### "mustang.jar not found"
Download from [MustangProject releases](https://github.com/ZUGFeRD/mustangproject/releases)

### Validation fails
- Ensure input invoice is valid ZUGFeRD PDF/A-3
- Check GhostScript version: `gs --version` (should be 10+)

## Output Verification

```bash
# Check PDF/A compliance
java -jar ~/.openclaw/tools/mustang/mustang.jar --action validate \
  --source Rechnung_komplett.pdf

# Should output: <summary status="valid"/>
```

## Notes

- **ZUGFeRD = Germany only**: Electronic invoicing standard for German B2B
- **Factur-X**: French equivalent (also supported)
- **EN16931**: European standard for e-invoices
- **Source PDFs**: Invoice must be ZUGFeRD PDF/A-3; attachment can be any PDF

## Dependencies

- Python 3.8+
- Java 11+ (MustangProject)
- GhostScript 10+
- MustangProject CLI 2.22.0+

## See Also

- [ZUGFeRD Standard](https://www.ferd-net.de/)
- [MustangProject](https://github.com/ZUGFeRD/mustangproject)
- [EN16931](https://ec.europa.eu/digital-building-blocks/wikis/display/DIGITAL/EN16931+compliance)
