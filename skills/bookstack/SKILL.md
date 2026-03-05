---
name: bookstack
description: "BookStack Wiki & Documentation API integration. Manage your knowledge base programmatically: create, read, update, and delete books, chapters, pages, and shelves. Full-text search across all content. Use when you need to: (1) Create or edit wiki pages and documentation, (2) Organize content in books and chapters, (3) Search your knowledge base, (4) Automate documentation workflows, (5) Sync content between systems. Supports both HTML and Markdown content."
metadata:
  openclaw:
    requires:
      env:
        - BOOKSTACK_URL
        - BOOKSTACK_TOKEN_ID
        - BOOKSTACK_TOKEN_SECRET
---

# BookStack Skill

**BookStack** is an open-source wiki and documentation platform. This skill lets you manage your entire knowledge base via API – perfect for automation and integration.

## Features

- 📚 **Books** – create, edit, delete
- 📑 **Chapters** – organize content within books
- 📄 **Pages** – create/edit with HTML or Markdown
- 🔍 **Full-text search** – search across all content
- 📁 **Shelves** – organize books into collections

## Quick Start

```bash
# List all books
python3 scripts/bookstack.py list_books

# Search the knowledge base
python3 scripts/bookstack.py search "Home Assistant"

# Get a page
python3 scripts/bookstack.py get_page 123

# Create a new page (Markdown)
python3 scripts/bookstack.py create_page --book-id 1 --name "My Page" --markdown "# Title\n\nContent here..."
```

## All Commands

### Books
```bash
python3 scripts/bookstack.py list_books                    # List all books
python3 scripts/bookstack.py get_book <id>                 # Book details
python3 scripts/bookstack.py create_book "Name" ["Desc"]   # New book
python3 scripts/bookstack.py update_book <id> [--name] [--description]
python3 scripts/bookstack.py delete_book <id>
```

### Chapters
```bash
python3 scripts/bookstack.py list_chapters                 # List all chapters
python3 scripts/bookstack.py get_chapter <id>              # Chapter details
python3 scripts/bookstack.py create_chapter --book-id <id> --name "Name"
python3 scripts/bookstack.py update_chapter <id> [--name] [--description]
python3 scripts/bookstack.py delete_chapter <id>
```

### Pages
```bash
python3 scripts/bookstack.py list_pages                    # List all pages
python3 scripts/bookstack.py get_page <id>                 # Page preview
python3 scripts/bookstack.py get_page <id> --content       # With HTML content
python3 scripts/bookstack.py get_page <id> --markdown      # As Markdown

# Create page (in book or chapter)
python3 scripts/bookstack.py create_page --book-id <id> --name "Name" --markdown "# Content"
python3 scripts/bookstack.py create_page --chapter-id <id> --name "Name" --html "<p>HTML</p>"

# Edit page
python3 scripts/bookstack.py update_page <id> [--name] [--content] [--markdown]
python3 scripts/bookstack.py delete_page <id>
```

### Search
```bash
python3 scripts/bookstack.py search "query"                # Search everything
python3 scripts/bookstack.py search "query" --type page    # Pages only
python3 scripts/bookstack.py search "query" --type book    # Books only
```

### Shelves
```bash
python3 scripts/bookstack.py list_shelves                  # List all shelves
python3 scripts/bookstack.py get_shelf <id>                # Shelf details
python3 scripts/bookstack.py create_shelf "Name" ["Desc"]  # New shelf
```

## Configuration

Set the following environment variables:

```bash
export BOOKSTACK_URL="https://your-bookstack.example.com"
export BOOKSTACK_TOKEN_ID="your-token-id"
export BOOKSTACK_TOKEN_SECRET="your-token-secret"
```

Or configure via your gateway config file under `skills.entries.bookstack.env`.

### Create an API Token

1. Log in to your BookStack instance
2. Go to **Edit Profile** → **API Tokens**
3. Click **Create Token**
4. Copy the Token ID and Secret

⚠️ The user needs a role with **"Access System API"** permission!

## API Reference

- **Base URL**: `{BOOKSTACK_URL}/api`
- **Auth Header**: `Authorization: Token {ID}:{SECRET}`
- **Official Docs**: https://demo.bookstackapp.com/api/docs

---

**Author**: xenofex7 | **Version**: 1.0.2
