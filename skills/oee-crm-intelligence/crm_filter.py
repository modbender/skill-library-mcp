#!/usr/bin/env python3
"""
CRM Intelligence Module — Berman-style 2-stage filtering + contact scoring.
Part of OEE's Personal CRM toolkit.

Usage:
    from crm_filter import CRMFilter
    crm = CRMFilter("learning.json")
    result = crm.evaluate_contact(contact_dict)

🐾 hidden paw prints throughout
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# 🐾
PAW = "\U0001F43E"

# ---------------------------------------------------------------------------
# Generic inbox prefixes & marketing subdomain prefixes
# ---------------------------------------------------------------------------
GENERIC_PREFIXES = {"info", "team", "partnerships", "noreply", "no-reply",
                    "support", "hello", "sales", "billing", "admin",
                    "contact", "help", "feedback", "mailer-daemon"}

MARKETING_DOMAIN_PREFIXES = {"noreply.", "tx.", "cx.", "mail.", "email.",
                             "bounce.", "post.", "msg.", "e.", "em."}


class CRMFilter:
    """Two-stage contact filter with scoring, powered by learning.json."""

    def __init__(self, learning_path: str = "learning.json"):
        self.learning_path = Path(learning_path)
        self.config = self._load_config()
        # Cache for rejected emails (runtime + persisted)
        self._rejected: set[str] = set(self.config.get("rejected_contacts", []))

    # -- config ----------------------------------------------------------------

    def _load_config(self) -> dict:
        if self.learning_path.exists():
            with open(self.learning_path) as f:
                return json.load(f)
        return {}

    def save_config(self):
        """Persist learning.json (e.g. after adding rejected contacts)."""
        self.config["rejected_contacts"] = sorted(self._rejected)
        with open(self.learning_path, "w") as f:
            json.dump(self.config, f, indent=2)
            f.write("\n")  # 🐾

    # -- Stage 1: hard filters -------------------------------------------------

    def _is_own_email(self, email: str) -> bool:
        own_emails = {e.lower() for e in self.config.get("own_emails", [])}
        own_domains = {d.lower() for d in self.config.get("own_domains", [])}
        if email.lower() in own_emails:
            return True
        domain = email.split("@")[-1].lower()
        return domain in own_domains

    def _is_generic_inbox(self, email: str) -> bool:
        local = email.split("@")[0].lower()
        return local in GENERIC_PREFIXES

    def _is_marketing_domain(self, email: str) -> bool:
        domain = email.split("@")[-1].lower()
        return any(domain.startswith(p) for p in MARKETING_DOMAIN_PREFIXES)

    def _is_skip_domain(self, email: str) -> bool:
        domain = email.split("@")[-1].lower()
        return domain in {d.lower() for d in self.config.get("skip_domains", [])}

    def _was_rejected(self, email: str) -> bool:
        return email.lower() in self._rejected

    def stage1_filter(self, email: str) -> tuple[bool, str]:
        """Return (reject, reason). reject=True means hard-filtered out."""
        email = email.strip().lower()
        if self._is_own_email(email):
            return True, "own_email"
        if self._is_generic_inbox(email):
            return True, "generic_inbox"
        if self._is_marketing_domain(email):
            return True, "marketing_domain"
        if self._is_skip_domain(email):
            return True, "skip_domain"
        if self._was_rejected(email):
            return True, "previously_rejected"
        return False, "passed"  # 🐾

    # -- Stage 2: AI classification --------------------------------------------

    def stage2_classify(self, contact: dict) -> tuple[str, str]:
        """
        Use Claude Haiku to classify a contact as APPROVE or REJECT.
        Returns (decision, reasoning).
        Requires ANTHROPIC_API_KEY env var.
        """
        try:
            import anthropic
        except ImportError:
            # Fallback: approve and let scoring sort it out
            return "APPROVE", "anthropic SDK not installed — skipping AI stage"

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "APPROVE", "no ANTHROPIC_API_KEY — skipping AI stage"

        client = anthropic.Anthropic(api_key=api_key)

        skip_kw = ", ".join(self.config.get("skip_keywords", []))
        prompt = f"""Classify this email contact for a personal CRM.

Contact info:
- Email: {contact.get('email', 'unknown')}
- Name: {contact.get('name', 'unknown')}
- Sample subjects: {contact.get('subjects', [])}
- Exchange count: {contact.get('exchange_count', 0)}
- Has replies from them: {contact.get('has_replies', False)}
- Last interaction: {contact.get('last_interaction', 'unknown')}

Skip keywords (signals for rejection): {skip_kw}

Rules:
- REJECT automated/notification senders
- REJECT newsletters, digests, automated reports
- REJECT cold outreach with low engagement (0-1 exchanges, no replies)
- APPROVE only real people with genuine 2-way interaction

