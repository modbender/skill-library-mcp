# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-02-09

### Security
- Enforced output directory restriction: Files can only be downloaded to the workspace `Downloads` folder (or subdirectories within it). Attempts to use `--out` to write outside this directory will now result in an error. This mitigates potential path traversal vulnerabilities.
