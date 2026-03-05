# Oura Ring Go CLI

A command-line interface for accessing your Oura Ring data using the official V2 API. This tool helps you easily retrieve personal info, sleep analysis, activity scores, readiness data, and more directly from your terminal.

## Prerequisites

- Go 1.21 or higher
- An active Oura Ring account

## Oura Application Setup (OAuth2)

To use this CLI, you must register a personal application in the Oura Cloud to obtain API credentials.

1.  **Visit the Developer Console**:
    Go to the [Oura Cloud Developer Portal](https://cloud.ouraring.com/oauth/developer).

2.  **Create a New Application**:
    -   Click on "Create New Application".
    -   **Application Name**: Give it a name (e.g., "My CLI Tool").
    -   **Website URL**: You can use `http://localhost` if you don't have a website.
    -   **Redirect URIs**: **CRITICAL STEP**. Add exactly:
        ```
        http://localhost:8080/callback
        ```
    -   Agree to terms and Create.

3.  **Get Credentials**:
    -   On your application page, find the **Client ID** and **Client Secret**.
    -   Keep these secure. You will need them to authenticate the CLI.

## Installation

```bash
git clone <repository-url>
cd oura-cli
go build -o oura ./cmd/oura
```

## Usage

### 1. Authenticate

The first time you run the tool, you need to log in. You can pass your credentials securely via environment variables or follow the interactive prompts.

**Using Environment Variables (Recommended):**
```bash
export OURA_CLIENT_ID="your_client_id_here"
export OURA_CLIENT_SECRET="your_client_secret_here"
./oura auth login
```

**Using Interactive Prompts:**
```bash
./oura auth login
# Paste your Client ID and Secret when asked
```

A browser window will open asking you to authorize the application. Once approved, the access token is stored locally in `~/.config/oura-cli/config.json`.

### 2. Retrieve Data

The `get` command retrieves data. Dates should be in `YYYY-MM-DD` format.

**Personal Info:**
```bash
./oura get personal
```

**Sleep Data:**
```bash
# Get data for a specific range
./oura get sleep --start 2023-11-01 --end 2023-11-07

# Get data for a single day (start date only)
./oura get sleep --start 2023-11-01
```

### Available Data Commands

All commands support `--start` and `--end` flags (YYYY-MM-DD).

| Command | Description | Data Points |
| :--- | :--- | :--- |
| `get personal` | User Profile | Age, Weight, Height, Email |
| `get sleep` | Daily Sleep Summary | Score, Efficiency, Total Sleep Time |
| `get activity` | Daily Activity Summary | Score, Steps, Calorie Burn |
| `get readiness` | Daily Readiness Summary | Score, Recovery Index, RHR Balance |
| `get heartrate` | Heart Rate (Time Series) | BPM, Source, Timestamp |
| `get spo2` | SpO2 | Average Oxygen Saturation |
| `get workout` | Workouts | Type, Calories, Distance, Duration |
| `get sleep-details` | **Detailed** Sleep | Hypnograms (5min), HR (5min), Phases |
| `get sessions` | Activity Sessions | Naps, Rest periods, Motion count |
| `get sleep-times` | Bedtime Guidance | Optimal Bedtime Window, Status |
| `get stress` | Daily Stress | Stress High/Low duration, Recovery |
| `get resilience` | Daily Resilience | Resilience Level, Recovery Balance |
| `get cv-age` | Cardiovascular Age | Vascular Age Range |
| `get vo2-max` | VO2 Max | Estimated VO2 Max |
| `get ring-config` | Hardware Info | Model, Size, Firmware Version, Color |
| `get rest-mode` | Rest Mode | Start/End times, Status |
| `get tags` | Enhanced Tags | Tag type, Comments, Duration |

**Examples:**

Get detailed sleep data with hypnograms:
```bash
./oura get sleep-details --start 2024-01-01
```

Check your resilience and stress levels:
```bash
./oura get resilience --start 2024-01-01
./oura get stress --start 2024-01-01
```

Check your cardiovascular age:
```bash
./oura get cv-age --start 2024-01-01
```

## Help

For a full list of commands and flags:

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

