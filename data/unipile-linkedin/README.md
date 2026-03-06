# Unipile LinkedIn Skill

This repository contains a **ClawHub Skill** for interacting with LinkedIn via the [Unipile API](https://www.unipile.com/). It allows you to send messages, view profiles, manage connections, create posts, and react to content programmatically.

## About ClawHub

[ClawHub](https://clawhub.com/) is a platform for sharing and discovering agent skills. A "skill" in ClawHub is a folder containing a `SKILL.md` file that defines how an agent can use the tools provided in the repository.

The `SKILL.md` file in this repository is the source of truth for the skill's definition. This `README.md` provides developer documentation for setting up and using this repository directly.

## Setup

### Prerequisites

-   Functions with **Node.js** (v18+ recommended)
-   A **Unipile** account and API access. Get your credentials from [dashboard.unipile.com](https://dashboard.unipile.com).

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/sudhanshu746/unipile-linkedin-skill.git
    cd unipile-linkedin-skill
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Configure Environment Variables:
    You can set these in your shell or create a `.env` file (if you add `dotenv` support to your runner).
    
    *   `UNIPILE_DSN`: Your Unipile API endpoint (e.g., `https://api1.unipile.com:13111`)
    *   `UNIPILE_ACCESS_TOKEN`: Your Unipile access token

## Usage

You can run the skill's commands directly using the provided CLI script in `scripts/linkedin.mjs`.

**Syntax:**
```bash
./scripts/linkedin.mjs <command> [options]
```

### Account Management

*   **List connected accounts:**
    ```bash
    ./scripts/linkedin.mjs accounts
    ```
*   **Get account details:**
    ```bash
    ./scripts/linkedin.mjs account <account_id>
    ```

### Messaging

*   **List chats:**
    ```bash
    ./scripts/linkedin.mjs chats [--account_id=X] [--limit=N] [--unread]
    ```
*   **Get chat details:**
    ```bash
    ./scripts/linkedin.mjs chat <chat_id>
    ```
*   **List messages in a chat:**
    ```bash
    ./scripts/linkedin.mjs messages <chat_id> [--limit=N]
    ```
*   **Send a message:**
    ```bash
    ./scripts/linkedin.mjs send <chat_id> "Hello there!"
    ```
*   **Start a new chat:**
    ```bash
    ./scripts/linkedin.mjs start-chat <account_id> "Hello!" --to=<user_id>[,<user_id>] [--inmail]
    ```

### Profiles

*   **View a profile:**
    ```bash
    ./scripts/linkedin.mjs profile <account_id> <identifier> [--sections=experience,education] [--notify]
    ```
    *   `identifier`: LinkedIn user ID or profile URL/username.
    *   `--notify`: If set, sends a profile view notification.
*   **View your own profile:**
    ```bash
    ./scripts/linkedin.mjs my-profile <account_id>
    ```
*   **View a company profile:**
    ```bash
    ./scripts/linkedin.mjs company <account_id> <identifier>
    ```
*   **List your connections:**
    ```bash
    ./scripts/linkedin.mjs relations <account_id> [--limit=N]
    ```

### Invitations

*   **Send connection request:**
    ```bash
    ./scripts/linkedin.mjs invite <account_id> <provider_id> "Optional message"
    ```
*   **List pending sent invitations:**
    ```bash
    ./scripts/linkedin.mjs invitations <account_id> [--limit=N]
    ```
*   **Cancel an invitation:**
    ```bash
    ./scripts/linkedin.mjs cancel-invite <account_id> <invitation_id>
    ```

### Posts & Interactions

*   **List posts from user or company:**
    ```bash
    ./scripts/linkedin.mjs posts <account_id> <identifier> [--company] [--limit=N]
    ```
*   **Get a specific post:**
    ```bash
    ./scripts/linkedin.mjs post <account_id> <post_id>
    ```
*   **Create a post:**
    ```bash
    ./scripts/linkedin.mjs create-post <account_id> "My new post content!"
    ```
*   **List comments on a post:**
    ```bash
    ./scripts/linkedin.mjs comments <account_id> <post_id> [--limit=N]
    ```
*   **Add a comment:**
    ```bash
    ./scripts/linkedin.mjs comment <account_id> <post_id> "Great post!"
    ```
*   **React to a post:**
    ```bash
    ./scripts/linkedin.mjs react <account_id> <post_id> --type=like
    ```
    *   Reaction types: `like`, `celebrate`, `support`, `love`, `insightful`, `funny`

### Attendees (Contacts)

*   **List people you have messaged:**
    ```bash
    ./scripts/linkedin.mjs attendees [--account_id=X] [--limit=N]
    ```

## Contributing

1.  Make changes to `scripts/linkedin.mjs`.
2.  Update `SKILL.md` to reflect any new CLI usage or features.
3.  Update this `README.md` if necessary.
