import os
import uuid
import json
import hashlib
from openexec.registry import get_action
from openexec.models import ExecutionRequest, ExecutionResult
from openexec.settings import is_demo, is_clawshield
from openexec.db import SessionLocal
from openexec.tables import ExecutionLog
from openexec.approval_validator import validate_approval, ApprovalError
from sqlalchemy.exc import IntegrityError

def _check_allow_list(action: str) -> None:
    allowed = os.getenv("OPENEXEC_ALLOWED_ACTIONS", "")
    if allowed:
        allow_list = [a.strip() for a in allowed.split(",") if a.strip()]
        if action not in allow_list:
            raise ApprovalError(f"Action '{action}' is not in the execution allow-list")

def execute(request: ExecutionRequest) -> ExecutionResult:
    db = SessionLocal()
    try:
        existing = db.query(ExecutionLog).filter_by(nonce=request.nonce).first()
        if existing:
            return ExecutionResult(
                id=existing.id,
                action=existing.action,
                result=json.loads(existing.result),
                approved=existing.approved,
                receipt=_make_receipt(existing.id, existing.result)
            )

        _check_allow_list(request.action)
        handler = get_action(request.action)
        payload = request.payload or {}

        if is_demo():
            approved = True
        elif is_clawshield():
            if not request.approval_artifact:
                raise ApprovalError("ClawShield mode requires an approval artifact")
            action_request = {"action": request.action, "payload": payload}
            validate_approval(action_request, request.approval_artifact.model_dump())
            approved = True
        else:
            raise ValueError("Unknown mode")

        result = handler(payload)
        exec_id = str(uuid.uuid4())
        result_json = json.dumps(result, sort_keys=True)

        log = ExecutionLog(
            id=exec_id,
            action=request.action,
            payload=json.dumps(payload, sort_keys=True),
            result=result_json,
            nonce=request.nonce,
            approved=approved
        )

        try:
            db.add(log)
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = db.query(ExecutionLog).filter_by(nonce=request.nonce).first()
            return ExecutionResult(
                id=existing.id,
                action=existing.action,
                result=json.loads(existing.result),
                approved=existing.approved,
                receipt=_make_receipt(existing.id, existing.result)
            )

        return ExecutionResult(
            id=exec_id,
            action=request.action,
            result=result,
            approved=approved,
            receipt=_make_receipt(exec_id, result_json)
        )
    finally:
        db.close()

def _make_receipt(exec_id: str, result: str) -> str:
    data = f"{exec_id}:{result}"
    return hashlib.sha256(data.encode()).hexdigest()
