#!/bin/bash
#
# Keepa API Client - curl + jq implementation
# Requires: curl, jq
#

set -e

# Configuration
KEEPA_API_KEY="${KEEPA_API_KEY:-}"
KEEPA_DOMAIN="${KEEPA_DOMAIN:-1}"
KEEPA_OUTPUT_FORMAT="${KEEPA_OUTPUT_FORMAT:-table}"
KEEPA_DEFAULT_DAYS="${KEEPA_DEFAULT_DAYS:-90}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ  $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }

# Get domain ID by name
get_domain_id() {
    case "$1" in
        US) echo "1" ;;
        UK) echo "3" ;;
        DE) echo "4" ;;
        FR) echo "5" ;;
        JP) echo "6" ;;
        CA) echo "7" ;;
        AU) echo "9" ;;
        IN) echo "10" ;;
        *) echo "1" ;;
    esac
}

# Get category ID by name
get_category_id() {
    case "$1" in
        Electronics) echo "172282" ;;
        Computers) echo "541966" ;;
        Home) echo "1055398" ;;
        Beauty) echo "3760911" ;;
        Sports) echo "3375251" ;;
        Toys) echo "165793011" ;;
        Clothing) echo "7141123011" ;;
        Books) echo "283155" ;;
        Office) echo "1064954" ;;
        Garden) echo "2972638011" ;;
        *) echo "172282" ;;
    esac
}

show_help() {
    cat << 'EOF'
Keepa API Client - Amazon Price History Tracker

Usage:
  keepa.sh <command> [arguments] [options]

Commands:
  asin <ASIN>              Query product by ASIN
  batch-asin <ASINs>       Query multiple ASINs
  price-history <ASIN>     Get price history
  search <keyword>         Search products
  bestsellers [category]   Get best sellers

Options:
  --domain <US|UK|DE|...>  Amazon marketplace (default: US)
  --days <number>          History days: 30, 90, 180 (default: 90)
  --output <table|json>    Output format (default: table)
  --category <name>        Category for search
  --help                   Show help

Examples:
  ./keepa.sh asin B08XYZ123
  ./keepa.sh price-history B08XYZ123 --days 30
  ./keepa.sh search "wireless earbuds" --category Electronics

Configuration:
  Export KEEPA_API_KEY or create ~/.teamclaw-skills/keepa-api/CONFIG.md

Get API Key: https://keepa.com/#!api
EOF
}

load_config() {
    local config_file=""
    if [[ -f ".teamclaw-skills/keepa-api/CONFIG.md" ]]; then
        config_file=".teamclaw-skills/keepa-api/CONFIG.md"
    elif [[ -f "$HOME/.teamclaw-skills/keepa-api/CONFIG.md" ]]; then
        config_file="$HOME/.teamclaw-skills/keepa-api/CONFIG.md"
    fi

    if [[ -n "$config_file" ]]; then
        while IFS=': ' read -r key value; do
            case "$key" in
                api_key) KEEPA_API_KEY="$value" ;;
                marketplace) KEEPA_DOMAIN="$(get_domain_id "$value")" ;;
                default_days) KEEPA_DEFAULT_DAYS="$value" ;;
                output_format) KEEPA_OUTPUT_FORMAT="$value" ;;
            esac
        done < <(grep -v '^#' "$config_file" 2>/dev/null | grep -v '^---' | grep -v '^$')
    fi
}

check_api_key() {
    if [[ -z "$KEEPA_API_KEY" ]]; then
        print_error "Keepa API key is not configured!"
        echo ""
        echo "Get API key from: https://keepa.com/#!api"
        echo "Then: export KEEPA_API_KEY=your_key"
        echo "Or create: ~/.teamclaw-skills/keepa-api/CONFIG.md"
        exit 1
    fi
}

# Make API request
keepa_request() {
    local endpoint="$1"
    local params="$2"
    local url="https://api.keepa.com/${endpoint}?key=${KEEPA_API_KEY}${params}"
    curl -s --compressed "$url"
}

