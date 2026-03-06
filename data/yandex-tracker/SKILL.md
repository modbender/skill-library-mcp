---
name: yandex-tracker
description: Work with Yandex Tracker (issues, queues, comments, attachments, links, search, bulk operations) via Python yandex_tracker_client. Use when the user asks to manage Tracker tasks, create/update/close issues, search, add comments, log time, manage links, or bulk-update issues.
metadata:
  openclaw:
    emoji: "📋"
    requires:
      bins: ["python3"]
      env: ["TRACKER_TOKEN"]
      envOneOf: ["TRACKER_ORG_ID", "TRACKER_CLOUD_ORG_ID"]
    install:
      - id: pip-yandex-tracker-client
        kind: pip
        package: yandex_tracker_client
        label: Install yandex_tracker_client (pip)
        provenance: https://pypi.org/project/yandex-tracker-client/
---

# Yandex Tracker (Python Client)

Use `yandex_tracker_client` to interact with Yandex Tracker API v2.

## How to work with this skill

**Write and execute Python scripts** to fulfill user requests. The workflow:

1. Write a self-contained Python script that initializes the client, performs all needed API calls, aggregates and formats the result, then prints it.
2. Save to `/tmp/tracker_script.py` and run: `python3 /tmp/tracker_script.py`
3. For simple one-liners it's fine to use `python3 -c "..."`, but prefer a file for anything multi-step.

**Aggregation:** The API returns lazy iterables — always collect into lists when you need to count, sort, filter, or display summaries. Combine multiple queries in one script (e.g. fetch issues then fetch comments for each, or join data from two queues) rather than making separate tool calls. Print structured output so the result is easy to read.

```python
# Example: aggregate issues by assignee across a queue
issues = list(client.issues.find(filter={'queue': 'QUEUE'}, per_page=100))
from collections import Counter
counts = Counter(str(i.assignee) for i in issues)
for assignee, n in counts.most_common():
    print(f'{n:3d}  {assignee}')
```

## Credentials

**Required env** (declare in skill metadata; set in `openclaw.json` → `env`):
- `TRACKER_TOKEN` — **Required.** Use a least-privilege OAuth token (oauth.yandex.ru) with only Tracker scope, or a temporary IAM token for Yandex Cloud. Do not use broad admin tokens.
- One of: `TRACKER_ORG_ID` (Yandex 360, numeric) or `TRACKER_CLOUD_ORG_ID` (Yandex Cloud, string)

## Client initialization (boilerplate — always include)

```python
import os
from yandex_tracker_client import TrackerClient

token = os.environ['TRACKER_TOKEN']
org_id = os.environ.get('TRACKER_ORG_ID')
cloud_org_id = os.environ.get('TRACKER_CLOUD_ORG_ID')

if cloud_org_id:
    client = TrackerClient(token=token, cloud_org_id=cloud_org_id)
else:
    client = TrackerClient(token=token, org_id=int(org_id))
```

## Get issue by key

```python
issue = client.issues['QUEUE-42']
print(issue.key, issue.summary, issue.status.id, issue.assignee.login if issue.assignee else None)
```

## Custom fields

Real queues almost always have custom fields (story points, business fields, etc.). Their keys look like `customFieldId` (camelCase) and are queue-specific.

```python
# Read — access by attribute name (same as standard fields)
print(issue.storyPoints)       # returns None if absent
print(issue.as_dict())         # dump all fields including custom ones — use to discover keys

# Update
issue.update(storyPoints=5, myCustomField='value')

# Filter by custom field in find()
issues = client.issues.find(filter={'queue': 'QUEUE', 'storyPoints': {'from': 3}})

# Discover all fields available in a queue (id is the key to use)
for f in client.fields.get_all():
    print(f.id, f.name)
```

Use `issue.as_dict()` on a real issue to discover which custom field keys the queue uses before writing update/filter code.

## issues.find() — search

```python
# Tracker Query Language string (copy from Tracker UI)
issues = client.issues.find('Queue: QUEUE Assignee: me() Status: inProgress')

# Structured filter (dict)
issues = client.issues.find(
    filter={
        'queue': 'QUEUE',               # queue key
        'assignee': 'user_login',       # login or 'me()'
        'author': 'user_login',
        'status': 'inProgress',         # status .id
        'type': 'bug',                  # issue type .id
        'priority': 'critical',         # priority .id
        'tags': ['backend', 'urgent'],  # all tags must match
        'created': {'from': '2026-01-01', 'to': '2026-02-01'},
        'updated': {'from': '2026-01-15'},
        'deadline': {'to': '2026-03-01'},
        'followers': 'user_login',
        'components': 'component_name',
    },
    order=['-updatedAt', '+priority'],  # prefix: - desc, + asc
    per_page=100,                       # max 100 per page; pagination is automatic
)
# Iterating auto-fetches all pages; wrap in list() to materialise
issues = list(issues)

# Batch fetch specific issues by key
issues = list(client.issues.find(keys=['QUEUE-1', 'QUEUE-2', 'QUEUE-3']))
```

