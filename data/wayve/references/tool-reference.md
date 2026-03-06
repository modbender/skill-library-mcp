# Wayve Tool Reference

Complete reference for all 20 Wayve MCP tools. Consult this when you need exact parameter names, types, or action options.

## Table of Contents
- [Planning & Context](#planning--context)
- [Activities](#activities)
- [Buckets](#buckets)
- [Projects](#projects)
- [Time Locks](#time-locks)
- [Week Reviews](#week-reviews)
- [Analytics](#analytics)
- [Knowledge Base](#knowledge-base)
- [Time Audits](#time-audits)
- [Checklist Items](#checklist-items)
- [Recurrence](#recurrence)
- [Focus Templates](#focus-templates)
- [User Settings](#user-settings)
- [Happiness Insights](#happiness-insights)
- [Bucket Frequencies](#bucket-frequencies)
- [Smart Suggestions](#smart-suggestions)

---

## Planning & Context

### `wayve_get_planning_context`
Get everything needed to plan a user's week in one call. **Call this first** when helping plan.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `week` | int 1-53 | No | Week number (default: current) |
| `year` | int | No | Year (default: current) |
| `response_format` | "json" / "markdown" | No | Output format |

Returns: buckets, activities (scheduled/unscheduled/incomplete), time_locks, user_preferences, last_week_review, frequency_progress, perfect_week template, knowledge_summary.

### `wayve_get_availability`
Find free time slots for scheduling.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `week` | int 1-53 | No | Week number (default: current) |
| `year` | int | No | Year (default: current) |
| `slot_duration_minutes` | int 15-240 | No | Minimum slot size (default: 30) |
| `response_format` | "json" / "markdown" | No | Output format |

Returns: total_available_hours, total_scheduled_hours, by_day (with slots array showing start/end/duration).

### `wayve_daily_brief`
Concise daily overview with today's schedule and priorities.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | YYYY-MM-DD | No | Date (default: today) |
| `response_format` | "json" / "markdown" | No | Output format |

Returns: scheduled activities (sorted by time), completed_count, top 5 unscheduled, today's time_locks.

---

## Activities

### `wayve_create_activity`
Create one or multiple activities.

**Single mode** — provide `title` + `bucket_id`:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string (max 500) | Yes | Activity title |
| `bucket_id` | UUID | Yes | Bucket to assign to |
| `description` | string (max 5000) | No | Details |
| `scheduled_date` | YYYY-MM-DD | No | When |
| `scheduled_time` | HH:MM | No | What time |
| `duration_minutes` | int 1-480 | No | How long |
| `project_id` | UUID | No | Link to project |
| `priority` | int 1-5 | No | 1=lowest, 5=highest |
| `energy_required` | high/medium/low | No | Energy cost |
| `time_flexibility` | fixed/flexible | No | Can it move? |
| `location_context` | home/office/gym/outdoors/anywhere | No | Where |

**Batch mode** — provide `activities` array (max 100 items) with same fields per item.

### `wayve_update_activity`
Update an existing activity.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Yes | Activity ID |
| `title` | string (max 500) | No | New title |
| `completed` | boolean | No | Mark done |
| `scheduled_date` | YYYY-MM-DD / null | No | Reschedule or unschedule |
| `scheduled_time` | HH:MM / null | No | Change time |
| `bucket_id` | UUID | No | Move to different bucket |
| `duration_minutes` | int 1-480 / null | No | Change duration |
| `priority` | int 1-5 / null | No | Change priority |
| `energy_required` | high/medium/low / null | No | Change energy |
| `project_id` | UUID / null | No | Link/unlink project |

### `wayve_delete_activity`
| Param | Type | Required |
|-------|------|----------|
| `id` | UUID | Yes |

### `wayve_search_activities`
Search activities by text, bucket, date range, or completion status.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string (max 200) | No | Text search in titles |
| `bucket_id` | UUID | No | Filter by bucket |
| `date_from` | YYYY-MM-DD | No | Start of range |
| `date_to` | YYYY-MM-DD | No | End of range |
| `completed` | boolean | No | Filter by status |
| `limit` | int 1-100 | No | Results (default: 20) |

---

## Buckets

### `wayve_manage_bucket`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | create / update / reorder | Yes | What to do |
| `id` | UUID | For update | Bucket ID |
| `name` | string (max 100) | For create | Bucket name |
| `color` | hex string | For create | e.g., "#10B981" |
| `intention` | string (max 500) | No | Why this area matters |
| `target_hours_per_week` | number 0-168 | No | Weekly target |
| `preferred_time_slot` | morning/afternoon/evening/flexible | No | When |
| `is_focus` | boolean | For update | Set as focus bucket |
| `archived` | boolean | No | true=archive, false=restore |
| `bucket_ids` | UUID[] | For reorder | New order |

---

## Projects

### `wayve_manage_project`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | create / update | Yes | What to do |
| `id` | UUID | For update | Project ID |
| `name` | string 1-200 | For create | Project name |
| `color` | hex string | For create | Color |
| `bucket_id` | UUID | No | Link to bucket |
| `description` | string (max 1000) | No | Details |
| `goal_type` | target / habit | No | Type (default: "target") |
| `target_value` | positive number | No | e.g., 100 pages |
| `target_unit` | string (max 50) | No | e.g., "hours", "pages" |
| `current_value` | number >= 0 | For update | Progress |
| `status` | active/completed/archived | For update | "archived" = soft delete |

---

## Time Locks

### `wayve_manage_timelock`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | create / update / delete | Yes | What to do |
| `id` | UUID | For update/delete | Time lock ID |
| `name` | string 1-200 | For create | Name |
| `start_time` | HH:MM | For create | Start |
| `end_time` | HH:MM | For create | End |
| `bucket_id` | UUID / null | No | Link to bucket |
| `color` | hex string | No | Color |
| `recurrence_type` | daily/weekly/biweekly/monthly | No | Default: weekly |
| `days_of_week` | int[] (0-6) | No | 0=Sunday |
| `is_active` | boolean | No | Default: true |
| `start_date` | YYYY-MM-DD | No | When it begins |
| `recurrence_end_date` | YYYY-MM-DD / null | No | When it ends |

---

## Week Reviews

### `wayve_manage_week_review`
**Action: `save`**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `week_number` | int 1-53 | Yes | Week |
| `year` | int | Yes | Year |
| `mood_rating` | int 1-5 | No | Overall mood |
| `energy_level` | int 1-5 | No | Energy |
| `fulfillment_rating` | int 1-5 | No | Fulfillment |
| `proud_of` | string (max 1000) | No | Wins |
| `what_worked` | string (max 1000) | No | Keep doing |
| `what_to_change` | string (max 1000) | No | Adjust |
| `focus_bucket_id` | UUID | No | Next week's focus |
| `wrap_up_status` | enum | No | Ritual status |
| `fresh_start_status` | enum | No | Ritual status |

**Action: `save_buckets`**
| Param | Type | Required |
|-------|------|----------|
| `week_review_id` | UUID | Yes |
| `buckets` | array (max 20) | Yes |

Each bucket: `{ bucket_id (UUID), score (1-5), satisfaction (1-5), note (max 1000), hours_planned, hours_actual, activities_planned, activities_completed }`

---

## Analytics

### `wayve_get_analytics`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | producer_score / task_patterns / energy_skill_matrix | Yes | Type of analysis |
| `week` | int 1-53 | No | For producer_score only |
| `year` | int | No | For producer_score only |

- **producer_score**: completion rate (0-100), per-bucket breakdown, 12-week trend
- **task_patterns**: frequently incomplete activities, energy patterns by time, bucket distribution (4 weeks)
- **energy_skill_matrix**: activities grouped by energy/skill, delegation candidates (8 weeks)

---

## Knowledge Base

### `wayve_manage_knowledge`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | list/get/create/update/delete/summary/save_insight | Yes | What to do |
| `id` | UUID | For get/update/delete | Entry ID |
| `category` | string (max 100) | For create/save_insight/list filter | Category |
| `key` | string (max 200) | For create/save_insight | Key name |
| `value` | string (max 2000) | For create/save_insight | Content |
| `confidence` | float 0-1 | No | Default: 0.8 |
| `source` | string (max 200) | For create/update | Auto "ai_conversation" for save_insight |

**save_insight** is a shortcut for create with source auto-set to "ai_conversation".

---

## Time Audits

### `wayve_manage_time_audit`
**Action: `start`**
| Param | Type | Required |
|-------|------|----------|
| `start_date` | YYYY-MM-DD | Yes |
| `end_date` | YYYY-MM-DD | Yes |
| `name` | string (max 100) | No (default: "Time Audit") |
| `interval_minutes` | int 15-120 | No (default: 30) |
| `active_hours_start` | HH:MM | No (default: 08:00) |
| `active_hours_end` | HH:MM | No (default: 20:00) |

**Action: `log_entry`**
| Param | Type | Required |
|-------|------|----------|
| `audit_id` | UUID | Yes |
| `what_did_you_do` | string 1-500 | Yes |
| `energy_level` | int 1-5 | Yes |
| `skill_level` | int 1-5 | No |
| `bucket_id` | UUID | No |
| `note` | string (max 500) | No |

**Action: `report`**
| Param | Type | Required |
|-------|------|----------|
| `audit_id` | UUID | Yes |

Returns: bucket_summary + delegation_candidates.

**Action: `delete`**
| Param | Type | Required |
|-------|------|----------|
| `audit_id` | UUID | Yes |

Permanently deletes the audit and all its entries.

---

## Checklist Items

### `wayve_manage_checklist`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | list/create/update/delete/bulk_create | Yes | What to do |
| `activity_id` | UUID | Yes | Parent activity |
| `item_id` | UUID | For update/delete | Checklist item |
| `title` | string (max 500) | For create | Item text |
| `completed` | boolean | For update | Toggle |
| `sort_order` | int >= 0 | No | Position |
| `items` | array (max 50) | For bulk_create | `[{ title, completed?, sort_order? }]` |

---

## Recurrence

### `wayve_manage_recurrence`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | get / set / delete | Yes | What to do |
| `activity_id` | UUID | Yes | Activity |
| `frequency` | daily/weekly/biweekly/monthly | For set | How often |
| `interval` | int 1-12 | No | Default: 1 |
| `days_of_week` | int[] (0-6) | No | For weekly/biweekly |
| `end_date` | YYYY-MM-DD | No | When to stop |

---

## Focus Templates

### `wayve_manage_focus_template`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | list/get_active/create/update/activate/delete | Yes | What to do |
| `id` | UUID | For update/activate/delete | Template ID |
| `name` | string (max 100) | For create | Template name |
| `description` | string (max 500) | No | Details |
| `is_perfect_week` | boolean | No | Perfect Week template |
| `distribution` | `{ "bucket_id": hours }` | For create | Hours per bucket |
| `total_hours` | float 0-168 | No | Total weekly hours |

---

## User Settings

### `wayve_manage_settings`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | get_preferences / update_preferences / get_profile / update_profile | Yes | What to do |
| `calendar_start_hour` | int 0-23 | No | Day starts at |
| `calendar_end_hour` | int 1-24 | No | Day ends at |
| `max_hours_per_day` | int 1-24 | No | Max schedulable |
| `sleep_hours_per_day` | float 0-24 | No | Sleep hours |
| `full_name` | string (max 100) | No | For update_profile |

---

## Happiness Insights

### `wayve_get_happiness_insights`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `recalculate` | boolean | No | Force fresh calculation (default: false) |

Returns mood correlations: what activities/buckets correlate with higher/lower mood scores.

---

## Bucket Frequencies

### `wayve_manage_bucket_frequency`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | list / create / update / delete | Yes | What to do |
| `id` | UUID | For update/delete | Frequency target ID |
| `bucket_id` | UUID | For create | Bucket to set target for |
| `frequency_type` | weekly / daily / monthly | For create | Tracking period |
| `target_count` | int 1-100 | For create | Activities per period |

Examples: "exercise 3x/week" → bucket_id=Health, frequency_type=weekly, target_count=3

### `wayve_get_frequency_progress`
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `week` | int 1-53 | No | Week number (default: current) |
| `year` | int | No | Year (default: current) |

Returns per-bucket frequency targets vs. actual completion for the week.

---

## Smart Suggestions

### `wayve_manage_smart_suggestions`
Track observational suggestions — patterns paired with proposals.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | list/create/accept/dismiss/snooze/delete | Yes | What to do |
| `id` | UUID | For accept/dismiss/snooze/delete | Suggestion ID (knowledge entry ID) |
| `pattern` | string (max 1000) | For create | What was observed |
| `proposal` | string (max 1000) | For create | What is proposed |
| `source_data` | object | No | Supporting analytics data (for create) |
| `created_from` | string (max 100) | No | Context: "wrap_up", "fresh_start", "life_audit", "analytics" |
| `snooze_until` | YYYY-MM-DD | For snooze | Resurface after this date |
| `status_filter` | pending/accepted/dismissed/snoozed | No | Filter for list action |

**Stored JSON value:** `{ pattern, proposal, source_data, status, created_from, snoozed_until }`

**Status flow:** pending → accepted / dismissed / snoozed. After `accepted`, Wayve is done.
