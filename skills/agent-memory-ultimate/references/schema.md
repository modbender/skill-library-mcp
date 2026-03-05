# Knowledge Base Schema

## Tables

### contacts

| Column     | Type    | Description                        |
| ---------- | ------- | ---------------------------------- |
| id         | INTEGER | Primary key                        |
| phone      | TEXT    | Phone number (E.164 format with +) |
| name       | TEXT    | Contact name (from VCF)            |
| source     | TEXT    | 'whatsapp', 'vcf', or 'manual'     |
| notes      | TEXT    | Optional notes                     |
| created_at | TEXT    | Timestamp                          |
| updated_at | TEXT    | Timestamp                          |

**Indexes:** phone, name

### wa_groups

| Column            | Type    | Description                 |
| ----------------- | ------- | --------------------------- |
| id                | INTEGER | Primary key                 |
| jid               | TEXT    | WhatsApp group JID (unique) |
| name              | TEXT    | Group name/subject          |
| participant_count | INTEGER | Number of members           |
| created_at        | TEXT    | Timestamp                   |

### wa_memberships

| Column    | Type    | Description              |
| --------- | ------- | ------------------------ |
| id        | INTEGER | Primary key              |
| group_jid | TEXT    | References wa_groups.jid |
| phone     | TEXT    | Member phone number      |
| is_admin  | INTEGER | 1 if admin, 0 otherwise  |

**Unique constraint:** (group_jid, phone)

### documents

| Column     | Type    | Description                        |
| ---------- | ------- | ---------------------------------- |
| id         | INTEGER | Primary key                        |
| type       | TEXT    | 'log', 'project', 'note', 'export' |
| path       | TEXT    | Relative file path (unique)        |
| title      | TEXT    | Document title                     |
| content    | TEXT    | Full text content                  |
| hash       | TEXT    | MD5 hash for change detection      |
| created_at | TEXT    | Timestamp                          |
| updated_at | TEXT    | Timestamp                          |
| metadata   | TEXT    | JSON for extra fields              |

**FTS:** documents_fts (title, content)

### chatgpt_conversations

| Column        | Type    | Description                           |
| ------------- | ------- | ------------------------------------- |
| id            | TEXT    | ChatGPT conversation ID (primary key) |
| title         | TEXT    | Conversation title                    |
| created_at    | TEXT    | Timestamp                             |
| updated_at    | TEXT    | Timestamp                             |
| message_count | INTEGER | Number of messages                    |
| model         | TEXT    | GPT model used                        |

### chatgpt_messages

| Column          | Type | Description                           |
| --------------- | ---- | ------------------------------------- |
| id              | TEXT | Message ID (primary key)              |
| conversation_id | TEXT | References chatgpt_conversations.id   |
| role            | TEXT | 'user', 'assistant', 'system', 'tool' |
| content         | TEXT | Message text                          |
| created_at      | TEXT | Timestamp                             |

**FTS:** chatgpt_fts (conv_id, role, content)

### tags

| Column | Type    | Description             |
| ------ | ------- | ----------------------- |
| id     | INTEGER | Primary key             |
| doc_id | INTEGER | References documents.id |
| tag    | TEXT    | Tag string              |

### schema_version

| Column     | Type    | Description           |
| ---------- | ------- | --------------------- |
| version    | INTEGER | Schema version number |
| applied_at | TEXT    | When applied          |

## Full-Text Search

FTS5 tables for fast text search:

- `documents_fts` — Search document titles and content
- `chatgpt_fts` — Search ChatGPT message content

### FTS Query Syntax

```sql
-- Simple term
SELECT * FROM documents_fts WHERE documents_fts MATCH 'project';

-- Phrase
SELECT * FROM documents_fts WHERE documents_fts MATCH '"exact phrase"';

-- Prefix
SELECT * FROM documents_fts WHERE documents_fts MATCH 'Bas*';

-- Boolean
SELECT * FROM documents_fts WHERE documents_fts MATCH 'project AND vision';
SELECT * FROM documents_fts WHERE documents_fts MATCH 'project OR plan';
SELECT * FROM documents_fts WHERE documents_fts MATCH 'project NOT cancelled';

-- Column-specific
SELECT * FROM documents_fts WHERE documents_fts MATCH 'title:readme';
```
