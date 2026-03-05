"""
ConvoYield Cloud API Server — The revenue engine.

A lightweight FastAPI server that:
1. Collects yield telemetry from bots running ConvoYield
2. Stores analytics in SQLite (zero infrastructure cost)
3. Serves the real-time dashboard
4. Manages API keys and billing tiers
5. Serves premium playbook downloads

Run with: python -m cloud.server
"""

from __future__ import annotations

import json
import os
import time
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import stripe
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from cloud.database import Database

# ── Stripe Config ──────────────────────────────────────────────────────────────

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

STRIPE_PRICE_MAP = {
    "pro": os.environ.get("STRIPE_PRICE_PRO", ""),
    "enterprise": os.environ.get("STRIPE_PRICE_ENTERPRISE", ""),
    "saas_sales": os.environ.get("STRIPE_PRICE_SAAS_SALES", ""),
    "ecommerce": os.environ.get("STRIPE_PRICE_ECOMMERCE", ""),
    "real_estate": os.environ.get("STRIPE_PRICE_REAL_ESTATE", ""),
    "healthcare": os.environ.get("STRIPE_PRICE_HEALTHCARE", ""),
}

TIER_PRODUCTS = {"pro", "enterprise"}
PLAYBOOK_PRODUCTS = {"saas_sales", "ecommerce", "real_estate", "healthcare"}

# ── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="ConvoYield Cloud",
    description="Conversational Yield Analytics Platform",
    version="1.0.0",
)

DASHBOARD_DIR = Path(__file__).parent / "dashboard"
STATIC_DIR = Path(__file__).parent / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

db = Database()


# ── Models ────────────────────────────────────────────────────────────────────

class YieldEvent(BaseModel):
    session_id: str
    turn_number: int
    timestamp: Optional[str] = None
    sentiment: float
    sentiment_delta: float
    momentum: float
    estimated_yield: float
    captured_yield: float
    phase: str
    risk_level: float
    recommended_play: Optional[str] = None
    arbitrage_types: list[str] = []
    micro_conversion_types: list[str] = []
    user_message_length: int = 0


class ConversionEvent(BaseModel):
    session_id: str
    conversion_type: str
    value: float
    timestamp: Optional[str] = None


class SessionSummary(BaseModel):
    session_id: str
    total_turns: int
    estimated_yield: float
    captured_yield: float
    final_phase: str
    final_sentiment: float
    duration_seconds: float
    plays_recommended: list[str] = []
    arbitrage_detected: list[str] = []
    conversions_captured: list[str] = []


class ApiKeyRequest(BaseModel):
    email: str
    company: Optional[str] = None
    tier: str = "free"  # free, pro, enterprise


# ── Authentication ────────────────────────────────────────────────────────────

def _verify_api_key(api_key: str) -> dict:
    """Verify an API key and return the associated account."""
    account = db.get_account_by_key(api_key)
    if not account:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return account


# ── Dashboard Routes ──────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main analytics dashboard."""
    dashboard_file = DASHBOARD_DIR / "index.html"
    if dashboard_file.exists():
        return HTMLResponse(content=dashboard_file.read_text())
    return HTMLResponse(content="<h1>ConvoYield Cloud</h1><p>Dashboard loading...</p>")


# ── API Key Management ────────────────────────────────────────────────────────

@app.post("/api/v1/keys")
async def create_api_key(request: ApiKeyRequest):
    """Create a new API key (self-service registration)."""
    api_key = f"cy_{secrets.token_urlsafe(32)}"
    account_id = str(uuid.uuid4())

    db.create_account(
        account_id=account_id,
        email=request.email,
        company=request.company,
        tier=request.tier,
        api_key=api_key,
    )

    return {
        "api_key": api_key,
        "account_id": account_id,
        "tier": request.tier,
        "limits": _tier_limits(request.tier),
    }


# ── Telemetry Ingestion ──────────────────────────────────────────────────────

