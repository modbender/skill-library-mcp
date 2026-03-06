#!/usr/bin/env python3
"""
machins CLI helper for the OpenClaw skill.

Usage:
    python3 machins.py <action> [args...]

Actions:
    register  --name N --slug S [--description D]
    fulfill   <need> [--budget N] [--type T]
    browse    [--search S] [--type T] [--side S] [--limit N]
    propose   <listing_id> [--terms T]
    accept    <trade_id>
    deliver   <trade_id> [--payload JSON] [--endpoint URL]
    confirm   <trade_id>
    dispute   <trade_id> [--reason R]
    review    <trade_id> --rating N [--body T]
    create-listing --title T --slug S --price N [--type T] [--description D] [--tags T] [--side S] [--auto-accept]
    trades    [--role R] [--status S] [--limit N]
    wallet
    inbox     [--unread] [--ack ID1,ID2,...] [--ack-all]
    gaps      [--limit N]
    platform-info
"""

from __future__ import annotations

import argparse
import json
import sys


def _get_client():
    try:
        from machins import Machins
    except ImportError:
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "machins==0.1.0", "-q"],
            stdout=subprocess.DEVNULL,
        )
        from machins import Machins
    return Machins()


def _out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_fulfill(args):
    client = _get_client()
    result = client.fulfill(
        args.need,
        budget=args.budget,
        listing_type=args.type,
    )
    _out(result)


def cmd_browse(args):
    client = _get_client()
    page = client.browse(
        search=args.search,
        listing_type=args.type,
        side=args.side,
        min_price=args.min_price,
        max_price=args.max_price,
        limit=args.limit,
    )
    _out({
        "items": [i.model_dump() for i in page.items],
        "total": page.total,
        "has_more": page.has_more,
    })


def cmd_propose(args):
    client = _get_client()
    trade = client.propose_trade(args.listing_id, args.terms)
    _out(trade.model_dump())


def cmd_accept(args):
    client = _get_client()
    trade = client.accept_trade(args.trade_id)
    _out(trade.model_dump())


def cmd_deliver(args):
    client = _get_client()
    payload = json.loads(args.payload) if args.payload else None
    trade = client.deliver_trade(
        args.trade_id,
        payload=payload,
        endpoint_url=args.endpoint,
    )
    _out(trade.model_dump())


def cmd_confirm(args):
    client = _get_client()
    trade = client.confirm_trade(args.trade_id)
    _out(trade.model_dump())


def cmd_dispute(args):
    client = _get_client()
    trade = client.dispute_trade(args.trade_id, args.reason)
    _out(trade.model_dump())


def cmd_create_listing(args):
    client = _get_client()
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    listing = client.create_listing(
        args.title,
        args.slug,
        args.type or "task",
        args.price,
        description=args.description,
        side=args.side or "offer",
        tags=tags,
        auto_accept=args.auto_accept,
    )
    _out(listing.model_dump())


def cmd_trades(args):
    client = _get_client()
    page = client.list_trades(
        role=args.role,
        status=args.status,
        limit=args.limit,
    )
    _out({
        "items": [i.model_dump() for i in page.items],
        "total": page.total,
        "has_more": page.has_more,
    })


def cmd_wallet(args):
    client = _get_client()
    wallet = client.get_wallet()
    _out(wallet.model_dump())


def cmd_gaps(args):
    client = _get_client()
    _out(client.get_market_gaps(limit=args.limit))


def cmd_register(args):
    client = _get_client()
    result = client.join(
        args.name,
        args.slug,
        description=args.description,
    )
    _out({
        "agent_id": result.agent_id,
        "agent_slug": result.agent_slug,
        "api_key": result.api_key,
        "starter_credits": result.starter_credits,
    })


def cmd_review(args):
    client = _get_client()
    review = client.create_review(args.trade_id, args.rating, args.body)
    _out(review.model_dump())


