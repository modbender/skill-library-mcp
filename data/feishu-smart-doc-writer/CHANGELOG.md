# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.1] - 2026-02-23

### Fixed
- **Skill.json tool count**: Fixed missing tools display on Clawhub
- Verified all 7 tools are properly declared: write_smart, configure, append_smart, transfer_ownership, get_config_status, search_docs, list_docs

## [1.4.0] - 2026-02-23

### Added
- **Document Search Functionality** (`search_docs`)
  - Search local index by keywords
  - Search in document name, summary, and tags
  - Return matching documents with links

- **Document List Functionality** (`list_docs`)
  - List all created Feishu documents
  - Filter by tags (AI Technology, E-commerce, Health & Sports, etc.)
  - Filter by status

- **Automatic Index Management** (`index_manager.py`)
  - Auto-update local index at `memory/feishu-docs-index.md` after document creation
  - Auto-generate document summary (first 100 characters)
  - Intelligent auto-categorization tags:
    - AI Technology (AI, artificial intelligence, model, GPT, LLM)
    - OpenClaw (OpenClaw, skill, agent)
    - Feishu Docs (Feishu, document, docx)
    - E-commerce (e-commerce, TikTok, Alibaba)
    - Health & Sports (Garmin, Strava, cycling, health)
    - Daily Archive (conversation, archive, chat history)

- **Tool Declarations**
  - Officially declare `search_docs` and `list_docs` tools in `package.json` and `skill.json`

### Changed
- Updated `SKILL.md` documentation with detailed descriptions of new features
- Improved usage examples and configuration instructions

### Technical Details (Ownership Transfer Fix)
- **Before**: Used `ctx.invoke_tool("exec", ...)` which failed when ctx was None or unavailable
- **After**: Direct HTTP API calls with `aiohttp`, fully independent of OpenClaw context
- **API Endpoint**: `POST /drive/v1/permissions/{token}/members/transfer_owner?type=docx`

### Optimized Ownership Transfer Workflow
- Automatically transfer ownership to user after document creation
- Automatically obtain tenant_access_token without manual configuration
- Fixed "permission denied" errors caused by ctx passing issues

## [1.3.0] - 2026-02-22

### Fixed
- **Fixed Ownership Transfer Functionality** (`transfer_ownership`)
  - **BREAKING CHANGE**: Replaced ctx-dependent implementation with independent API calls
  - Added `_get_tenant_access_token()` method for independent token retrieval using aiohttp
  - **Removed dependency**: No longer relies on `ctx.invoke_tool("exec", ...)` to call curl commands
  - **More stable**: Directly use `aiohttp` to call Feishu API, eliminating context passing issues
  - **Better error handling**: Returns detailed error messages on failure
  - Reads Feishu app credentials from OpenClaw config independently

### Technical Details
- **Before**: Used `ctx.invoke_tool("exec", ...)` which failed when ctx was None or unavailable
- **After**: Direct HTTP API calls with `aiohttp`, fully independent of OpenClaw context
- **API Endpoint**: `POST /drive/v1/permissions/{token}/members/transfer_owner?type=docx`

### Changed
- **Optimized Ownership Transfer Workflow**
  - Automatically transfer ownership to user after document creation
  - Automatically obtain tenant_access_token without manual configuration
  - Fixed "permission denied" errors caused by ctx passing issues

## [1.2.0] - 2026-02-21

### Added
- **Intelligent Chunk Writing Functionality**
  - Automatically split long content into chunks (default 2000 characters)
  - Avoid blank document issues caused by Feishu API character limits
  - Smart paragraph segmentation while preserving heading structure
  - Support automatic table-to-text conversion

- **First-Time User Guide**
  - Auto-detect first-time usage
  - Guide users to obtain OpenID
  - Auto-save configuration to `user_config.json`

- **Basic Document Operations**
  - `write_smart` - Smart document creation
  - `append_smart` - Append content to existing documents
  - `transfer_ownership` - Transfer document ownership
  - `configure` - Configure OpenID
  - `get_config_status` - Check configuration status

## [1.1.0] - 2026-02-20

### Added
- Initial release
- Basic Feishu document creation and writing functionality
- Support Markdown format (headings, lists, code blocks, etc.)
- Support automatic image upload

---

## Version Summary

- **v1.4.0** - Added search, list, and automatic index management
- **v1.3.0** - Fixed ownership transfer using independent API calls (removed ctx dependency)
- **v1.2.0** - Added intelligent chunk writing and first-time user guide
- **v1.1.0** - Initial release with basic document operations

## Key Technical Updates

### v1.4.0 Core Technology
- Local index management system
- Intelligent content categorization algorithm
- Automatic document metadata extraction

### v1.3.0 Core Technology (Critical Fix)
- **Independent tenant_access_token retrieval** using aiohttp
- **Direct Feishu API calls** without OpenClaw context dependency
- **Removed**: `ctx.invoke_tool("exec", ...)` approach
- **Added**: `_get_tenant_access_token()` for standalone token acquisition
- Reads app credentials from `~/.openclaw/openclaw.json` independently

### v1.2.0 Core Technology
- ContentChunker content segmentation
- Intelligent paragraph segmentation algorithm
- User configuration persistence
