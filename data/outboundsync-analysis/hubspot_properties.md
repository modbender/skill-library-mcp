# HubSpot properties updated by OutboundSync

Source: OutboundSync Help Center — “Which HubSpot properties are updated” (Last updated Jan 10, 2026).

## Default contact properties

| OutboundSync webhook field | Notes | HubSpot property label | HubSpot internal label | Type |
|---|---|---|---|---|
| `to_email` | from email object | Email | `email` | Single-line text |
| `to_name` or `to_email` | if `to_name` not present, use `to_email` | First Name | `firstname` | Single-line text |
| `to_name` | if not present leave blank | Last Name | `lastname` | Single-line text |
| `domain` | extracted after `@` | Website URL | `website` | Single-line text |
| `webhook owner` | if “Assign contact owner” enabled | Contact owner | `hubspot_owner_id` | Single-line text |

## Default company properties

Only used if “Create or update company” is enabled.

| OutboundSync webhook field | Notes | HubSpot property label | HubSpot internal label | Type |
|---|---|---|---|---|
| `domain` | extracted after `@` | Website URL | `website` | Single-line text |
| `domain` | extracted after `@` | Company Domain Name | `domain` | URL |

## Custom contact properties

### Property names and types

| Property Name | Event Type | HubSpot Property Type |
|---|---|---|
| Last app URL | ALL EVENTS | Single-line text |
| Last bounce time | EMAIL BOUNCE | Date picker |
| Last campaign ID | ALL EVENTS | Single-line text |
| Last campaign name | ALL EVENTS | Single-line text |
| Last connection status | CONNECTION REQUEST ACCEPTED OR SENT | Single-line text |
| Last connection status time | CONNECTION REQUEST ACCEPTED OR SENT | Date picker |
| Last email campaign ID | ALL EMAIL EVENTS | Single-line text |
| Last email campaign name | ALL EMAIL EVENTS | Single-line text |
| Last email lead category update ID | LEAD CATEGORY UPDATE | Single-line text |
| Last email lead category update name | LEAD CATEGORY UPDATE | Single-line text |
| Last email open message | EMAIL OPEN | Single-line text |
| Last email open subject | EMAIL OPEN | Single-line text |
| Last email open time | EMAIL OPEN | Date picker |
| Last email reply address | EMAIL REPLY | Single-line text |
| Last email reply message | EMAIL REPLY | Single-line text |
| Last email reply name | EMAIL REPLY | Single-line text |
| Last email reply subject | EMAIL REPLY | Single-line text |
| Last email reply time | EMAIL REPLY | Date picker |
| Last email sent address | EMAIL SENT | Single-line text |
| Last email sent message | EMAIL SENT | Single-line text |
| Last email sent name | EMAIL SENT | Single-line text |
| Last email sent subject | EMAIL SENT | Single-line text |
| Last email sent time | EMAIL SENT | Date picker |
| Last email sequence step | EMAIL SENT | Number |
| Last email unsubscribe time | LEAD UNSUBSCRIBED | Date picker |
| Last follow sender | FOLLOW SENT | Single-line text |
| Last follow time | FOLLOW SENT | Date picker |
| Last lead category ID | LEAD CATEGORY UPDATE | Single-line text |
| Last lead category name | LEAD CATEGORY UPDATE | Single-line text |
| Last like post URL | LIKED POST | Single-line text |
| Last like sender | LIKED POST | Single-line text |
| Last like time | LIKED POST | Date picker |
| Last link click time | EMAIL LINK CLICK | Date picker |
| Last link click URL | EMAIL LINK CLICK | Single-line text |
| Last reply social message | MESSAGE REPLY RECEIVED | Single-line text |
| Last reply social profile | MESSAGE REPLY RECEIVED | Single-line text |
| Last reply social sender | MESSAGE REPLY RECEIVED | Single-line text |
| Last reply social time | MESSAGE REPLY RECEIVED | Date picker |
| Last sent social message | MESSAGE SENT | Single-line text |
| Last sent social profile | MESSAGE SENT | Single-line text |
| Last sent social sender | MESSAGE SENT | Single-line text |
| Last sent social time | MESSAGE SENT | Date picker |
| Last social campaign ID | ALL SOCIAL EVENTS | Single-line text |
| Last social campaign name | ALL SOCIAL EVENTS | Single-line text |
| Last social lead category ID | LEAD CATEGORY UPDATE | Single-line text |
| Last social lead category name | LEAD CATEGORY UPDATE | Single-line text |
| Last update occurred | ALL EVENTS | Date picker |
| Last update source | ALL EVENTS | Single-line text |
| Last view sender | VIEWED PROFILE | Single-line text |
| Last view time | VIEWED PROFILE | Date picker |
| Number of email link clicks | EMAIL LINK CLICK | Number |
| Number of email opens | EMAIL OPEN | Number |

### Names and event by platform

Not every property is supported across every Sales Engagement Platform.

