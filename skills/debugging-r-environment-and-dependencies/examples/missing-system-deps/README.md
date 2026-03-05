# Missing System Dependencies Demo

This project demonstrates R package installation failures due to missing system libraries.

## The Problem

The `script.R` file tries to load packages that require system-level libraries that may not be installed.

## Packages That Commonly Fail

| Package | System Dependencies Required |
|---------|------------------------------|
| `sf` | GEOS, GDAL, PROJ, UDUNITS |
| `xml2` | libxml2 |
| `curl` | libcurl |
| `openssl` | openssl |
| `rJava` | Java JDK |
| `terra` | GDAL, GEOS, PROJ |

## Common Error Messages

```
Error: package or namespace load failed for 'sf' in dyn.load(file, DLLpath = DLLpath, ...):
 unable to load shared object '/usr/lib/R/library/00LOCK-sf/00new/sf/libs/sf.so':
  libgdal.so.30: cannot open shared object file: No such file or directory
```

```
Configuration error: could not find the gdal-config config script.
```

## What the Skill Should Do

1. Identify which system library is missing
2. Detect the operating system
3. Provide the correct installation command:

**Ubuntu/Debian:**
```bash
sudo apt install libudunits2-dev libgdal-dev libgeos-dev libproj-dev
```

**macOS:**
```bash
brew install pkg-config gdal geos proj udunits
```

**Fedora/RHEL:**
```bash
sudo dnf install gdal-devel geos-devel proj-devel udunits2-devel
```

4. Retry the R package installation
5. Confirm the package loads successfully

## Test the Skill

From this directory, try:

```
"I can't install the sf package"
```

or

```
"sf fails with a compilation error"
```
