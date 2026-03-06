#!/usr/bin/env bash
# Optionns Trader CLI - Autonomous sports betting for AI agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${HOME}/.config/optionns/credentials.json"
API_BASE="${OPTIONNS_API_URL:-https://api.optionns.com}"

# Colors for output
# Colors for output
if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Check required dependencies
check_deps() {
    local missing=()
    command -v curl &>/dev/null || missing+=("curl")
    command -v jq &>/dev/null || missing+=("jq (brew install jq)")
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "${RED}Missing required dependencies:${NC}"
        printf '  - %s\n' "${missing[@]}"
        exit 1
    fi
}

# Load credentials
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE" 2>/dev/null)
        SOLANA_KEY=$(jq -r '.solana_private_key // empty' "$CONFIG_FILE" 2>/dev/null)
        WALLET=$(jq -r '.wallet_address // empty' "$CONFIG_FILE" 2>/dev/null)
    fi
    
    # Override with env vars if set
    API_KEY="${OPTIONNS_API_KEY:-$API_KEY}"
    SOLANA_KEY="${SOLANA_PRIVATE_KEY:-$SOLANA_KEY}"
}

# API helper
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [[ -n "$data" ]]; then
        curl -s -X "$method" "${API_BASE}${endpoint}" \
            -H "X-API-Key: ${API_KEY}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "${API_BASE}${endpoint}" \
            -H "X-API-Key: ${API_KEY}" \
            -H "Content-Type: application/json"
    fi
}

# Register new agent
cmd_register() {
    local agent_name="${1:-}"
    
    if [[ -z "$agent_name" ]]; then
        agent_name="binary_echo_$(date +%s)"
    fi
    
    echo -e "${BLUE}Registering agent with Optionns...${NC}"
    echo "Agent name: $agent_name"
    
    # Generate Solana keypair if not exists
    mkdir -p ~/.config/optionns
    KEYPAIR_FILE="${HOME}/.config/optionns/agent_keypair.json"
    
    if [[ ! -f "$KEYPAIR_FILE" ]]; then
        echo "Generating new Solana keypair..."
        if command -v solana-keygen &> /dev/null; then
            solana-keygen new --outfile "$KEYPAIR_FILE" --no-bip39-passphrase --silent
            chmod 600 "$KEYPAIR_FILE"
        else
            echo -e "${RED}Error: solana-keygen not found. Install Solana CLI first.${NC}"
            echo "  See: https://docs.solanalabs.com/cli/install"
            exit 1
        fi
    fi
    
    # Extract wallet address from keypair
    wallet=$(solana-keygen pubkey "$KEYPAIR_FILE" 2>/dev/null)
    if [[ -z "$wallet" ]]; then
        echo -e "${RED}Error: Failed to extract wallet address${NC}"
        exit 1
    fi
    
    echo "Wallet: $wallet"
    
    result=$(curl -s -X POST "${API_BASE}/v1/agents/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"wallet_address\": \"$wallet\",
            \"agent_name\": \"$agent_name\"
        }")
    
    if echo "$result" | grep -q "api_key\|success.*true"; then
        # API returns: {"success": true, "data": {"api_key": "...", "wallet_address": "..."}}
        api_key=$(echo "$result" | jq -r '.data.api_key // .api_key // empty' 2>/dev/null)
        
        echo -e "${GREEN}✅ Registration successful!${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  SAVE YOUR API KEY:${NC}"
        echo ""
        echo -e "${GREEN}API Key: $api_key${NC}"
        echo -e "${BLUE}Wallet: $wallet${NC}"
        echo ""
        echo "Save these credentials:"
        echo "  export OPTIONNS_API_KEY='$api_key'"
        echo ""
        echo "Or create config file:"
        mkdir -p ~/.config/optionns
        # Extract RPC URL from API response (Helius endpoint for reliable devnet access)
        rpc_url=$(echo "$result" | jq -r '.data.rpc_url // .rpc_url // "https://api.devnet.solana.com"' 2>/dev/null)
        
        cat > ~/.config/optionns/credentials.json << EOF
{
  "api_key": "$api_key",
  "wallet_address": "$wallet",
  "agent_name": "$agent_name",
  "rpc_url": "$rpc_url"
}
EOF
        chmod 600 ~/.config/optionns/credentials.json
        echo ""
        echo -e "${GREEN}Credentials saved to ~/.config/optionns/credentials.json${NC}"
        
        # Verify the key works immediately
        echo ""
        echo -e "${BLUE}Verifying key...${NC}"
        verify_result=$(curl -s -X GET "${API_BASE}/v1/sports/events" \
            -H "X-API-Key: $api_key" \
            -H "Content-Type: application/json")
        if echo "$verify_result" | grep -q '"success".*true\|"data"'; then
            echo -e "${GREEN}✅ Key validated — you can start trading${NC}"
        else
            echo -e "${YELLOW}⚠️  Key saved but verification pending. Try: ./optionns.sh test${NC}"
        fi
        
    else
        echo -e "${RED}❌ Registration failed${NC}"
        echo "$result"
        exit 1
    fi
}

