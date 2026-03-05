# Examples (for LLMs)

This directory contains **copy-pasteable** reference implementations using Ant Design (antd) + React.

## How to use (LLM protocol)
1) Pick the closest example to the requested UI.
2) Copy the relevant files into the target codebase.
3) Replace:
   - entity names (User -> <Entity>)
   - columns/fields
   - API calls (replace mock service)
4) Ensure:
   - `rowKey` is set
   - empty/loading/error states exist
   - forms have validation rules

## Available
- `crud-users/` — CRUD List page with: Filters + Table + Drawer form + server-pagination mock.
