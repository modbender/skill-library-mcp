---
name: winget
description: Search, install, upgrade, and manage Windows packages via winget.
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
        "os": ["win32"],
        "requires": { "bins": ["winget"] },
      },
  }
---

# winget

Windows Package Manager CLI for searching, installing, upgrading, and managing software.
The Windows equivalent of Homebrew.

## Commands

### Search for packages

```powershell
winget search <query> --disable-interactivity --accept-source-agreements
```

### Show package details

```powershell
winget show <package-id> --disable-interactivity --accept-source-agreements
```

### Install a package

```powershell
winget install <package-id> --accept-package-agreements --accept-source-agreements --disable-interactivity
```

Install a specific version:

```powershell
winget install <package-id> --version <version> --accept-package-agreements --accept-source-agreements --disable-interactivity
```

### Upgrade packages

Check for available upgrades:

```powershell
winget upgrade --disable-interactivity --accept-source-agreements
```

Upgrade a specific package:

```powershell
winget upgrade <package-id> --accept-package-agreements --accept-source-agreements --disable-interactivity
```

Upgrade all packages:

```powershell
winget upgrade --all --accept-package-agreements --accept-source-agreements --disable-interactivity
```

### List installed packages

```powershell
winget list --disable-interactivity --accept-source-agreements
```

Filter by name:

```powershell
winget list <query> --disable-interactivity --accept-source-agreements
```

### Uninstall a package

```powershell
winget uninstall <package-id> --disable-interactivity
```

### Export / Import

Export installed packages to a JSON file:

```powershell
winget export -o packages.json --accept-source-agreements --disable-interactivity
```

Import and install from a JSON file:

```powershell
winget import -i packages.json --accept-package-agreements --accept-source-agreements --disable-interactivity
```

## Examples

```powershell
# Search for VS Code
winget search "Visual Studio Code" --disable-interactivity --accept-source-agreements

# Install Firefox
winget install Mozilla.Firefox --accept-package-agreements --accept-source-agreements --disable-interactivity

# Show info about a package
winget show Microsoft.PowerToys --disable-interactivity --accept-source-agreements

# List all installed packages
winget list --disable-interactivity --accept-source-agreements

# Upgrade everything
winget upgrade --all --accept-package-agreements --accept-source-agreements --disable-interactivity
```

## Notes

- Always use `--disable-interactivity` and `--accept-source-agreements` flags for non-interactive agent use.
- Use `--accept-package-agreements` when installing or upgrading to skip license prompts.
- Package IDs follow the `Publisher.PackageName` format (e.g., `Mozilla.Firefox`, `Microsoft.PowerToys`).
- Sources: `winget` (community repo) and `msstore` (Microsoft Store).
- Some installs require admin/elevated privileges. If a command fails, suggest the user run it in an elevated terminal.
- For WSL: prefix commands with `cmd.exe /c` or `powershell.exe -Command` to call the Windows-side winget.