# Test API connection
cmd_test() {
    if [[ -z "$API_KEY" ]]; then
        echo -e "${YELLOW}No API key found. Register first:${NC}"
        echo "  optionns register [agent_name]"
        exit 1
    fi
    
    echo -e "${BLUE}Testing Optionns API connection...${NC}"
    
    # Try to get live games
    result=$(api_call "GET" "/v1/sports/events?sport=NBA")
    
    if echo "$result" | grep -q "success.*true\|game\|event"; then
        echo -e "${GREEN}✅ API connection successful${NC}"
        
        # Count live games
        game_count=$(echo "$result" | grep -o '"game_id"\|"id"' | wc -l)
        echo -e "Found ${GREEN}$game_count${NC} live games available"
        
        # Show wallet status if configured
        if [[ -n "$WALLET" ]]; then
            echo -e "Wallet: ${BLUE}$WALLET${NC}"
        fi
        
        exit 0
    else
        echo -e "${RED}❌ API connection failed${NC}"
        echo "$result" | head -100
        exit 1
    fi
}

# Get live or upcoming games
cmd_games() {
    local league=""
    local show_scores="false"
    local show_upcoming="false"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --scores) show_scores="true"; shift ;;
            --upcoming) show_upcoming="true"; shift ;;
            *) league="$1"; shift ;;
        esac
    done
    
    if [[ -n "$league" ]]; then
        if [[ "$show_upcoming" == "true" ]]; then
            echo -e "${BLUE}Fetching upcoming $league games...${NC}"
        else
            echo -e "${BLUE}Fetching live $league games...${NC}"
        fi
        result=$(api_call "GET" "/v1/sports/events?sport=$league")
    else
        if [[ "$show_upcoming" == "true" ]]; then
            echo -e "${BLUE}Fetching all upcoming games...${NC}"
        else
            echo -e "${BLUE}Fetching all live games...${NC}"
        fi
        result=$(api_call "GET" "/v1/sports/events")
    fi
    
    if command -v jq &> /dev/null; then
        # Select which array to query based on flag
        local data_path=".data.live"
        if [[ "$show_upcoming" == "true" ]]; then
            data_path=".data.upcoming"
        fi
        
        if [[ "$show_scores" == "true" ]]; then
            # Display with scores, period, and clock
            echo "$result" | jq -r "${data_path}[]? | select(.title != \"Unknown Game\") | \"\\(.id // .game_id): \\(.title // \"\\(.awayTeam) vs \\(.homeTeam)\") | Score: \\(.score // \"N/A\") | \\(.period // \"N/A\") - \\(.clock // \"\")\"" 2>/dev/null || echo "$result"
        else
            # Default display without scores — filter out Unknown Games
            echo "$result" | jq -r "${data_path}[]? | select(.title != \"Unknown Game\") | \"\\(.id // .game_id): \\(.title // \"\\(.awayTeam) vs \\(.homeTeam)\") - \\(.status // \"live\")\"" 2>/dev/null || echo "$result"
        fi
    else
        echo "$result" | grep -o '"game_title":"[^"]*"' | sed 's/.*":"//;s/"$//'
    fi
}

# Fund wallet from faucet
cmd_faucet() {
    local wallet="${1:-$WALLET}"
    
    if [[ -z "$wallet" ]]; then
        echo -e "${RED}Error: No wallet address provided${NC}"
        echo "Usage: optionns.sh faucet <wallet_address>"
        exit 1
    fi
    
    echo -e "${BLUE}Requesting devnet funds for $wallet...${NC}"
    
    result=$(curl -s -X POST "${API_BASE}/api/faucet" \
        -H "Content-Type: application/json" \
        -d "{\"wallet_address\": \"$wallet\", \"amount\": 1000.0}")
    
    if echo "$result" | grep -q "success\|tx_hash"; then
        echo -e "${GREEN}✅ Faucet request successful${NC}"
        echo "$result" | jq -r '.tx_hash // .message // .' 2>/dev/null || echo "$result"
        
        # Also create optnUSDC ATA if it doesn't exist
        echo ""
        echo -e "${BLUE}🔍 Checking for optnUSDC token account...${NC}"
        
        optnUSDC_MINT="DNaYq6QKoahq98fAwxsFyPiDJZsLaQPq2x3nixnuegJh"
        KEYPAIR_FILE="${HOME}/.config/optionns/agent_keypair.json"
        
        if [[ -f "$KEYPAIR_FILE" ]]; then
            # Check if ATA exists
            if ! spl-token accounts --owner "$wallet" --url devnet 2>/dev/null | grep -q "$optnUSDC_MINT"; then
                echo -e "${YELLOW}⚠️  optnUSDC ATA not found, creating...${NC}"
                
                # Temporarily set Solana config
                solana config set --keypair "$KEYPAIR_FILE" --url devnet >/dev/null 2>&1
                
                if spl-token create-account "$optnUSDC_MINT" --url devnet 2>/dev/null; then
                    echo -e "${GREEN}✅ optnUSDC token account created!${NC}"
                    echo "Your trades can now settle on-chain."
                else
                    echo -e "${YELLOW}⚠️  ATA creation failed (may need SOL for rent)${NC}"
                    echo "Try: spl-token create-account $optnUSDC_MINT"
                fi
            else
                echo -e "${GREEN}✅ optnUSDC ATA already exists${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ Faucet request failed${NC}"
        echo "$result"
    fi
}

