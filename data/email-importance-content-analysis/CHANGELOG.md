# Changelog

## 1.0.1
- Add explicit **title/subject + sender** first-pass triage (sender is a weak signal).
- Add **fast-drop rules** for obviously sloppy spoof/ads to stop early.
- Clarify that **technical verification** (SPF/DKIM/DMARC, alignment, Reply-To, links/attachments) happens only after triage.
- Clarify that **content analysis** happens only after technical verification passes.

## 1.0.0
- Initial release: subject+sender triage → technical verification → content analysis.
