# Debugging R Environment and Dependencies

An AI skill for diagnosing and fixing R environment issues, including package installation failures, dependency conflicts, system library problems, renv errors, and Bioconductor version mismatches.

## Overview

This skill focuses on resolving **environment problems** rather than analysis logic. It helps restore a working R setup so that scripts and projects can run successfully.

## When to Use This Skill

Activate this skill when you encounter:

| Problem Type | Examples |
|--------------|----------|
| Package installation failures | `ERROR: dependency 'xyz' is not available` |
| Version conflicts | Package A requires version X, but version Y is installed |
| System dependency errors | Missing `libxml2`, `curl`, `openssl`, GEOS, GDAL |
| Compiler issues | `gfortran not found`, Xcode tools missing |
| renv problems | `renv::restore()` fails, corrupted cache |
| Bioconductor mismatches | "Bioc version 3.18 requires R 4.4.0" |
| Permission issues | Cannot write to library path |

## What This Skill Does

### 1. Diagnose the Environment
- Check R version and platform
- List installed packages and versions
- Inspect `renv.lock` or project library
- Identify Bioconductor version compatibility

### 2. Resolve Package Installation Issues
- Suggest correct CRAN/Bioconductor repositories
- Provide OS-specific system dependency commands
- Handle compilation failures on Linux/macOS/Windows

### 3. Fix Dependency Conflicts
- Align package versions to resolve conflicts
- Reinstall broken or corrupted packages
- Clean up corrupted package libraries

### 4. Repair Project Environments
- Restore with `renv::restore()`
- Rebuild `renv.lock` when needed
- Reinitialize project library if necessary

### 5. Bioconductor Troubleshooting
- Match Bioconductor version to R version
- Properly use `BiocManager::install()`
- Resolve bioinformatics package errors

### 6. System-Level Troubleshooting
- Install missing compilers (`gcc`, `gfortran`)
- Install development libraries for R packages
- Fix PATH or permission issues

## Example Usage

```
User: "I can't install sf package"

Skill actions:
- Detects missing system libraries (GEOS, GDAL, PROJ)
- Provides Ubuntu/Debian: sudo apt install libudunits2-dev libgdal-dev libgeos-dev libproj-dev
- Provides macOS: brew install pkg-config gdal geos proj udunits
- Retries R package installation
- Confirms successful library loading
```

## Common Problem Categories

| Category | Common Packages Affected |
|----------|--------------------------|
| Missing system libs | xml2, curl, openssl, sf, rJava |
| Compiler issues | Packages with C/C++/Fortran code |
| Version mismatch | Old R vs new packages |
| Bioconductor mismatch | Bioconductor 3.18+ requires R 4.4+ |
| renv problems | Cache corruption, lockfile issues |
| Permission issues | Cannot write to `/usr/lib/R/library` |

## See Also

- [running-r-analysis-in-existing-projects](../running-r-analysis-in-existing-projects/) - For actual analysis work within R projects
