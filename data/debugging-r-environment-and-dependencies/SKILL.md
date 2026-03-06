---
name: debugging-r-environment-and-dependencies
description: Diagnose and fix R environment issues, including package installation failures, dependency conflicts, system library problems, renv errors, and Bioconductor version mismatches.
---

# Debugging R Environment and Dependencies

This skill focuses on resolving problems related to R environments rather than analysis logic. It helps restore a working setup so that R scripts and projects can run successfully.

Use this skill when the user encounters:
- Package installation failures
- Version conflicts between packages
- renv or packrat environment issues
- Bioconductor version mismatches
- System dependency errors (e.g., missing compilers or libraries)
- R failing to start or load packages

---

## What This Skill Does

When activated, this skill will:

1. **Diagnose the environment**
   - Check R version
   - Check installed packages and versions
   - Inspect `renv.lock` or project library
   - Identify Bioconductor version compatibility

2. **Resolve package installation issues**
   - Suggest correct CRAN/Bioconductor repositories
   - Install missing system dependencies (e.g., `libxml2`, `curl`, `openssl`)
   - Handle compilation failures on Linux/macOS/Windows

3. **Fix dependency conflicts**
   - Align package versions
   - Reinstall broken packages
   - Clean corrupted package libraries

4. **Repair project environments**
   - Restore with `renv::restore()`
   - Rebuild `renv.lock`
   - Reinitialize project library if needed

5. **Bioconductor troubleshooting**
   - Match Bioconductor version to R version
   - Use `BiocManager::install()` correctly
   - Resolve common bioinformatics package errors

6. **System-level troubleshooting**
   - Install missing compilers (e.g., `gcc`, `gfortran`)
   - Install development libraries required for R packages
   - Fix PATH or permission issues

---

## Example User Requests That Should Trigger This Skill

- "I can't install tidyverse"
- "This package fails with a compilation error"
- "renv restore is broken"
- "Bioconductor says my version is incompatible"
- "library() fails even though the package is installed"
- "R says shared object cannot be loaded"

---

## Example Workflow

**User:** I get an error when installing `sf`.

**Skill actions:**
- Detect missing system libraries (GEOS, GDAL, PROJ)
- Provide OS-specific install commands
- Retry R package installation
- Confirm successful library loading

---

## Common Problem Categories

| Category | Examples |
|---------|----------|
| Missing system libs | xml2, curl, openssl, sf, rJava |
| Compiler issues | gfortran missing, Xcode tools missing |
| Version mismatch | old R vs new package |
| Bioconductor mismatch | wrong Bioc version for R |
| renv problems | corrupted cache, lockfile mismatch |
| Permission issues | cannot write to library path |

---

## Notes

- Do not modify analysis code unless necessary
- Prefer fixing the environment over rewriting scripts
- Always aim to make the project reproducible
- Recommend `renv` for future environment stability
