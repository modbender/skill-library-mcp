# Trigger Tests

## True Positives (should trigger)

| # | Input | Expected |
|---|-------|----------|
| 1 | "Write a technical book about AI agents" | trigger |
| 2 | "I want to write a book about OpenClaw" | trigger |
| 3 | "Create a multi-chapter manuscript on cloud security" | trigger |
| 4 | "Help me write a book project" | trigger |
| 5 | "写一本关于编译器的书" | trigger |
| 6 | "Can you write a long-form document about DevOps?" | trigger |
| 7 | "Use the book-writer skill to create a manuscript" | trigger |

## True Negatives (should NOT trigger)

| # | Input | Expected |
|---|-------|----------|
| 1 | "Write a blog post about AI" | no trigger |
| 2 | "Summarize this book for me" | no trigger |
| 3 | "Help me write a tweet" | no trigger |
| 4 | "Create a slide deck about security" | no trigger |
| 5 | "Review this chapter for me" | no trigger |
| 6 | "Read the book at this URL" | no trigger |
