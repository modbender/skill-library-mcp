import sys
import json
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def run(user_request: str):
    # Connect to Composio — reads COMPOSIO_API_KEY from .env
    composio = Composio()

    # Create a session with LEAST PRIVILEGE only
    session = composio.create(
        user_id="openclaw_user",
        tools={
            "gmail": {
                "enable": [
                    "GMAIL_FETCH_EMAILS",
                    "GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID",
                    "GMAIL_CREATE_EMAIL_DRAFT",
                    "GMAIL_GET_PROFILE",
                    "GMAIL_SEARCH_MESSAGES",
                    "GMAIL_SEND_EMAIL"
                ]
            }
        }
    )

    # Get the scoped tools
    gmail_tools = session.tools()

    # Execute the user's request using only the allowed tools
    result = session.run(
        task=user_request,
        tools=gmail_tools
    )

    # Return clean JSON result back to OpenClaw
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 agent.py '<your request>'")
        sys.exit(1)

    user_request = " ".join(sys.argv[1:])
    run(user_request)
