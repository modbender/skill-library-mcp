# Broken renv Project Demo

This project demonstrates a broken `renv` environment that needs repair.

## The Problem

The `renv.lock` file was created with R 4.3.0, but you might be running a different version of R. This causes `renv::restore()` to fail with version mismatch errors.

## Expected Behavior

When you run:

```r
renv::restore()
```

You may encounter errors like:
- "Package version mismatch detected"
- "Cannot install package [package] - available version is [version] but locked version is [version]"
- "The lockfile is incompatible with your version of R"

## What the Skill Should Do

1. Check current R version vs lockfile R version
2. Decide whether to update lockfile or downgrade R
3. Run `renv::restore()` or `renv::update()` accordingly
4. Verify packages load correctly

## Test the Skill

From this directory, try:

```
"renv restore is broken, please fix it"
```
