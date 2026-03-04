from __future__ import annotations
#!/usr/bin/env python3
"""
Insight Engine — main orchestrator.
Collect → Analyse → Reflect → Write to Notion.

Usage:
  python3 engine.py --mode daily
  python3 engine.py --mode weekly
  python3 engine.py --mode monthly
  python3 engine.py --mode daily --dry-run    # Ollama locally, skip Notion
  python3 engine.py --mode daily --data-only  # print data packet + prompt, no API calls

Required env vars:
  ANTHROPIC_API_KEY       Anthropic API key
  NOTION_API_KEY          Notion integration token
  LANGFUSE_BASE_URL       Langfuse server URL (default: http://localhost:3100)
  LANGFUSE_PUBLIC_KEY     Langfuse public key
  LANGFUSE_SECRET_KEY     Langfuse secret key
  NOTION_ROOT_PAGE_ID     Root Notion page ID
  NOTION_DAILY_DB_ID      Notion daily entries database ID

Or configure via config/analyst.yaml.
"""
import argparse, json, os, sys, yaml
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from collectors.langfuse_data import build_experiment_summary
from collectors.openclaw_logs import parse_daily_log, aggregate_log_events, read_memory_file
from collectors.git_collector import build_git_summary
from collectors.cp_trends import collect_cp_trends
from writers.notion_writer import write_daily_reflection, write_periodic_reflection

CONFIG_PATH = ROOT / 'config' / 'analyst.yaml'
PROMPT_DIR = ROOT / 'prompts'


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    # Fallback: env vars
    return {
        'langfuse': {
            'base_url': os.environ.get('LANGFUSE_BASE_URL', 'http://localhost:3100'),
            'public_key': os.environ.get('LANGFUSE_PUBLIC_KEY', ''),
            'secret_key': os.environ.get('LANGFUSE_SECRET_KEY', ''),
        },
        'openclaw': {
            'log_dir': os.environ.get('OPENCLAW_LOG_DIR', '/tmp/openclaw'),
            'memory_dir': os.environ.get('OPENCLAW_MEMORY_DIR', os.path.expanduser('~/.openclaw/memory')),
        },
        'notion': {
            'root_page_id': os.environ.get('NOTION_ROOT_PAGE_ID', ''),
            'daily_db_id': os.environ.get('NOTION_DAILY_DB_ID', ''),
        },
        'models': {
            'daily_analysis': os.environ.get('INSIGHT_DAILY_MODEL', 'anthropic/claude-sonnet-4-6'),
            'weekly_analysis': os.environ.get('INSIGHT_WEEKLY_MODEL', 'anthropic/claude-sonnet-4-6'),
            'monthly_analysis': os.environ.get('INSIGHT_MONTHLY_MODEL', 'anthropic/claude-opus-4-6'),
        },
        'thresholds': {
            'min_data_points_for_trend': 7,
            'anomaly_sigma': 2.0,
            'latency_p95_warn_ms': 10000,
            'cost_spike_pct': 50,
            'experiment_min_runs': 10,
        },
    }


def get_anthropic_key() -> str:
    key = os.environ.get('ANTHROPIC_API_KEY')
    if key:
        return key
    raise RuntimeError("Set ANTHROPIC_API_KEY env var.")


def call_claude(system_prompt: str, user_content: str, model: str) -> str:
    """Generate narrative via Anthropic API."""
    import anthropic
    client = anthropic.Anthropic(api_key=get_anthropic_key())
    print(f"[insight-engine] calling {model}...")
    msg = client.messages.create(
        model=model.replace('anthropic/', ''),
        max_tokens=2048,
        system=system_prompt,
        messages=[{'role': 'user', 'content': user_content}]
    )
    return msg.content[0].text


def call_ollama(system_prompt: str, user_content: str,
                model: str = 'mistral', base_url: str = 'http://localhost:11434') -> str:
    """Fallback: local Ollama for cost-free offline / dry-run use."""
    import requests as req
    resp = req.post(
        f'{base_url}/api/chat',
        json={
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content}
            ],
            'stream': False
        },
        timeout=120
    )
    resp.raise_for_status()
    return resp.json()['message']['content']


def build_daily_data_packet(cfg: dict, target_date: date) -> dict:
    """Collect and aggregate all data for a daily analysis. Pure Python — no LLM."""
    log_events = parse_daily_log(
        log_dir=cfg['openclaw']['log_dir'],
        target_date=target_date
    )
    log_summary = aggregate_log_events(log_events)

    memory_text = read_memory_file(
        memory_dir=cfg['openclaw']['memory_dir'],
        target_date=target_date
    ) or '(no memory file for this date)'

    try:
        langfuse_summary = build_experiment_summary(
            days_back=1, base_url=cfg['langfuse']['base_url'],
            public_key=cfg['langfuse'].get('public_key', ''),
            secret_key=cfg['langfuse'].get('secret_key', ''),
        )
    except Exception as e:
        langfuse_summary = {'error': str(e), 'note': 'Langfuse unavailable'}

    try:
        langfuse_week = build_experiment_summary(
            days_back=7, base_url=cfg['langfuse']['base_url'],
            public_key=cfg['langfuse'].get('public_key', ''),
            secret_key=cfg['langfuse'].get('secret_key', ''),
        )
    except Exception as e:
        langfuse_week = {'error': str(e)}

    git_summary = build_git_summary(since='1 day ago')

    cp_scores: dict = {}
    cp_api_url = os.environ.get('CP_API_URL', 'http://localhost:8765')
    try:
        import requests as req
        r = req.get(f'{cp_api_url}/status', timeout=5)
        if r.status_code == 200:
            cp_scores = r.json().get('confidence', {})
    except Exception:
        cp_scores = {'note': 'control plane unavailable'}

    cp_trends = collect_cp_trends(api_url=cp_api_url)

    return {
        'date': str(target_date),
        'log_summary': log_summary,
        'langfuse_today': langfuse_summary,
        'langfuse_7day': langfuse_week,
        'git_activity': git_summary,
        'cp_scores': cp_scores,
        'cp_trends': cp_trends,
        'memory_context': memory_text[:6000],
    }


