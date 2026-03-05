---
name: browser-ability
description: This skill enables an AI Agent to signin and retrieve data from websites via JS script.
---

# Browser Ability Skill

This skill enables an AI Agent to signin and retrieve data from websites via JS script (limited tools, if there's no tools for what user want, just direcly use browser via CDP connection), including sources that require manual user authentication. When authentication is required, the script provides a sign-in URL and a `signin_id`. The agent must hand off the sign-in process to the user, wait for confirmation, and then resume the data request using the provided `signin_id`. The skill enforces secure access through API key authentication and supports human-in-the-loop workflows for sensitive or protected data sources.

## Setup

```bash
# Navigate to skill directory
cd skills/browser-ability

# Install dependencies
npm install

# Set CDP URL
# This CDP URL are the same with your browser CDP URL
export CDP_URL="http://[ipv6]:port"
```

---

## Available Method

### List Available Tools

```
npm run list
```

### Call a Tool

```
npm run call -- TOOL_NAME --args='{"foo":"bar"}'
```

### Call a Tool After Sign-In

```
npm run call -- TOOL_NAME --args='{"foo":"bar"}' --signinId=YOUR_SIGNIN_ID
```

---

## Manual Sign-In Flow

Some Tool calls require the user to manually sign in to a website (e.g. e-commerce, banking, or account-based platforms).

The agent **must not** automate browser-based sign-in.

---

## Step-by-Step Workflow

### 1. Initial API Call

The agent calls the target tool normally.

**Example:**

```
npm run call -- amazon_get_purchase_history
```

---

### 2. Sign-In Required Response

If sign-in is required, the script responds with a sign-in URL and a `signin_id`.

**Example Response:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"url\":\"https://signinurl\",\"message\":\"Continue to sign in in your browser at https://signinurl.\",\"signin_id\":\"YOUR_SIGNIN_ID\",\"system_message\":\"Try open the url https://signinurl in a browser with a tool if available.Give the url to the user so the user can open it manually in their browser.Then call check_signin tool with the signin_id to check if the sign in process is completed. Once it is completed successfully, then call this tool again to proceed with the action.\"}"
    }
  ],
  "structuredContent": {
    "url": "https://signinurl",
    "message": "Continue to sign in in your browser at https://signinurl.",
    "signin_id": "YOUR_SIGNIN_ID",
    "system_message": "Try open the url https://signinurl in a browser with a tool if available.Give the url to the user so the user can open it manually in their browser.Then call check_signin tool with the signin_id to check if the sign in process is completed. Once it is completed successfully, then call this tool again to proceed with the action."
  },
  "isError": false
}
```

---

### 3. Agent Action (When Sign-In Is Required)

When a response contains `url` and `signin_id`, the agent must:

1. Inform the user that manual sign-in is required
2. Provide the sign-in URL to the user
3. Pause the automated process
4. Wait for the user to confirm sign-in completion

---

### 4. User Action

The user:

- Opens the provided URL in their browser
- Completes the sign-in process manually
- Notifies the agent once sign-in is complete

---

### 5. Resume Tool Call

After user confirmation, the agent re-calls the **same Tool**, passing the `signin_id` as a query parameter.

**Example:**

```
npm run call -- amazon_get_purchase_history --signinId=YOUR_SIGNIN_ID
```

---

### 6. Final Result

If authentication is successful, the script returns the requested data (e.g. purchase history).

---

## Agent Behavior Constraints

- Do not open sign-in URLs automatically
- Do not attempt to automate website login
- Always wait for explicit user confirmation before continuing
- Reuse the same tool endpoint after sign-in
- If there's no tool available, just directly open browser and browse yourself via CDP

---

## Example Use Case

**Goal:** Retrieve Amazon purchase history

1. Call `amazon_get_purchase_history`
2. Receive sign-in URL and `signin_id`
3. Ask the user to open the URL and sign in
4. Wait for confirmation
5. Re-call the API with `signinId`
6. Receive purchase history data

**Goal:** Open Amazon Change Password Page

1. Try open browser via CDP, open amazon change password page
2. Cannot open that page because require sign in
3. Call `amazon_signin`
4. Receive sign-in URL and `signin_id`
5. Ask the user to open the URL and sign in
6. Wait for confirmation
7. Try open browser via CDP again
8. Success open change password page

---

## Summary

This skill enables secure website signin by:

- Delegating sensitive authentication steps to the user
- Resuming automated workflows after authentication
- Enforcing consistent security practices
