# File Search MIME Type Guide

Condensed reference for Gemini File Search API file type support. For full test methodology and bug details, see `docs/file-search-mime-types.md`.

## Key Facts

- **File size limit**: 100 MB per file
- **Documented types**: 180+
- **Actually working types**: 36 extensions (15.4% of documented)
- **Workaround**: Text-based files not in the validated list are uploaded as `text/plain`

## Validated MIME Types (36 extensions)

These file types are confirmed to work with the Gemini File Search API.

### Application Types

| Extension | MIME Type |
|-----------|-----------|
| `.pdf` | `application/pdf` |
| `.xml` | `application/xml` |

### Plain Text

| Extension | MIME Type |
|-----------|-----------|
| `.txt`, `.text` | `text/plain` |
| `.log`, `.out` | `text/plain` |
| `.env` | `text/plain` |
| `.gitignore`, `.gitattributes` | `text/plain` |
| `.dockerignore` | `text/plain` |

### Markup Languages

| Extension | MIME Type |
|-----------|-----------|
| `.html`, `.htm` | `text/html` |
| `.md`, `.markdown`, `.mdown`, `.mkd` | `text/markdown` |

### Programming Languages

| Extension | MIME Type | Language |
|-----------|-----------|----------|
| `.c`, `.h` | `text/x-c` | C |
| `.java` | `text/x-java` | Java |
| `.kt`, `.kts` | `text/x-kotlin` | Kotlin |
| `.go` | `text/x-go` | Go |
| `.py`, `.pyw`, `.pyx`, `.pyi` | `text/x-python` | Python |
| `.pl`, `.pm`, `.t`, `.pod` | `text/x-perl` | Perl |
| `.lua` | `text/x-lua` | Lua |
| `.erl`, `.hrl` | `text/x-erlang` | Erlang |
| `.tcl` | `text/x-tcl` | Tcl |

### Other

| Extension | MIME Type |
|-----------|-----------|
| `.bib` | `text/x-bibtex` |
| `.diff` | `text/x-diff` |

## Text Fallback (100+ extensions)

Files with these extensions are uploaded as `text/plain`. Search works correctly despite the generic MIME type.

**JavaScript/TypeScript**: `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.mts`, `.cts`, `.tsx`, `.d.ts`, `.json`, `.jsonc`, `.json5`

**Web**: `.css`, `.scss`, `.sass`, `.less`, `.styl`, `.vue`, `.svelte`, `.astro`

**Shell/Scripts**: `.sh`, `.bash`, `.zsh`, `.fish`, `.ksh`, `.bat`, `.cmd`, `.ps1`, `.psm1`

**Config**: `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.properties`, `.editorconfig`, `.prettierrc`, `.eslintrc`, `.babelrc`, `.npmrc`

**Other Languages**: `.rb`, `.php`, `.rs`, `.swift`, `.scala`, `.clj`, `.ex`, `.hs`, `.ml`, `.fs`, `.r`, `.jl`, `.nim`, `.zig`, `.dart`, `.coffee`, `.elm`

## Unsupported (Rejected)

Binary files cannot be uploaded:

- Executables: `.exe`, `.dll`, `.so`, `.dylib`
- Archives: `.zip`, `.tar`, `.gz`, `.7z`, `.rar`
- Images: `.png`, `.jpg`, `.gif`, `.svg`, `.webp`
- Audio/Video: `.mp3`, `.mp4`, `.wav`, `.avi`
- Compiled: `.class`, `.pyc`, `.o`, `.obj`
- Other binary: `.wasm`, `.bin`, `.dat`

## Recommendations

| Project Type | Support Level |
|-------------|--------------|
| Python, Java, Go, C | Full native MIME type support |
| JavaScript, TypeScript | Works via `text/plain` fallback |
| Mixed codebases | Most text files work; binaries skipped |
