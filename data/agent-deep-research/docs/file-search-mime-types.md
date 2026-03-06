# Gemini File Search API: MIME Type Support

> **Last Updated:** 2025-12-21
> **API Documentation:** <https://ai.google.dev/gemini-api/docs/file-search#supported-files>

## Summary

The Gemini File Search API documentation lists support for 34 application types and 150+ text types. However, **empirical testing reveals that only 36 file extensions actually work** when uploading files to a File Search Store.

This document describes our findings and the fallback mechanism we've implemented to maximize file upload compatibility.

## The Problem

When testing MIME type support against the live Gemini File Search API:

| Documented | Tested | Passed | Failed |
|------------|--------|--------|--------|
| 180+ types | 234 extensions | **36** | **198** |

**Success rate: 15.4%**

Many common file types that are listed as supported in the documentation fail with API errors when uploaded. This includes widely-used formats like:

- JavaScript (`.js`, `.mjs`, `.cjs`)
- TypeScript (`.ts`, `.tsx`, `.d.ts`)
- JSON (`.json`)
- CSS (`.css`, `.scss`, `.sass`)
- YAML (`.yaml`, `.yml`)
- Ruby (`.rb`)
- PHP (`.php`)
- Rust (`.rs`)
- And many others...

## Validated MIME Types (36 extensions)

The following file types have been **confirmed to work** with the Gemini File Search API:

### Application Types (2)

| Extension | MIME Type |
|-----------|-----------|
| `.pdf` | `application/pdf` |
| `.xml` | `application/xml` |

### Text Types (34)

#### Plain Text

| Extension | MIME Type | Description |
|-----------|-----------|-------------|
| `.txt` | `text/plain` | Plain text |
| `.text` | `text/plain` | Plain text |
| `.log` | `text/plain` | Log files |
| `.out` | `text/plain` | Output files |
| `.env` | `text/plain` | Environment files |
| `.gitignore` | `text/plain` | Git ignore |
| `.gitattributes` | `text/plain` | Git attributes |
| `.dockerignore` | `text/plain` | Docker ignore |

#### Markup Languages

| Extension | MIME Type | Description |
|-----------|-----------|-------------|
| `.html` | `text/html` | HTML |
| `.htm` | `text/html` | HTML |
| `.md` | `text/markdown` | Markdown |
| `.markdown` | `text/markdown` | Markdown |
| `.mdown` | `text/markdown` | Markdown |
| `.mkd` | `text/markdown` | Markdown |

#### Programming Languages

| Extension | MIME Type | Language |
|-----------|-----------|----------|
| `.c` | `text/x-c` | C |
| `.h` | `text/x-c` | C Header |
| `.java` | `text/x-java` | Java |
| `.kt` | `text/x-kotlin` | Kotlin |
| `.kts` | `text/x-kotlin` | Kotlin Script |
| `.go` | `text/x-go` | Go |
| `.py` | `text/x-python` | Python |
| `.pyw` | `text/x-python` | Python (Windows) |
| `.pyx` | `text/x-python` | Cython |
| `.pyi` | `text/x-python` | Python Stub |
| `.pl` | `text/x-perl` | Perl |
| `.pm` | `text/x-perl` | Perl Module |
| `.t` | `text/x-perl` | Perl Test |
| `.pod` | `text/x-perl` | Perl POD |
| `.lua` | `text/x-lua` | Lua |
| `.erl` | `text/x-erlang` | Erlang |
| `.hrl` | `text/x-erlang` | Erlang Header |
| `.tcl` | `text/x-tcl` | Tcl |

#### Documentation & Specialized

| Extension | MIME Type | Description |
|-----------|-----------|-------------|
| `.bib` | `text/x-bibtex` | BibTeX |
| `.diff` | `text/x-diff` | Diff/Patch |

## Fallback Mechanism

To support common programming files that aren't in the validated list, we've implemented a **silent fallback to `text/plain`** for known text-based file types.

### How It Works

1. **Tier 1 - Validated Types:** If the file extension has a validated MIME type, use it directly
2. **Tier 2 - Text Fallback:** If the extension is a known text file, upload as `text/plain`
3. **Tier 3 - Rejection:** Binary and unknown files are rejected with a clear error

### Fallback Extensions (100+)

The following extensions are automatically uploaded as `text/plain`:

**JavaScript/TypeScript:**
`.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.mts`, `.cts`, `.tsx`, `.d.ts`, `.json`, `.jsonc`, `.json5`

**Web Technologies:**
`.css`, `.scss`, `.sass`, `.less`, `.styl`, `.vue`, `.svelte`, `.astro`

**Shell/Scripting:**
`.sh`, `.bash`, `.zsh`, `.fish`, `.ksh`, `.bat`, `.cmd`, `.ps1`, `.psm1`

**Configuration:**
`.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.properties`, `.editorconfig`, `.prettierrc`, `.eslintrc`, `.babelrc`, `.npmrc`

**Other Languages:**
`.rb`, `.php`, `.rs`, `.swift`, `.scala`, `.clj`, `.ex`, `.hs`, `.ml`, `.fs`, `.r`, `.jl`, `.nim`, `.zig`, `.dart`, `.coffee`, `.elm`, and many more...

## Unsupported File Types

The following types of files **cannot be uploaded** and will result in an error:

- **Binary executables:** `.exe`, `.dll`, `.so`, `.dylib`
- **Archives:** `.zip`, `.tar`, `.gz`, `.7z`, `.rar`
- **Images:** `.png`, `.jpg`, `.gif`, `.svg`, `.webp`
- **Audio/Video:** `.mp3`, `.mp4`, `.wav`, `.avi`
- **Compiled files:** `.class`, `.pyc`, `.o`, `.obj`
- **Other binary formats:** `.wasm`, `.bin`, `.dat`

## API Behavior Notes

1. **File Size Limit:** Maximum 100 MB per file
2. **Silent Success:** Files uploaded with fallback MIME types work correctly for search
3. **No Content Validation:** The API doesn't validate that file content matches the MIME type
4. **Extension-Based:** MIME type is determined solely by file extension

## Recommendations for Users

1. **Python, Java, Go, C projects:** Full native support - all files upload with correct MIME types
2. **JavaScript/TypeScript projects:** Files upload as `text/plain` via fallback - search works correctly
3. **Mixed codebases:** Most text files will work; binary files (images, compiled code) will be skipped
4. **Large files:** Keep files under 100 MB or they will be rejected

## Bug Report for API Team

### Issue
The Gemini File Search API rejects many MIME types that are listed as supported in the official documentation.

### Steps to Reproduce
1. Create a File Search Store
2. Attempt to upload a `.js` file with MIME type `text/javascript`
3. Observe the upload failure

### Expected Behavior
Files with documented MIME types should upload successfully.

### Actual Behavior
198 out of 234 tested MIME types fail to upload.

### Validated Test Results
See `/scripts/mime-type-validation-report.json` for the complete test results from 2025-12-21.

### Impact
- Developers cannot upload JavaScript, TypeScript, JSON, CSS, and many other common file types using their documented MIME types
- Workaround required: upload these files as `text/plain`

---

## Appendix: Test Methodology

Tests were conducted using the `@google/genai` SDK:

1. Created a temporary File Search Store
2. For each extension in our MIME type mapping:
   - Created a sample text file with that extension
   - Attempted upload with the documented MIME type
   - Recorded success or failure
3. Deleted the test store
4. Generated report of results

To run the validation suite yourself:
```bash
export GEMINI_API_KEY=your_key_here
npm run test:mime-types
```
