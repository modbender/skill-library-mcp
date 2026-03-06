#!/bin/bash
# CLI wrapper for FatSecret - Unified interface for all functions

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/../venv"
PYTHON_PATH="$VENV_PATH/bin/python3"

# Use persistent config directory (for containers/Docker)
export FATSECRET_CONFIG_DIR="${FATSECRET_CONFIG_DIR:-/home/node/clawd/config/fatsecret}"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Help function
show_help() {
    echo "FatSecret CLI - Unified Interface"
    echo "=================================="
    echo ""
    echo "USAGE:"
    echo "  $0 <command> [arguments]"
    echo ""
    echo "COMMANDS:"
    echo "  auth           - OAuth1 authentication (first time)"
    echo "  search <query> - Search foods"
    echo "  log            - Add food to diary (interactive)"
    echo "  quick <name> [quantity] [meal] - Quick log"
    echo "  barcode <code> - Barcode lookup"
    echo "  recipes <query> - Search recipes"
    echo "  help           - Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 auth"
    echo "  $0 search \"chicken breast\""
    echo "  $0 log"
    echo "  $0 quick egg 3 Breakfast"
    echo "  $0 barcode 0041270003490"
    echo ""
}

# Check if virtual environment exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: cd $(dirname "$SCRIPT_DIR") && python3 -m venv venv"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Check arguments
if [ $# -eq 0 ]; then
    show_help
    deactivate
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in
    auth|authentication)
        echo "🔐 Starting OAuth1 authentication..."
        "$PYTHON_PATH" "$SCRIPT_DIR/fatsecret_auth.py"
        ;;
    
    search)
        if [ $# -eq 0 ]; then
            echo "❌ Specify a search query"
            echo "Example: $0 search \"chicken breast\""
            deactivate
            exit 1
        fi
        QUERY="$1"
        MAX_RESULTS="${2:-5}"
        echo "🔍 Searching: $QUERY"
        "$PYTHON_PATH" -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from fatsecret_diary_simple import load_tokens, search_food
tokens = load_tokens()
if tokens:
    foods = search_food('$QUERY', tokens, $MAX_RESULTS)
    if foods:
        for i, food in enumerate(foods, 1):
            name = food.get('food_name', 'Unknown')
            brand = food.get('brand_name', '')
            brand_str = f' ({brand})' if brand else ''
            print(f'{i}. {name}{brand_str} (ID: {food.get(\"food_id\")})')
    else:
        print('❌ No results found')
else:
    print('❌ Tokens not found. Run first: $0 auth')
"
        ;;
    
    log|diary)
        echo "📝 Interactive diary mode..."
        "$PYTHON_PATH" "$SCRIPT_DIR/fatsecret_diary_simple.py"
        ;;
    
    quick)
        if [ $# -eq 0 ]; then
            echo "❌ Specify a food"
            echo "Example: $0 quick egg 3 Breakfast"
            deactivate
            exit 1
        fi
        FOOD="$1"
        QUANTITY="${2:-1}"
        MEAL="${3:-Breakfast}"
        echo "⚡ Quick log: $QUANTITY x $FOOD ($MEAL)"
        "$PYTHON_PATH" "$SCRIPT_DIR/fatsecret_diary_simple.py" "$FOOD" "$QUANTITY" "$MEAL"
        ;;
    
    barcode)
        if [ $# -eq 0 ]; then
            echo "❌ Specify a barcode"
            echo "Example: $0 barcode 0041270003490"
            deactivate
            exit 1
        fi
        BARCODE="$1"
        echo "📦 Searching barcode: $BARCODE"
        "$PYTHON_PATH" -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from fatsecret_client import FatSecretClient
fs = FatSecretClient()
result = fs.search_foods('$BARCODE', search_type='barcode')
if result and 'foods' in result and 'food' in result['foods']:
    food = result['foods']['food']
    if isinstance(food, list):
        food = food[0]
    print(f'✅ Found: {food.get(\"food_name\")}')
    print(f'   Brand: {food.get(\"brand_name\", \"-\")}')
    print(f'   ID: {food.get(\"food_id\")}')
else:
    print('❌ Product not found')
"
        ;;
    
    recipes)
        if [ $# -eq 0 ]; then
            echo "❌ Specify a recipe query"
            echo "Example: $0 recipes \"low carb dinner\""
            deactivate
            exit 1
        fi
        QUERY="$1"
        echo "🍳 Searching recipes: $QUERY"
        "$PYTHON_PATH" -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from fatsecret_client import FatSecretClient
fs = FatSecretClient()
result = fs.search_recipes('$QUERY')
if result and 'recipes' in result and 'recipe' in result['recipes']:
    recipes = result['recipes']['recipe']
    if not isinstance(recipes, list):
        recipes = [recipes]
    for i, recipe in enumerate(recipes[:5], 1):
        name = recipe.get('recipe_name', 'Unknown')
        desc = recipe.get('recipe_description', '')[:100]
        print(f'{i}. {name}')
        if desc:
            print(f'   {desc}...')
else:
    print('❌ No recipes found')
"
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        echo "❌ Unknown command: $COMMAND"
        show_help
        ;;
esac

# Deactivate virtual environment
deactivate