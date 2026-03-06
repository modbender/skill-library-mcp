#!/usr/bin/env python3
"""
Linear query script - calls api.linear.app/graphql directly.
No third-party proxy or SDK dependency.
"""
import argparse
import json
import os
import sys
import urllib.request

ENDPOINT = "https://api.linear.app/graphql"

PRIORITY_LABELS = {0: "None", 1: "Urgent", 2: "High", 3: "Normal", 4: "Low"}


def get_api_key():
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        print("Error: LINEAR_API_KEY env var not set", file=sys.stderr)
        print("Create at Linear → Settings → Account → Security & Access → API keys", file=sys.stderr)
        sys.exit(1)
    return key


def gql(query, variables=None):
    key = get_api_key()
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Authorization": key,
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            if "errors" in result:
                for err in result["errors"]:
                    print(f"GraphQL error: {err.get('message')}", file=sys.stderr)
                sys.exit(1)
            return result.get("data", {})
    except urllib.error.HTTPError as e:
        print(f"Linear API error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def print_table(items, fields, headers=None):
    if not items:
        print("No results.")
        return
    headers = headers or fields
    rows = [[str(item.get(f, "") or "")[:60] for f in fields] for item in items]
    widths = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header_row = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    print(sep)
    print(header_row)
    print(sep)
    for row in rows:
        print("| " + " | ".join(v.ljust(widths[i]) for i, v in enumerate(row)) + " |")
    print(sep)
    print(f"\n{len(items)} results")


def get_team_id(team_name):
    data = gql("{ teams { nodes { id name } } }")
    teams = data["teams"]["nodes"]
    match = next((t for t in teams if t["name"].lower() == team_name.lower()), None)
    if not match:
        names = [t["name"] for t in teams]
        print(f"Error: team '{team_name}' not found. Available: {', '.join(names)}", file=sys.stderr)
        sys.exit(1)
    return match["id"]


def get_state_id(team_id, state_name):
    data = gql("""
        query($teamId: String!) {
            team(id: $teamId) { states { nodes { id name } } }
        }
    """, {"teamId": team_id})
    states = data["team"]["states"]["nodes"]
    match = next((s for s in states if s["name"].lower() == state_name.lower()), None)
    if not match:
        names = [s["name"] for s in states]
        print(f"Error: state '{state_name}' not found. Available: {', '.join(names)}", file=sys.stderr)
        sys.exit(1)
    return match["id"]


def cmd_teams(args):
    data = gql("{ teams { nodes { id name key description } } }")
    teams = data["teams"]["nodes"]
    print_table(teams, ["key", "name", "description"])


def cmd_my_issues(args):
    query = """
        query($filter: IssueFilter, $first: Int) {
            viewer {
                assignedIssues(filter: $filter, first: $first) {
                    nodes { identifier title state { name } priority updatedAt }
                }
            }
        }
    """
    variables = {"first": args.limit}
    if args.state:
        variables["filter"] = {"state": {"name": {"eq": args.state}}}

    data = gql(query, variables)
    issues = data["viewer"]["assignedIssues"]["nodes"]
    rows = [{
        "id": i["identifier"],
        "title": i["title"],
        "state": i["state"]["name"],
        "priority": PRIORITY_LABELS.get(i["priority"], str(i["priority"])),
        "updated": i["updatedAt"][:10],
    } for i in issues]
    print_table(rows, ["id", "title", "state", "priority", "updated"])


def cmd_issues(args):
    team_id = get_team_id(args.team)
    query = """
        query($teamId: String!, $filter: IssueFilter, $first: Int) {
            team(id: $teamId) {
                issues(filter: $filter, first: $first, orderBy: updatedAt) {
                    nodes { identifier title state { name } assignee { name } priority updatedAt }
                }
            }
        }
    """
    variables = {"teamId": team_id, "first": args.limit}
    if args.state:
        variables["filter"] = {"state": {"name": {"eq": args.state}}}

    data = gql(query, variables)
    issues = data["team"]["issues"]["nodes"]
    rows = [{
        "id": i["identifier"],
        "title": i["title"],
        "state": i["state"]["name"],
        "assignee": (i["assignee"] or {}).get("name", ""),
        "priority": PRIORITY_LABELS.get(i["priority"], str(i["priority"])),
        "updated": i["updatedAt"][:10],
    } for i in issues]
    print_table(rows, ["id", "title", "state", "assignee", "priority", "updated"])


def cmd_issue(args):
    query = """
        query($id: String!) {
            issue(id: $id) {
                identifier title description state { name }
                assignee { name } priority createdAt updatedAt url
            }
        }
    """
    data = gql(query, {"id": args.id})
    issue = data.get("issue")
    if not issue:
        print(f"Issue {args.id} not found", file=sys.stderr)
        sys.exit(1)
    print(f"{issue['identifier']}: {issue['title']}")
    print(f"State: {issue['state']['name']} | Priority: {PRIORITY_LABELS.get(issue['priority'], '?')}")
    print(f"Assignee: {(issue['assignee'] or {}).get('name', 'Unassigned')}")
    print(f"URL: {issue['url']}")
    if issue.get("description"):
        print(f"\n{issue['description']}")


def cmd_search(args):
    query = """
        query($query: String!, $first: Int) {
            issueSearch(query: $query, first: $first) {
                nodes { identifier title state { name } team { name } updatedAt }
            }
        }
    """
    data = gql(query, {"query": args.query, "first": args.limit})
    issues = data["issueSearch"]["nodes"]
    rows = [{
        "id": i["identifier"],
        "title": i["title"],
        "state": i["state"]["name"],
        "team": i["team"]["name"],
        "updated": i["updatedAt"][:10],
    } for i in issues]
    print_table(rows, ["id", "title", "state", "team", "updated"])


def cmd_create(args):
    team_id = get_team_id(args.team)
    variables = {
        "input": {
            "teamId": team_id,
            "title": args.title,
        }
    }
    if args.description:
        variables["input"]["description"] = args.description
    if args.priority is not None:
        variables["input"]["priority"] = args.priority
    if args.state:
        state_id = get_state_id(team_id, args.state)
        variables["input"]["stateId"] = state_id

    mutation = """
        mutation($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue { identifier title url }
            }
        }
    """
    data = gql(mutation, variables)
    issue = data["issueCreate"]["issue"]
    print(f"Created {issue['identifier']}: {issue['title']}")
    print(f"URL: {issue['url']}")


def cmd_update(args):
    # Resolve identifier to ID
    query = """
        query($id: String!) { issue(id: $id) { id identifier } }
    """
    data = gql(query, {"id": args.id})
    issue = data.get("issue")
    if not issue:
        print(f"Issue {args.id} not found", file=sys.stderr)
        sys.exit(1)

    update = {}
    if args.title:
        update["title"] = args.title
    if args.description:
        update["description"] = args.description
    if args.priority is not None:
        update["priority"] = args.priority
    if args.state:
        # Get team for this issue to look up state
        team_query = """
            query($id: String!) { issue(id: $id) { team { id } } }
        """
        team_data = gql(team_query, {"id": args.id})
        team_id = team_data["issue"]["team"]["id"]
        update["stateId"] = get_state_id(team_id, args.state)

    if not update:
        print("Error: no fields to update", file=sys.stderr)
        sys.exit(1)

    mutation = """
        mutation($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue { identifier title state { name } }
            }
        }
    """
    data = gql(mutation, {"id": issue["id"], "input": update})
    updated = data["issueUpdate"]["issue"]
    print(f"Updated {updated['identifier']}: {updated['title']} [{updated['state']['name']}]")


def cmd_projects(args):
    if args.team:
        team_id = get_team_id(args.team)
        query = """
            query($teamId: String!) {
                team(id: $teamId) {
                    projects { nodes { id name state description updatedAt } }
                }
            }
        """
        data = gql(query, {"teamId": team_id})
        projects = data["team"]["projects"]["nodes"]
    else:
        query = "{ projects { nodes { id name state description updatedAt } } }"
        data = gql(query)
        projects = data["projects"]["nodes"]

    rows = [{
        "name": p["name"],
        "state": p.get("state", ""),
        "description": (p.get("description") or "")[:40],
        "updated": p["updatedAt"][:10],
    } for p in projects]
    print_table(rows, ["name", "state", "description", "updated"])


def cmd_cycles(args):
    team_id = get_team_id(args.team)
    query = """
        query($teamId: String!) {
            team(id: $teamId) {
                cycles { nodes { number name startsAt endsAt completedAt issueCountHistory } }
            }
        }
    """
    data = gql(query, {"teamId": team_id})
    cycles = data["team"]["cycles"]["nodes"]
    rows = [{
        "number": str(c["number"]),
        "name": c.get("name") or f"Cycle {c['number']}",
        "starts": c["startsAt"][:10],
        "ends": c["endsAt"][:10],
        "completed": c["completedAt"][:10] if c.get("completedAt") else "",
    } for c in cycles]
    print_table(rows, ["number", "name", "starts", "ends", "completed"])


def cmd_states(args):
    team_id = get_team_id(args.team)
    query = """
        query($teamId: String!) {
            team(id: $teamId) { states { nodes { name type position } } }
        }
    """
    data = gql(query, {"teamId": team_id})
    states = sorted(data["team"]["states"]["nodes"], key=lambda s: s["position"])
    rows = [{"name": s["name"], "type": s["type"]} for s in states]
    print_table(rows, ["name", "type"])


def main():
    parser = argparse.ArgumentParser(description="Query Linear via GraphQL API")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("teams")

    p = sub.add_parser("my-issues")
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=25)

    p = sub.add_parser("issues")
    p.add_argument("--team", required=True)
    p.add_argument("--state")
    p.add_argument("--limit", type=int, default=25)

    p = sub.add_parser("issue")
    p.add_argument("id", help="Issue identifier e.g. ENG-123")

    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("create")
    p.add_argument("--team", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description")
    p.add_argument("--priority", type=int, choices=[0, 1, 2, 3, 4])
    p.add_argument("--state")

    p = sub.add_parser("update")
    p.add_argument("id", help="Issue identifier e.g. ENG-123")
    p.add_argument("--title")
    p.add_argument("--description")
    p.add_argument("--state")
    p.add_argument("--priority", type=int, choices=[0, 1, 2, 3, 4])

    p = sub.add_parser("projects")
    p.add_argument("--team")

    p = sub.add_parser("cycles")
    p.add_argument("--team", required=True)

    p = sub.add_parser("states")
    p.add_argument("--team", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "teams": cmd_teams,
        "my-issues": cmd_my_issues,
        "issues": cmd_issues,
        "issue": cmd_issue,
        "search": cmd_search,
        "create": cmd_create,
        "update": cmd_update,
        "projects": cmd_projects,
        "cycles": cmd_cycles,
        "states": cmd_states,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
