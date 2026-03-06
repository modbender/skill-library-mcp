---
name: Maven Build Skill
description: Run Maven with full passthrough support for all Maven capabilities.
---

# Maven Build Skill

Run Maven with full passthrough support for all Maven capabilities.

## Usage

```bash
node {baseDir}/scripts/mvn.mjs --dir "/path/to/project" -- clean test -DskipTests
node {baseDir}/scripts/mvn.mjs --dir "/path/to/project" -- package -Pprod -T 1C
node {baseDir}/scripts/mvn.mjs --dir "/path/to/project" -- help:effective-pom
node {baseDir}/scripts/mvn.mjs -- -v
node {baseDir}/scripts/mvn.mjs -- --version
```

## Options

- `--dir <path>`: optional working directory for Maven
- `--`: optional separator; arguments after it are passed to `mvn` unchanged
- All non-wrapper args are passed directly to Maven

### Wrapper help

```bash
node {baseDir}/scripts/mvn.mjs --help-skill
```

## Notes

- Requires `node` and `mvn` binaries in PATH.
- The wrapper itself only parses `--dir`; everything else is forwarded as-is.
- Uses process spawn with `shell: false` for safer execution.
