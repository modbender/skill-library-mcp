---
name: axe-accessibility
description: Accessibility testing and remediation using the axe MCP Server. Use when creating or modifying UI code (HTML, JSX, TSX, Vue, Svelte, CSS) to ensure accessibility compliance. Triggers on tasks involving web pages, components, forms, navigation, modals, tables, images, or any user-facing markup. Also use when explicitly asked to check accessibility or run an axe scan.
---

# axe Accessibility Skill

Test web pages for accessibility violations and get AI-powered remediation guidance using the axe DevTools MCP Server.

## Prerequisites

- Docker running locally
- `AXE_API_KEY` environment variable set
- Docker image pulled: `dequesystems/axe-mcp-server:latest`

## Tools

The wrapper script at `scripts/axe-mcp.js` (Node.js — no extra dependencies) provides two tools:

### analyze

Scan a live web page for accessibility violations. Requires a URL (works with localhost).

```bash
node scripts/axe-mcp.js analyze <url>
```

Returns JSON-RPC response. The violations are in `result.content[0].text` (JSON string) under the `data` array. Each violation has: `rule`, `impact`, `description`, `selector`, `source`, `helpUrl`.

### remediate

Get AI-powered fix guidance for a specific violation. Handles HTML with quotes/brackets safely.

```bash
node scripts/axe-mcp.js remediate <ruleId> <elementHtml> <issueRemediation> [pageUrl]
```

Returns `general_description`, `remediation`, and `code_fix` in `result.content[0].text`.

### tools-list

List available MCP tools.

```bash
node scripts/axe-mcp.js tools-list
```

## Workflow

When modifying UI code and a live page is available:

1. **Analyze** — `node scripts/axe-mcp.js analyze <url>`
2. **Parse** — extract violations from the JSON response
3. **Remediate** — for each unique rule violation, call remediate with ruleId, element HTML, and issue description
4. **Apply** — implement the recommended code fixes in source
5. **Verify** — re-run analyze to confirm zero violations

When no live page is available (static code review), apply accessibility best practices directly:
- Images: `alt` text (or `alt=""` for decorative)
- Forms: inputs need associated `<label>` elements
- Interactive elements: keyboard accessible, visible focus
- Color contrast: WCAG AA (4.5:1 normal text, 3:1 large text)
- ARIA: valid, complete, not redundant with native semantics
- Headings: proper hierarchy (h1 → h2 → h3)
- Dynamic content: focus management for modals, SPAs, live regions

## Notes

- Each `remediate` call uses AI credits from your organization's allocation
- The analyze tool spins up a real browser in Docker — allow ~30s for results
- Works with localhost URLs for local development testing
> **Note**: Requires a paid Axe DevTools for Web subscription.

## Support

For technical support, bug reports, and feature requests:

- **Email**: [helpdesk@deque.com](mailto:helpdesk@deque.com)
- **Support Portal**: [support.deque.com](https://support.deque.com)
- **[Support Guide](.github/SUPPORT.md)**

## Pricing & Sales

- **Product Page**: [deque.com/axe/mcp-server](https://www.deque.com/axe/mcp-server/)
- **Contact Sales**: [deque.com/contact](https://www.deque.com/contact)

## About Deque

[Deque Systems](https://www.deque.com) is the trusted leader in digital accessibility.

- **LinkedIn**: [Deque Systems](https://www.linkedin.com/company/deque-systems/)
