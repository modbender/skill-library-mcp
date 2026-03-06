import re
from config import settings

FORBIDDEN_KEYWORDS = [
    "DROP", "ALTER", "DELETE", "INSERT",
    "UPDATE", "TRUNCATE", "MERGE",
    "CREATE", "GRANT", "REVOKE"
]

def validate_query(sql: str):
    sql_upper = sql.upper()

    if not sql_upper.strip().startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed.")

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_upper):
            raise ValueError(f"Keyword '{keyword}' is not allowed.")

    if "LIMIT" not in sql_upper:
        sql = sql.rstrip(";") + f" LIMIT {settings.MAX_ROWS}"

    return sql