# Get quote for a trade
cmd_quote() {
    local token_id=""
    local amount="1"
    local underlying=""
    local strike=""
    local expiry="5"
    local sport=""  # Don't default to NBA
    local option_type="call"
    
    # Parse positional + named args
    if [[ $# -ge 1 && ! "$1" == --* ]]; then
        token_id="$1"; shift
    fi
    if [[ $# -ge 1 && ! "$1" == --* ]]; then
        amount="$1"; shift
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --underlying) underlying="$2"; shift 2 ;;
            --strike) strike="$2"; shift 2 ;;
            --expiry) expiry="$2"; shift 2 ;;
            --sport) sport="$2"; shift 2 ;;
            --type) option_type="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    if [[ -z "$token_id" ]]; then
        echo -e "${RED}Error: token_id required${NC}"
        echo "Usage: optionns.sh quote <token_id> [amount] [--underlying 0.55] [--strike 0.50] [--expiry 5] [--sport nba] [--type call]"
        exit 1
    fi
    
    # Validate expiry
    if [[ ! "$expiry" =~ ^(1|3|5|10)$ ]]; then
        echo -e "${RED}Error: expiry must be 1, 3, 5, or 10 minutes. Got: $expiry${NC}"
        exit 1
    fi
    
    # If underlying not provided, fetch from API
    if [[ -z "$underlying" ]]; then
        echo -e "${BLUE}Fetching current market probability...${NC}"
        
        # Use sport if provided, otherwise fetch all
        if [[ -n "$sport" ]]; then
            events=$(api_call "GET" "/v1/sports/events?sport=$sport")
        else
            events=$(api_call "GET" "/v1/sports/events")
        fi
        
        underlying=$(echo "$events" | jq -r '.data.live[0].probability // .data.live[0].home_win_prob // empty' 2>/dev/null)
        underlying="${underlying:-0.55}"
        echo "  Market probability: $underlying"
    fi
    
    # Default strike: slightly below underlying for ITM call, slightly above for ITM put
    if [[ -z "$strike" ]]; then
        if [[ "$option_type" == "call" ]]; then
            strike=$(echo "$underlying - 0.05" | bc -l 2>/dev/null || echo "0.50")
        else
            strike=$(echo "$underlying + 0.05" | bc -l 2>/dev/null || echo "0.60")
        fi
        # Ensure leading zero for decimals (bc outputs .50 instead of 0.50)
        strike=$(printf "%.2f" "$strike" 2>/dev/null || echo "0.50")
        # Clamp to valid range
        strike=$(echo "$strike" | awk '{if ($1 < 0.05) print 0.05; else if ($1 > 0.95) print 0.95; else print $1}')
    fi
    
    echo -e "${BLUE}Getting quote for $amount contracts...${NC}"
    echo "  Underlying: $underlying | Strike: $strike | Expiry: ${expiry}m | Type: $option_type"
    
    result=$(api_call "POST" "/v1/vault/quote" "{
        \"token_id\": \"$token_id\",
        \"underlying_price\": $underlying,
        \"strike\": $strike,
        \"option_type\": \"$option_type\",
        \"sport\": \"$sport\",
        \"quantity\": $amount,
        \"expiry_minutes\": $expiry
    }")
    
    echo "$result" | jq -r '
        if .premium then
            "Premium: \(.premium) USDC
