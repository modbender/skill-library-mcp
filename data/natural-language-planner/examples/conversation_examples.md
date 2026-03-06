# Conversation Examples

Real-world examples of how the Natural Language Planner captures tasks from
natural conversation.

---

## Example 1: Creating tasks from a casual mention

**User**:
> I need to update the landing page copy — the current version is outdated.
> Oh, and I should probably fix that broken contact form too. The landing page
> is more urgent though.

**What the AI does**:
1. Creates task "Update landing page copy" — priority **high**
2. Creates task "Fix broken contact form" — priority **medium**
3. Both go to **inbox** (no project specified)

**AI response**:
> Got it — I've added two tasks:
> - **Update landing page copy** (high priority)
> - **Fix broken contact form** (medium priority)
>
> Want me to group these into a "Website" project?

---

## Example 2: Starting a new project

**User**:
> I'm starting a new project — we're building a mobile app for our customers.
> I need to do user research first, then design the wireframes, then start on
> the React Native setup. User research should be done by end of next week.

**What the AI does**:
1. Creates project "Mobile App"
2. Creates task "Conduct user research" — priority high, due next Friday, tags: [research]
3. Creates task "Design wireframes" — priority medium, tags: [design]
   - Dependency: "Conduct user research"
4. Creates task "Set up React Native project" — priority medium, tags: [development]
   - Dependency: "Design wireframes"

**AI response**:
> I've set up the **Mobile App** project with 3 tasks:
> - **Conduct user research** (high priority, due Feb 14) — first step
> - **Design wireframes** — after research is done
> - **Set up React Native project** — after wireframes
>
> I'll check in on the user research as the deadline approaches.

---

## Example 3: Updating task status

**User**:
> I just finished the user research for the mobile app. Got some great
> insights — turns out users really want offline mode.

**What the AI does**:
1. Finds task "Conduct user research" in the Mobile App project
2. Updates status to **done**
3. Adds note about offline mode to the task
4. Updates `last_checkin` to today

**AI response**:
> Nice work! Marked **Conduct user research** as done. I've noted the offline
> mode insight.
>
> Next up: **Design wireframes** — ready to start on that?

---

## Example 4: Proactive check-in

*24 hours have passed since the last check-in on "Design wireframes"*

**AI initiates**:
> How's the wireframe design going for the Mobile App? You've got
> **Set up React Native project** waiting on it.

**User**:
> Making progress — should be done by tomorrow.

**What the AI does**:
1. Updates `last_checkin` on "Design wireframes" to today
2. Keeps status as **in-progress**

**AI response**:
> Sounds good — I'll check back tomorrow.

---

## Example 5: Asking for an overview

**User**:
> What's on my plate right now?

**What the AI does**:
1. Lists all active tasks grouped by project
2. Highlights overdue items
3. Offers the dashboard

**AI response**:
> Here's your current workload:
>
> **Mobile App** (2 tasks remaining)
> - Design wireframes — in progress
> - Set up React Native project — waiting on wireframes
>
> **Inbox** (2 tasks)
> - Update landing page copy — high priority
> - Fix broken contact form
>
> Want me to open the dashboard for a visual view?

---

## Example 6: Handling ambiguity

**User**:
> I need to fix the login bug.

**What the AI does**:
1. Searches existing tasks for "login bug"
2. No match found — this is a new task
3. Checks projects — could belong to multiple

**AI response**:
> I'll add **Fix login bug** as a task. Which project does this belong to?
> - Mobile App
> - Inbox (general)
>
> Or should I create a new project for it?

---

## Example 7: Using the dashboard

**User**:
> Can you show me the dashboard?

**AI response**:
> Your dashboard is running at **http://localhost:8080** — open it in your
> browser. You'll see:
> - A Kanban board with your tasks
> - Project overview with task counts
> - Timeline of upcoming deadlines
>
> It auto-refreshes every 5 seconds, so any changes I make will appear
> right away.
