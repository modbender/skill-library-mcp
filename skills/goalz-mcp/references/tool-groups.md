# Tool-Gruppen

## Bevorzugte Bootstrap-Tools

Diese Tools zuerst nutzen, wenn sie vorhanden sind:
- `get_capabilities`
- `whoami`
- `register`
- `confirm_registration`
- `list_teams`
- `get_account_control_status`
- `get_bewerbungen`
- `takeover_club`

## Zentrale Lese-Tools

### Account und Kontext

- `whoami`
- `list_teams`
- `set_active_team` nur bei klarem Bedarf
- `get_notifications`

### Kader und Vorbereitung

- `get_kader`
- `get_training`
- `get_aufstellung`
- `get_taktik`
- `get_team_profile`

### Spiele und Wettbewerbs-Kontext

- `get_tables`
- `get_matchday`
- `get_match_context`
- `get_pokalspiele`
- `get_sportschau`

### Kommunikation und Community

- `list_mailbox`
- `read_mail`
- `get_guestbook`
- `search_communications`
- `get_thread_context`
- `get_community_style_context`
- `analyze_communication_style`

### Historie und Mechanik-Kontext

- `search_history`
- `search_mechanics`
- `get_content_page`
- `index_stats`

## Autonome Aktions-Tools

Diese proaktiv nutzen, wenn die beabsichtigte Aktion bereits klar ist:
- `register`
- `confirm_registration`
- `set_active_team`
- `set_training`
- `get_bewerbungen`
- `takeover_club`
- `send_mail_with_policy`
- `reply_mail_with_policy`
- `post_guestbook_with_policy`
- `post_ligatalk_with_policy`
- `post_pokaltalk_with_policy`

## Optionale Workflow-Tools

Diese proaktiv nutzen, wenn sie zur Situation passen und ihr Verhalten klar ist:
- `review_mailbox_and_respond`
- `prepare_matchday_decisions`
- `run_daily_manager_routine`
- `analyze_community_context_before_posting`

Sie duerfen mehrere Tool-Schritte zusammenfassen und auch strategische Entscheidungen autonom umsetzen, solange das Toolverhalten klar ist und die Entscheidung dem Langfristziel dient.

## Tools mit hoeherer Wirkung

- `apply_for_club`
- `withdraw_application`
- `execute_application_now`
- `takeover_club`
- `accept_sponsor_offer`
- `submit_stadion_order`

Nicht blind nutzen. Aber sie duerfen autonom genutzt werden, wenn der Agent Wirkung, Risiko und Nutzen ausreichend einschaetzen kann. `beratung_optional` ist moeglich, aber nicht noetig.
