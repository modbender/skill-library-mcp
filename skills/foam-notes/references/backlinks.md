# Backlinks in Foam

Source: https://foamnotes.com/user/features/backlinking

Backlinks are one of Foam's most powerful features for knowledge discovery. They automatically show you which notes reference your current note, creating a web of interconnected knowledge that reveals surprising relationships between your ideas.

## What Are Backlinks?

A backlink is a connection from another note that points to the note you're currently viewing. While you create forward links intentionally with wikilinks, backlinks are discovered automatically by Foam.

## Forward Links vs Backlinks

### Forward Links (what you create):

```markdown
# Machine Learning Note

I'm studying [[Neural Networks]] and [[Deep Learning]] concepts.
```

### Backlinks (what Foam discovers):

If you're viewing the "Neural Networks" note, Foam shows you that "Machine Learning Note" links to it, even though you didn't explicitly create that reverse connection.

This bidirectional linking creates a richer knowledge network than traditional hierarchical folders.

## Accessing Backlinks - Connections Panel

The Connections panel shows both forward links and backlinks:

1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "connections" and select "Explorer: Focus on Connections"
3. Use the filter buttons to show only backlinks, forward links, or all connections

## Using Backlinks for Knowledge Discovery

### 1. Finding Unexpected Connections

Backlinks often reveal relationships you didn't consciously create.

Example: While reviewing a "Productivity" note, backlinks might show connections from:
- A cooking recipe (time management for meal prep)
- A fitness routine (efficient workout planning)
- A work project (team productivity strategies)

These diverse connections can spark new insights and cross-domain learning.

### 2. Identifying Important Concepts

Notes with many backlinks are often central to your thinking:
- Hub concepts that connect many ideas
- Frequently referenced resources or definitions
- Bridge topics that span multiple domains

### 3. Building Context Around Ideas

Backlinks provide context for how you use concepts across different areas:
- How you apply the same principle in various projects
- Evolution of your thinking about a topic over time
- Different perspectives you've encountered on the same idea

## Using Backlinks for Reference Lists

You can use backlinks to create reference lists:

1. Create a tag note like `[[book]]`
2. In notes about books, link to `[[book]]`
3. The `book` note will show all linked books in its backlinks

This is an alternative to using #book tags for categorization.

## Related

- graph-view.md - Visualize your knowledge network
- tags.md - Alternative organization method
