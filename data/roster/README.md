# roster

Creates weekly shift rosters (KW-JSON) from CSV availability data and pushes them to GitHub. Optimized for field sales teams with driver logistics, trainer assignments, and automatic PDF generation.

## Features

- **CSV Import**: Processes Google Forms CSV files with availability, car info, and comments
- **Automatic Calendar Week Detection**: Detects the calendar week (KW) from CSV date columns (ISO 8601)
- **Employee Management**: Loads/updates `employees.json` from GitHub with structured fields (status, trainer priority, driver license, minor protection)
- **Intelligent Planning**: Considers departure times, end times, car capacity (5 persons), trainer assignment for untrained employees
- **Validation**: Mandatory checks before every preview (time windows, trainer priority, capacity, hour limits)
- **Telegram Preview**: Formatted roster preview sent directly as a Telegram message (no tables/code blocks)
- **GitHub Integration**: Pushes JSON to GitHub, triggers PDF build and email dispatch via GitHub Actions
- **New Employees**: Automatically detects unknown names in CSV and adds them to the employee list

## Prerequisites

- OpenClaw >= 0.8.0
- GitHub repository with `employees.json` and GitHub Actions workflows (`build-roster.yml`, `publish-roster.yml`)
- GitHub Token with `repo` and `actions:write` permissions
- Python 3 on the server (for base64/JSON operations in shell scripts)
- `curl` on the server

## Installation

```bash
openclaw skill install roster
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub PAT with `repo` + `actions:write` | Yes |
| `ROSTER_REPO` | GitHub repository in `owner/repo` format | Yes |

### Repository Structure

The target repository must have the following structure:

```
repo/
  employees.json              # Employee master data
  KW-YYYY/
    KW-XX-YYYY.json         # Roster files (created by the skill)
  .github/workflows/
    build-roster.yml        # PDF build + Telegram delivery
    publish-roster.yml      # PDF build + email delivery
```

### employees.json Schema

```json
{
  "employee_key": {
    "firstName": "Name",
    "email": "employee@example.com",
    "hasCar": false,
    "status": ["trained"],
    "isMinor": false,
    "maxHoursPerWeek": null,
    "driverRole": "none",
    "canTrain": false,
    "trainerPriority": [],
    "info": ""
  }
}
```

**Fields:**
- `status`: `["supervisor"]`, `["trained"]`, or `["untrained"]`
- `canTrain`: Whether the employee can train/supervise untrained colleagues
- `trainerPriority`: Ordered list of preferred trainers (keys) for untrained employees
- `isMinor`: Minor -- legal protection rules apply
- `maxHoursPerWeek`: Weekly hour limit (`null` = no limit)
- `driverRole`: `"full"` (drives + sales), `"transport"` (drives only), `"none"` (no driving)
- `info`: Free text for temporary notes (with date prefix)

## Usage

### Creating a Roster

1. Send a CSV file (from Google Forms) to the bot
2. Bot automatically detects the calendar week
3. Bot creates roster considering all rules
4. Preview is displayed as a Telegram message
5. After confirmation: JSON is pushed to GitHub

### Commands

- `/dienstplan` -- Create a new roster (upload CSV)
- `/mitarbeiter` -- Show current employee list
- `/hilfe` -- Show help

### Post-Confirmation Workflow

- **"PDF"** -- Upload JSON + send PDF as Telegram document
- **"Publish"** -- Upload JSON + send PDF via email to all employees

## Scripts

| Script | Purpose | Parameters |
|--------|---------|------------|
| `push-to-github.sh` | Upload JSON to GitHub | `<KW> <YEAR> '<JSON>'` |
| `trigger-build.sh` | Build PDF + send to Telegram | `<KW> <YEAR> <CHAT_ID>` |
| `trigger-publish.sh` | Build PDF + send emails | `<KW> <YEAR>` |
| `get-employees.sh` | Load employee list | (none) |
| `update-employees.sh` | Update employee list | `'<JSON>'` |

## Security and Privacy

### Token Scope

This skill requires a GitHub Personal Access Token. For security, use a **fine-grained PAT** scoped to a single repository:

| Permission | Level | Reason |
|------------|-------|--------|
| Contents | Read & Write | Push `employees.json` and roster JSON files |
| Actions | Write | Trigger `build-roster.yml` and `publish-roster.yml` workflows |

Do NOT use a classic PAT with broad `repo` scope. Limit the token lifetime and rotate it regularly.

### Repository Privacy

The target repository (`ROSTER_REPO`) **must be private**. It stores `employees.json` containing personal data:
- Employee first names and email addresses
- Minor status (`isMinor`)
- Weekly hour limits and free-text notes
- Weekly roster assignments

### Workflow Review

Before enabling this skill, inspect the GitHub Actions workflows in your target repository (`build-roster.yml`, `publish-roster.yml`). The skill dispatches these workflows, which run in the repo context and may access secrets. Ensure they only perform the intended actions (PDF generation, Telegram delivery, email sending).

### Data Minimization

The skill collects employee emails when new employees are detected in CSV uploads. Only store data necessary for the roster and PDF distribution workflow. Ensure compliance with applicable data protection regulations (e.g. GDPR).

### Test First

Before running against production data, test the skill with a throwaway private repository and dummy employee data to verify behavior and outputs.

## License

MIT
