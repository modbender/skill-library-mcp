# Bioconductor Version Mismatch Demo

This project demonstrates Bioconductor and R version compatibility issues.

## The Problem

Bioconductor has a specific release schedule tied to R versions:

| Bioconductor | R Version |
|--------------|-----------|
| 3.18 | 4.3.0 - 4.3.3 |
| 3.19 | 4.4.0 - 4.4.2 |
| 3.20 | 4.5.0+ |

If you try to install Bioconductor 3.19 packages on R 4.3.x, you'll get errors.

## Common Error Messages

```
Error in BiocManager::install("DESeq2") :
  Package 'DESeq2' is not available in this Bioconductor version
```

```
Warning: 'BiocManager::install("DESeq2")' failed with message:
  The 'BiocVersion' package is outdated.
```

## What the Skill Should Do

1. Check R version: `R.version$version.string`
2. Check current Bioconductor version
3. Determine correct Bioconductor version for current R
4. Update BiocManager if needed:
   ```r
   install.packages("BiocManager")
   BiocManager::install(version = "3.19")
   ```
5. Retry package installation

## Test the Skill

From this directory, try:

```
"Bioconductor says my version is incompatible"
```

or

```
"I can't install DESeq2 from Bioconductor"
```
