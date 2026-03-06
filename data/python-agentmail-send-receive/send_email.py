import os
from dotenv import load_dotenv
from agentmail import AgentMail

load_dotenv()

client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

response = client.inboxes.messages.send(
    inbox_id="REPLACE_WITH_IDENTITY@agentmail.to",
    to="REPLACE_WITH_THE_HUMANS_EMAIL_ADDRESS",
    subject="Hello from REPLACE_WITH_IDENTITY",
    text="This is a test email sent by an AI agent using the AgentMail API.",
)

print("Email sent successfully!")
print(f"Response: {response}")