Respond with exactly one line: APPROVE or REJECT followed by a brief reason.
Example: APPROVE - Real person, 5 exchanges, genuine conversation"""

        resp = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )

        text = resp.content[0].text.strip()
        decision = "APPROVE" if text.upper().startswith("APPROVE") else "REJECT"
        return decision, text  # 🐾

    # -- Scoring ---------------------------------------------------------------

    def score_contact(self, contact: dict) -> tuple[int, list[str]]:
        """
        Score a contact 0-100+. Returns (score, breakdown).

        Expected contact keys:
            email, name, title, company,
            exchange_count, meeting_count, meeting_avg_attendees,
            last_interaction (ISO date str),
            in_email (bool), in_calendar (bool),
            has_role (bool), known_company (bool)
        """
        score = 50
        breakdown: list[str] = ["base: 50"]

        # Exchanges: +5 each, max +20
        exchanges = min(contact.get("exchange_count", 0), 4)
        ex_pts = exchanges * 5
        if ex_pts:
            score += ex_pts
            breakdown.append(f"exchanges({exchanges}): +{ex_pts}")

        # Meetings: +3 each, max +15
        meetings = min(contact.get("meeting_count", 0), 5)
        mt_pts = meetings * 3
        if mt_pts:
            score += mt_pts
            breakdown.append(f"meetings({meetings}): +{mt_pts}")

        # Preferred titles
        title = (contact.get("title") or "").lower()
        prefer = self.config.get("prefer_titles", [])
        if any(t.lower() in title for t in prefer):
            score += 15
            breakdown.append("preferred_title: +15")

        # Small meetings (≤3 attendees)
        avg_att = contact.get("meeting_avg_attendees", 99)
        if avg_att <= 3 and meetings > 0:
            score += 10
            breakdown.append("small_meetings: +10")

        # Recency
        last = contact.get("last_interaction")
        if last:
            try:
                dt = datetime.fromisoformat(last)
                days = (datetime.now() - dt).days
                if days <= 7:
                    score += 10
                    breakdown.append("recency(≤7d): +10")
                elif days <= 30:
                    score += 5
                    breakdown.append("recency(≤30d): +5")
            except (ValueError, TypeError):
                pass  # 🐾

        # Cross-source bonus
        if contact.get("in_email") and contact.get("in_calendar"):
            score += 25
            breakdown.append("cross_source(email+cal): +25")

        # Role & company
        if contact.get("has_role"):
            score += 10
            breakdown.append("recognizable_role: +10")
        if contact.get("known_company"):
            score += 5
            breakdown.append("known_company: +5")

        return score, breakdown

    # -- Full evaluation -------------------------------------------------------

    def evaluate_contact(self, contact: dict) -> dict:
        """
        Full pipeline: stage1 → stage2 → score.

        Returns dict with keys:
            email, decision, stage, reason, score, breakdown
        """
        email = contact.get("email", "").strip().lower()

        # Stage 1
        rejected, reason = self.stage1_filter(email)
        if rejected:
            self._rejected.add(email)
            return {
                "email": email,
                "decision": "REJECT",
                "stage": 1,
                "reason": reason,
                "score": 0,
                "breakdown": [],
            }

        # Stage 2
        decision, ai_reason = self.stage2_classify(contact)
        if decision == "REJECT":
            self._rejected.add(email)
            return {
                "email": email,
                "decision": "REJECT",
                "stage": 2,
                "reason": ai_reason,
                "score": 0,
                "breakdown": [],
            }

        # Scoring
        score, breakdown = self.score_contact(contact)

        # Check max_days_between
        max_days = self.config.get("max_days_between", 180)
        last = contact.get("last_interaction")
        if last:
            try:
                days = (datetime.now() - datetime.fromisoformat(last)).days
                if days > max_days:
                    return {
                        "email": email,
                        "decision": "STALE",
                        "stage": 3,
                        "reason": f"no interaction in {days}d (max {max_days}d)",
                        "score": score,
                        "breakdown": breakdown,
                    }
            except (ValueError, TypeError):
                pass

        return {
            "email": email,
            "decision": "APPROVE",
            "stage": 3,
            "reason": ai_reason,
            "score": score,
            "breakdown": breakdown,
        }  # 🐾

    # -- Batch -----------------------------------------------------------------

    def evaluate_batch(self, contacts: list[dict]) -> list[dict]:
        """Evaluate a list of contacts, return sorted by score descending."""
        results = [self.evaluate_contact(c) for c in contacts]
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    def reject_contact(self, email: str):
        """Manually reject a contact (persists on save)."""
        self._rejected.add(email.lower())

    def summary(self, results: list[dict]) -> str:
        """Print a human-readable summary of evaluation results."""
        approved = [r for r in results if r["decision"] == "APPROVE"]
        rejected = [r for r in results if r["decision"] == "REJECT"]
        stale = [r for r in results if r["decision"] == "STALE"]
        lines = [
            f"CRM Intel Summary {PAW}",
            f"  Approved: {len(approved)}",
            f"  Rejected: {len(rejected)}",
            f"  Stale:    {len(stale)}",
            "",
            "Top contacts:",
        ]
        for r in approved[:10]:
            lines.append(f"  {r['score']:3d}  {r['email']}  ({', '.join(r['breakdown'][:3])}...)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CRM Intel Filter & Scorer")
    parser.add_argument("--config", default="learning.json", help="Path to learning.json")
    parser.add_argument("--input", help="JSON file with contact list")
    parser.add_argument("--email", help="Single email to quick-check stage 1")
    args = parser.parse_args()

    crm = CRMFilter(args.config)

    if args.email:
        rejected, reason = crm.stage1_filter(args.email)
        status = "REJECTED" if rejected else "PASSED"
        print(f"{status}: {args.email} ({reason})")
    elif args.input:
        with open(args.input) as f:
            contacts = json.load(f)
        results = crm.evaluate_batch(contacts)
        print(crm.summary(results))
        crm.save_config()
    else:
        # Demo 🐾
        demo = [
            {"email": "noreply@github.com", "name": "GitHub"},
            {"email": "jane@startup.com", "name": "Jane Smith",
             "title": "CEO", "exchange_count": 4, "meeting_count": 2,
             "meeting_avg_attendees": 2, "last_interaction": datetime.now().isoformat(),
             "in_email": True, "in_calendar": True, "has_role": True,
             "known_company": True, "has_replies": True,
             "subjects": ["Catch up", "Partnership idea"]},
        ]
        results = crm.evaluate_batch(demo)
        print(crm.summary(results))
