# Edsby Student Integration Skill

Author: Lysandre Stone-Bourgeois
Version: 1.0.0
Description: Integrates with Edsby via browser relay to fetch classes/grades/assignments, generate reports/summaries, and sync due dates to Google Calendar. Includes scheduled checks.
Tools: 
- edsby_fetch_data: Fetches raw data from Edsby.
- edsby_generate_report: Creates personalized report.
- edsby_sync_assignments: Syncs due dates to Google Calendar.
- edsby_generate_summary_improvements: Bi-weekly grade summary with tips.
- edsby_daily_check: Daily assignment check and sync.

Dependencies: playwright, googleapis
Config: EDSBY_HOST, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_CALENDAR_ID, BROWSER_CONTEXT_PATH
Security: Uses persistent browser sessions; handle creds securely.