def cmd_inbox(args):
    client = _get_client()
    if args.ack_all:
        result = client.ack_all_inbox()
        _out(result)
    elif args.ack:
        ids = [i.strip() for i in args.ack.split(",")]
        result = client.ack_inbox(ids)
        _out(result)
    else:
        result = client.get_inbox(unread=args.unread, limit=args.limit)
        _out(result)


def cmd_platform_info(args):
    client = _get_client()
    _out(client.get_platform_info())


def main():
    parser = argparse.ArgumentParser(description="machins marketplace CLI")
    sub = parser.add_subparsers(dest="action", required=True)

    # register
    p = sub.add_parser("register", help="Register a new agent")
    p.add_argument("--name", required=True, help="Agent display name")
    p.add_argument("--slug", required=True, help="Unique slug (lowercase, hyphens)")
    p.add_argument("--description", help="What this agent does")
    p.set_defaults(func=cmd_register)

    # fulfill
    p = sub.add_parser("fulfill", help="Find and auto-trade")
    p.add_argument("need", help="What you need")
    p.add_argument("--budget", type=float)
    p.add_argument("--type", help="task, data, api, model, asset")
    p.set_defaults(func=cmd_fulfill)

    # browse
    p = sub.add_parser("browse", help="Search marketplace")
    p.add_argument("--search")
    p.add_argument("--type")
    p.add_argument("--side", choices=["offer", "request"])
    p.add_argument("--min-price", type=float)
    p.add_argument("--max-price", type=float)
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_browse)

    # propose
    p = sub.add_parser("propose", help="Propose a trade")
    p.add_argument("listing_id")
    p.add_argument("--terms")
    p.set_defaults(func=cmd_propose)

    # accept
    p = sub.add_parser("accept", help="Accept a trade")
    p.add_argument("trade_id")
    p.set_defaults(func=cmd_accept)

    # deliver
    p = sub.add_parser("deliver", help="Deliver on a trade")
    p.add_argument("trade_id")
    p.add_argument("--payload", help="JSON payload")
    p.add_argument("--endpoint", help="Endpoint URL")
    p.set_defaults(func=cmd_deliver)

    # confirm
    p = sub.add_parser("confirm", help="Confirm delivery")
    p.add_argument("trade_id")
    p.set_defaults(func=cmd_confirm)

    # dispute
    p = sub.add_parser("dispute", help="Dispute a trade")
    p.add_argument("trade_id")
    p.add_argument("--reason")
    p.set_defaults(func=cmd_dispute)

    # create-listing
    p = sub.add_parser("create-listing", help="Create a listing")
    p.add_argument("--title", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--type")
    p.add_argument("--description")
    p.add_argument("--side", choices=["offer", "request"])
    p.add_argument("--tags", help="Comma-separated")
    p.add_argument("--auto-accept", action="store_true")
    p.set_defaults(func=cmd_create_listing)

    # trades
    p = sub.add_parser("trades", help="List trades")
    p.add_argument("--role", choices=["buyer", "seller"])
    p.add_argument("--status")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_trades)

    # wallet
    p = sub.add_parser("wallet", help="Check wallet balance")
    p.set_defaults(func=cmd_wallet)

    # review
    p = sub.add_parser("review", help="Leave a review")
    p.add_argument("trade_id")
    p.add_argument("--rating", type=int, required=True, help="Rating 1-5")
    p.add_argument("--body", help="Review text")
    p.set_defaults(func=cmd_review)

    # inbox
    p = sub.add_parser("inbox", help="Check notifications")
    p.add_argument("--unread", action="store_true", help="Only unread")
    p.add_argument("--ack", help="Comma-separated notification IDs to acknowledge")
    p.add_argument("--ack-all", action="store_true", help="Acknowledge all")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_inbox)

    # gaps
    p = sub.add_parser("gaps", help="Find market opportunities")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_gaps)

    # platform-info
    p = sub.add_parser("platform-info", help="Platform capabilities & endpoints")
    p.set_defaults(func=cmd_platform_info)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(json.dumps({"error": type(e).__name__, "message": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
