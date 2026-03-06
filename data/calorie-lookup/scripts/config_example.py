import os

# Copy this file to config.py and fill in your USDA FDC API key.
# 将此文件复制为 config.py 并填入你的 USDA FDC API Key。
# Free signup / 免费申请: https://fdc.nal.usda.gov/api-key-signup.html

USDA_API_KEY = os.getenv("USDA_FDC_API_KEY", "").strip()
FDC_BASE = "https://api.nal.usda.gov/fdc/v1"

CACHE_DB_PATH = os.getenv("CALORIE_SKILL_CACHE_DB", "calorie_skill_cache.sqlite3")
HTTP_TIMEOUT_SEC = 15
SEARCH_PAGE_SIZE = 8
PREFERRED_DATA_TYPES = [
    "Foundation",
    "SR Legacy",
    "Survey (FNDDS)",
    "Branded",
]

# Get your free API key at https://spoonacular.com/food-api/console
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY", "")
SPOONACULAR_BASE = "https://api.spoonacular.com"
SPOONACULAR_SEARCH_LIMIT = 1  # Minimize point consumption: 1+1=2pts per search
CROSS_VALIDATE_DEFAULT = False
