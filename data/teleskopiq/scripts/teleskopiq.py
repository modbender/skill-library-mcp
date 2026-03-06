#!/usr/bin/env python3
"""Teleskopiq API CLI \u2014 interact with the Teleskopiq GraphQL API."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

import requests

ENDPOINT = os.environ.get("TELESKOPIQ_ENDPOINT", "https://teleskopiq.com/api/graphql")
API_KEY = os.environ.get("TELESKOPIQ_API_KEY", "")

DEFAULT_AI_PROMPT = (
    "Write a complete YouTube script for this video using the channel's style. "
    "Include proper section headers (##), and use production tags "
    "[B-ROLL: ...], [VISUAL: ...], [GRAPHIC: ...], [MUSIC: ...], [SFX: ...] throughout."
)


def gql(query, variables=None):
    if not API_KEY:
        print("Error: TELESKOPIQ_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    body = {"query": query}
    if variables:
        body["variables"] = variables
    r = requests.post(
        ENDPOINT,
        json=body,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        print(f"GraphQL errors: {json.dumps(data['errors'], indent=2)}", file=sys.stderr)
        sys.exit(1)
    return data["data"]


def parse_channel_id():
    """Extract channel ID from API key format: tsk_{channelId}_{64hex}."""
    parts = API_KEY.split("_")
    if len(parts) >= 3 and parts[0] == "tsk":
        return parts[1]
    print("Error: cannot parse channel ID from API key", file=sys.stderr)
    sys.exit(1)


def ws_endpoint():
    """Convert HTTP endpoint to WebSocket endpoint."""
    pass  # ws_endpoint kept for legacy, unused


def ai_write_script(script_id, prompt):
    """Use Teleskopiq AI to write a script via SSE (Server-Sent Events) subscription."""
    channel_id = parse_channel_id()

    subscription_query = """subscription ChatJob(
  $pageId: String!, $message: String!, $currentScript: String,
  $history: [ChatHistoryInput!]!, $activeChannelId: String, $aiMode: String
) {
  chatJob(pageId: $pageId, message: $message, currentScript: $currentScript,
    history: $history, activeChannelId: $activeChannelId, aiMode: $aiMode
  ) { type text thought script error }
}"""

    variables = {
        "pageId": script_id,
        "message": prompt,
        "currentScript": "",
        "history": [],
        "activeChannelId": channel_id,
        "aiMode": "author",
    }

    payload = json.dumps({
        "query": subscription_query,
        "variables": variables,
    })

    accumulated = []
    with requests.post(
        ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {API_KEY}",
        },
        data=payload,
        stream=True,
        timeout=180,
    ) as resp:
        if not resp.ok:
            print(f"Error: HTTP {resp.status_code}", file=sys.stderr)
            sys.exit(1)

        done = False
        for line in resp.iter_lines(decode_unicode=True):
            if done:
                break
            if not line.startswith("data: "):
                continue
            data = line[6:].strip()
            if not data:
                continue
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                continue

            job = (parsed.get("data") or {}).get("chatJob") or {}
            chunk_type = job.get("type", "")
            if chunk_type in ("text_chunk", "script_chunk", "script") and job.get("text"):
                accumulated.append(job["text"])
                print(".", end="", flush=True)
            elif chunk_type == "complete":
                done = True
            if job.get("error"):
                print(f"\nAI error: {job['error']}", file=sys.stderr)
                done = True

    content = "".join(accumulated)
    print(f"\nAI writing complete: {len(content)} chars")
    if content:
        print(f"Preview: {content[:200]}...")
    return content


def save_script_content(script_id, content):
    """Save content to a script via updateScript mutation."""
    q = """mutation UpdateScript($input: UpdateScriptInput!) {
      updateScript(input: $input) { success }
    }"""
    gql(q, {"input": {"id": script_id, "content": content}})
    print(f"Script {script_id} content saved.")


def poll_script(script_id, field, attempts=7, interval=5):
    """Poll script query until field is populated."""
    q = """query($id: String!) {
      script(id: $id) {
        title metadata { titles description tags }
        thumbnailIdeas { text visual }
        thumbnails { url }
      }
    }"""
    for i in range(attempts):
        if i > 0:
            print(f"  polling ({i}/{attempts-1})...")
        time.sleep(interval)
        data = gql(q, {"id": script_id})
        val = data.get("script", {}).get(field)
        if val:
            return data["script"]
    return None


def cmd_get_style(_args):
    q = """{
      styleProfile {
        channelName channelDescription targetAudience tone speakers
        signature_phrases structure additionalInstructions
        vocabulary { words phrases }
        pacingTargets { targetMinutes targetWPM }
      }
    }"""
    data = gql(q)
    sp = data.get("styleProfile", {})
    if not sp:
        print("No style profile found.")
        return

    print("=== Channel Style Profile ===")
    print(f"Channel: {sp.get('channelName', 'N/A')}")
    print(f"Description: {sp.get('channelDescription', 'N/A')}")
    print(f"Audience: {sp.get('targetAudience', 'N/A')}")
    print(f"Tone: {sp.get('tone', 'N/A')}")
    print(f"Speakers: {sp.get('speakers', 'N/A')}")

    pacing = sp.get("pacingTargets") or {}
    if pacing:
        mins = pacing.get("targetMinutes", "?")
        wpm = pacing.get("targetWPM", "?")
        print(f"Pacing: {mins} min target, {wpm} WPM")

    vocab = sp.get("vocabulary") or {}
    words = vocab.get("words") or []
    phrases = vocab.get("phrases") or []
    if words:
        print("Vocabulary: " + ", ".join(words))
    if phrases:
        print("Vocabulary phrases: " + ", ".join(phrases))

    sig = sp.get("signature_phrases") or []
    if sig:
        quoted = ['"' + p + '"' for p in sig]
        print("Signature phrases: " + ", ".join(quoted))

    structure = sp.get("structure")
    if structure:
        print(f"Structure: {structure}")

    additional = sp.get("additionalInstructions")
    if additional:
        print(f"Additional instructions: {additional}")


def cmd_list_scripts(_args):
    data = gql("{ scripts { id title status { name } scheduledFor } }")
    scripts = data.get("scripts", [])
    if not scripts:
        print("No scripts found.")
        return
    for s in scripts:
        sched = s.get("scheduledFor") or "unscheduled"
        status = s.get("status", {}).get("name", "?")
        print(f"  {s['id']}  [{status}]  {s['title']}  ({sched})")


def cmd_create_script(args):
    q = """mutation CreateScript($input: CreateScriptInput!) {
      createScript(input: $input) { id title status { name } }
    }"""
    inp = {"title": args.title}
    if args.content:
        inp["content"] = args.content
    data = gql(q, {"input": inp})
    s = data["createScript"]
    print(f"Created: {s['id']}  [{s['status']['name']}]  {s['title']}")
    return s["id"]


def cmd_generate_metadata(args):
    sid = args.script_id
    s = gql("query($id: String!) { script(id: $id) { title content } }", {"id": sid})["script"]
    content = s.get("content") or ""
    if not content:
        print("Warning: script has no content, metadata may be poor", file=sys.stderr)
    print(f"Starting metadata job for {sid}...")
    gql('mutation($sid: String!, $c: String!) { startMetadataJob(scriptId: $sid, scriptContent: $c) { success } }',
        {"sid": sid, "c": content})
    print("Polling for results...")
    result = poll_script(sid, "metadata")
    if result and result.get("metadata"):
        m = result["metadata"]
        print(f"\nTitles: {json.dumps(m.get('titles', []), indent=2)}")
        desc = m.get('description', '')[:200]
        print(f"Description: {desc}")
        print("Tags: " + ", ".join(m.get("tags", [])))
    else:
        print("Timeout \u2014 metadata not ready yet. Try querying the script later.")


def cmd_generate_thumbnails(args):
    sid = args.script_id
    s = gql('query($id: String!) { script(id: $id) { thumbnailIdeas { text visual } } }',
            {"id": sid})["script"]
    ideas = s.get("thumbnailIdeas") or []
    if not ideas:
        print("No thumbnail ideas found. Generate metadata first.")
        return
    for i, idea in enumerate(ideas):
        txt = idea.get("text", "")[:60]
        print(f"Starting thumbnail job {i}: {txt}...")
        gql('mutation($sid: String!, $idea: String!, $idx: Int!) { startThumbnailJob(scriptId: $sid, idea: $idea, ideaIndex: $idx) { success } }',
            {"sid": sid, "idea": idea.get("text", ""), "idx": i})
    print(f"Started {len(ideas)} thumbnail jobs. Polling...")
    result = poll_script(sid, "thumbnails", attempts=10, interval=5)
    if result and result.get("thumbnails"):
        for t in result["thumbnails"]:
            print(f"  {t['url']}")
    else:
        print("Timeout \u2014 thumbnails not ready yet. Query the script later.")


def cmd_auto_schedule(args):
    sid = args.script_id
    urgent = getattr(args, "urgent", False)
    q = """mutation AutoScheduleScript($scriptId: String!, $urgent: Boolean) {
      autoScheduleScript(scriptId: $scriptId, urgent: $urgent) {
        scriptId scheduledFor slotsChecked bumped
      }
    }"""
    variables = {"scriptId": sid}
    if urgent:
        variables["urgent"] = True
    data = gql(q, variables)
    result = data["autoScheduleScript"]
    bumped_msg = f", bumped {result['bumped']} script(s)" if result.get("bumped") else ""
    print(f"Auto-scheduled {result['scriptId']} for {result['scheduledFor']} (checked {result['slotsChecked']} slots{bumped_msg})")
    return result


def cmd_schedule(args):
    sid = args.script_id
    dt = args.date
    tm = args.time or "12:00"
    iso = f"{dt}T{tm}:00Z"
    status = args.status or "ReadyToShoot"
    q = f'mutation {{ updateScript(input: {{ id: "{sid}", scheduledFor: "{iso}", status: {status} }}) {{ success }} }}'
    gql(q)
    print(f"Scheduled {sid} for {iso} [{status}]")


def cmd_ai_write(args):
    prompt = args.prompt or DEFAULT_AI_PROMPT

    print("=== Creating script ===")
    q = """mutation CreateScript($input: CreateScriptInput!) {
      createScript(input: $input) { id title status { name } }
    }"""
    data = gql(q, {"input": {"title": args.title}})
    sid = data["createScript"]["id"]
    print(f"Created: {sid}")

    print("\n=== AI writing script ===")
    content = ai_write_script(sid, prompt)

    if content:
        save_script_content(sid, content)

    print(f"\nScript ID: {sid}")


def next_sunday():
    today = datetime.utcnow()
    days = (6 - today.weekday()) % 7
    if days == 0:
        days = 7
    return (today + timedelta(days=days)).strftime("%Y-%m-%d")


def cmd_full_flow(args):
    use_ai = getattr(args, "ai_write", False)
    prompt = getattr(args, "prompt", None) or DEFAULT_AI_PROMPT

    print("=== Creating script ===")
    q = """mutation CreateScript($input: CreateScriptInput!) {
      createScript(input: $input) { id title status { name } }
    }"""
    inp = {"title": args.title}
    if not use_ai:
        inp["content"] = args.content
    data = gql(q, {"input": inp})
    sid = data["createScript"]["id"]
    print(f"Created: {sid}")

    if use_ai:
        print("\n=== AI writing script ===")
        content = ai_write_script(sid, prompt)
        if content:
            save_script_content(sid, content)
    else:
        content = args.content

    print("\n=== Generating metadata ===")
    gql('mutation($sid: String!, $c: String!) { startMetadataJob(scriptId: $sid, scriptContent: $c) { success } }',
        {"sid": sid, "c": content or ""})
    result = poll_script(sid, "metadata")
    if result and result.get("metadata"):
        n = len(result["metadata"].get("titles", []))
        print(f"Metadata ready: {n} titles")
    else:
        print("Metadata timeout \u2014 continuing anyway")

    print("\n=== Generating thumbnails ===")
    s = gql('query($id: String!) { script(id: $id) { thumbnailIdeas { text visual } } }', {"id": sid})["script"]
    ideas = s.get("thumbnailIdeas") or []
    for i, idea in enumerate(ideas):
        gql('mutation($sid: String!, $idea: String!, $idx: Int!) { startThumbnailJob(scriptId: $sid, idea: $idea, ideaIndex: $idx) { success } }',
            {"sid": sid, "idea": idea.get("text", ""), "idx": i})
    if ideas:
        print(f"Started {len(ideas)} thumbnail jobs")
        poll_script(sid, "thumbnails", attempts=10, interval=5)

    if args.date:
        dt = args.date
        tm = args.time or "12:00"
        iso = f"{dt}T{tm}:00Z"
        print(f"\n=== Scheduling for {iso} ===")
        gql(f'mutation {{ updateScript(input: {{ id: "{sid}", scheduledFor: "{iso}", status: ReadyToShoot }}) {{ success }} }}')
        print(f"Done! Script {sid} scheduled for {iso}")
    else:
        print("\n=== Auto-scheduling ===")
        urgent = getattr(args, "urgent", False)
        auto_q = """mutation AutoScheduleScript($scriptId: String!, $urgent: Boolean) {
          autoScheduleScript(scriptId: $scriptId, urgent: $urgent) { scriptId scheduledFor slotsChecked bumped }
        }"""
        variables = {"scriptId": sid}
        if urgent:
            variables["urgent"] = True
        result = gql(auto_q, variables)["autoScheduleScript"]
        bumped_msg = f", bumped {result['bumped']} script(s)" if result.get("bumped") else ""
        print(f"Done! Script {sid} auto-scheduled for {result['scheduledFor']} (checked {result['slotsChecked']} slots{bumped_msg})")


def main():
    parser = argparse.ArgumentParser(description="Teleskopiq API CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("get-style")
    sub.add_parser("list-scripts")

    p = sub.add_parser("create-script")
    p.add_argument("--title", required=True)
    p.add_argument("--content", default="")

    p = sub.add_parser("generate-metadata")
    p.add_argument("--script-id", required=True)

    p = sub.add_parser("generate-thumbnails")
    p.add_argument("--script-id", required=True)

    p = sub.add_parser("auto-schedule")
    p.add_argument("--script-id", required=True)
    p.add_argument("--urgent", action="store_true", help="Take next slot and bump displaced scripts forward")

    p = sub.add_parser("schedule")
    p.add_argument("--script-id", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--time", default="12:00")
    p.add_argument("--status", default="ReadyToShoot")

    p = sub.add_parser("ai-write")
    p.add_argument("--title", required=True)
    p.add_argument("--prompt", default=None, help="Custom writing prompt for AI")

    p = sub.add_parser("full-flow")
    p.add_argument("--title", required=True)
    p.add_argument("--content", default=None)
    p.add_argument("--ai-write", action="store_true", help="Use Teleskopiq AI to write the script")
    p.add_argument("--prompt", default=None, help="Custom writing prompt for AI (requires --ai-write)")
    p.add_argument("--date", default=None)
    p.add_argument("--time", default="12:00")
    p.add_argument("--urgent", action="store_true", help="Use urgent scheduling")

    args = parser.parse_args()
    cmds = {
        "get-style": cmd_get_style,
        "list-scripts": cmd_list_scripts,
        "create-script": cmd_create_script,
        "generate-metadata": cmd_generate_metadata,
        "generate-thumbnails": cmd_generate_thumbnails,
        "auto-schedule": cmd_auto_schedule,
        "schedule": cmd_schedule,
        "ai-write": cmd_ai_write,
        "full-flow": cmd_full_flow,
    }
    if args.command not in cmds:
        parser.print_help()
        sys.exit(1)

    if args.command == "full-flow" and not getattr(args, "ai_write", False) and not args.content:
        print("Error: full-flow requires either --content or --ai-write", file=sys.stderr)
        sys.exit(1)

    cmds[args.command](args)


if __name__ == "__main__":
    main()
