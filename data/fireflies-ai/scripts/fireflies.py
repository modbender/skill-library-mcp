#!/usr/bin/env python3
"""Fireflies.ai meeting intelligence CLI — query transcripts, summaries, action items, contacts.

Zero dependencies beyond Python stdlib. All data stays on Fireflies servers.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime

API_URL = "https://api.fireflies.ai/graphql"
SOCKS_PROXY = "socks5h://127.0.0.1:1080"


def get_api_key():
    key = os.environ.get("FIREFLIES_API_KEY", "")
    if not key:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("FIREFLIES_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not key:
        print("Error: FIREFLIES_API_KEY not set. Get one at https://app.fireflies.ai/integrations/custom/fireflies", file=sys.stderr)
        sys.exit(1)
    return key


def _try_curl(payload, api_key):
    """Try via curl with SOCKS5 proxy (for datacenter IPs blocked by Cloudflare)."""
    try:
        result = subprocess.run(
            ["curl", "--socks5-hostname", "127.0.0.1:1080", "-s", "-X", "POST",
             "-H", "Content-Type: application/json",
             "-H", f"Authorization: Bearer {api_key}",
             "--data", json.dumps(payload),
             "--max-time", "30",
             API_URL],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def graphql(query, variables=None):
    api_key = get_api_key()
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError):
        # Direct request failed (likely Cloudflare block), try SOCKS5 proxy
        result = _try_curl(payload, api_key)
        if not result:
            print("API error: direct and proxy requests both failed", file=sys.stderr)
            sys.exit(1)
    if "errors" in result:
        print(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}", file=sys.stderr)
        sys.exit(1)
    return result.get("data", {})


# ── Queries ──────────────────────────────────────────────────────────────────

def cmd_meetings(args):
    """List/search meetings."""
    params = []
    variables = {}
    var_defs = []

    if args.limit:
        var_defs.append("$limit: Int")
        params.append("limit: $limit")
        variables["limit"] = args.limit

    if args.skip:
        var_defs.append("$skip: Int")
        params.append("skip: $skip")
        variables["skip"] = args.skip

    if getattr(args, "from", None):
        var_defs.append("$fromDate: DateTime")
        params.append("fromDate: $fromDate")
        variables["fromDate"] = f"{getattr(args, 'from')}T00:00:00.000Z"

    if args.to:
        var_defs.append("$toDate: DateTime")
        params.append("toDate: $toDate")
        variables["toDate"] = f"{args.to}T23:59:59.999Z"

    if args.host:
        var_defs.append("$host: String")
        params.append("host_email: $host")
        variables["host"] = args.host

    if args.participant:
        var_defs.append("$participants: [String]")
        params.append("participants: $participants")
        variables["participants"] = [args.participant]

    if args.mine:
        params.append("mine: true")

    param_str = f"({', '.join(params)})" if params else ""
    var_str = f"({', '.join(var_defs)})" if var_defs else ""

    query = f"""
    query Transcripts{var_str} {{
      transcripts{param_str} {{
        id
        title
        date
        dateString
        duration
        host_email
        organizer_email
        participants
        transcript_url
        summary {{
          short_summary
          action_items
          keywords
        }}
      }}
    }}
    """
    data = graphql(query, variables if variables else None)
    return data.get("transcripts", [])


def cmd_search(args):
    """Search meetings by keyword."""
    scope = args.scope if args.scope else "all"
    query = """
    query Search($keyword: String!, $scope: TranscriptsQueryScope, $limit: Int) {
      transcripts(keyword: $keyword, scope: $scope, limit: $limit) {
        id
        title
        date
        dateString
        duration
        host_email
        participants
        summary {
          short_summary
          keywords
        }
      }
    }
    """
    variables = {"keyword": args.keyword, "scope": scope, "limit": args.limit or 20}
    data = graphql(query, variables)
    return data.get("transcripts", [])


def cmd_transcript(args):
    """Get full transcript."""
    query = """
    query Transcript($id: String!) {
      transcript(id: $id) {
        id
        title
        date
        dateString
        duration
        host_email
        organizer_email
        participants
        transcript_url
        audio_url
        video_url
        speakers { id name }
        sentences {
          index
          speaker_name
          text
          start_time
          end_time
        }
        meeting_attendees {
          displayName
          email
          phoneNumber
        }
      }
    }
    """
    data = graphql(query, {"id": args.id})
    return data.get("transcript")


def cmd_summary(args):
    """Get meeting summary."""
    query = """
    query Transcript($id: String!) {
      transcript(id: $id) {
        id
        title
        dateString
        duration
        summary {
          keywords
          action_items
          outline
          shorthand_bullet
          overview
          bullet_gist
          gist
          short_summary
          short_overview
          meeting_type
          topics_discussed
          transcript_chapters
        }
      }
    }
    """
    data = graphql(query, {"id": args.id})
    return data.get("transcript")


def cmd_actions(args):
    """Get action items from a meeting."""
    query = """
    query Transcript($id: String!) {
      transcript(id: $id) {
        id
        title
        dateString
        summary {
          action_items
        }
      }
    }
    """
    data = graphql(query, {"id": args.id})
    return data.get("transcript")


def cmd_analytics(args):
    """Get meeting analytics."""
    query = """
    query Transcript($id: String!) {
      transcript(id: $id) {
        id
        title
        dateString
        duration
        analytics {
          sentiments {
            negative_pct
            neutral_pct
            positive_pct
          }
          categories {
            questions
            date_times
            metrics
            tasks
          }
          speakers {
            speaker_id
            name
            duration
            word_count
            longest_monologue
            monologues_count
            filler_words
            questions
            duration_pct
            words_per_minute
          }
        }
      }
    }
    """
    data = graphql(query, {"id": args.id})
    return data.get("transcript")


def cmd_attendees(args):
    """Get meeting attendees."""
    query = """
    query Transcript($id: String!) {
      transcript(id: $id) {
        id
        title
        dateString
        meeting_attendees {
          displayName
          email
          phoneNumber
          name
          location
        }
        meeting_attendance {
          name
          join_time
          leave_time
        }
      }
    }
    """
    data = graphql(query, {"id": args.id})
    return data.get("transcript")


def cmd_contacts(args):
    """List all contacts."""
    query = """
    query Contacts {
      contacts {
        email
        name
        picture
        last_meeting_date
      }
    }
    """
    data = graphql(query)
    return data.get("contacts", [])


def cmd_user(args):
    """Get current user info."""
    query = """
    query User {
      user {
        user_id
        name
        email
        num_transcripts
        recent_meeting
        minutes_consumed
        is_admin
        integrations
      }
    }
    """
    data = graphql(query)
    return data.get("user")


def cmd_users(args):
    """List team members."""
    query = """
    query Users {
      users {
        user_id
        name
        email
        num_transcripts
        recent_meeting
        minutes_consumed
        is_admin
      }
    }
    """
    data = graphql(query)
    return data.get("users", [])


# ── Human-readable formatting ───────────────────────────────────────────────

def format_human(data, command):
    if data is None:
        return "No data found."
    if command == "meetings" or command == "search":
        if not data:
            return "No meetings found."
        lines = []
        for t in data:
            dur = f" ({t.get('duration', 0) // 60}m)" if t.get("duration") else ""
            lines.append(f"📅 {t.get('dateString', 'N/A')}{dur} — {t.get('title', 'Untitled')}")
            lines.append(f"   ID: {t.get('id', 'N/A')}")
            if t.get("host_email"):
                lines.append(f"   Host: {t['host_email']}")
            summary = (t.get("summary") or {}).get("short_summary")
            if summary:
                lines.append(f"   Summary: {summary[:200]}")
            lines.append("")
        return "\n".join(lines)
    elif command == "transcript":
        t = data
        lines = [f"# {t.get('title', 'Untitled')}", f"Date: {t.get('dateString', 'N/A')}", ""]
        for s in (t.get("sentences") or []):
            lines.append(f"[{s.get('speaker_name', '?')}] {s.get('text', '')}")
        return "\n".join(lines)
    elif command == "summary":
        t = data
        s = t.get("summary") or {}
        lines = [f"# {t.get('title', 'Untitled')} — Summary", ""]
        if s.get("overview"):
            lines += ["## Overview", s["overview"], ""]
        if s.get("short_summary"):
            lines += ["## Short Summary", s["short_summary"], ""]
        if s.get("action_items"):
            lines += ["## Action Items"]
            for item in s["action_items"]:
                lines.append(f"  - {item}")
            lines.append("")
        if s.get("keywords"):
            lines += [f"Keywords: {', '.join(s['keywords'])}"]
        if s.get("topics_discussed"):
            lines += ["", "## Topics Discussed"]
            for topic in s["topics_discussed"]:
                lines.append(f"  - {topic}")
        return "\n".join(lines)
    elif command == "actions":
        t = data
        items = (t.get("summary") or {}).get("action_items") or []
        if not items:
            return f"No action items for: {t.get('title', 'Untitled')}"
        lines = [f"# Action Items — {t.get('title', 'Untitled')}", ""]
        for i, item in enumerate(items, 1):
            lines.append(f"  {i}. {item}")
        return "\n".join(lines)
    elif command == "analytics":
        t = data
        a = t.get("analytics") or {}
        lines = [f"# Analytics — {t.get('title', 'Untitled')}", ""]
        sent = a.get("sentiments") or {}
        if sent:
            lines += [f"Sentiment: +{sent.get('positive_pct',0):.0f}% / ~{sent.get('neutral_pct',0):.0f}% / -{sent.get('negative_pct',0):.0f}%", ""]
        for sp in (a.get("speakers") or []):
            lines.append(f"🎙️ {sp.get('name','?')}: {sp.get('word_count',0)} words, {sp.get('duration_pct',0):.0f}% talk time, {sp.get('words_per_minute',0):.0f} wpm")
        return "\n".join(lines)
    elif command == "attendees":
        t = data
        lines = [f"# Attendees — {t.get('title', 'Untitled')}", ""]
        for a in (t.get("meeting_attendees") or []):
            name = a.get("displayName") or a.get("name") or "Unknown"
            email = a.get("email") or ""
            lines.append(f"  - {name} <{email}>")
        att = t.get("meeting_attendance") or []
        if att:
            lines += ["", "## Attendance"]
            for a in att:
                lines.append(f"  - {a.get('name','?')}: joined {a.get('join_time','?')}, left {a.get('leave_time','?')}")
        return "\n".join(lines)
    elif command == "contacts":
        if not data:
            return "No contacts found."
        lines = []
        for c in data:
            lines.append(f"👤 {c.get('name', 'Unknown')} <{c.get('email', '')}>  Last met: {c.get('last_meeting_date', 'N/A')}")
        return "\n".join(lines)
    elif command == "user":
        u = data
        return f"User: {u.get('name')} <{u.get('email')}>\nTranscripts: {u.get('num_transcripts')}\nMinutes: {u.get('minutes_consumed')}\nAdmin: {u.get('is_admin')}"
    elif command == "users":
        if not data:
            return "No team members found."
        lines = []
        for u in data:
            lines.append(f"👤 {u.get('name', '?')} <{u.get('email', '')}> — {u.get('num_transcripts', 0)} transcripts")
        return "\n".join(lines)
    return json.dumps(data, indent=2, default=str)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fireflies.ai meeting intelligence CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command", required=True)

    # meetings
    p = sub.add_parser("meetings", help="List meetings")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--skip", type=int)
    p.add_argument("--from", dest="from", help="From date (YYYY-MM-DD)")
    p.add_argument("--to", help="To date (YYYY-MM-DD)")
    p.add_argument("--host", help="Filter by host email")
    p.add_argument("--participant", help="Filter by participant email")
    p.add_argument("--mine", action="store_true", help="Only my meetings")

    # search
    p = sub.add_parser("search", help="Search meetings by keyword")
    p.add_argument("keyword", help="Search keyword")
    p.add_argument("--scope", choices=["title", "sentences", "all"], default="all")
    p.add_argument("--limit", type=int, default=20)

    # transcript
    p = sub.add_parser("transcript", help="Get full transcript")
    p.add_argument("id", help="Meeting/transcript ID")

    # summary
    p = sub.add_parser("summary", help="Get meeting summary")
    p.add_argument("id", help="Meeting/transcript ID")

    # actions
    p = sub.add_parser("actions", help="Get action items")
    p.add_argument("id", help="Meeting/transcript ID")

    # analytics
    p = sub.add_parser("analytics", help="Get meeting analytics")
    p.add_argument("id", help="Meeting/transcript ID")

    # attendees
    p = sub.add_parser("attendees", help="Get meeting attendees")
    p.add_argument("id", help="Meeting/transcript ID")

    # contacts
    sub.add_parser("contacts", help="List contacts")

    # user
    sub.add_parser("user", help="Get current user info")

    # users
    sub.add_parser("users", help="List team members")

    args = parser.parse_args()

    dispatch = {
        "meetings": cmd_meetings,
        "search": cmd_search,
        "transcript": cmd_transcript,
        "summary": cmd_summary,
        "actions": cmd_actions,
        "analytics": cmd_analytics,
        "attendees": cmd_attendees,
        "contacts": cmd_contacts,
        "user": cmd_user,
        "users": cmd_users,
    }

    result = dispatch[args.command](args)

    if args.human:
        print(format_human(result, args.command))
    else:
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
