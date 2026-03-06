# Shelf Lifecycle

## Status Flow

```
                    ┌──────────┐
                    │ uploading│
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ parsing  │
                    └────┬─────┘
                         │
                    ┌────▼──────────┐
                    │ structuring   │
                    └────┬──────────┘
                         │
                    ┌────▼──────────┐
                    │ verifying     │
                    └────┬──────┬───┘
                         │      │
              (review    │      │  (no review)
               mode)     │      │
                    ┌────▼───┐  │
                    │ review │  │
                    └──┬──┬──┘  │
                       │  │     │
            (approve)  │  │     │
                    ┌──▼──┘     │
                    │           │
                    ▼           ▼
               ┌────────┐
               │ ready  │
               └────────┘

  Any step can fail:
               ┌────────┐    retry     ┌───────────┐
               │ failed │ ──────────►  │ uploading  │
               └────────┘              └───────────┘
```

## Status Definitions

| Status        | Meaning                                  |
| ------------- | ---------------------------------------- |
| `uploading`   | Upload accepted and queued               |
| `parsing`     | Source content extraction in progress    |
| `structuring` | Filesystem layout generation in progress |
| `verifying`   | Output checks in progress                |
| `review`      | Waiting for approval (review mode only)  |
| `ready`       | Finalized and available                  |
| `failed`      | Processing failed; retry available       |

## Review Mode

- **Dashboard uploads:** review mode enabled by default
- **API uploads:** review mode disabled unless `review=true` is passed

In `review` status, you can:

- **Approve** (`POST /v1/shelves/{id}/approve`): optionally apply file operations (rename, delete, mkdir, write), then transition to `ready`
- **Regenerate** (`POST /v1/shelves/{id}/regenerate`): re-run structuring and verification from scratch

## Failed Shelves

When processing fails, the response includes:

- `errorMessage`: human-readable description of what went wrong
- `failedAtStep`: which pipeline step failed (`parsing`, `structuring`, `verifying`)

Retry with `POST /v1/shelves/{id}/retry` to re-trigger the full pipeline.

## Templates

Templates guide how Shelv organizes the document. They improve consistency but don't guarantee identical output across different source documents.

| Template         | Typical use                                 |
| ---------------- | ------------------------------------------- |
| `book`           | Books, manuals, long-form publications      |
| `legal-contract` | Contracts and legal agreements              |
| `academic-paper` | Research papers and journal-style documents |

### Example: `book` output structure

```
README.md
metadata.json
parts/
  part-1-foundations/
    chapter-01-introduction.md
    chapter-02-background.md
  part-2-analysis/
    chapter-03-methodology.md
    chapter-04-results.md
```

### Example: `legal-contract` output structure

```
README.md
metadata.json
clauses/
  definitions.md
  scope-of-work.md
  payment-terms.md
  force-majeure.md
  termination.md
schedules/
  schedule-a-pricing.md
  schedule-b-sla.md
```

### Example: `academic-paper` output structure

```
README.md
metadata.json
sections/
  abstract.md
  introduction.md
  methodology.md
  results.md
  discussion.md
  conclusion.md
references.md
```

Exact file names and directory depth vary by source document. Always discover paths at runtime using `tree` or `find` rather than hardcoding.