| Property Name | Channel Type | Instantly | Smartlead | EmailBison | HeyReach |
|---|---|:---:|:---:|:---:|:---:|
| Last app URL | EMAIL OR SOCIAL | ✅ | ✅ | ❌ | ✅ |
| Last bounce time | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last campaign ID | EMAIL OR SOCIAL | ✅ | ✅ | ✅ | ✅ |
| Last campaign name | EMAIL OR SOCIAL | ✅ | ✅ | ✅ | ✅ |
| Last connection status | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last connection status time | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last email campaign ID | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email campaign name | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email lead category update ID | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email lead category update name | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email open message | EMAIL | ❌ | ✅ | ✅ | ❌ |
| Last email open subject | EMAIL | ❌ | ✅ | ✅ | ❌ |
| Last email open time | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email reply address | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email reply message | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email reply name | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email reply subject | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email reply time | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email sent address | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email sent message | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email sent name | EMAIL | ❌ | ❌ | ✅ | ❌ |
| Last email sent subject | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email sent time | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email sequence step | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last email unsubscribe time | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last follow sender | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last follow time | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last lead category ID | EMAIL OR SOCIAL | ✅ | ✅ | ✅ | ✅ |
| Last lead category name | EMAIL OR SOCIAL | ✅ | ✅ | ✅ | ✅ |
| Last like post URL | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last like sender | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last like time | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last link click time | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last link click URL | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Last reply social message | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last reply social profile | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last reply social sender | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last reply social time | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last sent social message | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last sent social profile | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last sent social sender | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last sent social time | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last social campaign ID | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last social campaign name | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last social lead category ID | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last social lead category name | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last update occurred | EMAIL OR SOCIAL | ✅ | ✅ | ✅ | ✅ |
| Last update source | EMAIL OR SOCIAL | ✅ | ✅ | ✅ | ✅ |
| Last view sender | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Last view time | SOCIAL | ❌ | ❌ | ❌ | ✅ |
| Number of email link clicks | EMAIL | ✅ | ✅ | ✅ | ❌ |
| Number of email opens | EMAIL | ✅ | ✅ | ✅ | ❌ |

### Property names and internal labels

> **Note (\*\*):** The Help Center table currently maps “Last email reply subject” to `os_last_reply_message` (same as “Last email reply message”). Rows marked (\*\*) are affected. If you rely on reply subject specifically, confirm the internal label in your HubSpot portal.

| Property Name | HubSpot internal label |
|---|---|
| Last app URL | `os_last_app_url` |
| Last bounce time | `os_last_bounce_time` |
| Last campaign ID | `os_last_campaign_id` |
| Last campaign name | `os_last_campaign_name` |
| Last connection status | `os_last_connection_status` |
| Last connection status time | `os_last_connection_status_time` |
| Last email campaign ID | `os_last_email_campaign_id` |
| Last email campaign name | `os_last_email_campaign_name` |
| Last email lead category update ID | `os_last_email_lead_category_id` |
| Last email lead category update name | `os_last_email_lead_category_name` |
| Last email open message | `os_last_open_message` |
| Last email open subject | `os_last_open_subject` |
| Last email open time | `os_last_open_time` |
| Last email reply address | `os_last_reply_address` |
| Last email reply message | `os_last_reply_message` |
| Last email reply name | `os_last_reply_name` |
| Last email reply subject (**) | `os_last_reply_message` |
| Last email reply time | `os_last_reply_time` |
| Last email sent address | `os_last_sent_address` |
| Last email sent message | `os_last_sent_message` |
| Last email sent name | `os_last_sent_name` |
| Last email sent subject | `os_last_sent_subject` |
| Last email sent time | `os_last_sent_time` |
| Last email sequence step | `os_last_email_sequence_step` |
| Last email unsubscribe time | `os_last_unsubscribe_time` |
| Last follow sender | `os_last_follow_sender` |
| Last follow time | `os_last_follow_time` |
| Last lead category ID | `os_last_lead_category_id` |
| Last lead category name | `os_last_lead_category_name` |
| Last like post URL | `os_last_like_post_url` |
| Last like sender | `os_last_like_sender` |
| Last like time | `os_last_like_time` |
| Last link click time | `os_last_link_click_time` |
| Last link click URL | `os_last_link_click_url` |
| Last reply social message | `os_last_reply_social_message` |
| Last reply social profile | `os_last_reply_social_profile` |
| Last reply social sender | `os_last_reply_social_sender` |
| Last reply social time | `os_last_reply_social_time` |
| Last sent social message | `os_last_sent_social_message` |
| Last sent social profile | `os_last_sent_social_profile` |
| Last sent social sender | `os_last_sent_social_sender` |
| Last sent social time | `os_last_sent_social_time` |
| Last social campaign ID | `os_last_social_campaign_id` |
| Last social campaign name | `os_last_social_campaign_name` |
| Last social lead category ID | `os_last_social_lead_category_id` |
| Last social lead category name | `os_last_social_lead_category_name` |
| Last update occurred | `os_last_update_occurred` |
| Last update source | `os_last_update_source` |
| Last view sender | `os_last_view_sender` |
| Last view time | `os_last_view_time` |
| Number of email link clicks | `os_number_of_email_link_clicks` |
| Number of email opens | `os_number_of_email_opens` |
