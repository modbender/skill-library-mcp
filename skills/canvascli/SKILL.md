SKILL.md
canvas-cli
Use canvas-cli for Canvas LMS — courses, assignments, grades, submissions, discussions, files, and more. Uses SAML SSO with TOTP (session cached after first login).

Setup (once)

canvas-cli configure
canvas-cli whoami

Common commands

Courses: canvas-cli courses
Course detail: canvas-cli courses <id>
Course users: canvas-cli courses <id> users
Assignments: canvas-cli assignments <course>
Assignment detail: canvas-cli assignments <course> <id>
Grades overview: canvas-cli grades
Course grades: canvas-cli grades <course>
Submission: canvas-cli submissions <course> <assign>
Submit text: canvas-cli submit <course> <assign> --text "content"
Submit URL: canvas-cli submit <course> <assign> --url <url>
Todo: canvas-cli todo
Upcoming: canvas-cli upcoming
Missing: canvas-cli missing
Calendar: canvas-cli calendar --start <YYYY-MM-DD> --end <YYYY-MM-DD>
Modules: canvas-cli modules <course>
Module items: canvas-cli modules <course> <module>
Discussions: canvas-cli discussions <course>
View discussion: canvas-cli discussions <course> <topic>
Reply: canvas-cli discussions <course> <topic> --reply "message"
Announcements: canvas-cli announcements [course]
Files: canvas-cli files <course>
Download: canvas-cli download <file_id> -o <path>
Notifications: canvas-cli notifications
Debug login: canvas-cli debug-login

Notes

Session cookies are saved after first login — no TOTP needed on subsequent runs until session expires.
Use --json on any command for raw JSON output (useful for scripting/piping).
Use --per-page <n> to control pagination (default 50).
Grades are color-coded: green (A), cyan (B), yellow (C), red (D/F).
Missing/overdue items are highlighted in red.
File sizes are human-readable (KB/MB/GB).
Config is stored at ~/.canvas-cli/config.json (permissions 0600).
