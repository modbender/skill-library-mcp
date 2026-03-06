---
name: ezbookkeeping
description: ezBookkeeping is a lightweight, self-hosted personal finance app with a user-friendly interface and powerful bookkeeping features. This skill allows AI agents to add and query transactions, accounts, categories and tags in ezBookkeeping via ezBookkeeping API Tools.
---

# ezBookkeeping API Tools

[ezBookkeeping](https://ezbookkeeping.mayswind.net) provides a tool script called **ezBookkeeping API Tools** that allows users or AI agents to conveniently call the API endpoints from the command line using **sh** or **PowerShell**. Users only need to configure two environment variables: the ezBookkeeping server address `EBKTOOL_SERVER_BASEURL` and the API token `EBKTOOL_TOKEN`.

## Usage

### List all supported commands

Linux / macOS

```bash
sh {baseDir}/scripts/ebktools.sh list
```

Windows

```powershell
{baseDir}\scripts\ebktools.ps1 list
```

### Show help for a specific command

Linux / macOS

```bash
sh {baseDir}/scripts/ebktools.sh help <command>
```

Windows

```powershell
{baseDir}\scripts\ebktools.ps1 help <command>
```

### Call API

Linux / macOS

```bash
sh {baseDir}/scripts/ebktools.sh <command> [command-options]
```

Windows

```powershell
{baseDir}\scripts\ebktools.ps1 <command> [command-options]
```

## Troubleshooting

If the script reports that the `EBKTOOL_SERVER_BASEURL` or `EBKTOOL_TOKEN` environment variable is not set, inform the user that they must configure these variables themselves. The user may set them as system environment variables or create a `.env` file containing them and place the file in the user home directory. **DO NOT** request the values of these variables and do not assist in setting them. These variables must be configured by the user.

The meanings of these environment variables are as follows:

| Variable | Required | Description |
| --- | --- | --- |
| `EBKTOOL_SERVER_BASEURL` | Required | ezBookkeeping server base URL (e.g., http://localhost:8080) |
| `EBKTOOL_TOKEN` | Required | ezBookkeeping API token |

## Reference

ezBookkeeping: [https://ezbookkeeping.mayswind.net](https://ezbookkeeping.mayswind.net)