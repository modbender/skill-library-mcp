# SurrealQL Quick Reference

A concise cheatsheet for the most commonly used SurrealQL statements, types, functions, and patterns.

## Namespace and Database

```surql
USE NS my_namespace DB my_database;
```

## CRUD Operations

```surql
-- Create with auto-generated ID
CREATE person SET name = "Alice", age = 30;

-- Create with specific ID
CREATE person:alice SET name = "Alice", age = 30;

-- Insert (upsert semantics)
INSERT INTO person { id: person:alice, name: "Alice", age: 30 };

-- Select all
SELECT * FROM person;

-- Select with conditions
SELECT name, age FROM person WHERE age > 25 ORDER BY name LIMIT 10;

-- Update (merge)
UPDATE person:alice SET age = 31;

-- Update with MERGE (partial update)
UPDATE person:alice MERGE { email: "alice@example.com" };

-- Replace (full overwrite)
UPDATE person:alice CONTENT { name: "Alice", age: 31, email: "alice@example.com" };

-- Delete
DELETE person:alice;
DELETE FROM person WHERE age < 18;
```

## Record Links and Graph Relations

```surql
-- Create a graph edge
RELATE person:alice -> knows -> person:bob SET since = d"2024-01-15";

-- Traverse outbound
SELECT ->knows->person.name FROM person:alice;

-- Traverse inbound
SELECT <-knows<-person.name FROM person:bob;

-- Multi-hop traversal
SELECT ->knows->person->works_at->company.name FROM person:alice;

-- Bidirectional
SELECT <->knows<->person.name FROM person:alice;
```

## Data Types

| Type | Example |
|------|---------|
| String | `"hello"` |
| Int | `42` |
| Float | `3.14` |
| Bool | `true`, `false` |
| None/Null | `NONE`, `NULL` |
| Datetime | `d"2026-02-19T12:00:00Z"` |
| Duration | `1h30m`, `7d`, `100ms` |
| Record ID | `person:alice`, `post:ulid()` |
| Array | `[1, 2, 3]` |
| Object | `{ key: "value" }` |
| Geometry | `{ type: "Point", coordinates: [-73.97, 40.77] }` |
| Bytes | `<bytes>"base64encoded"` |
| UUID | `u"550e8400-e29b-41d4-a716-446655440000"` |

## Schema Definition

```surql
-- Define table with schema enforcement
DEFINE TABLE person SCHEMAFULL;

-- Define fields
DEFINE FIELD name ON person TYPE string;
DEFINE FIELD age ON person TYPE int DEFAULT 0;
DEFINE FIELD email ON person TYPE option<string> ASSERT string::is::email($value);
DEFINE FIELD tags ON person TYPE array<string> DEFAULT [];
DEFINE FIELD created ON person TYPE datetime DEFAULT time::now() READONLY;

-- Define indexes
DEFINE INDEX idx_email ON person FIELDS email UNIQUE;
DEFINE INDEX idx_name ON person FIELDS name SEARCH ANALYZER ascii BM25;

-- Define vector index
DEFINE INDEX idx_embedding ON document FIELDS embedding MTREE DIMENSION 1536 DIST COSINE;
```

## Common Functions

### String Functions
```surql
string::concat("a", "b")       -- "ab"
string::lowercase("ABC")       -- "abc"
string::split("a,b,c", ",")    -- ["a", "b", "c"]
string::trim(" hello ")        -- "hello"
string::len("hello")           -- 5
string::contains("hello", "ell")  -- true
```

### Array Functions
```surql
array::len([1, 2, 3])          -- 3
array::distinct([1, 1, 2])     -- [1, 2]
array::flatten([[1, 2], [3]])   -- [1, 2, 3]
array::sort([3, 1, 2])         -- [1, 2, 3]
array::push([1, 2], 3)         -- [1, 2, 3]
array::filter([1, 2, 3], |$v| $v > 1)  -- [2, 3]
```

### Math Functions
```surql
math::sum([1, 2, 3])           -- 6
math::mean([1, 2, 3])          -- 2
math::max([1, 2, 3])           -- 3
math::min([1, 2, 3])           -- 1
math::round(3.7)               -- 4
math::abs(-5)                  -- 5
```

