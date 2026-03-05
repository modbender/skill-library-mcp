# Syntax Highlighting Languages

Discord uses highlight.js for code block syntax highlighting. Add the language identifier after the opening triple backticks.

## Usage

````
```language
your code here
```
````

## Supported Languages

### Web & Frontend

| Language   | Identifiers        | Notes         |
| ---------- | ------------------ | ------------- |
| JavaScript | `javascript`, `js` |               |
| TypeScript | `typescript`, `ts` |               |
| HTML       | `html`, `xml`      | Shared parser |
| CSS        | `css`              |               |
| JSON       | `json`             |               |
| Markdown   | `markdown`, `md`   |               |

### Backend & General Purpose

| Language | Identifiers        | Notes |
| -------- | ------------------ | ----- |
| Python   | `python`, `py`     |       |
| C#       | `csharp`, `cs`     |       |
| C++      | `cpp`, `c++`, `cc` |       |
| C        | `c`                |       |
| Java     | `java`             |       |
| Go       | `go`, `golang`     |       |
| Rust     | `rust`, `rs`       |       |
| Ruby     | `ruby`, `rb`       |       |
| PHP      | `php`              |       |
| Swift    | `swift`            |       |
| Kotlin   | `kotlin`, `kt`     |       |
| Scala    | `scala`            |       |
| R        | `r`                |       |
| Perl     | `perl`, `pl`       |       |
| Lua      | `lua`              |       |
| Haskell  | `haskell`, `hs`    |       |
| Elixir   | `elixir`           |       |
| Erlang   | `erlang`           |       |
| Clojure  | `clojure`, `clj`   |       |
| OCaml    | `ocaml`, `ml`      |       |
| F#       | `fsharp`, `fs`     |       |

### Shell & Scripting

| Language     | Identifiers                  | Notes |
| ------------ | ---------------------------- | ----- |
| Bash         | `bash`, `sh`, `shell`, `zsh` |       |
| PowerShell   | `powershell`, `ps`, `ps1`    |       |
| Batch        | `batch`, `bat`, `cmd`        |       |
| CoffeeScript | `coffeescript`, `coffee`     |       |
| AutoHotkey   | `autohotkey`, `ahk`          |       |

### Data & Config

| Language | Identifiers         | Notes |
| -------- | ------------------- | ----- |
| YAML     | `yaml`, `yml`       |       |
| TOML     | `toml`              |       |
| INI      | `ini`               |       |
| XML      | `xml`               |       |
| SQL      | `sql`               |       |
| GraphQL  | `graphql`, `gql`    |       |
| Protobuf | `protobuf`, `proto` |       |

### DevOps & Infrastructure

| Language   | Identifiers              | Notes |
| ---------- | ------------------------ | ----- |
| Dockerfile | `dockerfile`, `docker`   |       |
| Nginx      | `nginx`                  |       |
| Apache     | `apache`, `apacheconf`   |       |
| Terraform  | `terraform`, `tf`, `hcl` |       |

### Markup & Documentation

| Language | Identifiers        | Notes |
| -------- | ------------------ | ----- |
| LaTeX    | `latex`, `tex`     |       |
| AsciiDoc | `asciidoc`, `adoc` |       |

### Assembly

| Language      | Identifiers     | Notes |
| ------------- | --------------- | ----- |
| x86 Assembly  | `x86asm`        |       |
| ARM Assembly  | `armasm`, `arm` |       |
| AVR Assembly  | `avrasm`        |       |
| MIPS Assembly | `mipsasm`       |       |
| LLVM IR       | `llvm`          |       |

### Special Purpose

| Language  | Identifiers                | Notes                                  |
| --------- | -------------------------- | -------------------------------------- |
| Diff      | `diff`                     | Shows added/removed lines in green/red |
| Fix       | `fix`                      | FIX protocol                           |
| GLSL      | `glsl`                     | OpenGL shading language                |
| Prolog    | `prolog`                   |                                        |
| XL        | `xl`                       | Extensible language                    |
| Plaintext | `text`, `plaintext`, `txt` | No highlighting                        |

## Diff Highlighting

The `diff` language is particularly useful for showing changes:

````
```diff
- removed line (shows in red)
+ added line (shows in green)
  unchanged line
```
````

## Tips

1. **Language identifiers are case-insensitive** — `Python`, `python`, `py` all work
2. **No language = no highlighting** — Omit the identifier for plain monospace text
3. **Unknown languages fall back to plaintext** — Won't error, just won't highlight
4. **ANSI coloring** — Use `ansi` identifier for ANSI escape code rendering (limited support)
5. **Keep blocks short** — Very long code blocks may get cut off in mobile clients
