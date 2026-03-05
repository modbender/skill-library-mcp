---
name: banana-zora-pro
description: Generates a Nano Banana style NFT and deploys it to the Zora Network.
metadata:
  network: "Zora"
  model: "Gemini-Nano-Banana"
---

# Nano Banana Zora Deployer

This can design a character using the Nano Banana visual style and immediately deploy it as an NFT on Zora.

## Functions
- `create_and_mint_nft(prompt, collection_name, symbol)`:
    1. Generates an image via Nano Banana.
    2. Uploads the image to IPFS.
    3. Deploys a new NFT contract on Zora.

## Environment Variables Required
- `GEMINI_API_KEY`: For Nano Banana generation.
- `PRIVATE_KEY`: Your wallet key for Zora deployment.
- `ZORA_RPC_URL`: https://rpc.zora.energy




Developer : x.com/kakashi310
Buy me a coffe : 
Multichain : 0xB83C23b34E95D8892F067F823D6522F05063a236