# Format price (Keepa uses cents)
format_price() {
    local price="$1"
    if [[ -z "$price" ]] || [[ "$price" == "null" ]] || [[ "$price" == "0" ]]; then
        echo "N/A"
    elif [[ "$price" == "-1" ]]; then
        echo "Out of Stock"
    else
        local dollars=$((price / 100))
        local cents=$((price % 100))
        printf "%d.%02d" "$dollars" "$cents"
    fi
}

# Display product (table format)
display_product_table() {
    local response="$1"

    # Use jq to parse JSON
    local product=$(echo "$response" | jq -r '.products[0] // empty')

    if [[ -z "$product" ]]; then
        print_error "Product not found or API error"
        echo "$response" | jq -r '.error_message // "Unknown error"'
        exit 1
    fi

    local title=$(echo "$product" | jq -r '.title // "N/A"')
    local asin=$(echo "$product" | jq -r '.asin // "N/A"')
    local brand=$(echo "$product" | jq -r '.brand // "N/A"')

    # Get category from categoryTree
    local category=$(echo "$product" | jq -r '.categoryTree[-1].name // .categories[0] // "N/A"')

    local price=$(echo "$product" | jq -r '.price // 0')
    local priceNew=$(echo "$product" | jq -r '.priceNew // 0')
    local priceUsed=$(echo "$product" | jq -r '.priceUsed // 0')
    local rating=$(echo "$product" | jq -r '.rating // 0')
    local ratingCount=$(echo "$product" | jq -r '.ratingCount // 0')

    # Get rank from salesRanks (first entry) or rank field
    local rank=$(echo "$product" | jq -r '.rank // .salesRanks | if type == "object" then (to_entries[0].value[1] // 0) else . end')

    # Get monthly sold
    local monthlySold=$(echo "$product" | jq -r '.monthlySold // 0')

    # Availability
    local availability=$(echo "$product" | jq -r '.availabilityAmazon // 0')

    echo ""
    echo "═══ Keepa Product Report ═══"
    echo ""
    echo "ASIN: $asin"
    echo "Title: $title"
    echo "Brand: $brand"
    echo "Category: $category"
    echo ""
    echo "Current Price:"

    if [[ "$availability" == "-1" ]]; then
        echo "  Amazon: Out of Stock / Not Available"
    else
        echo "  Amazon: \$$(format_price $price)"
    fi
    echo "  3rd Party New: \$$(format_price $priceNew)"
    echo "  3rd Party Used: \$$(format_price $priceUsed)"
    echo ""
    echo "Sales Rank: #${rank:-N/A}"
    if [[ "$monthlySold" != "0" ]] && [[ -n "$monthlySold" ]]; then
        echo "Monthly Sold: $monthlySold units"
    fi
    echo "Rating: $rating/5 ($ratingCount reviews)"
    echo ""
}

# Display price history
display_price_history() {
    local response="$1"
    local days="$2"

    echo ""
    echo "═══ Price History (${days} days) ═══"
    echo ""

    # Get price history array
    echo "$response" | jq -r '
        .products[0].priceHistory[:20][]? |
        if . and .[0] then
            "Date: \(((.[0] / 1000) | todate)) | Price: $\(.[1] / 100 | if . < 1 then "N/A" else (. | tostring) end)"
        else
            empty
        end
    ' 2>/dev/null || echo "No price history available"

    echo ""
}

# Query by ASIN
cmd_asin() {
    local asin="$1"
    shift
    local days="$KEEPA_DEFAULT_DAYS"
    local show_history=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --days) days="$2"; shift 2 ;;
            --output) KEEPA_OUTPUT_FORMAT="$2"; shift 2 ;;
            --domain) KEEPA_DOMAIN="$(get_domain_id "$2")"; shift 2 ;;
            --history) show_history=true; shift ;;
            *) shift ;;
        esac
    done

    check_api_key
    print_info "Querying ASIN: $asin (Domain: $KEEPA_DOMAIN)"

    local params="&domain=$KEEPA_DOMAIN&asin=$asin&history=1&rating=1"
    local response
    response=$(keepa_request "product" "$params")

    # Check for errors
    local error=$(echo "$response" | jq -r '.error // empty')
    if [[ -n "$error" ]]; then
        print_error "API Error: $error"
        exit 1
    fi

    if [[ "$KEEPA_OUTPUT_FORMAT" == "json" ]]; then
        echo "$response" | jq '.'
    else
        display_product_table "$response"
        if [[ "$show_history" == "true" ]]; then
            display_price_history "$response" "$days"
        fi
    fi
}

