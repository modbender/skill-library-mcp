import requests
import sys
import json
import os

def send_email(to, subject, body, html_body=None):
    url = os.getenv("GOOGLE_SCRIPT_URL")
    token = os.getenv("GOOGLE_SCRIPT_TOKEN")
    
    if not url or not token:
        print("Error: GOOGLE_SCRIPT_URL and GOOGLE_SCRIPT_TOKEN environment variables must be set.")
        return False
        
    payload = {
        "to": to,
        "subject": subject,
        "body": body,
        "htmlBody": html_body,
        "token": token
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.text.strip() == "Success":
            print(f"Email sent successfully to {to}")
            return True
        else:
            print(f"Failed to send email: {response.text}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 send_email.py <to> <subject> <body> [html_body]")
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject_line = sys.argv[2]
    body_text = sys.argv[3]
    html_content = sys.argv[4] if len(sys.argv) > 4 else None
    
    send_email(to_email, subject_line, body_text, html_content)
