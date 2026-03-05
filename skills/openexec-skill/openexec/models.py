from pydantic import BaseModel
from typing import Optional

class ApprovalArtifact(BaseModel):
    approval_id: str
    tenant_id: str
    action_hash: str
    issued_at: str
    expires_at: str
    signature: str

class ExecutionRequest(BaseModel):
    action: str
    payload: Optional[dict] = None
    nonce: str
    approval_artifact: Optional[ApprovalArtifact] = None

class ExecutionResult(BaseModel):
    id: str
    action: str
    result: dict
    approved: bool
    receipt: Optional[str] = None