### Time Functions
```surql
time::now()                    -- Current datetime
time::day(d"2026-02-19")       -- 19
time::month(d"2026-02-19")     -- 2
time::year(d"2026-02-19")      -- 2026
time::format(time::now(), "%Y-%m-%d")
```

### Crypto and Rand
```surql
rand::uuid::v7()               -- Generate UUIDv7
rand::int(1, 100)              -- Random integer
rand::float(0.0, 1.0)          -- Random float
crypto::argon2::generate("password")
crypto::argon2::compare(hash, "password")
```

### Type Functions
```surql
type::is::string("hello")      -- true
type::is::int(42)              -- true
type::thing("person", "alice")  -- person:alice
```

## Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `WHERE age = 30` |
| `!=` | Not equals | `WHERE age != 30` |
| `>`, `>=`, `<`, `<=` | Comparison | `WHERE age > 25` |
| `AND`, `OR`, `NOT` | Logical | `WHERE age > 25 AND name != "Bob"` |
| `IN` | Containment | `WHERE status IN ["active", "pending"]` |
| `CONTAINS` | Array contains | `WHERE tags CONTAINS "admin"` |
| `CONTAINSALL` | Contains all | `WHERE tags CONTAINSALL ["a", "b"]` |
| `CONTAINSANY` | Contains any | `WHERE tags CONTAINSANY ["a", "b"]` |
| `~` | Fuzzy match | `WHERE name ~ "alice"` |
| `@@` | Full-text match | `WHERE content @@ "search term"` |
| `??` | Null coalesce | `email ?? "no-email"` |
| `?:` | Ternary | `age >= 18 ?: "minor"` |

## Subqueries and Expressions

```surql
-- Subquery in SELECT
SELECT *, (SELECT count() FROM ->wrote->post GROUP ALL) AS post_count FROM person;

-- LET bindings
LET $adults = SELECT * FROM person WHERE age >= 18;
SELECT * FROM $adults WHERE name STARTS WITH "A";

-- IF expression
SELECT *, IF age >= 18 THEN "adult" ELSE "minor" END AS category FROM person;

-- FOR loop (scripting)
FOR $p IN (SELECT * FROM person) {
    UPDATE $p.id SET verified = true;
};
```

## Transactions

```surql
BEGIN TRANSACTION;
    CREATE account:a SET balance = 100;
    CREATE account:b SET balance = 200;
    UPDATE account:a SET balance -= 50;
    UPDATE account:b SET balance += 50;
COMMIT TRANSACTION;
```

## Live Queries

```surql
LIVE SELECT * FROM person;
LIVE SELECT * FROM person WHERE age > 25;
KILL $live_query_id;
```

## Access Control

```surql
-- Define access method
DEFINE ACCESS user_auth ON DATABASE TYPE RECORD
    SIGNUP (CREATE user SET email = $email, pass = crypto::argon2::generate($pass))
    SIGNIN (SELECT * FROM user WHERE email = $email AND crypto::argon2::compare(pass, $pass))
    DURATION FOR SESSION 24h;

-- Define scope-level permissions
DEFINE TABLE post SCHEMAFULL
    PERMISSIONS
        FOR select FULL
        FOR create WHERE $auth.id != NONE
        FOR update WHERE author = $auth.id
        FOR delete WHERE author = $auth.id;
```

## Vector Search

```surql
-- Define vector index
DEFINE INDEX idx_vec ON document FIELDS embedding MTREE DIMENSION 1536 DIST COSINE;

-- Query nearest neighbors
SELECT *, vector::similarity::cosine(embedding, $query_vec) AS score
FROM document
WHERE embedding <|10|> $query_vec
ORDER BY score DESC;
```

## Common One-Liners

```surql
-- Count records
SELECT count() FROM person GROUP ALL;

-- Group and aggregate
SELECT department, count(), math::mean(salary) FROM employee GROUP BY department;

-- Deduplicate
SELECT array::distinct(->tagged->tag.name) FROM post;

-- Paginate
SELECT * FROM post ORDER BY created DESC LIMIT 20 START 40;

-- Check if record exists
IF (SELECT * FROM person:alice) THEN "exists" ELSE "not found" END;

-- Bulk upsert from array
INSERT INTO person $data ON DUPLICATE KEY UPDATE name = $input.name, age = $input.age;
```
