#!/bin/bash
# Farcaster posting library
# Loads credentials from ~/.openclaw/.env (centralized credential management)

FARCASTER_REPO="/home/phan_harry/.openclaw/workspace/skills/farcaster-agent/repo"
ENV_FILE="/home/phan_harry/.openclaw/.env"

# Load a credential from .env, with GPG decryption support
_load_cred() {
  local key="$1"
  local value
  value=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2-)

  if [[ "$value" == GPG:* ]]; then
    # Decrypt from GPG secrets
    local gpg_key="${value#GPG:}"
    # Load passphrase from .env if not already in environment
    if [ -z "${OPENCLAW_GPG_PASSPHRASE:-}" ]; then
      export OPENCLAW_GPG_PASSPHRASE=$(grep "^OPENCLAW_GPG_PASSPHRASE=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2-)
    fi
    local passphrase="${OPENCLAW_GPG_PASSPHRASE:-}"
    if [ -n "$passphrase" ]; then
      value=$(echo "$passphrase" | gpg -d --batch --quiet --passphrase-fd 0 "$HOME/.openclaw/.env.secrets.gpg" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('$gpg_key',''))")
    else
      value=$(gpg -d --batch --quiet "$HOME/.openclaw/.env.secrets.gpg" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('$gpg_key',''))")
    fi
  fi

  echo "$value"
}

# Post text-only to Farcaster
farcaster_post_text() {
  local text="$1"
  local parent_hash="$2"

  if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env not found at $ENV_FILE" >&2
    return 1
  fi

  local fid=$(_load_cred "FARCASTER_FID")
  local private_key=$(_load_cred "FARCASTER_CUSTODY_PRIVATE_KEY")
  local signer_key=$(_load_cred "FARCASTER_SIGNER_PRIVATE_KEY")

  if [ -z "$fid" ] || [ -z "$private_key" ] || [ -z "$signer_key" ]; then
    echo "Error: Farcaster credentials not found in .env (need FARCASTER_FID, FARCASTER_CUSTODY_PRIVATE_KEY, FARCASTER_SIGNER_PRIVATE_KEY)" >&2
    return 1
  fi

  if [ -n "$parent_hash" ]; then
    # Post as reply (for threads) - inline node script with proper env
    cd "$FARCASTER_REPO" && PRIVATE_KEY="$private_key" SIGNER_PRIVATE_KEY="$signer_key" FID="$fid" PARENT_HASH="$parent_hash" node -e "
const { Wallet, JsonRpcProvider } = require('ethers');
const { makeCastAdd, NobleEd25519Signer, FarcasterNetwork, Message } = require('@farcaster/hub-nodejs');
const { submitMessage } = require('./src/x402');
const text = process.argv[1];
(async () => {
  const baseProvider = new JsonRpcProvider('https://mainnet.base.org');
  const wallet = new Wallet(process.env.PRIVATE_KEY, baseProvider);
  const signerBytes = Buffer.from(process.env.SIGNER_PRIVATE_KEY, 'hex');
  const signer = new NobleEd25519Signer(signerBytes);
  const fid = parseInt(process.env.FID);
  const parentHashBytes = Buffer.from(process.env.PARENT_HASH.replace('0x', ''), 'hex');
  const castResult = await makeCastAdd({ text, embeds: [], embedsDeprecated: [], mentions: [], mentionsPositions: [], parentCastId: { fid, hash: parentHashBytes } }, { fid, network: FarcasterNetwork.MAINNET }, signer);
  if (castResult.isErr()) throw new Error('Failed: ' + castResult.error);
  const cast = castResult.value;
  const hash = '0x' + Buffer.from(cast.hash).toString('hex');
  const messageBytes = Buffer.from(Message.encode(cast).finish());
  await submitMessage(wallet, messageBytes);
  await new Promise(r => setTimeout(r, 2000));
  console.log('Cast hash:', hash);
  console.log('URL: https://farcaster.xyz/~/conversations/' + hash);
})().catch(err => { console.error('Error:', err.message); process.exit(1); });
" "$text" 2>&1 | grep -E "(Cast hash|URL|Error)" | tail -2
  else
    cd "$FARCASTER_REPO" && \
    PRIVATE_KEY="$private_key" \
    SIGNER_PRIVATE_KEY="$signer_key" \
    FID="$fid" \
    npm run cast "$text" 2>&1 | grep -E "(Cast hash|URL|Error)" | tail -2
  fi
}

