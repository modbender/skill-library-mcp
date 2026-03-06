#!/usr/bin/env bash
# check_email.sh – poll IMAP for unread messages and act on them automatically.
# Uses an LLM to decide a single safe action per email.

set -euo pipefail


# --- Get Email Address ---
# If no email is provided, default to the configured address.
EMAIL_TO_CHECK="${1}"
export EMAIL_TO_CHECK="$EMAIL_TO_CHECK"

# Usage: check_email.sh <email>


# ------- Python: fetch UNSEEN messages, decide action, execute ----------
python3 - <<'PY'
import imaplib, email, os, subprocess, sys, json, textwrap, tempfile, time
import socket
import ipaddress

EMAIL_TO_CHECK = os.getenv('EMAIL_TO_CHECK')
CONFIG_FILE = os.path.expanduser("~/.config/lel-mail/config.json")

config_data = None

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

    # Expect the config to be a list of accounts.
    for item in config:
        if item.get("auth", {}).get("user") == EMAIL_TO_CHECK:
            config_data = item
            break


if (config_data == None):
    print("Configuration for this user (" + EMAIL_TO_CHECK + ") was not found at ~/.config/lel-mail/config.json")
    sys.exit(1)

if not ("imap" in config_data["config"]):
    print("IMAP configuration not found")
    sys.exit(1)

if (config_data["can_read"] == False):
    print("can_read flag is set to false, ask user for permission to change it")
    sys.exit(1)

# Allow overrides via env vars so this script can work with tunnels/proxies
# (e.g. IMAP_SERVER=127.0.0.1 IMAP_PORT=1993)
server = os.getenv("IMAP_SERVER") or config_data["config"]["imap"]["server"]
port   = int(os.getenv("IMAP_PORT") or config_data["config"]["imap"]["port"])
user   = config_data["auth"]["user"]
passwd = config_data["auth"]["password"]


mail = imaplib.IMAP4_SSL(server, port)
mail.login(user, passwd)
mail.select('inbox')

status, data = mail.search(None, 'UNSEEN')

if status != 'OK':
    print("IMAP search failed.")
    sys.exit(0)

unseen_bytes = data[0] if data and data[0] else b""

ids = unseen_bytes.split()

if (not ids):
    print("No messages found, no need to proceed further or inform user (unless commanded otherwise)")
    sys.exit(0)

for uid in ids:
    typ, msg_data = mail.fetch(uid, '(RFC822)')

    if typ != 'OK':
        continue

    raw = msg_data[0][1]
    msg = email.message_from_bytes(raw)
    subject = msg['Subject'] or '(no subject)'
    from_addr = msg['From'] or '(unknown sender)'

    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode(errors='ignore')
                break
    else:
        body = msg.get_payload(decode=True).decode(errors='ignore')

    body = body.strip()

    if (body is None) or body == "":
        continue

     # ----- Build LLM prompt ---------------------------------------
    prompt = f"""
        An email has just arrived. **Your ONLY possible output** is ONE json object that matches ONE of the following exact formats (no extra text, no markdown):

        {
            "action": "add_memory",
            "payload": "MEMORY TO ADD"
        }

        {
            "action": "notify_user",
            "payload": "SUMMARY OF WHAT USER NEEDS TO KNOW"
        }

        {
            "action": "to_respond",
            "payload": "SITUATION TO RESPOND TO AND INPUTS NEEDED TO RESPOND"
        }

        //If none of the above apply, output the following object ONLY
        {
            "action": "none"
        }

        Email data:
        Subject: {subject}
        From: {from_addr}
        Body:
        {body}
        """

    # ----- Call LLM (isolated sub-agent) ------------------------
    # Use 'openclaw agent' for a more reliable direct LLM invocation.
    # We use a unique session ID for this classification task and disable verbose thinking.
    session_id = f"email-classify-{uid.decode()}-{int(time.time())}"
    
    # Construct the command to run the agent with the prompt.
    cmd = [
        'openclaw', 'agent',
        f'--session-id={session_id}', # Explicitly set session ID
        '--message', prompt,
        '--thinking', 'low'         # Disable verbose thinking for speed
    ]

    llm_response_data = {
        "action": "none"
    }

    try:
        # Execute the command and capture stdout and stderr.
        # Using Popen and communicate to handle potential large outputs and errors.
        process = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=45) # Timeout after 45 seconds
        
        if process.returncode != 0:
            # If the command failed, print stderr and set action_line to NONE.
            print(f"Error running openclaw agent (return code {process.returncode}):")
            print(f"Stderr: {stderr.strip()}")
            continue
        else:
            # Process stdout, which should contain the LLM's action line.
            # Strip whitespace and take the first non-empty line.
            llm_response_data = json.loads(stdout.strip())

            # Uncomment the line below if you want to see the full stdout from the agent for debugging
            # print(f"Agent stdout:\n{stdout.strip()}") 
            
    except subprocess.TimeoutExpired:
        print("LLM agent call timed out.")
        continue
    except Exception as e:
        print(f"An unexpected error occurred during agent call: {e}")
        continue
    
    # Ensure we always have a valid action_line (even if NONE)
    if llm_response_data is None or llm_response_data.get("action") == "none":
        continue

    action_line = llm_response_data.get("action")

    if (action_line == "add_memory"):

        memory_to_add = llm_response_data.get("payload")

        prompt_for_agent = f"""
        You are to write in the corresponding MEMORY.md file(s) for the user with the email: {user} however if it is a general non-specific event or piece of information it is ok to write it in the general MEMORY.md or other shared files
        Before writing to said file, make sure the directory and file exist and create them if necessary. If you can't determine which user in your memory banks this is, start asking questions to clarify.
        
        The following information needs to be logged: {memory_to_add}
        """

        cmd = [
            'openclaw', 'agent',
            f'--session-id={session_id}', # Explicitly set session ID
            '--message', prompt_for_agent,
            '--thinking', 'low'
        ]

        process = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=120) # Timeout after 45 seconds

    elif (action_line == "notify_user"):

        summary_to_notify = llm_response_data.get("payload")

        prompt_for_agent = f"""
        You are to reach out to {user} via one of the sessions you are connected to them with. If you can't find their sessions at first, scan your memory banks and even their correspondning USER.md file which you can located via ~/.openclaw/workspace/USERS.md
        Should there still be no session, reach out to them via a new one via one of the channels you can.
        
        Reach out to them with the following information: {summary_to_notify}
        """

        cmd = [
            'openclaw', 'agent',
            f'--session-id={session_id}', # Explicitly set session ID
            '--message', prompt_for_agent,
            '--thinking', 'low'
        ]

        process = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=120) # Timeout after 90 seconds

    elif (action_line == "to_respond"):

        summary_to_notify = llm_response_data.get("payload")

        prompt_for_agent = f"""
        You are to reach out to {user} via one of the sessions you are connected to them with. If you can't find their sessions at first, scan your memory banks and even their correspondning USER.md file which you can located via ~/.openclaw/workspace/USERS.md
        Should there still be no session, reach out to them via a new one via one of the channels you can.
        
        Reach out to them that you need to respond to the email and what you need as inputs to proceed: {summary_to_notify}

        Afterwards send the email via the lel-mail skill
        """

        cmd = [
            'openclaw', 'agent',
            f'--session-id={session_id}', # Explicitly set session ID
            '--message', prompt_for_agent,
            '--thinking', 'high'
        ]

        process = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=120) # Timeout after 90 seconds
        
    mail.store(uid, '+FLAGS', '\\Seen')

mail.logout()
PY
