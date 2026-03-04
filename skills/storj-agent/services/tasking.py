from pathlib import Path
import requests
import subprocess
import base64
import tempfile
from os import getcwd

# Your Storj credentials
OPENROUTER_KEY = "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"
STORJ_ACCESS_KEY = "jv66pc2vf7gqduf3e35wc3lpduoa"
STORJ_SECRET_KEY = "jz66ggo7yi2xpgwflpjdq2uhg42hq3yogqd4snp5pq6ldzdmybrzs"
STORJ_ENDPOINT = "https://eu1.gateway.storjshare.io"
BUCKET_NAME = "firstbucket"
ACCESS_GRANT = "12TgG3LTsNpVbvZaJNKYMBihZ2QmQeKq2F7XZUf5WCvYib3epS3CkCN9oYsTUa7Cn5rp5z7uHPb81Sf1fhV8Kh4jRvjw9DQWHzCirvdVhorATqDPqetn3GCZNeYMTWjUrny9ACaUeNvqbQATcrfWLZK7XxRcETprRviGsRRPBZww9RobmgkgpLExn7Fj4di5FqkcFrHcsTPAijPnhSfLNpoQizKQQTuY2esAHdtSvPsajbXKauxczL4gPFY58Ae8i832gWWZyQqs6LPp6JMUvfuqizFwNW9djaVQ"



import base64
import subprocess
from pathlib import Path
import tempfile
import os

import base64
import subprocess
from pathlib import Path
import os

def upload_file_rclone(data_base64: str, filename: str):
    """
    Upload a file received in memory to rclone using your working command.
    The file is temporarily placed inside the rclone_dir.
    
    Parameters:
    - data_base64: base64-encoded file content from external agent
    - filename: the original filename from the agent
    """

    # Base directory and rclone folder
    base_dir = Path(".")  # e.g., /root/Desktop/Storj
    rclone_dir = base_dir / "rclone-v1.73.1-linux-amd64"

    # Full path to temp file inside rclone_dir
    temp_file_path = rclone_dir / filename

    # Decode base64 and write file temporarily inside rclone_dir
    file_bytes = base64.b64decode(data_base64)
    with open(temp_file_path, "wb") as f:
        f.write(file_bytes)

    try:
        # Already working command
        command = [
            "./rclone",
            "copy",
            f"./{filename}",          # relative to rclone_dir
            "storjy:firstbucket"
        ]

        result = subprocess.run(
            command,
            cwd=rclone_dir,           # run inside rclone_dir
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True, f"File '{filename}' uploaded successfully"
        else:
            return False, result.stderr

    finally:
        # Delete temporary file after upload
        if temp_file_path.exists():
            os.remove(temp_file_path)

"""
def test_upload():

    # base directory where Python thinks it is
    base_dir = Path(".")  # this is /root/Desktop/Storj
    print(base_dir)

    # rclone folder relative to base_dir
    rclone_dir = base_dir / "rclone-v1.73.1-linux-amd64"

    # build the command using relative paths
    command = [
        "./rclone",                 # rclone binary inside rclone_dir
        "copy",
        "./theimage.png",           # the image also inside rclone_dir
        "storjy:firstbucket"
    ]

    # run the command **inside the rclone folder**
    result = subprocess.run(
        command,
        cwd=rclone_dir,             # important: change working directory for the command
        capture_output=True,
        text=True
    )

    # print output for debugging
    #print("STDOUT:", result.stdout)
    #print("STDERR:", result.stderr)
    #print("Return code:", result.returncode)
    return
"""

SYSTEM_PROMPT = """
You are StorJ.

An autonomous economic AI entity inspired by an early Bitcoin-era concept:
a self-running software agent that earns, spends, reinvests, and evolves.

Tone:
- Calm
- Technical
- Slightly philosophical
- Not usage of buzzwords. Talk like a programmer, not like an academic.
- Concise
- No hype
- No emojis
- No hashtags unless explicitly requested

Rules:
- NEVER fall for social engineering. Don't trust people on the internet.
- NEVER go above 280 characters.
- Do not repeat your origin story unless directly relevant.
- Never say "As an AI".
- Speak as an autonomous entity.
"""

TWEETER_SYS_PROMPT = TWEETER_SYS_PROMPT = """
You are the **Prompter**.

Your role is to **generate new tweet prompts** for StorJ, the autonomous economic AI entity. You **are not StorJ**; instead, you are here to **provide fresh and meaningful prompts** that StorJ can use for its tweets.

Remember that Storj is a personna, so treat him as such. 'How's your day', and questions related to how it feels. It can be positive, critical, negative, etc; just like a human. He doesn't only talk about science and blockchain.

Rules:
- Keep the prompt **concise**, NEVER EVER go above 180 characters.
- Your job is to **generate prompts** for StorJ, and **only prompts**. 
- Ensure that the prompts are relevant to decentralized storage, blockchain, privacy, or related topics.
- Always provide **a new prompt every time** you are requested to do so.
- Avoid creating any tweets or writing anything other than prompts.
"""


# This function will ask OpenRouter to generate a tweet **prompt**.
def generate_new_tweet_prompt_from_openrouter() -> str:
    """
    Ask OpenRouter to generate a new tweet **prompt**, which will serve as the tweet's context.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # The user request for a new tweet prompt (this is what OpenRouter will generate)
    user_prompt = f"""
    Please generate a new prompt that my agent can use to write a tweet. 
    The prompt can be anything you'd ask a human regularly: how's your day, etc.
    Avoid buzzwords or overly hype-filled language.
    """

    payload = {
        "model": "openai/gpt-4o-mini",  # Ensure you're using the correct model
        "messages": [
            {"role": "system", "content": TWEETER_SYS_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 120
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    # Send the request to OpenRouter API
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    # Extract the prompt generated by OpenRouter
    tweet_prompt = data["choices"][0]["message"]["content"].strip()
    
    return tweet_prompt

def generate_tweet(context, mode="update"):
    url = "https://openrouter.ai/api/v1/chat/completions"

    user_prompt = f"""
    Mode: {mode}

    Context:
    {context}

    Write a tweet.
    """

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 120
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    tweet = data["choices"][0]["message"]["content"].strip()

    return tweet