## issues.create()

```python
issue = client.issues.create(
    queue='QUEUE',              # required
    summary='Bug: login fails', # required
    type={'name': 'Bug'},       # or {'id': 'bug'} — use client.issue_types.get_all()
    description='Steps...',
    assignee='user_login',
    priority='critical',        # id: 'blocker','critical','major','normal','minor','trivial'
    followers=['login1', 'login2'],
    tags=['backend', 'urgent'],
    components=['component_name'],
    parent='QUEUE-10',          # parent issue key
    sprint={'id': 123},         # sprint id
)
print(issue.key)
```

## issue.update()

```python
issue.update(
    summary='New title',
    description='Updated text',
    assignee='other_login',
    priority='minor',
    # Lists: pass full replacement OR mutation dict
    tags=['new_tag'],                         # replace entirely
    tags={'add': ['tag1'], 'remove': ['tag2']},  # partial mutation
    followers={'add': ['login1']},
    components={'add': ['comp'], 'remove': []},
)
```

## issue.transitions — status changes

```python
# Always list first — transition IDs are queue-specific, never guess
for t in issue.transitions.get_all():
    print(t.id, t.to.id, t.to.display)

# Execute — all kwargs optional
issue.transitions['close'].execute(
    comment='Fixed in v2.3',
    resolution='fixed',  # 'fixed','wontFix','duplicate','invalid','later' — queue-dependent
)
```

## issue.comments

```python
for c in list(issue.comments.get_all()):
    print(c.id, c.createdBy.login, c.text)

# Create
issue.comments.create(
    text='Fixed in v2.3',
    summonees=['login1', 'login2'],   # triggers @mention notification
    attachments=['path/to/file.png'], # file paths — auto-uploaded, converted to IDs
)

issue.comments[42].update(text='Corrected note', summonees=['login1'])
issue.comments[42].delete()
```

## issue.links

```python
for link in issue.links:
    print(link.type.id, link.direction, link.object.key)

# relationship values (standard):
# 'relates', 'blocks', 'is blocked by',
# 'duplicates', 'is duplicated by',
# 'depends on', 'is dependent of',
# 'is subtask for', 'is parent task for'
issue.links.create(issue='OTHER-10', relationship='relates')
issue.links[42].delete()
```

## issue.attachments

```python
for a in issue.attachments:
    print(a.id, a.name, a.mimetype, a.size)

issue.attachments.create('/path/to/file.txt')   # upload by path
a.download_to('/tmp/')                           # download to dir
issue.attachments[42].delete()
```

## issue.worklog

```python
# Create worklog entry
issue.worklog.create(
    duration='PT1H30M',              # ISO 8601: PT30M, PT2H, P1D, P1DT2H30M
    comment='Fixed auth bug',        # optional
    start='2026-02-24T10:00:00+03:00',  # optional, defaults to now
)

for w in list(issue.worklog.get_all()):
    print(w.id, w.duration, w.comment, w.createdBy.login)

issue.worklog[42].update(duration='PT2H', comment='Revised estimate')
issue.worklog[42].delete()

# Fetch worklogs across multiple issues at once
entries = client.worklog.find(issue=['QUEUE-1', 'QUEUE-2'], createdBy='me()')
```

## Queues

```python
queue = client.queues['QUEUE']
print(queue.key, queue.name, queue.lead.login)

for q in client.queues.get_all():
    print(q.key, q.name)
```

## Bulk operations

```python
# issues arg: list of keys OR list of issue objects from find()

# Bulk update — any issue field as kwarg
bc = client.bulkchange.update(
    ['QUEUE-1', 'QUEUE-2', 'QUEUE-3'],
    priority='minor',
    assignee='user_login',
    tags={'add': ['reviewed'], 'remove': ['draft']},
)
bc.wait()
print(bc.status)  # 'COMPLETE' or 'FAILED'

# Bulk transition — transition id + optional field values
bc = client.bulkchange.transition(
    ['QUEUE-1', 'QUEUE-2'],
    'close',                # transition id
    resolution='wontFix',   # optional extra fields
)
bc.wait()

# Bulk move to another queue
bc = client.bulkchange.move(
    ['QUEUE-1', 'QUEUE-2'],
    'NEWQUEUE',
    move_all_fields=False,        # copy all field values
    move_to_initial_status=False, # reset to initial status
)
bc.wait()
```

## Object fields reference

All objects are **dynamic** — accessing a missing attribute returns `None`, not `AttributeError`.  
Call `.as_dict()` on any object to get a plain `dict`.

**Reference fields** (status, priority, assignee, queue, type…) are `Reference` objects — access `.id`, `.display`, `.key`, or `.login` directly without a second request.

### Issue

