#!/usr/bin/env python3
"""Starter GTM workflows for Salesforce skill."""

from __future__ import annotations

from salesforce_client import SalesforceClient


def with_next_action(workflow_name: str, rows: list[dict], summary: str, follow_up_query: str, automation_idea: str) -> dict:
    return {
        'workflow': workflow_name,
        'summary': summary,
        'count': len(rows),
        'next_best_action': {
            'follow_up_query': follow_up_query,
            'automation_idea': automation_idea,
        },
        'rows': rows,
    }


def top_accounts_to_work_today(sf: SalesforceClient, limit: int = 25):
    query = f"""
        SELECT Id, Name, Domain__c, Website,
               accountIntentScore6sense__c, accountBuyingStage6sense__c,
               Churned__c, LastActivityDate, Owner.Name
        FROM Account
        WHERE accountIntentScore6sense__c >= 70
          AND accountBuyingStage6sense__c IN ('Consideration','Decision','Purchase')
          AND (Churned__c = false OR Churned__c = null)
        ORDER BY accountIntentScore6sense__c DESC
        LIMIT {limit}
    """
    rows = sf.query(query)
    out = []
    for r in rows:
        if sf.has_open_opportunity(r['Id']):
            continue
        if sf.was_contacted_recently(r['Id'], days=30):
            continue
        out.append({
            'account_name': r.get('Name'),
            'account_domain': r.get('Domain__c') or r.get('Website'),
            'reason_to_act': 'High intent and no recent outreach/open opp',
            'priority_score': r.get('accountIntentScore6sense__c'),
            'owner': (r.get('Owner') or {}).get('Name') if isinstance(r.get('Owner'), dict) else None,
            'suggested_next_step': 'Create outbound touch with tailored 6sense context',
        })
    rows = out[:limit]
    return with_next_action(
        workflow_name='top_accounts_to_work_today',
        rows=rows,
        summary='High-intent accounts with no open opp and no recent outreach.',
        follow_up_query='Show decision makers and latest campaign touches for these accounts.',
        automation_idea='Schedule a daily 8am run and send top 10 to sales channel.',
    )


def pipeline_rescue_board(sf: SalesforceClient, stale_days: int = 14, limit: int = 50):
    query = f"""
        SELECT Id, Name, StageName, CloseDate, LastActivityDate, LastActivityInDays,
               AccountId, Account.Name, Account.Churned__c, Owner.Name
        FROM Opportunity
        WHERE IsClosed = false
          AND LastActivityInDays >= {stale_days}
        ORDER BY LastActivityInDays DESC
        LIMIT {limit}
    """
    rows = sf.query(query)
    out = []
    for r in rows:
        out.append({
            'account_name': (r.get('Account') or {}).get('Name') if isinstance(r.get('Account'), dict) else None,
            'account_domain': None,
            'reason_to_act': f"Open opp stale for {r.get('LastActivityInDays')} days",
            'priority_score': r.get('LastActivityInDays'),
            'owner': (r.get('Owner') or {}).get('Name') if isinstance(r.get('Owner'), dict) else None,
            'suggested_next_step': 'Schedule rescue call and update mutual action plan',
            'opportunity_name': r.get('Name'),
            'stage': r.get('StageName'),
        })
    return with_next_action(
        workflow_name='pipeline_rescue_board',
        rows=out,
        summary='Open opportunities with stale activity that need intervention.',
        follow_up_query='Show last 3 activities and owner notes for each stale opportunity.',
        automation_idea='Run every weekday and alert owners when staleness exceeds threshold.',
    )


def campaign_followup_opportunities(sf: SalesforceClient, limit: int = 100):
    query = f"""
        SELECT Id, Campaign.Name, HasResponded, Status, CreatedDate,
               Contact.AccountId, Contact.Account.Name, Contact.Name,
               Lead.Company, Lead.Name
        FROM CampaignMember
        WHERE HasResponded = true
        ORDER BY CreatedDate DESC
        LIMIT {limit}
    """
    rows = sf.query(query)
    out = []
    for r in rows:
        account_id = None
        account_name = None
        if isinstance(r.get('Contact'), dict) and isinstance(r['Contact'].get('Account'), dict):
            account_id = r['Contact']['Account'].get('Id') or r['Contact'].get('AccountId')
            account_name = r['Contact']['Account'].get('Name')

        # keep simple heuristic: no recent touch at account level
        if account_id and sf.was_contacted_recently(account_id, days=21):
            continue

        lead_company = (r.get('Lead') or {}).get('Company') if isinstance(r.get('Lead'), dict) else None
        out.append({
            'account_name': account_name or lead_company,
            'account_domain': None,
            'reason_to_act': 'Campaign response without recent follow-up signal',
            'priority_score': 1,
            'owner': None,
            'suggested_next_step': 'Route to owner for timely follow-up',
            'campaign': (r.get('Campaign') or {}).get('Name') if isinstance(r.get('Campaign'), dict) else None,
        })
    return with_next_action(
        workflow_name='campaign_followup_opportunities',
        rows=out,
        summary='Campaign responders with no recent follow-up signal.',
        follow_up_query='Show responsible owner and best contact for each response cluster.',
        automation_idea='Run after major campaigns and auto-create follow-up tasks for owners.',
    )


if __name__ == '__main__':
    sf = SalesforceClient()
    print(top_accounts_to_work_today(sf))
