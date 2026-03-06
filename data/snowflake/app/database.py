import snowflake.connector
from config import settings

def get_connection():
    return snowflake.connector.connect(
        user=settings.SNOWFLAKE_USER,
        account=settings.SNOWFLAKE_ACCOUNT,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
        role=settings.SNOWFLAKE_ROLE,
        client_session_keep_alive=False
    )

def execute_query(sql: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS={settings.QUERY_TIMEOUT_SECONDS}")
        cursor.execute(sql)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]

        return {
            "query_id": cursor.sfqid,
            "row_count": len(results),
            "results": results
        }
    finally:
        cursor.close()
        conn.close()
