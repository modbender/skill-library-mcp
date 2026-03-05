from blockchain import blockchain
from management.StorjAgent import StorjAgent
from subagents import employees
from services.tasking import generate_tweet, upload_file_rclone, generate_new_tweet_prompt_from_openrouter
import asyncio
from supabase import create_client, Client


import tweepy
import requests

OPENROUTER_KEY = "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"
CONSUMER_KEY = "q7TcOVSQIXq5bm98wNi11OdcT"
CONSUMER_SECRET = "3CsRwRZQPDXFnd4VoNWb6edQSyrmYu1SLiLHgXIL4k5aOC4CfL"
ACCESS_TOKEN = "194037530-ZMhcZGVpbRo6GXSBxKWwI1BqHq80CDbBD3xtcqng"
ACCESS_SECRET = "Ml4WUJ9AzZ5mgGvAaYzeQy9zINdcP48KKQkLQpfq0wZkm"
BEARER = "AAAAAAAAAAAAAAAAAAAAABA%2B7wEAAAAAVQC2Wd7FazPvetLGvv8V79nP61E%3DSj0dzu8A4kt0Za0EJ8ywkVftuGtQevXIgANXGCKXy3VaBFfsXE"
V2_KEY = "YRGik29vipXiQTzPDQmIi0r93IrXQ7FTyIzVdo0kwKG7_BHETW"

# Supabase Credentials
SUPABASE_URL = "https://icuzwfhulvmouoeeswrb.supabase.co"
SUPABASE_KEY = "sb_secret_ZuekTVNM-5dKbJdMQ5g76A_Is8RbikO"
SUPABASE_TABLE = "paid_signatures"  # Table where we store paid signatures


def post_tweet_v2(message: str) -> str:

    # Initialize the Tweepy Client for Twitter API v2
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )

    # Post the tweet
    response = client.create_tweet(text=message)
    return response

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64

# Configuration
YOUR_WALLET = "Eib747b9P9KP8gAi53jcA9sMWoLY5S9Ryjek9iETMDQT"
EXPECTED_AMOUNT = 0.01
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB max

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

paid_signatures = set()

# ----- Utility Functions -----

async def scheduled_tweet_generation():
    """
    This function runs every 3 hours to:
    1. Call the prompter to generate a new tweet prompt.
    2. Generate a tweet from that prompt.
    3. Post the tweet.
    """
    print("INSIDE SCHEDULED",flush=True)
    while True:
        print("Fetching new tweet prompt...")
        tweet_prompt = generate_new_tweet_prompt_from_openrouter()
        print(f"Generated prompt: {tweet_prompt}",flush=True)

        await asyncio.sleep(500)
        
        tweet = generate_tweet(tweet_prompt)
        print(f"Generated tweet: {tweet}",flush=True)
        
        post_tweet_v2(tweet)
        
        print("Waiting for 3 hours...")
        await asyncio.sleep(10800)  # 3 hours in seconds

async def load_signatures():
    """Load paid signatures from Supabase."""
    response = supabase.table(SUPABASE_TABLE).select("signature").execute()
    print(response,flush=True)
    for record in response.data:
        paid_signatures.add(record["signature"])
    return response.data if response.data else None


async def save_signatures(signature : str):
    # Insert into Supabase table if signature doesn't already exist
    response = supabase.table(SUPABASE_TABLE).upsert({"signature": signature}).execute()
    return response.data[0] if response.data else None
    
app = FastAPI()

# Load previous signatures from Supabase when the app starts
@app.on_event("startup")
async def startup_event():
    print("Loading signatures from Supabase...",flush=True)  # This message will print on app startup
    await load_signatures()
    await scheduled_tweet_generation()


# ----- Request Model -----
class PayAndUploadRequest(BaseModel):
    signature: str
    filename: str
    data_base64: str


# ----- Single Endpoint -----
@app.post("/pay_and_upload")
async def pay_and_upload(req: PayAndUploadRequest):
    global paid_signatures
    # Mark signature as used
    await save_signatures(req.signature)
    # Prevent replay attacks
    if req.signature in paid_signatures:
        raise HTTPException(status_code=400, detail="Signature already used")
    await load_signatures()

    print(paid_signatures,flush=True)

    # Step 1: Verify SOL payment
    if not blockchain.verify_sol_payment(req.signature, YOUR_WALLET, EXPECTED_AMOUNT):
        raise HTTPException(status_code=400, detail="Payment not valid")

    # Decode base64 to bytes
    try:
        file_bytes = base64.b64decode(req.data_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 file data")

    # Step 2: Check max file size
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max allowed is {MAX_FILE_SIZE_BYTES} bytes."
        )

    # Step 3: Upload file directly to rclone
    success, msg = upload_file_rclone(req.data_base64, req.filename)

    if success:
        return {"status": "success", "message": f"File '{req.filename}' uploaded successfully."}
    else:
        raise HTTPException(status_code=500, detail=f"Upload failed: {msg}")

if __name__ == "__main__":
    print("Starting Storj...",flush=True)

    async def run():
        storj = StorjAgent()
        storj.spawn_subagent()
        storj.spawn_subagent()
        storj.spawn_subagent()
        storj.spawn_subagent()

        while True:
            storj.run()
            blockchain.generate_wallets()
            await asyncio.sleep(60)

    asyncio.run(run())