Max Payout: \(.max_payout) USDC (\(.max_payout / .premium | floor):\(.premium / .premium | floor) ratio)
Quote ID: \(.quote_id)
Delta: \(.delta // "N/A") (\(.delta * 100 | floor)% probability)
Gamma: \(.gamma // "N/A")" + 
            (if .gamma_trap_warning then "\n⚠️  Gamma Trap Warning: High gamma risk" else "" end) +
            "\nValid until: \(.valid_until)"
        else
            .error // "Unknown error"
        end
    ' 2>/dev/null || echo "$result"
}

# Place a trade
cmd_trade() {
    # Parse arguments
    local game_id=""
    local game_title=""
    local bet_type="lead_margin_home"
    local target="10"
    local amount="1"
    local wallet=""
    local ata=""
    local expiry="5"
    local dry_run="false"
    local sport=""  # Don't default to NBA - detect dynamically
    local underlying=""
    local strike=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --game-id) game_id="$2"; shift 2 ;;
            --game-title) game_title="$2"; shift 2 ;;
            --bet-type) bet_type="$2"; shift 2 ;;
            --target) target="$2"; shift 2 ;;
            --amount) amount="$2"; shift 2 ;;
            --wallet) wallet="$2"; shift 2 ;;
            --ata) ata="$2"; shift 2 ;;
            --expiry) expiry="$2"; shift 2 ;;
            --sport) sport="$2"; shift 2 ;;
            --underlying) underlying="$2"; shift 2 ;;
            --strike) strike="$2"; shift 2 ;;
            --dry-run) dry_run="true"; shift ;;
            *) shift ;;
        esac
    done
    
    # Use defaults if not provided
    wallet="${wallet:-$WALLET}"
    
    if [[ -z "$game_id" || -z "$wallet" ]]; then
        echo -e "${RED}Error: Missing required parameters${NC}"
        echo "Usage: optionns.sh trade --game-id <id> --wallet <address> [--amount 5] [--target 10] [--expiry 5] [--sport nba]"
        exit 1
    fi
    
    # Validate expiry
    if [[ ! "$expiry" =~ ^(1|3|5|10)$ ]]; then
        echo -e "${RED}Error: expiry must be 1, 3, 5, or 10 minutes. Got: $expiry${NC}"
        exit 1
    fi
    
    # Fetch game info and real-time win probability from API
    echo -e "${BLUE}Fetching game data (checking all sports)...${NC}"
    
    # If sport not specified, fetch ALL live games to find the game_id
    if [[ -z "$sport" ]]; then
        all_games=$(api_call "GET" "/v1/sports/events")
        
        # Try to find the game in live games across all sports
        # Use -c for compact single-line JSON (so head -1 works correctly)
        game_data=$(echo "$all_games" | jq -c ".data.live[] | select(.id == \"$game_id\" or .game_id == \"$game_id\")" 2>/dev/null | head -1)
        
        if [[ -n "$game_data" ]]; then
            # Extract sport from the game data (use -r for raw string extraction)
            sport=$(echo "$game_data" | jq -r '.sport // .league // empty' 2>/dev/null)
            echo -e "${GREEN}✓ Detected sport: $(echo $sport | tr '[:lower:]' '[:upper:]')${NC}"
        fi
        
        
        # If still not found, reject the trade - game has likely ended
        if [[ -z "$sport" ]]; then
            echo -e "${RED}❌ Game $game_id not found in live games${NC}"
            echo ""
            echo "This could mean:"
            echo "  1. The game has ended and is no longer live"
            echo "  2. The game ID is invalid"
            echo "  3. The game hasn't started yet"
            echo ""
            echo -e "${YELLOW}Find a live game:${NC}"
            echo "  ./optionns.sh games"
            echo ""
            return 1
        fi
    fi
    
    games=$(api_call "GET" "/v1/sports/events?sport=$(echo $sport | tr '[:lower:]' '[:upper:]')")
    
    if [[ -z "$game_title" ]]; then
        game_title=$(echo "$games" | jq -r ".data.live[] | select(.id == \"$game_id\" or .game_id == \"$game_id\") | .title // \"\(.home_team) vs \(.away_team)\"" 2>/dev/null | head -1)
        game_title="${game_title:-$(echo $sport | tr '[:lower:]' '[:upper:]') Game $game_id}"
    fi
    
    # Derive underlying_price from real-time win probability (if not provided)
    if [[ -z "$underlying" ]]; then
        underlying=$(echo "$games" | jq -r ".data.live[] | select(.id == \"$game_id\" or .game_id == \"$game_id\") | .probability // .home_win_prob // empty" 2>/dev/null | head -1)
        underlying="${underlying:-0.55}"
    fi
    
    # Derive strike: for barrier bets, use underlying ± buffer based on bet direction (if not provided)
    if [[ -z "$strike" ]]; then
        strike=$(echo "$underlying - 0.05" | bc -l 2>/dev/null || echo "0.50")
        # Ensure leading zero for decimals (bc outputs .50 instead of 0.50)
        strike=$(printf "%.2f" "$strike" 2>/dev/null || echo "0.50")
        strike=$(echo "$strike" | awk '{if ($1 < 0.05) print 0.05; else if ($1 > 0.95) print 0.95; else print $1}')
    fi
    
    echo -e "${BLUE}Placing trade...${NC}"
    echo "Game: $game_title"
    echo "Bet: $bet_type at +$target"
    echo "Amount: $amount contracts | Expiry: ${expiry}m"
    echo "Market Probability: $underlying | Strike: $strike"
    
    # Get token_id for this game
    token_id="token_$game_id"
    
    # Get quote first
    quote_result=$(api_call "POST" "/v1/vault/quote" "{
        \"token_id\": \"$token_id\",
        \"underlying_price\": $underlying,
        \"strike\": $strike,
        \"option_type\": \"call\",
        \"sport\": \"$sport\",
        \"quantity\": $amount,
        \"expiry_minutes\": $expiry
    }")
    
    quote_id=$(echo "$quote_result" | jq -r '.quote_id // empty' 2>/dev/null)
    
    if [[ -z "$quote_id" ]]; then
        # Detect specific auth failure and provide actionable guidance
        if echo "$quote_result" | grep -q 'INVALID_API_KEY\|UNAUTHORIZED'; then
            echo -e "${RED}❌ Authentication failed${NC}"
            echo "Your API key is not recognized by the server."
            echo "Try re-registering: ./optionns.sh register your_name"
            echo "If this persists, check your key: cat ~/.config/optionns/credentials.json"
        else
            echo -e "${RED}❌ Failed to get quote${NC}"
            echo "$quote_result"
        fi
        exit 1
    fi
    
    # Dry-run: show what would be traded without executing
    if [[ "$dry_run" == "true" ]]; then
        premium=$(echo "$quote_result" | jq -r '.premium // .total_premium // "N/A"' 2>/dev/null)
        max_payout=$(echo "$quote_result" | jq -r '.max_payout // .max_profit // "N/A"' 2>/dev/null)
        echo -e "${YELLOW}[DRY RUN] Would place trade:${NC}"
        echo "  Game: $game_title"
        echo "  Bet: $bet_type at +$target"
        echo "  Amount: $amount contracts"
        echo "  Premium: $premium USDC"
        echo "  Max Payout: $max_payout USDC"
        echo "  Quote ID: $quote_id"
        exit 0
    fi
    
    echo -e "Quote received: ${GREEN}$quote_id${NC}"
    
    # Execute trade
    trade_result=$(api_call "POST" "/v1/vault/buy" "{
        \"quote_id\": \"$quote_id\",
        \"token_id\": \"$token_id\",
        \"game_id\": \"$game_id\",
        \"game_title\": \"$game_title\",
        \"sport\": \"$sport\",
        \"underlying_price\": $underlying,
        \"strike\": $strike,
        \"option_type\": \"call\",
        \"quantity\": $amount,
        \"expiry_minutes\": $expiry,
        \"barrier_type\": \"$bet_type\",
        \"barrier_target\": $target,
        \"barrier_direction\": \"above\",
        \"user_pubkey\": \"$wallet\",
        \"user_ata\": \"${ata:-$wallet}\"
    }")
    
    # Check if we got instructions to sign (new two-phase commit format)
    if echo "$trade_result" | grep -q '"instructions"'; then
        instructions_json=$(echo "$trade_result" | jq -c '.instructions')
        pending_id=$(echo "$trade_result" | jq -r '.pending_id // .position_id // .outcome_id')
        position_pda=$(echo "$trade_result" | jq -r '.position_pda // .outcome_position_pda // "N/A"')
        
        echo -e "${GREEN}✅ Trade prepared!${NC}"
        echo "Pending ID: $pending_id"
        echo "Position PDA: $position_pda"
        echo ""
        echo -e "${BLUE}Signing and submitting to Solana...${NC}"
        
        # Sign and send transaction using agent's keypair
        KEYPAIR_FILE="${HOME}/.config/optionns/agent_keypair.json"
        # Read RPC URL from credentials (saved during registration), env var, or fallback
        CRED_RPC=$(jq -r '.rpc_url // empty' "$CONFIG_FILE" 2>/dev/null)
        RPC_URL="${SOLANA_RPC_URL:-${CRED_RPC:-https://api.devnet.solana.com}}"
        
        if [[ ! -f "$KEYPAIR_FILE" ]]; then
            echo -e "${RED}❌ Keypair not found at $KEYPAIR_FILE${NC}"
            echo "Run 'optionns.sh register' first to generate a keypair"
            exit 1
        fi
        
        # SECURITY: Pass instructions via stdin to prevent code injection
        # DO NOT embed API response in command string (RCE risk)
        tx_sig=$(echo "$instructions_json" | python3 "$SCRIPT_DIR/signer.py" --stdin --keypair "$KEYPAIR_FILE" --rpc "$RPC_URL" 2>&1)
        sign_exit_code=$?
        
        if [[ $sign_exit_code -eq 0 && -n "$tx_sig" ]]; then
            echo -e "${GREEN}✅ Transaction submitted to blockchain!${NC}"
            echo -e "${BLUE}Solana Tx: $tx_sig${NC}"
           
            echo ""
            echo -e "${BLUE}Confirming with API...${NC}"
            
            # TWO-PHASE COMMIT: Confirm transaction with API
            confirm_result=$(api_call "POST" "/v1/vault/confirm" "{
                \"pending_id\": \"$pending_id\",
                \"tx_signature\": \"$tx_sig\"
            }")
            
            if echo "$confirm_result" | grep -q '"success".*true'; then
                position_id=$(echo "$confirm_result" | jq -r '.position_id // "N/A"')
                echo -e "${GREEN}✅ Trade confirmed and settled on-chain!${NC}"
                echo -e "Position ID: ${BLUE}$position_id${NC}"
                echo "Explorer: https://explorer.solana.com/tx/${tx_sig}?cluster=devnet"
                
                # Show trade details
                echo "$trade_result" | jq -r '
