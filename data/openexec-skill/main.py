from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openexec.models import ExecutionRequest
from openexec.receipts import verify_receipt
from openexec.engine import execute
from openexec.approval_validator import ApprovalError
from openexec.db import init_db
import os
import datetime

VERSION = "0.1.10"

@asynccontextmanager
async def lifespan(application):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"service": "OpenExec", "status": "running", "version": VERSION}

@app.get("/health")
async def health():
    exec_mode = os.getenv("OPENEXEC_MODE", "demo")
    sig_status = "enabled" if exec_mode == "clawshield" else "disabled"
    allowed_actions = os.getenv("OPENEXEC_ALLOWED_ACTIONS", "")
    if allowed_actions:
        allow_list = [a.strip() for a in allowed_actions.split(",") if a.strip()]
        restriction = "restricted"
    else:
        allow_list = None
        restriction = "open"
    result = {
        "status": "healthy",
        "exec_mode": exec_mode,
        "signature_verification": sig_status,
        "restriction": restriction,
    }
    if allow_list is not None:
        result["allow_list"] = allow_list
    else:
        result["warning"] = "No execution allow-list configured"
    return result

@app.get("/version")
def version():
    return {
        "version": VERSION,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/ready")
def ready():
    return {"ready": True}

@app.post("/execute")
def execute_action(request: ExecutionRequest):
    try:
        result = execute(request)
        return result.model_dump()
    except ApprovalError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class ReceiptVerifyRequest(BaseModel):
    exec_id: str
    result: str
    receipt: str

@app.post("/receipts/verify")
def verify_receipt_endpoint(req: ReceiptVerifyRequest):
    valid = verify_receipt(req.exec_id, req.result, req.receipt)
    return {"valid": valid}