| Attribute | Notes |
|---|---|
| `key` | `str` — `'QUEUE-42'` |
| `summary` | `str` |
| `description` | `str \| None` |
| `status` | Reference → `.id` e.g. `'inProgress'`, `.display` localized name |
| `priority` | Reference → `.id` e.g. `'normal'` / `'critical'` |
| `type` | Reference → `.id` e.g. `'bug'` / `'task'` |
| `queue` | Reference → `.key` e.g. `'QUEUE'` |
| `assignee` | Reference \| None → `.login`, `.display` |
| `reporter` | Reference → `.login`, `.display` |
| `createdBy` | Reference → `.login` |
| `createdAt` | `str` ISO-8601 |
| `updatedAt` | `str` ISO-8601 |
| `deadline` | `str \| None` — date `'2026-03-01'` |
| `tags` | `list[str]` |
| `followers` | `list[Reference]` → each `.login` |
| `components` | `list[Reference]` → each `.display` |
| `fixVersions` | `list[Reference]` → each `.display` |
| `sprint` | `list[Reference] \| None` → each `.display` |
| `parent` | Reference \| None → `.key` |
| `votes` | `int` |

### Comment

| Attribute | Notes |
|---|---|
| `id` | `int` |
| `text` | `str` |
| `textHtml` | `str` |
| `createdBy` | Reference → `.login`, `.display` |
| `createdAt` / `updatedAt` | `str` ISO-8601 |
| `summonees` | `list[Reference]` |
| `attachments` | `list[Reference]` |

### Link

| Attribute | Notes |
|---|---|
| `id` | `int` |
| `type` | Reference → `.id` e.g. `'relates'`, `'blocks'`, `'is blocked by'` |
| `direction` | `str` — `'inward'` / `'outward'` |
| `object` | Reference → `.key`, `.display` (the linked issue) |
| `createdBy` | Reference → `.login` |
| `createdAt` | `str` ISO-8601 |

### Attachment

| Attribute | Notes |
|---|---|
| `id` | `int` |
| `name` | `str` — filename |
| `content` | `str` — download URL |
| `mimetype` | `str` |
| `size` | `int` — bytes |
| `createdBy` | Reference → `.login` |
| `createdAt` | `str` ISO-8601 |

### Transition

| Attribute | Notes |
|---|---|
| `id` | `str` — transition key, e.g. `'close'`, `'start_progress'` |
| `to` | Reference → `.id`, `.display` (target status) |
| `screen` | Reference \| None |

### Worklog entry

| Attribute | Notes |
|---|---|
| `id` | `int` |
| `issue` | Reference → `.key` |
| `comment` | `str \| None` |
| `start` | `str` ISO-8601 datetime |
| `duration` | `str` ISO-8601 duration e.g. `'PT1H30M'` |
| `createdBy` | Reference → `.login` |
| `createdAt` | `str` ISO-8601 |

### Queue

| Attribute | Notes |
|---|---|
| `id` | `int` |
| `key` | `str` |
| `name` | `str` |
| `description` | `str \| None` |
| `lead` | Reference → `.login`, `.display` |
| `assignAuto` | `bool` |
| `defaultType` | Reference |
| `defaultPriority` | Reference |
| `teamUsers` | `list[Reference]` → each `.login` |

### User

| Attribute | Notes |
|---|---|
| `uid` | `int` |
| `login` | `str` |
| `firstName` / `lastName` | `str` |
| `display` | `str` — full name |
| `email` | `str` |

### BulkChange

| Attribute | Notes |
|---|---|
| `id` | `str` |
| `status` | `str` — `'COMPLETE'` / `'FAILED'` / `'PROCESSING'` |
| `statusText` | `str` |
| `executionChunkPercent` | `int` |
| `executionIssuePercent` | `int` |

---

## Users

```python
# Find user by login, email, or display name — use when user says "assign to Иванов"
for u in client.users.get_all():
    print(u.login, u.display, u.email)

# Get current user
me = client.myself
print(me.login)
```

## Sprints

```python
# Boards list
for b in client.boards.get_all():
    print(b.id, b.name)

# Sprints for a board
for s in client.boards[123].sprints.get_all():
    print(s.id, s.name, s.status)  # status: 'active','closed','draft'

# Assign issue to sprint by id (found above)
issue.update(sprint={'id': 456})
```

## Error handling

```python
from yandex_tracker_client import exceptions

try:
    issue = client.issues['QUEUE-99999']
except exceptions.NotFound:
    print('Issue not found')
except exceptions.Forbidden:
    print('No access to this queue or issue')
except exceptions.BadRequest as e:
    print('Invalid field or value:', e)
except exceptions.Conflict:
    # Concurrent modification — re-fetch and retry
    issue = client.issues['QUEUE-42']
    issue.update(...)
```

Available exception classes: `NotFound`, `Forbidden`, `BadRequest`, `Conflict`, `TrackerClientError` (base).

## Notes

- `org_id` must be an `int`; `cloud_org_id` is a string.
- For Yandex Cloud orgs: use `cloud_org_id=` instead of `org_id=`, and optionally `iam_token=` for temporary IAM tokens instead of `token=`.
- To get valid resolution IDs for a queue: `[r.id for r in client.resolutions.get_all()]`.
- Print results clearly — use formatted strings, tables, or JSON so the user gets a readable summary.
