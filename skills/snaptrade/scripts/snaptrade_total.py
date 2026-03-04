#!/usr/bin/env python3
import math
from typing import Any, Dict, List, Tuple

from snaptrade_common import load_config, get_client


def extract_amount(balance_obj: Any) -> Tuple[float, str]:
    # balance_obj may be dict or model
    if balance_obj is None:
        return (0.0, "")
    if isinstance(balance_obj, dict):
        total = balance_obj.get("total") or {}
        amount = total.get("amount")
        currency = total.get("currency", "")
    else:
        total = getattr(balance_obj, "total", None)
        amount = None
        currency = ""
        if isinstance(total, dict):
            amount = total.get("amount")
            currency = total.get("currency", "")
        else:
            amount = getattr(total, "amount", None)
            currency = getattr(total, "currency", "")
    if amount is None:
        return (0.0, currency or "")
    return (float(amount), currency or "")


def main():
    cfg = load_config()
    client = get_client(cfg)
    user_id = cfg["user_id"]
    user_secret = cfg["user_secret"]

    # Trigger a manual refresh for all authorizations, then wait for all accounts to sync.
    # Skip refresh/wait on initial sync.
    import time
    from datetime import datetime, timezone

    def parse_ts(ts):
        if not ts:
            return None
        try:
            # handle Z suffix
            if isinstance(ts, str):
                if ts.endswith('Z'):
                    ts = ts.replace('Z', '+00:00')
                return datetime.fromisoformat(ts)
        except Exception:
            return None
        return None

    def is_closed(a):
        status = a.get("status") if isinstance(a, dict) else getattr(a, "status", None)
        if status and str(status).lower() == "closed":
            return True
        meta = a.get("meta") if isinstance(a, dict) else getattr(a, "meta", None)
        meta_status = None
        if isinstance(meta, dict):
            meta_status = meta.get("status")
        else:
            meta_status = getattr(meta, "status", None) if meta else None
        return str(meta_status).lower() == "closed"

    def list_accounts():
        resp = client.account_information.list_user_accounts(user_id=user_id, user_secret=user_secret)
        accounts = getattr(resp, "body", resp)
        if not isinstance(accounts, list):
            accounts = list(accounts) if accounts is not None else []
        # exclude closed accounts
        accounts = [a for a in accounts if not is_closed(a)]
        return accounts

    accounts = list_accounts()
    # Determine if this is initial sync for any account or newly linked accounts
    initial_sync = False
    newly_linked = False
    for a in accounts:
        sync = a.get("sync_status") if isinstance(a, dict) else getattr(a, "sync_status", None)
        holdings = (sync or {}).get("holdings") if isinstance(sync, dict) else getattr(sync, "holdings", None)
        initial_done = None
        if isinstance(holdings, dict):
            initial_done = holdings.get("initial_sync_completed")
        else:
            initial_done = getattr(holdings, "initial_sync_completed", None) if holdings else None
        if initial_done is False:
            initial_sync = True
            break
        # treat very recently created accounts as newly linked
        created = a.get("created_date") if isinstance(a, dict) else getattr(a, "created_date", None)
        created_ts = parse_ts(created)
        if created_ts and (datetime.now(timezone.utc) - created_ts).total_seconds() < 300:
            newly_linked = True

    disabled_auth_ids = set()
    disabled_connections = []
    if not initial_sync and not newly_linked:
        ref_ts = datetime.now(timezone.utc)
        try:
            auth_resp = client.connections.list_brokerage_authorizations(user_id=user_id, user_secret=user_secret)
            authorizations = getattr(auth_resp, "body", auth_resp)
            if not isinstance(authorizations, list):
                authorizations = list(authorizations) if authorizations is not None else []
            for auth in authorizations:
                auth_id = auth.get("id") if isinstance(auth, dict) else getattr(auth, "id", None)
                disabled = auth.get("disabled") if isinstance(auth, dict) else getattr(auth, "disabled", None)
                brokerage = auth.get("brokerage") if isinstance(auth, dict) else getattr(auth, "brokerage", None)
                bname = None
                if isinstance(brokerage, dict):
                    bname = brokerage.get("display_name") or brokerage.get("name")
                else:
                    bname = getattr(brokerage, "display_name", None) or getattr(brokerage, "name", None)
                if disabled:
                    if auth_id:
                        disabled_auth_ids.add(auth_id)
                    if bname:
                        disabled_connections.append(bname)
                    continue
                if not auth_id:
                    continue
                try:
                    client.connections.refresh_brokerage_authorization(
                        authorization_id=auth_id, user_id=user_id, user_secret=user_secret
                    )
                except Exception:
                    # best-effort refresh; continue
                    pass
        except Exception:
            pass

        # Wait for all accounts to show last_successful_sync > ref_ts (max 60s)
        deadline = time.time() + 60
        laggards = None
        while time.time() < deadline:
            laggards = []
            accounts = list_accounts()
            for a in accounts:
                name = a.get("name") if isinstance(a, dict) else getattr(a, "name", None)
                number = a.get("number") if isinstance(a, dict) else getattr(a, "number", None)
                auth_id = a.get("brokerage_authorization") if isinstance(a, dict) else getattr(a, "brokerage_authorization", None)
                if auth_id and auth_id in disabled_auth_ids:
                    continue
                sync = a.get("sync_status") if isinstance(a, dict) else getattr(a, "sync_status", None)
                holdings = (sync or {}).get("holdings") if isinstance(sync, dict) else getattr(sync, "holdings", None)
                last_sync = None
                if isinstance(holdings, dict):
                    last_sync = holdings.get("last_successful_sync")
                else:
                    last_sync = getattr(holdings, "last_successful_sync", None) if holdings else None
                ts = parse_ts(last_sync)
                if ts is None or ts <= ref_ts:
                    laggards.append({"name": name, "number": number, "last_sync": last_sync, "created_date": a.get("created_date") if isinstance(a, dict) else getattr(a, "created_date", None)})
            if not laggards:
                break
            time.sleep(1)

        if laggards:
            # If laggards are newly linked (<5 min old), proceed anyway
            still_wait = []
            for l in laggards:
                created_ts = parse_ts(l.get("created_date"))
                if not created_ts or (datetime.now(timezone.utc) - created_ts).total_seconds() >= 300:
                    still_wait.append(l)
            if still_wait:
                print({"error": "sync_timeout", "laggards": still_wait, "disabled_connections": sorted(set(disabled_connections))})
                return

    resp = client.account_information.list_user_accounts(user_id=user_id, user_secret=user_secret)
    accounts = getattr(resp, "body", resp)
    total_value = 0.0
    currency = None

    if not isinstance(accounts, list):
        # try to coerce
        accounts = list(accounts) if accounts is not None else []

    for acct in accounts:
        account_id = acct.get("id") if isinstance(acct, dict) else getattr(acct, "id", None)
        if not account_id:
            continue
        holdings_resp = client.account_information.get_user_holdings(
            user_id=user_id, user_secret=user_secret, account_id=account_id
        )
        holdings = getattr(holdings_resp, "body", holdings_resp)
        # holdings may be dict with account.balance.total
        bal = None
        if isinstance(holdings, dict):
            bal = (((holdings.get("account") or {}).get("balance") or {}).get("total"))
            if bal:
                amount = bal.get("amount")
                cur = bal.get("currency")
            else:
                amount = None
                cur = None
        else:
            acct_obj = getattr(holdings, "account", None)
            bal_obj = getattr(acct_obj, "balance", None) if acct_obj else None
            total_obj = getattr(bal_obj, "total", None) if bal_obj else None
            amount = getattr(total_obj, "amount", None) if total_obj else None
            cur = getattr(total_obj, "currency", None) if total_obj else None
        if amount is None:
            continue
        total_value += float(amount)
        if cur and not currency:
            currency = cur

    currency = currency or cfg.get("currency", "")
    # print as JSON for easy parsing
    result = {"total_value": round(total_value, 2), "currency": currency}
    if disabled_connections:
        result["disabled_connections"] = sorted(set(disabled_connections))
    print(result)


if __name__ == "__main__":
    main()
