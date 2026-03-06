from __future__ import annotations
"""
Notion writer — appends insight engine reflections to Notion databases.
Uses existing Daily Activity Log DB for daily; creates weekly/monthly DBs as needed.

Env vars:
  NOTION_API_KEY        Notion integration token
  NOTION_ROOT_PAGE_ID   Root Notion page ID (for creating weekly/monthly DBs)
  NOTION_DAILY_DB_ID    Notion database ID for daily entries
"""
import os
import requests
from datetime import date
from typing import Literal

NOTION_VERSION = '2022-06-28'


def _api_key() -> str:
    key = os.environ.get('NOTION_API_KEY') or os.environ.get('NOTION_KEY')
    if key:
        return key
    raise RuntimeError('Set NOTION_API_KEY env var.')


def _headers() -> dict:
    return {
        'Authorization': f'Bearer {_api_key()}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION,
    }


def _markdown_to_blocks(text: str) -> list[dict]:
    """Convert markdown text to Notion block objects (simple converter)."""
    blocks = []
    for line in text.split('\n'):
        if line.startswith('## '):
            blocks.append({
                'object': 'block', 'type': 'heading_2',
                'heading_2': {'rich_text': [{'type': 'text', 'text': {'content': line[3:]}}]}
            })
        elif line.startswith('**') and line.endswith('**'):
            blocks.append({
                'object': 'block', 'type': 'heading_3',
                'heading_3': {'rich_text': [{'type': 'text', 'text': {'content': line[2:-2]}}]}
            })
        elif line.startswith('- '):
            blocks.append({
                'object': 'block', 'type': 'bulleted_list_item',
                'bulleted_list_item': {'rich_text': [{'type': 'text', 'text': {'content': line[2:]}}]}
            })
        elif line.strip():
            blocks.append({
                'object': 'block', 'type': 'paragraph',
                'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': line}}]}
            })
    return blocks[:100]  # Notion API limit per request


def _find_existing_page(db_id: str, title: str) -> str | None:
    """Return page ID if a page with this title already exists in the DB."""
    resp = requests.post(
        f'https://api.notion.com/v1/databases/{db_id}/query',
        headers=_headers(),
        json={'filter': {'property': 'Name', 'title': {'equals': title}}, 'page_size': 1},
        timeout=15
    )
    if resp.ok:
        results = resp.json().get('results', [])
        if results:
            return results[0]['id']
    return None


def write_daily_reflection(content: str, target_date: date, cfg: dict) -> str:
    """
    Write daily insight reflection to the Daily Activity Log database.
    Idempotent — updates existing page for today if one already exists.
    """
    db_id = cfg['notion']['daily_db_id'] or os.environ.get('NOTION_DAILY_DB_ID', '')
    if not db_id:
        raise RuntimeError('Set NOTION_DAILY_DB_ID in config or env var.')

    title = f'Insight Engine — {target_date}'
    blocks = _markdown_to_blocks(content)

    existing_id = _find_existing_page(db_id, title)
    if existing_id:
        requests.patch(
            f'https://api.notion.com/v1/pages/{existing_id}',
            headers=_headers(),
            json={'properties': {'Notes': {'rich_text': [{'text': {'content': content[:2000]}}]}}},
            timeout=15
        ).raise_for_status()
        rerun_blocks = [
            {'object': 'block', 'type': 'divider', 'divider': {}},
            {'object': 'block', 'type': 'heading_2',
             'heading_2': {'rich_text': [{'type': 'text', 'text': {'content': f'Re-run — {date.today()}'}}]}},
        ] + blocks
        requests.patch(
            f'https://api.notion.com/v1/blocks/{existing_id}/children',
            headers=_headers(),
            json={'children': rerun_blocks[:50]},
            timeout=30
        )
        print(f'[notion] Updated existing daily page: {existing_id}')
        return existing_id

    payload = {
        'parent': {'database_id': db_id},
        'properties': {
            'Name': {'title': [{'text': {'content': title}}]},
            'Date': {'date': {'start': str(target_date)}},
            'Category': {'select': {'name': 'Insight Engine'}},
            'Model': {'select': {'name': cfg['models']['daily_analysis'].replace('anthropic/', '')}},
            'Notes': {'rich_text': [{'text': {'content': content[:2000]}}]},
        },
        'children': blocks,
    }

    resp = requests.post(
        'https://api.notion.com/v1/pages',
        headers=_headers(),
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    page_id = resp.json()['id']
    print(f'[notion] Created daily page: {page_id}')
    return page_id


def _get_or_create_periodic_db(period: Literal['weekly', 'monthly'], cfg: dict) -> str:
    """Get or create the weekly/monthly reflections database."""
    root_page_id = (cfg['notion'].get('root_page_id') or
                    os.environ.get('NOTION_ROOT_PAGE_ID', ''))
    if not root_page_id:
        raise RuntimeError('Set NOTION_ROOT_PAGE_ID in config or env var.')

    db_key = f'{period}_db_id'
    if db_id := cfg['notion'].get(db_key):
        return db_id

    # Search for existing DB
    resp = requests.post(
        'https://api.notion.com/v1/search',
        headers=_headers(),
        json={
            'query': f'Insight Engine — {period.title()} Reflections',
            'filter': {'value': 'database', 'property': 'object'},
        },
        timeout=15
    )
    results = resp.json().get('results', [])
    if results:
        db_id = results[0]['id']
        cfg['notion'][db_key] = db_id
        return db_id

    # Create it
    db_title = f'Insight Engine — {period.title()} Reflections'
    resp = requests.post(
        'https://api.notion.com/v1/databases',
        headers=_headers(),
        json={
            'parent': {'type': 'page_id', 'page_id': root_page_id},
            'title': [{'type': 'text', 'text': {'content': db_title}}],
            'properties': {
                'Name': {'title': {}},
                'Period': {'date': {}},
                'Model': {'rich_text': {}},
                'Notes': {'rich_text': {}},
            },
        },
        timeout=15
    )
    resp.raise_for_status()
    db_id = resp.json()['id']
    cfg['notion'][db_key] = db_id
    print(f'[notion] Created {period} DB: {db_id}')
    return db_id


def write_periodic_reflection(
    content: str,
    period: Literal['weekly', 'monthly'],
    cfg: dict
) -> str:
    """Write weekly or monthly reflection to its Notion database."""
    db_id = _get_or_create_periodic_db(period, cfg)
    today = date.today()
    title = f'Insight Engine — {period.title()} ending {today}'
    model_key = f'{period}_analysis'

    payload = {
        'parent': {'database_id': db_id},
        'properties': {
            'Name': {'title': [{'text': {'content': title}}]},
            'Period': {'date': {'start': str(today)}},
            'Model': {'rich_text': [{'text': {'content': cfg['models'].get(model_key, 'unknown')}}]},
            'Notes': {'rich_text': [{'text': {'content': content[:2000]}}]},
        },
        'children': _markdown_to_blocks(content),
    }

    resp = requests.post(
        'https://api.notion.com/v1/pages',
        headers=_headers(),
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    page_id = resp.json()['id']
    print(f'[notion] Created {period} page: {page_id}')
    return page_id