def build_weekly_data_packet(cfg: dict, week_ending: date) -> dict:
    days = [week_ending - timedelta(days=i) for i in range(6, -1, -1)]
    daily_summaries = {}
    for d in days:
        events = parse_daily_log(log_dir=cfg['openclaw']['log_dir'], target_date=d)
        daily_summaries[str(d)] = aggregate_log_events(events)

    try:
        langfuse_week = build_experiment_summary(
            days_back=7, base_url=cfg['langfuse']['base_url'],
            public_key=cfg['langfuse'].get('public_key', ''),
            secret_key=cfg['langfuse'].get('secret_key', ''),
        )
    except Exception as e:
        langfuse_week = {'error': str(e)}

    return {
        'week_ending': str(week_ending),
        'week_starting': str(days[0]),
        'daily_summaries': daily_summaries,
        'langfuse_7day': langfuse_week,
    }


def build_monthly_data_packet(cfg: dict, month_ending: date) -> dict:
    days = [month_ending - timedelta(days=i) for i in range(29, -1, -1)]
    daily_summaries = {}
    for d in days:
        events = parse_daily_log(log_dir=cfg['openclaw']['log_dir'], target_date=d)
        daily_summaries[str(d)] = aggregate_log_events(events)

    try:
        langfuse_month = build_experiment_summary(
            days_back=30, base_url=cfg['langfuse']['base_url'],
            public_key=cfg['langfuse'].get('public_key', ''),
            secret_key=cfg['langfuse'].get('secret_key', ''),
        )
    except Exception as e:
        langfuse_month = {'error': str(e)}

    return {
        'month_ending': str(month_ending),
        'daily_summaries': daily_summaries,
        'langfuse_30day': langfuse_month,
    }


def run(mode: str, dry_run: bool = False, data_only: bool = False):
    cfg = load_config()
    today = date.today()
    print(f"[insight-engine] mode={mode} date={today} dry_run={dry_run}")

    if mode == 'daily':
        data = build_daily_data_packet(cfg, today)
        system_prompt = (PROMPT_DIR / 'daily_analyst.md').read_text()
        user_content = (
            f"Analyse this operational data and produce today's reflection:\n\n"
            f"```json\n{json.dumps(data, indent=2, default=str)}\n```"
        )
    elif mode == 'weekly':
        data = build_weekly_data_packet(cfg, today)
        system_prompt = (PROMPT_DIR / 'weekly_analyst.md').read_text()
        user_content = (
            f"Analyse this 7-day operational data and produce the weekly synthesis:\n\n"
            f"```json\n{json.dumps(data, indent=2, default=str)}\n```"
        )
    elif mode == 'monthly':
        data = build_monthly_data_packet(cfg, today)
        system_prompt = (PROMPT_DIR / 'monthly_analyst.md').read_text()
        user_content = (
            f"Analyse this 30-day operational data and produce the monthly strategic analysis:\n\n"
            f"```json\n{json.dumps(data, indent=2, default=str)}\n```"
        )
    else:
        print(f"Unknown mode: {mode}. Use daily, weekly, or monthly.")
        sys.exit(1)

    if data_only:
        print("=== SYSTEM PROMPT ===")
        print(system_prompt)
        print("\n=== USER CONTENT ===")
        print(user_content)
        return

    if dry_run:
        ollama_model = os.environ.get('OLLAMA_MODEL', 'mistral')
        ollama_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        print(f"[insight-engine] dry run — calling local Ollama ({ollama_model})...")
        reflection = call_ollama(system_prompt, user_content,
                                 model=ollama_model, base_url=ollama_url)
        print("\n" + "=" * 60)
        print(reflection)
        return

    model = cfg['models'][f'{mode}_analysis']
    reflection = call_claude(system_prompt, user_content, model)

    if mode == 'daily':
        write_daily_reflection(content=reflection, target_date=today, cfg=cfg)
        print(f"[insight-engine] daily reflection written to Notion ✅")
    else:
        write_periodic_reflection(content=reflection, period=mode, cfg=cfg)
        print(f"[insight-engine] {mode} reflection written to Notion ✅")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Insight Engine')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly'], required=True)
    parser.add_argument('--dry-run', action='store_true',
                        help='Use Ollama locally, skip Notion write')
    parser.add_argument('--data-only', action='store_true',
                        help='Output data packet + prompt to stdout, no API calls')
    args = parser.parse_args()
    run(mode=args.mode, dry_run=args.dry_run, data_only=args.data_only)
