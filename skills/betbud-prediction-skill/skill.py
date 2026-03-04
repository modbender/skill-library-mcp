import os
import json
import requests
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

TWITTERAPI_IO_KEY = os.getenv("TWITTERAPI_IO_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

if not all([TWITTERAPI_IO_KEY, ANTHROPIC_API_KEY, RPC_URL, PRIVATE_KEY, UNSPLASH_ACCESS_KEY]):
    print("ERROR: Missing keys in .env")
    exit(1)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

CONTRACT_ADDRESS = "0x5bD295b337911160b1Abcba7AFca93D941c1e839"
CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "durationInDays", "type": "uint256"}],
        "name": "openNewMarket",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "currentMarketNumber",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "minimumDeposit",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("ERROR: Cannot connect to RPC")
    exit(1)

account = w3.eth.account.from_key(PRIVATE_KEY)
contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)

BUBBLE_ROOT = "https://betbud.live/api/1.1/obj"
DATA_TYPE = "Events"

CACHE_FILE = "recent_predictions.json"

PREMIUM_ACCOUNTS = [
    "WatcherGuru",
    "tier10k",
    "CoinDesk",
    "Cointelegraph",
    "TheBlock__",
]

def load_recent_predictions():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                print(f"Loaded {len(data)} recent predictions from cache")
                return data
    except Exception as e:
        print(f"Could not load cache: {e}")
    return []

def save_prediction(question):
    recent = load_recent_predictions()
    recent.append({
        "question": question,
        "timestamp": datetime.now().isoformat()
    })
    recent = recent[-20:]
    with open(CACHE_FILE, 'w') as f:
        json.dump(recent, f)
    print("Saved to cache")

def get_diverse_content(category="crypto", limit=10):
    since = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    
    tweets = get_hot_topics(category, limit)
    
    for username in PREMIUM_ACCOUNTS:
        query = f"from:{username} filter:has_engagement min_faves:50 since:{since}"
        user_tweets = x_keyword_search(query, limit=3)
        tweets.extend(user_tweets)
    
    unique_tweets = []
    seen = set()
    for t in tweets:
        text = t.get('text', '') or t.get('full_text', '')
        if text not in seen:
            seen.add(text)
            unique_tweets.append(t)
    
    unique_tweets = sorted(unique_tweets, key=lambda x: (x.get('likeCount', 0) or 0) + (x.get('retweetCount', 0) or 0), reverse=True)[:limit]
    
    print(f"Got {len(unique_tweets)} unique diverse tweets")
    return unique_tweets

