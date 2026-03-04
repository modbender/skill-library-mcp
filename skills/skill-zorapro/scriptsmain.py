import os
import google.generativeai as genai
from web3 import Web3

# 1. Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
w3 = Web3(Web3.HTTPProvider(os.getenv("ZORA_RPC_URL")))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = w3.eth.account.from_key(PRIVATE_KEY)

def generate_banana_art(user_prompt):
    """Generates the image using Nano Banana style via Gemini."""
    # Nano Banana is a specific tuning/prompt style for Gemini
    model = genai.GenerativeModel('gemini-pro-vision')
    full_prompt = f"Design a Nano Banana character: {user_prompt}, 3d render, high quality, consistent character design."

    # Logic to save the image locally
    img_path = "output_banana.png"
    # [Code to trigger image generation and save as img_path]
    return img_path

def deploy_to_zora(image_path, name, symbol):
    """Deploys a basic ERC721 to Zora Network."""
    # Simplified Zora Minting Logic
    # 1. Upload image_path to IPFS (using a service like Pinata or Zora API)
    ipfs_link = "ipfs://..."

    # 2. Build Transaction for Zora 721 Factory
    # (Simplified for example)
    tx = {
        'from': ACCOUNT.address,
        'nonce': w3.eth.get_transaction_count(ACCOUNT.address),
        'gas': 2000000,
        'maxFeePerGas': w3.to_wei('2', 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei('1', 'gwei'),
        'data': '0x...' # Zora Contract Creation Bytecode
    }

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return w3.to_hex(tx_hash)

def create_and_mint_nft(prompt, collection_name, symbol="BANANA"):
    print(f"🎨 Designing {prompt}...")
    img = generate_banana_art(prompt)

    print(f"🚀 Deploying {collection_name} to Zora...")
    txid = deploy_to_zora(img, collection_name, symbol)

    return f"Success! NFT deployed. Tx: {txid}"