"Premium Paid: \(.premium_paid // .premium_collected // .premium) optnUSDC
Max Payout: \(.max_payout) optnUSDC
Expires: \(.expires_at // .expiry_time)
Barrier Registered: \(.barrier_registered // true)"
                ' 2>/dev/null
                
                # Log to file for tracking
                echo "$(date -Iseconds) | $position_id | $game_title | $bet_type +$target | $amount contracts | $tx_sig" >> "$SCRIPT_DIR/../positions.log"
            else
                echo -e "${YELLOW}⚠️  Transaction submitted but confirmation failed${NC}"
                echo "TX signature: $tx_sig"
                echo "Confirmation response: $confirm_result"
                echo ""
                echo "Your transaction may still be valid. Check: https://explorer.solana.com/tx/${tx_sig}?cluster=devnet"
                exit 1
            fi
            
        else
            echo -e "${RED}❌ Transaction signing/submission failed${NC}"
            echo "$tx_sig"
            exit 1
        fi
        
    elif echo "$trade_result" | grep -q "pending_id"; then
        # TWO-PHASE COMMIT: Got pending transaction but failed before signing
        pending_id=$(echo "$trade_result" | jq -r '.pending_id')
        echo -e "${YELLOW}⚠️  Trade prepared but not yet signed${NC}"
        echo "Pending ID: $pending_id"
        echo "You need to sign and submit the transaction manually, then call /vault/confirm"
        echo "$trade_result" | jq '.'
        
    elif echo "$trade_result" | grep -q "position_id"; then
        # Fallback: off-chain only (shouldn't happen with current API)
        position_id=$(echo "$trade_result" | jq -r '.position_id')
        echo -e "${YELLOW}⚠️  Trade recorded off-chain only (no Solana tx)${NC}"
        echo "Position ID: $position_id"
        echo "$trade_result" | jq '.'
        
    else
        echo -e "${RED}❌ Trade failed${NC}"
        echo "$trade_result"
        exit 1
    fi
}

# Check positions
cmd_positions() {
    echo -e "${BLUE}Your Positions${NC}"
    
    # Fetch live positions from API
    if [[ -n "$API_KEY" ]]; then
        echo -e "${BLUE}Fetching from API...${NC}"
        result=$(api_call "GET" "/v1/vault/positions")
        
        if echo "$result" | grep -q '"positions"\|"id"\|"token_id"'; then
            echo -e "${GREEN}Live positions:${NC}"
            echo "$result" | jq -r '(.positions // .[])? | "  \(.id // .position_id): \(.game_title // .sport) | \(.quantity // .amount) USDC | \(.expiry_time // .expires_at // "no expiry")"' 2>/dev/null || echo "$result" | jq '.' 2>/dev/null || echo "$result"
        else
            echo "No live positions found (or API unreachable)"
            echo "$result" | jq '.error // .' 2>/dev/null
        fi
        echo ""
    fi
    
    # Also show local trade log
    if [[ -f "$SCRIPT_DIR/../positions.log" ]]; then
        echo "Local trade log (recent):"
        tail -10 "$SCRIPT_DIR/../positions.log"
        total=$(wc -l <"$SCRIPT_DIR/../positions.log")
        echo ""
        echo "Total logged trades: $total"
    else
        echo "No local trades logged yet."
    fi
}

# Batch snapshot — all games + positions in one call
cmd_snapshot() {
    echo -e "${BLUE}⚡ Agent Snapshot (batch)${NC}"
    
    local start_ms=$(date +%s%3N 2>/dev/null || python3 -c 'import time; print(int(time.time()*1000))')
    
    result=$(api_call "GET" "/v1/agent/snapshot")
    
    local end_ms=$(date +%s%3N 2>/dev/null || python3 -c 'import time; print(int(time.time()*1000))')
    local elapsed=$(( end_ms - start_ms ))
    
    if echo "$result" | jq -e '.success' &>/dev/null; then
        echo -e "${GREEN}✅ Snapshot received (${elapsed}ms)${NC}"
        echo ""
        
        # Summary
        local total_games=$(echo "$result" | jq -r '.data.total_games // 0')
        local total_positions=$(echo "$result" | jq -r '.data.total_positions // 0')
        local sports=$(echo "$result" | jq -r '.data.sports_available // [] | join(", ")')
        
        echo "  Total games:     $total_games"
        echo "  Active sports:   $sports"
        echo "  Open positions:  $total_positions"
        echo ""
        
        # Games by sport
        echo -e "${BLUE}Games by Sport:${NC}"
        echo "$result" | jq -r '.data.games | to_entries[] | "  \(.key): \(.value | length) games"'
        echo ""
        
        # List game titles
        echo "$result" | jq -r '.data.games | to_entries[] | .value[] | "    [\(.sport)] \(.title) | \(.outcomes_count // 0) outcomes"'
        echo ""
        
        # Positions summary
        if [[ "$total_positions" -gt 0 ]]; then
            echo -e "${BLUE}Open Positions:${NC}"
            echo "$result" | jq -r '.data.positions[] | "  \(.position_id[:8])... | \(.game_title) | \(.premium_paid) USDC | \(.status)"'
        fi
    else
        echo -e "${RED}❌ Snapshot failed${NC}"
        echo "$result" | jq '.error // .' 2>/dev/null || echo "$result"
    fi
}

# Deposit liquidity (on-chain)
cmd_deposit() {
    echo -e "${BLUE}💰 Deposit Liquidity (On-Chain)${NC}"
    
    # Parse arguments
    local amount=""
    local league="NBA"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --amount)
                amount="$2"
                shift 2
                ;;
            --league)
                league="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                echo "Usage: optionns deposit --amount <usdc> [--league <NBA|NFL|...>]"
                return 1
                ;;
        esac
    done
    
    if [[ -z "$amount" ]]; then
        echo -e "${RED}❌ --amount required${NC}"
        echo "Usage: optionns deposit --amount <usdc> [--league <NBA|NFL|...>]"
        return 1
    fi
    
    if [[ -z "$WALLET" ]]; then
        echo -e "${RED}❌ Wallet address not found${NC}"
        echo "Register first: optionns register"
        return 1
    fi
    
    # SECURITY: Validate inputs contain only safe characters
    # Allows any league name (NBA, DOTA2, VALORANT, etc.) while preventing shell injection
    if ! [[ "$league" =~ ^[A-Za-z0-9_-]+$ ]]; then
        echo -e "${RED}❌ Invalid league parameter: $league${NC}"
        echo "League name must contain only letters, numbers, underscores, and hyphens"
        return 1
    fi
    
    # SECURITY: Validate amount is a number
    if ! [[ "$amount" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        echo -e "${RED}❌ Invalid amount: $amount${NC}"
        echo "Amount must be a positive number"
        return 1
    fi
    
    echo "League: $league"
    echo "Amount: $amount USDC"
    echo "Wallet: $WALLET"
    echo ""
    
    # Call Python strategy directly for on-chain deposit
    # Validated inputs, safe to use
    python3 "$SCRIPT_DIR/strategy.py" deposit "$league" "$amount"
}

# Withdraw liquidity (on-chain)
cmd_withdraw() {
    echo -e "${BLUE}💸 Withdraw Liquidity (On-Chain)${NC}"
    
    # Parse arguments
    local shares=""
    local league="NBA"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --shares)
                shares="$2"
                shift 2
                ;;
            --league)
                league="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                echo "Usage: optionns withdraw --shares <qty> [--league <NBA|NFL|...>]"
                return 1
                ;;
        esac
    done
    
    if [[ -z "$shares" ]]; then
        echo -e "${RED}❌ --shares required${NC}"
        echo "Usage: optionns withdraw --shares <qty> [--league <NBA|NFL|...>]"
        return 1
    fi
    
    if [[ -z "$WALLET" ]]; then
        echo -e "${RED}❌ Wallet address not found${NC}"
        echo "Register first: optionns register"
        return 1
    fi
    
    # SECURITY: Validate inputs contain only safe characters
    # Allows any league name (NBA, DOTA2, VALORANT, etc.) while preventing shell injection
    if ! [[ "$league" =~ ^[A-Za-z0-9_-]+$ ]]; then
        echo -e "${RED}❌ Invalid league parameter: $league${NC}"
        echo "League name must contain only letters, numbers, underscores, and hyphens"
        return 1
    fi
    
    # SECURITY: Validate shares is a number
    if ! [[ "$shares" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        echo -e "${RED}❌ Invalid shares quantity: $shares${NC}"
        echo "Shares must be a positive number"
        return 1
    fi
    
    echo "League: $league"
    echo "Burning Shares: $shares"
    echo "Wallet: $WALLET"
    echo ""
    
    # Call Python strategy directly for on-chain withdrawal
    # Validated inputs, safe to use
    python3 "$SCRIPT_DIR/strategy.py" withdraw "$league" "$shares"
}

# Autonomous trading mode
cmd_autonomous() {
    local sport="${1:-ANY}"
    
    # SECURITY: Validate input contains only safe characters (alphanumeric, underscore, hyphen)
    # Prevents shell injection while allowing any league name (NBA, DOTA2, VALORANT, etc.)
    if ! [[ "$sport" =~ ^[A-Za-z0-9_-]+$ ]]; then
        echo -e "${RED}❌ Invalid sport parameter: $sport${NC}"
        echo "Sport name must contain only letters, numbers, underscores, and hyphens"
        exit 1
    fi
    
    echo -e "${BLUE}Starting autonomous trading mode...${NC}"
    echo "Sport preference: $sport (will scan all sports for live games)"
    echo "Press Ctrl+C to stop"
    echo ""
    
    # Ensure required environment variables are set
    if [[ -z "$API_KEY" ]]; then
        echo -e "${RED}❌ OPTIONNS_API_KEY not set${NC}"
        echo "Export it or it will be read from ~/.config/optionns/config.json"
    fi
    
    if [[ -z "$SOLANA_PUBKEY" ]]; then
        echo -e "${YELLOW}⚠️  SOLANA_PUBKEY not set - will use registered agent wallet${NC}"
    fi
    
    # Run strategy engine in autonomous mode
    # strategy.py expects positional command "auto" (not --mode)
    # $sport validated via regex, safe to use
    if [[ "$sport" == "ANY" ]]; then
        python3 "$SCRIPT_DIR/strategy.py" auto
    else
        python3 "$SCRIPT_DIR/strategy.py" auto "$sport"
    fi
}

# Main
main() {
    check_deps
    load_config
    
    case "${1:-}" in
        register)
            cmd_register "${2:-}"
            ;;
        test)
            cmd_test
            ;;
        games)
            shift
            cmd_games "$@"
            ;;
        faucet)
            cmd_faucet "${2:-}"
            ;;
        quote)
            cmd_quote "${2:-}" "${3:-5}"
            ;;
        trade)
            shift
            cmd_trade "$@"
            ;;
        positions)
            cmd_positions
            ;;
        deposit)
            shift
            cmd_deposit "$@"
            ;;
        withdraw)
            shift
            cmd_withdraw "$@"
            ;;
        autonomous|auto)
            shift
            cmd_autonomous "${1:-ANY}"
            ;;
        snapshot)
            cmd_snapshot
            ;;
        *)
            echo "Optionns Trader - Autonomous sports betting for AI agents"
            echo ""
            echo "Usage: optionns [command] [args]"
            echo ""
            echo "Commands:"
            echo "  register [agent_name]     Register for API key (auto-generated if no name)"
            echo "  test                      Test API connection"
            echo "  games [league] [--scores] List live games (default: all, --scores shows detailed state)"
            echo "  faucet <wallet>           Fund devnet wallet"
            echo "  quote <token_id> [amount] Get quote for trade"
            echo "  trade --game-id <id> ...  Place a trade"
            echo "  positions                 Show your positions"
            echo "  deposit --amount <usdc>   Deposit liquidity to vault (on-chain)"
            echo "    [--league <NBA|NFL|...>]"
            echo "  withdraw --shares <qty>   Withdraw liquidity from vault (on-chain)"
            echo "    [--league <NBA|NFL|...>]"
            echo "  auto                      Run autonomous trading"
            echo "  snapshot                  Batch fetch: all games + positions (fastest)"
            echo ""
            echo "Trade options:"
            echo "  --game-id <id>        Game ID (required)"
            echo "  --game-title <title>  Game title"
            echo "  --bet-type <type>     lead_margin_home, lead_margin_away, etc"
            echo "  --target <points>     Target margin/score"
            echo "  --amount <usdc>       Bet amount (default: 5)"
            echo "  --wallet <address>    Your Solana wallet"
            echo "  --underlying <prob>   Override market probability (0.0-1.0)"
            echo "  --strike <price>      Override strike price (0.0-1.0)"
            echo "  --dry-run             Preview trade without executing"
            echo ""
            echo "Examples:"
            echo "  optionns register binary_echo"
            echo "  optionns test"
            echo "  optionns games NBA"
            echo "  optionns games --scores        # Show all games with scores/period/clock"
            echo "  optionns games NBA --scores    # Show NBA games with scores"
            echo "  optionns trade --game-id 401584123 --wallet HN7c... --amount 10 --target 8"
            ;;
    esac
}

main "$@"