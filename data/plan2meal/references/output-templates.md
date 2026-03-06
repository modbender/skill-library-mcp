# Plan2Meal Output Templates

Use these concise formats.

## Success: recipe added

✅ Recipe added successfully!

📖 **<Recipe Name>**
🔗 Source: <domain>
⚙️ Method: `<method>`
⏰ Scraped at: <time>

🥘 **Ingredients** (<count>)
• <item>
• <item>

## Success: list recipes

📚 **Your Recipes** (<total> total)

• `<id>` - <name>
• `<id>` - <name>

## Success: search

🔍 **Search Results** for "<term>" (<count>)

• `<id>` - <name>
• `<id>` - <name>

## Success: list created

✅ Grocery list created!

🛒 **<name>**
ID: `<id>`

## Error: auth required

❌ You're not authenticated for Plan2Meal.
Run: `plan2meal login`

## Error: invalid URL

❌ Invalid URL. Please provide a valid recipe URL.

## Error: backend/config

❌ Plan2Meal backend is unreachable or misconfigured.
Default backend is `https://gallant-bass-875.convex.cloud` unless `CONVEX_URL` is overridden.
