# Ultimate Fork and Skill Scanner

Scan GitHub forks and ClawHub skills to discover valuable changes and emerging trends.

## Setup
- **Forks:** Execute as part of your GitHub intelligence module; automate via cron.
- **Skills:** Identify and explore top ClawHub skills.

## Code Layout
- **Skill Code:** Located in `scripts/`
- **Data & Logs:** Track analysis in `data/`
- **Reports:** Auto-generates in `Cron_Tasks/` with detailed insights.

## Key Phases

### Fork Scanner
1. **Bash Pre-Filter:** Triage 1,000 forks, discard non-active.
2. **Sub-Agent Fan-Out:** Distribute candidate analysis for parallel processing.
3. **Main Agent Assembly:** Finalize report and insights.
4. **Scheduled Runs:** Mon/Thu.

### Skill Scanner
1. **Evaluate 10 Skills:** Score by functionality, relevance, and maintenance.
2. **In-Depth Author Scan:** Check top author’s other skills.
3. **Compile Insights:** Lay practical improvement steps.

## Continuous Improvement
- Integrate learnings into day-to-day operations.
- Continually update skill interests, reflecting evolving needs.

For more information and advanced configurations, please refer to the META or detailed execution recipes in the skill package.