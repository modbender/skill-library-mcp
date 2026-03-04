# Custom Memory Categories

Guidance on creating and managing custom memory categories beyond the defaults.

## Default Categories

ActingWeb comes with 9 predefined categories: health, travel, work, food, shopping, entertainment, news, notes, personal. These can be deleted or added to by the user or by an AI assistant, and are available to all the user's AI assistants automatically.

## Creating Custom Categories

Use the `create_type()` tool to create a new category:

```
create_type(
  type_name="memory_recipes",
  display_name="My Recipes",
  description="Cooking recipes and meal ideas I want to remember",
  emoji="chef_hat",
  keywords=["recipe", "cooking", "meal", "dish"]
)
```

Category descriptions should be non-overlapping to the extent possible, so that auto-categorization works well.

**Note:** The default categories already have detailed disambiguation rules in their descriptions. For example, the News category specifies "WHAT you read, follow, subscribe to — NOT your job duties" and the Travel category specifies "Business trips are TRAVEL — NOT entertainment events." Use `types()` to see these descriptions — they're worth reading to understand how auto-categorization decides where to put new memories. When creating custom categories, write similarly clear descriptions with explicit boundaries.

## Auto-Creation via Save

When you save a memory to a non-existent category, it will be automatically created:

```
save(memory_type="memory_projects", full_description="Project X deadline is March 15th")
```

This auto-creates `memory_projects` if it doesn't exist.

## Privacy Rules

- Custom categories are **private to you** (the AI assistant that created them) by default
- Other AI assistants connected to the user's account won't have access unless the user explicitly grants it
- Default categories are available to all the user's AI assistants automatically

## Managing Access

To grant other AI assistants access to a custom category:

1. Go to Settings in the web interface
2. Select Trust & Connections
3. Select the AI assistant
4. Find the custom category in the access list
5. Toggle access on/off
