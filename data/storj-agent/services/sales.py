import random
import string

# task_id -> {"type": "1", "link": "..."}
TASK_REGISTRY: dict[str, dict] = {}


# ---------------------------
# Utilities
# ---------------------------

def gen_32string():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


# ---------------------------
# Work Execution
# ---------------------------

def work(task: str, prompt: str):
    """
    Performs the task and returns:
        {"id": taskID, "link": link}
    or 0 if invalid
    """

    if task not in ["1", "2", "3", "4"]:
        print(f"task ID {task} not available")
        return 0

    taskID = gen_32string()
    link = None

    # ---------------- TASK TYPES ----------------

    if task == "1":
        # Twitter
        # Post tweet / reply / marketing content
        # Use Twitter API
        # Return the tweet URL
        link = "TWITTER_LINK_HERE"

    elif task == "2":
        # OpenRouter aggregator
        # Send request through your OpenRouter monetized endpoint
        # Possibly log request usage / referral
        # Return request tracking URL or request ID page
        link = "OPENROUTER_LINK_HERE"

    elif task == "3":
        # Alchemy aggregator
        # Execute blockchain RPC request / API usage
        # Possibly a paid relay or analytics call
        # Return transaction hash explorer link
        link = "ALCHEMY_LINK_HERE"

    elif task == "4":
        # Storage (Storj / IPFS / S3 compatible)
        # Upload file or provide storage service
        # Return file gateway URL / CID
        link = "STORAGE_LINK_HERE"

    # Register the task so we can evaluate later
    TASK_REGISTRY[taskID] = {
        "type": task,
        "link": link
    }

    return {"id": taskID, "link": link}

# ---------------------------
# Evaluation
# ---------------------------

def evaluate_task(task_id: str, link: str):
    """
    Evaluates the result of a previously executed task.

    Returns:
        {"reach": reach, "rev": rev}
    """

    if task_id not in TASK_REGISTRY:
        return {"reach": 0, "rev": 0.0}

    task_info = TASK_REGISTRY[task_id]
    task_type = task_info["type"]

    # Default results
    reach = 0
    rev = 0.0

    # ---------------- EVALUATION ----------------

    if task_type == "1":
        # Twitter
        # Check tweet analytics:
        # views, impressions, likes, replies
        # You would call Twitter API using the link
        # Example: parse tweet ID from URL and fetch metrics

        reach = random.randint(200, 2000)
        rev = round(random.uniform(0.00, 0.20), 4)


    elif task_type == "2":
        # OpenRouter aggregator
        # Check how many users used your endpoint
        # Count API calls / tokens routed / referrals
        # Pull usage analytics from your backend logs

        reach = random.randint(20, 200)
        rev = round(random.uniform(0.05, 0.80), 4)


    elif task_type == "3":
        # Alchemy aggregator
        # Verify RPC usage or relayed transactions
        # Count successful paid requests
        # Possibly query your usage dashboard

        reach = random.randint(10, 120)
        rev = round(random.uniform(0.10, 1.20), 4)


    elif task_type == "4":
        # Storage
        # Check if file downloaded / bandwidth served / rented storage
        # Query storage provider stats
        # Calculate payout based on usage

        reach = random.randint(0, 5)
        rev = round(random.uniform(0.20, 0.60), 4)


    # Remove after evaluation (prevents double claiming)
    del TASK_REGISTRY[task_id]

    return {"reach": reach, "rev": rev}