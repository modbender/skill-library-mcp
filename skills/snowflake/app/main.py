from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from validator import validate_query
from database import execute_query

app = FastAPI(
    title="Snowflake Data Engineering Skill",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    sql: str

@app.post("/execute")
def run_query(request: QueryRequest):
    try:
        validated_sql = validate_query(request.sql)
        result = execute_query(validated_sql)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
