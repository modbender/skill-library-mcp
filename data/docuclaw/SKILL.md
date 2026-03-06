---
name: DocuClaw
description: Sovereign document intelligence & archival system. Extracts structured data from invoices, receipts, and contracts 100% locally using AI.
---

# DocuClaw Skill

DocuClaw provides a sovereign data infrastructure for processing and archiving documents. It uses multimodal LLMs to extract structured information from scans, photos, and emails, storing everything in human-readable, version-controllable Markdown files.

## Use Cases

- **Expense Management**: Extract totals, taxes, and dates from receipts for tax filing.
- **Contract Analysis**: Monitor expiration dates and renewal clauses in legal documents.
- **Sovereign Archival**: Maintain a local-first, GDPR/GoBD compliant archive of all physical and digital mail.
- **Unified Querying**: Ask questions about your document history without cloud exposure.

## Key Features

- **100% Local**: Zero cloud dependency. Your private data never leaves your hardware.
- **Plug-and-Play Parsers**: Extensible architecture for country-specific document formats.
- **AI-Powered**: Supports Ollama, OpenAI Vision, or any multimodal model for intelligent extraction.
- **Markdown Schema**: Normalizes all documents into a universal schema with YAML metadata.

## Workflow Example

1. **Input**: A PDF invoice or a photo of a receipt.
2. **Process**: Run `docuclaw process` to trigger AI extraction.
3. **Archive**: Document is saved to your local vault as `YYYY/MM/filename.md`.
4. **Action**: The extracted data is synced to your calendar or accounting tool.

## Integration

DocuClaw is designed to work seamlessly with the OpenClaw ecosystem, allowing AI agents to perform RAG (Retrieval-Augmented Generation) over your local document archive.