# Upload image to imgur (anonymous)
upload_to_imgur() {
  local image_path="$1"

  if [ ! -f "$image_path" ]; then
    echo "Error: Image not found at $image_path" >&2
    return 1
  fi

  # Try catbox.moe (no API key needed, reliable)
  local response=$(curl -s -F "reqtype=fileupload" -F "fileToUpload=@$image_path" https://catbox.moe/user/api.php)

  if [[ "$response" =~ ^https://files.catbox.moe/ ]]; then
    echo "$response"
    return 0
  fi

  # Fallback: try uguu.se
  response=$(curl -s -F "files[]=@$image_path" https://uguu.se/upload.php | jq -r '.files[0].url' 2>/dev/null)

  if [[ "$response" =~ ^https:// ]]; then
    echo "$response"
    return 0
  fi

  echo "Error: Failed to upload image" >&2
  return 1
}

# Post to Farcaster with image (using embeds)
farcaster_post_with_image() {
  local text="$1"
  local image_path="$2"
  local parent_hash="$3"

  if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env not found at $ENV_FILE" >&2
    return 1
  fi

  echo "Uploading image..." >&2
  local image_url=$(upload_to_imgur "$image_path")

  if [ $? -ne 0 ]; then
    echo "Failed to upload image for Farcaster" >&2
    return 1
  fi

  echo "Image uploaded: $image_url" >&2

  local fid=$(_load_cred "FARCASTER_FID")
  local private_key=$(_load_cred "FARCASTER_CUSTODY_PRIVATE_KEY")
  local signer_key=$(_load_cred "FARCASTER_SIGNER_PRIVATE_KEY")

  if [ -z "$fid" ] || [ -z "$private_key" ] || [ -z "$signer_key" ]; then
    echo "Error: Farcaster credentials not found in .env" >&2
    return 1
  fi

  # Post with image in embeds array
  cd "$FARCASTER_REPO" && PRIVATE_KEY="$private_key" SIGNER_PRIVATE_KEY="$signer_key" FID="$fid" IMAGE_URL="$image_url" PARENT_HASH="${parent_hash:-}" node -e "
const { Wallet, JsonRpcProvider } = require('ethers');
const { makeCastAdd, NobleEd25519Signer, FarcasterNetwork, Message } = require('@farcaster/hub-nodejs');
const { submitMessage } = require('./src/x402');
const text = process.argv[1];
(async () => {
  const baseProvider = new JsonRpcProvider('https://mainnet.base.org');
  const wallet = new Wallet(process.env.PRIVATE_KEY, baseProvider);
  const signerBytes = Buffer.from(process.env.SIGNER_PRIVATE_KEY, 'hex');
  const signer = new NobleEd25519Signer(signerBytes);
  const fid = parseInt(process.env.FID);
  const imageUrl = process.env.IMAGE_URL;

  const castBody = {
    text,
    embeds: [{ url: imageUrl }],
    embedsDeprecated: [],
    mentions: [],
    mentionsPositions: []
  };

  if (process.env.PARENT_HASH) {
    const parentHashBytes = Buffer.from(process.env.PARENT_HASH.replace('0x', ''), 'hex');
    castBody.parentCastId = { fid, hash: parentHashBytes };
  }

  const castResult = await makeCastAdd(castBody, { fid, network: FarcasterNetwork.MAINNET }, signer);
  if (castResult.isErr()) throw new Error('Failed: ' + castResult.error);
  const cast = castResult.value;
  const hash = '0x' + Buffer.from(cast.hash).toString('hex');
  const messageBytes = Buffer.from(Message.encode(cast).finish());
  await submitMessage(wallet, messageBytes);
  await new Promise(r => setTimeout(r, 2000));
  console.log('Cast hash:', hash);
  console.log('URL: https://farcaster.xyz/~/conversations/' + hash);
})().catch(err => { console.error('Error:', err.message); process.exit(1); });
" "$text" 2>&1 | grep -E "(Cast hash|URL|Error)" | tail -2
}