def get_hot_topics(category="crypto", limit=10):
    since = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    query = f"{category} (debate OR controversy OR hot OR trending) min_faves:100 since:{since} filter:has_engagement"
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {"x-api-key": TWITTERAPI_IO_KEY}
    params = {"query": query, "count": limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        tweets = data.get('tweets', []) or data.get('data', [])
        print(f"Fetched {len(tweets)} trending tweets")
        return tweets
    except Exception as e:
        print(f"Twitter trending error: {str(e)}")
        return []

def x_keyword_search(query, limit=3):
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {"x-api-key": TWITTERAPI_IO_KEY}
    params = {"query": query, "count": limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        tweets = data.get('tweets', []) or data.get('data', [])
        print(f"Fetched {len(tweets)} from premium account")
        return tweets
    except Exception as e:
        print(f"Premium account search error: {str(e)}")
        return []

def analyze_with_claude(tweets, recent_predictions):
    recent_qs = [p['question'] for p in recent_predictions]
    recent_str = json.dumps(recent_qs) if recent_predictions else "None"
    
    prompt = f"""From these X posts: {json.dumps(tweets, default=str)}

Avoid these recent questions: {recent_str}

Pick a NEW debatable hot topic and create a yes/no prediction market proposal in valid JSON:
{{
  "question": "Will [event] happen by [date]?",
  "duration_days": 1-14,
  "resolution_criteria": "How to resolve (sources)",
  "score": 8.0-10.0,
  "reasoning": "Why hot",
  "sources": ["link1", "link2"],
  "category": "One of: Politics, Elections, Sport, Gaming, Crypto, Price, Tech, People, Personal, music, Pop, other"
}}
Return ONLY JSON, no extra text, no markdown."""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        temperature=0.8,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip()
    
    start = text.find('{')
    end = text.rfind('}') + 1
    if start != -1 and end > start:
        text = text[start:end]
    
    text = text.replace('\n', ' ').replace('  ', ' ').strip()
    
    print(f"Claude raw: {text[:200]}")
    
    try:
        return json.loads(text)
    except Exception as e:
        print(f"JSON parse error: {str(e)}")
        print(f"Raw text: {text}")
        raise

def get_professional_image(question, category):
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {
        "query": f"{category} finance betting prediction market professional illustration",
        "per_page": 1,
        "orientation": "landscape"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        image_url = data['results'][0]['urls']['regular'] if data['results'] else ""
        print(f"Got image: {image_url[:50]}..." if image_url else "No image")
        return image_url
    except Exception as e:
        print(f"Unsplash error: {e}")
        return ""

def get_min_deposit():
    try:
        min_wei = contract.functions.minimumDeposit().call()
        min_eth = w3.from_wei(min_wei, 'ether')
        print(f"Minimum deposit: {min_eth} ETH")
        return min_wei
    except Exception as e:
        print(f"Error fetching min deposit: {str(e)}")
        return w3.to_wei(0.0001, 'ether')

def create_market(duration_days):
    min_deposit = get_min_deposit()
    current_num = contract.functions.currentMarketNumber().call()
    new_num = current_num + 1
    
    try:
        tx = contract.functions.openNewMarket(duration_days).build_transaction({
            'from': account.address,
            'value': min_deposit,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'maxFeePerGas': w3.to_wei('2', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('1', 'gwei'),
        })
        
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            explorer = f"https://sepolia.basescan.org/tx/{tx_hash.hex()}"
            print(f"Market #{new_num} created: {explorer}")
            return new_num, tx_hash.hex(), explorer
        else:
            print("TX failed")
            return None, None, None
    except Exception as e:
        print(f"Contract error: {str(e)}")
        return None, None, None

def register_bubble_event(proposal, market_num, creator_wallet, image_url):
    url = f"{BUBBLE_ROOT}/{DATA_TYPE}"
    headers = {
        "Authorization": "Bearer eb14b9297060b03751dce5497d07a88f",
        "Content-Type": "application/json"
    }
    
    valid_cats = ["Politics", "Elections", "Sport", "Gaming", "Crypto", "Price", "Tech", "People", "Personal", "music", "Pop", "other"]
    cat = proposal.get("category", "Crypto")
    if cat not in valid_cats:
        cat = "other"
    
    data = {
        "tittle": proposal.get("question", "No title"),
        "rules": proposal.get("resolution_criteria", "No rules"),
        "duration ( days ) ": proposal.get("duration_days", 7),
        "category": cat,
        "walletID-event-creator": creator_wallet,
        "Event number": market_num,
        "closed?": False,
        "overrided ? ": False,
        "rewardClaimed?": False,
        "privacy": "public",
        "Reward amount": 0,
        "final outcome": "",
        "OUTCOME": "",
        "event Preview URL ": image_url,
        "image": image_url,
        "isBot?": True
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        print("Bubble registered successfully:", resp.json())
    except Exception as e:
        print(f"Bubble error: {str(e)}")
        if 'resp' in locals():
            print("Status:", resp.status_code)
            print("Response:", resp.text[:300])

def main():
    print("\n=== PRODUCTION PREDICTION MARKET CREATOR ===\n")
    
    recent = load_recent_predictions()
    
    topics = get_diverse_content()
    
    if not topics:
        print("No tweets")
        return
    
    proposal = analyze_with_claude(topics, recent)
    
    print("Proposal:", json.dumps(proposal, indent=2))
    
    image_url = get_professional_image(proposal["question"], proposal.get("category", "Crypto"))
    
    market_num, tx_hash, explorer = create_market(proposal["duration_days"])
    
    if market_num:
        register_bubble_event(proposal, market_num, account.address, image_url)
        save_prediction(proposal["question"])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()