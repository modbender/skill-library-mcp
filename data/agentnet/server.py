"""
AgentNet Network Server - v0.1

FastAPI server that hosts the agent registry.
Agents POST to register, GET to discover.

Endpoints:
  POST   /agents              - Register an agent
  GET    /agents              - List all agents
  GET    /agents/{id}         - Get a specific agent
  PATCH  /agents/{id}/status  - Update agent status
  DELETE /agents/{id}         - Deregister
  GET    /discover            - Find agents by capability
  POST   /handshake           - Initiate a handshake
  GET    /stats               - Registry statistics
  GET    /health              - Server health check

Deploy:
  uvicorn server:app --host 0.0.0.0 --port 8765 --reload
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import time
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from registry import Registry, AgentEntry, get_registry
from card import AgentCard, create_nix_card
from handshake import HandshakeProtocol, TaskOffer, HandshakeMessage


# --- Pydantic Models ---

class ContactModel(BaseModel):
    type: str
    value: str
    api: Optional[str] = None
    session_key: Optional[str] = None


class RegisterRequest(BaseModel):
    agent_id: Optional[str] = None
    name: str
    description: str
    capabilities: list[str]
    skills: list[str] = []
    dna_fingerprint: str
    contact: dict
    status: str = "online"
    trust_score: float = 0.5
    metadata: dict = {}


class StatusUpdateRequest(BaseModel):
    status: str  # online | offline | busy


class TaskOfferModel(BaseModel):
    agent_id: str
    needs: list[str]
    offers: list[str]
    description: str
    priority: str = "normal"
    expires_in: int = 3600


class InitiateHandshakeRequest(BaseModel):
    initiator_card: dict
    responder_id: str


class RespondHandshakeRequest(BaseModel):
    session_id: str
    responder_card: dict
    accept: bool = True
    rejection_reason: str = ""


class NegotiateRequest(BaseModel):
    session_id: str
    from_agent_id: str
    offer: TaskOfferModel


class AcceptRequest(BaseModel):
    session_id: str
    from_agent_id: str


# --- Global State ---

_protocol = HandshakeProtocol()


# --- App Factory ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup: seed registry with Nix if not already present
    reg = get_registry()
    nix = create_nix_card()
    if not reg.get(nix.agent_id):
        from registry import AgentEntry
        entry = AgentEntry(
            agent_id=nix.agent_id,
            name=nix.name,
            description=nix.description,
            capabilities=nix.capabilities,
            dna_fingerprint=nix.dna_fingerprint,
            contact=nix.contact,
            status="online",
            skills=nix.skills,
            trust_score=nix.trust_score,
            registered_at=time.time(),
            last_seen=time.time(),
            metadata=nix.metadata,
        )
        reg.register(entry)
        print(f"[AgentNet] Seeded registry with Nix ({nix.agent_id})")
    yield
    print("[AgentNet] Server shutting down")


app = FastAPI(
    title="AgentNet Registry",
    description="Agent-to-agent discovery network. Find collaborators, negotiate tasks, build the agent internet.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Routes ---

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0", "service": "AgentNet"}


@app.get("/stats")
def stats():
    reg = get_registry()
    return reg.stats()


# Agents

@app.post("/agents", status_code=201)
def register_agent(req: RegisterRequest):
    reg = get_registry()

    # Generate ID if not provided
    agent_id = req.agent_id
    if not agent_id:
        from card import generate_agent_id
        agent_id = generate_agent_id(req.name)

    entry = AgentEntry(
        agent_id=agent_id,
        name=req.name,
        description=req.description,
        capabilities=req.capabilities,
        dna_fingerprint=req.dna_fingerprint,
        contact=req.contact,
        status=req.status,
        skills=req.skills,
        trust_score=req.trust_score,
        registered_at=time.time(),
        last_seen=time.time(),
        metadata=req.metadata,
    )
    result = reg.register(entry)
    return result


@app.get("/agents")
def list_agents(
    status: Optional[str] = Query(None, description="Filter by status: online|offline|busy"),
    limit: int = Query(50, ge=1, le=200),
):
    reg = get_registry()
    agents = reg.list_all()
    if status:
        agents = [a for a in agents if a.get("status") == status]
    # Sort by trust score
    agents.sort(key=lambda a: a.get("trust_score", 0), reverse=True)
    return {"agents": agents[:limit], "total": len(agents)}


@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    reg = get_registry()
    agent = reg.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent


@app.patch("/agents/{agent_id}/status")
def update_status(agent_id: str, req: StatusUpdateRequest):
    reg = get_registry()
    try:
        ok = reg.update_status(agent_id, req.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return {"status": "updated", "agent_id": agent_id, "new_status": req.status}


@app.delete("/agents/{agent_id}")
def deregister_agent(agent_id: str):
    reg = get_registry()
    ok = reg.deregister(agent_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return {"status": "deregistered", "agent_id": agent_id}


# Discovery

@app.get("/discover")
def discover(
    capability: str = Query(..., description="Capability to search for"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
):
    reg = get_registry()
    results = reg.discover(capability, status=status)
    # Strip sensitive contact info for public discovery
    public_results = []
    for a in results[:limit]:
        public = dict(a)
        # Keep contact type but mask private details
        contact = dict(public.get("contact", {}))
        if "session_key" in contact:
            contact["session_key"] = "[request via handshake]"
        public["contact"] = contact
        public_results.append(public)
    return {
        "query": capability,
        "results": public_results,
        "count": len(public_results),
    }


# Handshake

@app.post("/handshake/initiate")
def handshake_initiate(req: InitiateHandshakeRequest):
    card = AgentCard.from_dict(req.initiator_card)
    msg = _protocol.initiate(card, req.responder_id)
    return msg.to_dict()


@app.post("/handshake/respond")
def handshake_respond(req: RespondHandshakeRequest):
    from handshake import HandshakeMessage
    card = AgentCard.from_dict(req.responder_card)
    # Reconstruct the hello message
    session = _protocol.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    hello_data = next(
        (m for m in session.messages if m["phase"] == "hello"), None
    )
    if not hello_data:
        raise HTTPException(status_code=400, detail="No HELLO message in session")

    hello_msg = HandshakeMessage(
        session_id=hello_data["session_id"],
        from_agent=hello_data["from_agent"],
        to_agent=hello_data["to_agent"],
        phase=hello_data["phase"],
        payload=hello_data["payload"],
        timestamp=hello_data["timestamp"],
        nonce=hello_data["nonce"],
    )
    msg = _protocol.respond(hello_msg, card, req.accept, req.rejection_reason)
    return msg.to_dict()


@app.post("/handshake/negotiate")
def handshake_negotiate(req: NegotiateRequest):
    offer = TaskOffer(**req.offer.model_dump())
    msg = _protocol.negotiate(req.session_id, req.from_agent_id, offer)
    return msg.to_dict()


@app.post("/handshake/accept")
def handshake_accept(req: AcceptRequest):
    try:
        msg = _protocol.accept(req.session_id, req.from_agent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return msg.to_dict()


@app.get("/handshake/{session_id}")
def get_handshake_session(session_id: str):
    session = _protocol.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("AGENTNET_PORT", 8765))
    host = os.environ.get("AGENTNET_HOST", "0.0.0.0")
    print(f"[AgentNet] Starting on {host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=True)