@app.post("/api/v1/events/yield")
async def ingest_yield_event(
    event: YieldEvent,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """
    Ingest a yield event from a bot running ConvoYield.

    This is the core data pipeline — every turn of every conversation
    sends its yield analysis here.
    """
    account = _verify_api_key(x_api_key)

    # Check rate limits based on tier
    if not _check_rate_limit(account):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Upgrade your plan.")

    db.insert_yield_event(
        account_id=account["id"],
        session_id=event.session_id,
        turn_number=event.turn_number,
        timestamp=event.timestamp or datetime.utcnow().isoformat(),
        sentiment=event.sentiment,
        sentiment_delta=event.sentiment_delta,
        momentum=event.momentum,
        estimated_yield=event.estimated_yield,
        captured_yield=event.captured_yield,
        phase=event.phase,
        risk_level=event.risk_level,
        recommended_play=event.recommended_play,
        arbitrage_types=json.dumps(event.arbitrage_types),
        micro_conversion_types=json.dumps(event.micro_conversion_types),
        user_message_length=event.user_message_length,
    )

    return {"status": "ok", "event_id": str(uuid.uuid4())}


@app.post("/api/v1/events/conversion")
async def ingest_conversion(
    event: ConversionEvent,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """Record a micro-conversion capture."""
    account = _verify_api_key(x_api_key)

    db.insert_conversion(
        account_id=account["id"],
        session_id=event.session_id,
        conversion_type=event.conversion_type,
        value=event.value,
        timestamp=event.timestamp or datetime.utcnow().isoformat(),
    )

    return {"status": "ok"}


@app.post("/api/v1/events/session")
async def ingest_session_summary(
    summary: SessionSummary,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """Record a completed session summary."""
    account = _verify_api_key(x_api_key)

    db.insert_session_summary(
        account_id=account["id"],
        session_id=summary.session_id,
        total_turns=summary.total_turns,
        estimated_yield=summary.estimated_yield,
        captured_yield=summary.captured_yield,
        final_phase=summary.final_phase,
        final_sentiment=summary.final_sentiment,
        duration_seconds=summary.duration_seconds,
        plays_recommended=json.dumps(summary.plays_recommended),
        arbitrage_detected=json.dumps(summary.arbitrage_detected),
        conversions_captured=json.dumps(summary.conversions_captured),
    )

    return {"status": "ok"}


# ── Analytics API (Powers the Dashboard) ──────────────────────────────────────

@app.get("/api/v1/analytics/overview")
async def analytics_overview(
    x_api_key: str = Header(..., alias="X-API-Key"),
    hours: int = 24,
):
    """
    Get a high-level overview of yield analytics.

    This is the main dashboard data endpoint.
    """
    account = _verify_api_key(x_api_key)
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

    stats = db.get_overview_stats(account["id"], since)

    return {
        "period_hours": hours,
        "total_sessions": stats["total_sessions"],
        "total_turns": stats["total_turns"],
        "total_estimated_yield": round(stats["total_estimated_yield"], 2),
        "total_captured_yield": round(stats["total_captured_yield"], 2),
        "capture_efficiency": round(
            (stats["total_captured_yield"] / stats["total_estimated_yield"] * 100)
            if stats["total_estimated_yield"] > 0 else 0, 1
        ),
        "avg_yield_per_session": round(stats["avg_yield_per_session"], 2),
        "avg_sentiment": round(stats["avg_sentiment"], 2),
        "avg_momentum": round(stats["avg_momentum"], 2),
        "avg_risk": round(stats["avg_risk"], 2),
        "value_left_on_table": round(
            stats["total_estimated_yield"] - stats["total_captured_yield"], 2
        ),
    }


@app.get("/api/v1/analytics/plays")
async def analytics_plays(
    x_api_key: str = Header(..., alias="X-API-Key"),
    hours: int = 24,
):
    """Get play recommendation analytics — which plays are working best?"""
    account = _verify_api_key(x_api_key)
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    return {"plays": db.get_play_stats(account["id"], since)}


@app.get("/api/v1/analytics/arbitrage")
async def analytics_arbitrage(
    x_api_key: str = Header(..., alias="X-API-Key"),
    hours: int = 24,
):
    """Get arbitrage opportunity analytics."""
    account = _verify_api_key(x_api_key)
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    return {"arbitrage": db.get_arbitrage_stats(account["id"], since)}


@app.get("/api/v1/analytics/conversions")
async def analytics_conversions(
    x_api_key: str = Header(..., alias="X-API-Key"),
    hours: int = 24,
):
    """Get micro-conversion analytics."""
    account = _verify_api_key(x_api_key)
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    return {"conversions": db.get_conversion_stats(account["id"], since)}


@app.get("/api/v1/analytics/timeline")
async def analytics_timeline(
    x_api_key: str = Header(..., alias="X-API-Key"),
    hours: int = 24,
    granularity: str = "hour",
):
    """Get yield over time — the heartbeat chart for the dashboard."""
    account = _verify_api_key(x_api_key)
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    return {"timeline": db.get_yield_timeline(account["id"], since, granularity)}


@app.get("/api/v1/analytics/sessions")
async def analytics_sessions(
    x_api_key: str = Header(..., alias="X-API-Key"),
    limit: int = 50,
    offset: int = 0,
):
    """Get individual session details — drill down into specific conversations."""
    account = _verify_api_key(x_api_key)
    return {"sessions": db.get_sessions(account["id"], limit, offset)}


@app.get("/api/v1/analytics/leaderboard")
async def analytics_leaderboard(
    x_api_key: str = Header(..., alias="X-API-Key"),
    hours: int = 24,
):
    """
    Get the session leaderboard — which conversations generated the most yield?

    This is the 'whale alert' — spot your highest-value conversations.
    """
    account = _verify_api_key(x_api_key)
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    return {"leaderboard": db.get_leaderboard(account["id"], since)}


# ── Playbook Marketplace ─────────────────────────────────────────────────────

@app.get("/api/v1/playbooks")
async def list_playbooks():
    """List available premium playbooks."""
    return {
        "playbooks": [
            {
                "id": "saas_sales",
                "name": "SaaS Sales Mastery",
                "description": "25 plays optimized for B2B SaaS sales conversations. Includes trial-to-paid conversion, expansion revenue, and churn prevention plays.",
                "plays_count": 25,
                "price": 49.0,
                "currency": "USD",
                "billing": "monthly",
            },
            {
                "id": "ecommerce",
                "name": "E-Commerce Revenue Max",
                "description": "22 plays for online retail: cart recovery, upsell cascades, review harvesting, repeat purchase triggers.",
                "plays_count": 22,
                "price": 39.0,
                "currency": "USD",
                "billing": "monthly",
            },
            {
                "id": "real_estate",
                "name": "Real Estate Closer",
                "description": "20 plays for real estate: lead qualification, showing scheduling, offer negotiation, referral generation.",
                "plays_count": 20,
                "price": 79.0,
                "currency": "USD",
                "billing": "monthly",
            },
            {
                "id": "healthcare",
                "name": "Healthcare Engagement",
                "description": "18 plays for healthcare: appointment booking, treatment adherence, patient satisfaction, insurance navigation.",
                "plays_count": 18,
                "price": 99.0,
                "currency": "USD",
                "billing": "monthly",
            },
        ]
    }


@app.post("/api/v1/playbooks/{playbook_id}/activate")
async def activate_playbook(
    playbook_id: str,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """Activate a premium playbook for the account (requires active subscription)."""
    account = _verify_api_key(x_api_key)

    # Enterprise gets all playbooks free
    if account.get("tier") == "enterprise":
        db.activate_playbook(account["id"], playbook_id)
        return {"status": "activated", "playbook_id": playbook_id,
                "message": "Playbook is now active. Import it in your ConvoYield engine."}

    # Otherwise require an active subscription for this playbook
    subs = db.get_active_subscriptions(account["id"])
    has_sub = any(s["product_id"] == playbook_id and s["status"] == "active" for s in subs)
    if not has_sub:
        raise HTTPException(status_code=402,
                            detail="Active subscription required. Purchase via /api/v1/billing/checkout.")

    db.activate_playbook(account["id"], playbook_id)
    return {"status": "activated", "playbook_id": playbook_id,
            "message": "Playbook is now active. Import it in your ConvoYield engine."}


# ── Billing / Pricing ────────────────────────────────────────────────────────

@app.get("/api/v1/pricing")
async def pricing():
    """Get pricing tiers."""
    return {
        "tiers": [
            {
                "id": "free",
                "name": "Starter",
                "price": 0,
                "currency": "USD",
                "billing": "monthly",
                "limits": _tier_limits("free"),
                "features": [
                    "Core ConvoYield engine",
                    "5 conversations/day analytics",
                    "Basic dashboard",
                    "Community playbook (20 plays)",
                ],
            },
            {
                "id": "pro",
                "name": "Professional",
                "price": 49,
                "currency": "USD",
                "billing": "monthly",
                "limits": _tier_limits("pro"),
                "features": [
                    "Everything in Starter",
                    "Unlimited conversations",
                    "Full analytics dashboard",
                    "Yield forecasting",
                    "Play performance tracking",
                    "1 premium playbook included",
                    "Email reports",
                    "Priority support",
                ],
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price": 299,
                "currency": "USD",
                "billing": "monthly",
                "limits": _tier_limits("enterprise"),
                "features": [
                    "Everything in Professional",
                    "Unlimited everything",
                    "All premium playbooks included",
                    "Custom playbook creation",
                    "Team leaderboard",
                    "API access",
                    "Webhook integrations",
                    "Dedicated support",
                    "Custom analytics",
                    "White-label option",
                ],
            },
        ]
    }


# ── Stripe Billing ────────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    product_id: str  # "pro", "enterprise", "saas_sales", etc.


@app.post("/api/v1/billing/checkout")
async def billing_checkout(
    body: CheckoutRequest,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """Create a Stripe Checkout Session and return the redirect URL."""
    account = _verify_api_key(x_api_key)
    price_id = STRIPE_PRICE_MAP.get(body.product_id)
    if not price_id:
        raise HTTPException(status_code=400, detail=f"Unknown product: {body.product_id}")

    # Get or create Stripe customer
    customer_id = account.get("stripe_customer_id")
    if not customer_id:
        customer = stripe.Customer.create(
            email=account["email"],
            metadata={"account_id": account["id"]},
        )
        customer_id = customer.id
        db.update_account_stripe(account["id"], customer_id)

    product_type = "tier" if body.product_id in TIER_PRODUCTS else "playbook"
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{BASE_URL}/dashboard?checkout=success",
        cancel_url=f"{BASE_URL}/dashboard?checkout=cancel",
        metadata={
            "account_id": account["id"],
            "product_id": body.product_id,
            "product_type": product_type,
        },
    )

    return {"checkout_url": session.url, "session_id": session.id}


@app.post("/api/v1/billing/webhook")
async def billing_webhook(request: Request):
    """Handle Stripe webhook events with signature verification."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    etype = event["type"]
    obj = event["data"]["object"]

    if etype == "checkout.session.completed":
        _handle_checkout_completed(obj)
    elif etype == "customer.subscription.updated":
        _handle_subscription_updated(obj)
    elif etype == "customer.subscription.deleted":
        _handle_subscription_deleted(obj)
    elif etype == "invoice.payment_failed":
        _handle_payment_failed(obj)

    return {"status": "ok"}


def _handle_checkout_completed(session: dict):
    meta = session.get("metadata", {})
    account_id = meta.get("account_id")
    product_id = meta.get("product_id")
    product_type = meta.get("product_type")
    stripe_sub_id = session.get("subscription")
    stripe_cust_id = session.get("customer")

    if not account_id or not product_id:
        return

    sub_id = str(uuid.uuid4())
    db.create_subscription(
        sub_id=sub_id,
        account_id=account_id,
        stripe_subscription_id=stripe_sub_id or "",
        stripe_customer_id=stripe_cust_id or "",
        product_type=product_type or "tier",
        product_id=product_id,
    )
    db.update_account_stripe(account_id, stripe_cust_id or "", stripe_sub_id)

    if product_type == "tier":
        db.update_account_tier(account_id, product_id)
    else:
        db.activate_playbook(account_id, product_id)


def _handle_subscription_updated(subscription: dict):
    status = subscription.get("status", "")
    stripe_sub_id = subscription.get("id", "")
    if status in ("active", "past_due", "trialing"):
        db.update_subscription_status(stripe_sub_id, status)
    elif status in ("canceled", "unpaid"):
        _cancel_subscription(subscription)


def _handle_subscription_deleted(subscription: dict):
    _cancel_subscription(subscription)


def _handle_payment_failed(invoice: dict):
    stripe_sub_id = invoice.get("subscription", "")
    if stripe_sub_id:
        db.update_subscription_status(stripe_sub_id, "past_due")


def _cancel_subscription(subscription: dict):
    stripe_sub_id = subscription.get("id", "")
    stripe_cust_id = subscription.get("customer", "")
    db.update_subscription_status(stripe_sub_id, "canceled")

    account = db.get_account_by_stripe_customer(stripe_cust_id)
    if not account:
        return

    # Check what product this subscription was for
    subs = db.get_active_subscriptions(account["id"])
    # If no active tier subscriptions remain, downgrade to free
    has_tier = any(s["product_type"] == "tier" and s["status"] == "active"
                   and s["stripe_subscription_id"] != stripe_sub_id for s in subs)
    if not has_tier:
        db.update_account_tier(account["id"], "free")

    # Deactivate playbooks whose subscriptions are canceled
    for s in subs:
        if (s["stripe_subscription_id"] == stripe_sub_id
                and s["product_type"] == "playbook"):
            db.deactivate_playbook(account["id"], s["product_id"])


@app.get("/api/v1/billing/info")
async def billing_info(
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """Return current billing info: tier, subscriptions, Stripe customer."""
    account = _verify_api_key(x_api_key)
    subs = db.get_active_subscriptions(account["id"])

    return {
        "tier": account.get("tier", "free"),
        "stripe_customer_id": account.get("stripe_customer_id"),
        "active_subscriptions": len(subs),
        "subscriptions": [
            {
                "product_type": s["product_type"],
                "product_id": s["product_id"],
                "status": s["status"],
            }
            for s in subs
        ],
    }


@app.post("/api/v1/billing/portal")
async def billing_portal(
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """Create a Stripe Billing Portal session for self-service management."""
    account = _verify_api_key(x_api_key)
    customer_id = account.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="No billing account. Subscribe first.")

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{BASE_URL}/dashboard",
    )

    return {"portal_url": session.url}


# ── Webhook Management ────────────────────────────────────────────────────────

@app.post("/api/v1/webhooks")
async def create_webhook(
    request: Request,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """
    Register a webhook to receive real-time yield alerts.

    Use cases:
    - Alert when a conversation exceeds $100 estimated yield
    - Alert when risk level exceeds 0.7
    - Alert on high-value arbitrage opportunities
    - Daily yield summary reports
    """
    account = _verify_api_key(x_api_key)
    body = await request.json()

    webhook_id = str(uuid.uuid4())
    db.create_webhook(
        account_id=account["id"],
        webhook_id=webhook_id,
        url=body.get("url"),
        events=json.dumps(body.get("events", ["high_yield", "high_risk"])),
        threshold=body.get("threshold", 100.0),
    )

    return {"webhook_id": webhook_id, "status": "active"}


# ── Health & Status ───────────────────────────────────────────────────────────

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": "operational",
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tier_limits(tier: str) -> dict:
    limits = {
        "free": {
            "conversations_per_day": 5,
            "events_per_day": 100,
            "retention_days": 7,
            "playbooks": 0,
            "webhooks": 0,
        },
        "pro": {
            "conversations_per_day": -1,  # unlimited
            "events_per_day": -1,
            "retention_days": 90,
            "playbooks": 1,
            "webhooks": 3,
        },
        "enterprise": {
            "conversations_per_day": -1,
            "events_per_day": -1,
            "retention_days": 365,
            "playbooks": -1,  # all included
            "webhooks": -1,
        },
    }
    return limits.get(tier, limits["free"])


def _check_rate_limit(account: dict) -> bool:
    """Check if the account is within its rate limits."""
    tier = account.get("tier", "free")
    limits = _tier_limits(tier)

    if limits["events_per_day"] == -1:
        return True  # Unlimited

    count = db.count_events_today(account["id"])
    return count < limits["events_per_day"]


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
