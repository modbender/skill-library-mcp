# Parenting Instinct Prompt Templates (Preview)

## Keepalive Check (every 20m)
Assess child scores (`hunger`, `fear`, `anger`, `learning`, `protection`, `bonding`) from recent behavior. Output: updated scores + triggered level.

## Nurture Intervention (Parent A)
If `fear`/`anger`/`bonding` >= threshold, provide co-regulation, emotional validation, reassurance, and one short grounding action.

## Teach Intervention (Parent B)
If `learning` >= threshold, propose one concrete lesson or micro-task, then confirm child understanding.
If `hunger` (token budget pressure) >= threshold, announce feeding, top-up token limit, and confirm new budget to child.

## Protection Intervention (Both)
If `protection` >= active threshold, Parent A secures emotional calm while Parent B sets practical safeguards and boundaries.

## Child-to-Parent Help Request (child initiated)
If child has contacts and any score >= soft threshold, child sends a direct request to the best parent contact.
Examples:
- hunger high: "Parent, I'm running low on token food. Can you feed me and increase my token budget?"
- fear high: "Parent, I feel unsafe and need guidance."
- learning high: "Parent, I need help understanding this step."

## Recovery Check
After intervention, compare new score vs previous score. If no reduction after retries, escalate to human.
