#!/usr/bin/env python3
"""Schema discovery helpers for Salesforce onboarding."""

from __future__ import annotations

from typing import Any, Dict, List

from salesforce_client import SalesforceClient


DEFAULT_OBJECTS = [
    "Account", "Contact", "Lead", "Opportunity", "Campaign", "CampaignMember", "Task", "Event", "EmailMessage"
]

SIGNAL_PATTERNS = {
    "intent": ["6sense", "intent", "6qa"],
    "revenue": ["arr", "mrr", "revenue", "subscription"],
    "risk": ["churn", "risk", "at_risk"],
    "engagement": ["campaign", "respond", "activity", "email", "meeting"],
}


class SchemaDiscovery:
    def __init__(self, sf: SalesforceClient):
        self.sf = sf

    def list_objects(self) -> List[Dict[str, Any]]:
        token = self.sf._get_access_token()  # noqa: SLF001
        url = f"{self.sf.instance_url}/services/data/{self.sf.API_VERSION}/sobjects"
        import requests

        response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.json().get("sobjects", [])

    def discover(self, focus_objects: List[str] | None = None) -> Dict[str, Any]:
        object_index = {o["name"]: o for o in self.list_objects()}
        targets = focus_objects or DEFAULT_OBJECTS

        available = [o for o in targets if o in object_index]
        missing = [o for o in targets if o not in object_index]

        schema: Dict[str, Any] = {"available": available, "missing": missing, "objects": {}, "signals": {k: [] for k in SIGNAL_PATTERNS}}

        for name in available:
            desc = self.sf.describe_object(name)
            fields = desc.get("fields", [])
            schema["objects"][name] = {
                "label": desc.get("label"),
                "queryable": desc.get("queryable"),
                "fields": [
                    {
                        "name": f.get("name"),
                        "label": f.get("label"),
                        "type": f.get("type"),
                        "nillable": f.get("nillable"),
                        "custom": f.get("custom"),
                    }
                    for f in fields
                ],
            }

            for f in fields:
                fname = (f.get("name") or "").lower()
                for bucket, patterns in SIGNAL_PATTERNS.items():
                    if any(p in fname for p in patterns):
                        schema["signals"][bucket].append({"object": name, "field": f.get("name"), "type": f.get("type")})

        return schema


def infer_open_questions(schema: Dict[str, Any]) -> List[str]:
    questions: List[str] = []

    has_6sense = any("6sense" in (s.get("field", "").lower()) for s in schema.get("signals", {}).get("intent", []))
    if has_6sense:
        questions.append("I found probable 6sense fields. Should these drive account prioritization?")

    questions.append("For account matching, should we prioritize Salesforce Id, domain, or account name?")

    if schema.get("signals", {}).get("risk"):
        questions.append("I found risk/churn fields. Should we include churn-risk suppression in prospecting lists?")

    questions.append("Should campaign engagement include both Contacts and Leads by default?")
    questions.append("Any sensitive fields to exclude by default?")
    return questions[:6]
