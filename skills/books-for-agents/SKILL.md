---
name: Books for Agents
description: An open source knowledge base of structured book summaries,
  available to any AI agent via MCP.
---

# Books for Agents

An open source knowledge base of structured book summaries, available to any AI agent via MCP.

## Setup

1. If you don't have the `books-for-agents` MCP server installed, add it:

```
claude mcp add --transport http books-for-agents https://booksforagents.com/mcp
```

Or add to your MCP config file:

```json
{
  "mcpServers": {
    "books-for-agents": {
      "url": "https://booksforagents.com/mcp"
    }
  }
}
```

2. Once connected, you have access to all tools below.

## What you can do

### Search for books

Use `search_books` to find books by topic, keyword, or question. Supports hybrid search (full-text + semantic vector embeddings).

```
search_books({ query: "how to build better habits" })
search_books({ query: "leadership", category: "business" })
search_books({ query: "cognitive biases and decision making", limit: 3 })
```

### Read a book summary

Use `get_book` to retrieve the full structured summary of a specific book by slug or title (partial match supported).

```
get_book({ slug: "atomic-habits" })
get_book({ title: "Deep Work" })
```

### Read a specific section

Use `get_book_section` to retrieve only one section of a book — saves tokens when you don't need the full summary. Available sections: `ideas`, `frameworks`, `quotes`, `connections`, `when-to-use`.

```
get_book_section({ slug: "the-lean-startup", section: "frameworks" })
get_book_section({ slug: "clean-code", section: "quotes" })
get_book_section({ slug: "thinking-fast-and-slow", section: "when-to-use" })
```

### Browse categories

Use `list_categories` to see all available categories and how many books each one has.

```
list_categories()
```

### Suggest a new book

Use `suggest_book` to add a book to the generation backlog. Checks for duplicates against published books and existing backlog entries.

```
suggest_book({ title: "Thinking in Bets", author: "Annie Duke", category: "psychology" })
```

### See the backlog

Use `list_backlog` to see all pending books waiting to be generated, along with their status.

```
list_backlog()
```

### Generate a book summary

Use `generate_book` to get the template, example, metadata, and instructions needed to generate the next book summary. You can specify a title or let it pick the next pending one.

```
generate_book()
generate_book({ title: "Never Split the Difference" })
```

After generating the content, call `submit_book` to publish it.

### Publish a book summary

Use `submit_book` to publish a generated summary directly to the knowledge base. Call this after generating content with `generate_book`.

```
submit_book({
  slug: "never-split-the-difference",
  title: "Never Split the Difference",
  author: "Chris Voss",
  category: "business",
  content: "---\ntitle: \"Never Split the Difference\"\n..."
})
```

## Tips

- Use `get_book_section` instead of `get_book` when you only need one part — it saves significant tokens.
- Use `search_books` with natural language queries — the semantic search understands meaning, not just keywords.
- When generating a book, follow the template and instructions returned by `generate_book` exactly. All content must be in English.
- Connections between books use `[[slug]]` format and must reference existing books only.