# Search products
cmd_search() {
    local query="$1"
    shift
    local page="1"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --page) page="$2"; shift 2 ;;
            --domain) KEEPA_DOMAIN="$(get_domain_id "$2")"; shift 2 ;;
            --output) KEEPA_OUTPUT_FORMAT="$2"; shift 2 ;;
            --category) shift 2 ;;  # Keepa search API doesn't support category
            *) shift ;;
        esac
    done

    check_api_key
    print_info "Searching: \"$query\" (Domain: $KEEPA_DOMAIN, Page: $page)"

    local encoded_query=$(echo "$query" | sed 's/ /+/g')
    local params="&domain=$KEEPA_DOMAIN&query=$encoded_query&page=$page"

    local response
    response=$(keepa_request "search" "$params")

    # Check for errors
    local has_error=$(echo "$response" | jq -r '.error // empty')
    if [[ -n "$has_error" ]]; then
        print_error "API Error: $(echo "$response" | jq -r '.error.message // "Unknown error"')"
        exit 1
    fi

    if [[ "$KEEPA_OUTPUT_FORMAT" == "json" ]]; then
        echo "$response" | jq '.'
    else
        echo ""
        echo "═══ Search Results: \"$query\" ═══"
        echo ""

        local count=$(echo "$response" | jq -r '.products | length // 0')
        if [[ "$count" -eq 0 ]]; then
            echo "No products found."
            echo ""
            echo "Note: Keepa search API has limited results."
            echo "Try using ASIN lookup instead for specific products."
        else
            echo "Found $count products:"
            echo ""

            echo "$response" | jq -r '
                .products[:10][]? |
                "• \(.asin) | \(.title // "N/A" | .[0:60]) | $\(.price / 100)"
            ' 2>/dev/null
        fi

        echo ""
    fi
}

# Get best sellers
cmd_bestsellers() {
    shift
    local category="Electronics"
    local page="1"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --category) category="$2"; shift 2 ;;
            --page) page="$2"; shift 2 ;;
            --domain) KEEPA_DOMAIN="$(get_domain_id "$2")"; shift 2 ;;
            *) shift ;;
        esac
    done

    check_api_key
    local category_id="$(get_category_id "$category")"
    print_info "Best Sellers: $category (Domain: $KEEPA_DOMAIN, Page: $page)"

    local params="&domain=$KEEPA_DOMAIN&categoryId=$category_id&page=$page"
    local response
    response=$(keepa_request "bestsellers" "$params")

    if [[ "$KEEPA_OUTPUT_FORMAT" == "json" ]]; then
        echo "$response" | jq '.'
    else
        echo ""
        echo "═══ Best Sellers: $category ═══"
        echo ""

        echo "$response" | jq -r '
            .products[:20][]? |
            "#\(.bestsellersList?.rank // "N/A") | \(.asin) | \(.title // "N/A" | .[0:50]) | $\(.price / 100)"
        ' 2>/dev/null

        echo ""
    fi
}

# Main
main() {
    load_config

    if [[ -z "$1" ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        show_help
        exit 0
    fi

    local command="$1"
    shift

    case "$command" in
        asin)
            [[ -z "$1" ]] && { print_error "ASIN required"; exit 1; }
            cmd_asin "$@"
            ;;
        batch-asin)
            [[ -z "$1" ]] && { print_error "ASINs required"; exit 1; }
            # For batch, just query first ASIN for now
            local first_asin=$(echo "$1" | cut -d',' -f1)
            cmd_asin "$first_asin" "$@"
            ;;
        search)
            [[ -z "$1" ]] && { print_error "Query required"; exit 1; }
            cmd_search "$@"
            ;;
        price-history)
            [[ -z "$1" ]] && { print_error "ASIN required"; exit 1; }
            cmd_asin "$@" --history
            ;;
        bestsellers)
            cmd_bestsellers "$@"
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
