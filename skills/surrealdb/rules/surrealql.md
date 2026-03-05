# SurrealQL Reference

This is the comprehensive SurrealQL language reference for SurrealDB v3. SurrealQL is a SQL-like query language designed for SurrealDB's multi-model architecture, supporting document, graph, relational, vector, time-series, geospatial, and full-text search operations in a single language.

---

## Statements

### CREATE

Creates one or more records in a table.

```surql
-- Create a record with a random ID
CREATE person CONTENT {
    name: 'Tobie',
    age: 33,
    email: 'tobie@surrealdb.com'
};

-- Create a record with a specific ID
CREATE person:tobie SET
    name = 'Tobie',
    age = 33;

-- Create with a UUID-based ID
CREATE person:uuid() SET name = 'Jane';

-- Create with a ULID-based ID
CREATE person:ulid() SET name = 'John';

-- Create multiple records
CREATE person CONTENT [
    { name: 'Alice', age: 28 },
    { name: 'Bob', age: 35 }
];

-- Create with RETURN clause
CREATE person SET name = 'Eve' RETURN id, name;

-- Create with RETURN NONE (no output)
CREATE person SET name = 'Frank' RETURN NONE;

-- Create with RETURN BEFORE / AFTER / DIFF
CREATE person SET name = 'Grace' RETURN AFTER;
```

### SELECT

Retrieves records from one or more tables.

```surql
-- Select all fields from a table
SELECT * FROM person;

-- Select specific fields
SELECT name, age FROM person;

-- Select with alias
SELECT name AS full_name, math::floor(age) AS years FROM person;

-- Conditional filtering
SELECT * FROM person WHERE age > 30 AND name != 'Tobie';

-- Ordering results
SELECT * FROM person ORDER BY age DESC;

-- Limit and pagination
SELECT * FROM person LIMIT 10 START 20;

-- Grouping with aggregation
SELECT country, count() AS total FROM person GROUP BY country;

-- Nested field access
SELECT name.first, address.city FROM person;

-- Array filtering within records
SELECT emails[WHERE active = true] FROM person;

-- Select with value keyword (returns flat array)
SELECT VALUE name FROM person;

-- Select from specific record
SELECT * FROM person:tobie;

-- Select with FETCH to resolve record links
SELECT *, author.name FROM article FETCH author;

-- Select with SPLIT to unnest arrays
SELECT * FROM person SPLIT emails;

-- Select with TIMEOUT
SELECT * FROM person TIMEOUT 5s;

-- Select with PARALLEL execution
SELECT * FROM person PARALLEL;

-- Select with EXPLAIN to analyze query plan
SELECT * FROM person WHERE age > 30 EXPLAIN;
SELECT * FROM person WHERE age > 30 EXPLAIN FULL;

-- Subquery in SELECT
SELECT *, (SELECT count() FROM ->wrote->article GROUP ALL) AS article_count FROM person;
```

### UPDATE

Modifies existing records.

```surql
-- Update all records in a table
UPDATE person SET active = true;

-- Update a specific record
UPDATE person:tobie SET age = 34;

-- Merge data into a record
UPDATE person:tobie MERGE {
    settings: { theme: 'dark', lang: 'en' }
};

-- Update with CONTENT (replaces entire record)
UPDATE person:tobie CONTENT {
    name: 'Tobie',
    age: 34,
    active: true
};

-- Conditional update
UPDATE person SET verified = true WHERE age >= 18;

-- Update with RETURN clause
UPDATE person:tobie SET age = 35 RETURN DIFF;
UPDATE person:tobie SET age = 36 RETURN BEFORE;
UPDATE person:tobie SET age = 37 RETURN AFTER;

-- Increment / decrement numeric fields
UPDATE person:tobie SET age += 1;
UPDATE product:widget SET stock -= 5;

-- Append to an array
UPDATE person:tobie SET tags += 'admin';

-- Remove from an array
UPDATE person:tobie SET tags -= 'guest';
```

### DELETE

Removes records from tables.

```surql
-- Delete all records in a table
DELETE person;

-- Delete a specific record
DELETE person:tobie;

-- Conditional delete
DELETE person WHERE active = false;

-- Delete with RETURN
DELETE person:tobie RETURN BEFORE;

-- Delete with TIMEOUT
DELETE person WHERE last_login < time::now() - 1y TIMEOUT 30s;
```

### UPSERT

Creates a record if it does not exist, or updates it if it does.

```surql
-- Upsert a specific record
UPSERT person:tobie SET
    name = 'Tobie',
    age = 34,
    updated_at = time::now();

-- Upsert with CONTENT
UPSERT person:tobie CONTENT {
    name: 'Tobie',
    age: 34,
    company: 'SurrealDB'
};

-- Upsert with MERGE
UPSERT person:tobie MERGE {
    last_seen: time::now()
};
```

### INSERT

Inserts records, supporting bulk operations and ON DUPLICATE KEY UPDATE.

```surql
-- Insert a single record
INSERT INTO person {
    id: person:tobie,
    name: 'Tobie',
    age: 33
};

-- Bulk insert
INSERT INTO person [
    { name: 'Alice', age: 28 },
    { name: 'Bob', age: 35 },
    { name: 'Charlie', age: 42 }
];

-- Insert with ON DUPLICATE KEY UPDATE (upsert behavior)
INSERT INTO person {
    id: person:tobie,
    name: 'Tobie',
    age: 34
} ON DUPLICATE KEY UPDATE age = $input.age;

-- INSERT IGNORE: skip on conflict instead of error
-- (Silently ignores records that violate unique constraints)
```

### RELATE

Creates graph edges (relationships) between records.

```surql
-- Create a basic relationship
RELATE person:tobie->wrote->article:surreal;

-- Create a relationship with properties (SET syntax)
RELATE person:tobie->bought->product:laptop SET
    quantity = 1,
    price = 1299.99,
    purchased_at = time::now();

-- Create a relationship with CONTENT
RELATE person:alice->follows->person:bob CONTENT {
    since: time::now(),
    notifications: true
};

-- Relate multiple records at once
RELATE person:tobie->knows->[person:alice, person:bob, person:charlie];

-- Relate with a specific edge ID
RELATE person:tobie->wrote->article:surreal SET
    id = wrote:first_article;

-- Return the created edge
RELATE person:tobie->likes->post:123 RETURN AFTER;
```

### DEFINE NAMESPACE

Defines a namespace, the top-level organizational unit.

```surql
DEFINE NAMESPACE myapp;

-- With OVERWRITE
DEFINE NAMESPACE OVERWRITE myapp;

-- With IF NOT EXISTS
DEFINE NAMESPACE IF NOT EXISTS myapp;

-- With COMMENT
DEFINE NAMESPACE myapp COMMENT 'Production namespace';
```

### DEFINE DATABASE

Defines a database within a namespace.

```surql
DEFINE DATABASE mydb;

DEFINE DATABASE OVERWRITE mydb;

DEFINE DATABASE IF NOT EXISTS mydb;

DEFINE DATABASE mydb COMMENT 'Main application database';
```

### DEFINE TABLE

Defines a table with schema enforcement, type, permissions, and other options.

```surql
-- Schemaless table (default: any fields allowed)
DEFINE TABLE article SCHEMALESS;

-- Schemafull table (only defined fields allowed)
DEFINE TABLE person SCHEMAFULL;

-- Table with TYPE NORMAL (standard document table)
DEFINE TABLE person TYPE NORMAL SCHEMAFULL;

-- Table with TYPE ANY (can hold documents and be used as graph edges)
DEFINE TABLE flexible TYPE ANY SCHEMALESS;

-- Table with TYPE RELATION (graph edge table)
DEFINE TABLE wrote TYPE RELATION IN person OUT article;

-- Relation table with ENFORCED (strict in/out types)
DEFINE TABLE purchased TYPE RELATION IN person OUT product ENFORCED;

-- Relation table with FROM/TO syntax (aliases for IN/OUT)
DEFINE TABLE likes TYPE RELATION FROM person TO post;

-- Drop table: deletes records immediately upon write, useful for write-only audit logs
DEFINE TABLE events DROP;

-- Computed table view (auto-updated projection)
DEFINE TABLE person_by_age AS
    SELECT age, count() AS total
    FROM person
    GROUP BY age;

-- Table with changefeed
DEFINE TABLE orders CHANGEFEED 7d;

-- Table with changefeed including original data
DEFINE TABLE orders CHANGEFEED 30d INCLUDE ORIGINAL;

-- Table with permissions
DEFINE TABLE post SCHEMALESS
    PERMISSIONS
        FOR select FULL
        FOR create WHERE $auth.id != NONE
        FOR update WHERE author = $auth.id
        FOR delete WHERE author = $auth.id OR $auth.role = 'admin';

-- Table with COMMENT
DEFINE TABLE person SCHEMAFULL COMMENT 'Stores user profiles';
```

### DEFINE FIELD

Defines a field on a table with type constraints, defaults, assertions, and permissions.

```surql
-- Basic typed field
DEFINE FIELD name ON TABLE person TYPE string;

-- Numeric field
DEFINE FIELD age ON TABLE person TYPE int;

-- Optional field (can be null)
DEFINE FIELD nickname ON TABLE person TYPE option<string>;

-- Field with default value
DEFINE FIELD created_at ON TABLE person TYPE datetime DEFAULT time::now();

-- Field with VALUE (set on every create/update)
DEFINE FIELD updated_at ON TABLE person VALUE time::now();

-- Computed field (read-only, derived from other fields)
DEFINE FIELD full_name ON TABLE person VALUE string::concat(name.first, ' ', name.last);

-- READONLY field (cannot be changed after creation)
DEFINE FIELD created_at ON TABLE person TYPE datetime VALUE time::now() READONLY;

-- Field with ASSERT (validation constraint)
DEFINE FIELD email ON TABLE person TYPE string
    ASSERT string::is::email($value);

-- Field with range assertion
DEFINE FIELD age ON TABLE person TYPE int
    ASSERT $value >= 0 AND $value <= 150;

-- Record link field
DEFINE FIELD author ON TABLE article TYPE record<person>;

-- Array field with inner type
DEFINE FIELD tags ON TABLE article TYPE array<string>;

-- Set field (unique elements)
DEFINE FIELD categories ON TABLE article TYPE set<string>;

-- Nested object field
DEFINE FIELD address ON TABLE person TYPE object;
DEFINE FIELD address.street ON TABLE person TYPE string;
DEFINE FIELD address.city ON TABLE person TYPE string;
DEFINE FIELD address.zip ON TABLE person TYPE string;

-- Array of records
DEFINE FIELD reviewers ON TABLE article TYPE array<record<person>>;

-- Field with FLEXIBLE type (accepts any type, stores as-is)
DEFINE FIELD metadata ON TABLE article FLEXIBLE TYPE object;

-- Field with permissions
DEFINE FIELD email ON TABLE person TYPE string
    PERMISSIONS
        FOR select WHERE $auth.id = id OR $auth.role = 'admin'
        FOR update WHERE $auth.id = id;

-- Overwrite existing field definition
DEFINE FIELD OVERWRITE name ON TABLE person TYPE string;

-- IF NOT EXISTS
DEFINE FIELD IF NOT EXISTS name ON TABLE person TYPE string;

-- Geometry field
DEFINE FIELD location ON TABLE place TYPE geometry<point>;

-- Vector embedding field
DEFINE FIELD embedding ON TABLE document TYPE array<float> DEFAULT [];

-- Duration field
DEFINE FIELD duration ON TABLE event TYPE duration;

-- Decimal field (precise numeric)
DEFINE FIELD price ON TABLE product TYPE decimal;

-- Bytes field
DEFINE FIELD payload ON TABLE message TYPE bytes;

-- UUID field
DEFINE FIELD session_id ON TABLE session TYPE uuid;

-- Enum-like pattern using ASSERT
DEFINE FIELD status ON TABLE order TYPE string
    ASSERT $value IN ['pending', 'processing', 'shipped', 'delivered', 'cancelled'];
```

### DEFINE INDEX

Creates indexes for query optimization, uniqueness, full-text search, and vector similarity search.

```surql
-- Standard index
DEFINE INDEX age_idx ON TABLE person COLUMNS age;

-- Unique index
DEFINE INDEX email_idx ON TABLE person COLUMNS email UNIQUE;

-- Composite index
DEFINE INDEX name_age_idx ON TABLE person COLUMNS name, age;

-- Full-text search index with analyzer
DEFINE INDEX content_search ON TABLE article COLUMNS content
    SEARCH ANALYZER ascii BM25;

-- Full-text search with BM25 tuning
DEFINE INDEX content_search ON TABLE article COLUMNS content
    SEARCH ANALYZER ascii BM25(1.2, 0.75);

-- Full-text search with highlights enabled
DEFINE INDEX content_search ON TABLE article COLUMNS content
    SEARCH ANALYZER ascii BM25 HIGHLIGHTS;

-- HNSW vector index (for approximate nearest neighbor search)
DEFINE INDEX embedding_idx ON TABLE document FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE;

-- HNSW with tuning parameters
DEFINE INDEX embedding_idx ON TABLE document FIELDS embedding
    HNSW DIMENSION 3072
    DIST COSINE
    TYPE F32
    EFC 150
    M 12;

-- MTREE vector index (for exact metric space search)
DEFINE INDEX embedding_idx ON TABLE document FIELDS embedding
    MTREE DIMENSION 1536 DIST EUCLIDEAN;

-- MTREE with capacity tuning
DEFINE INDEX embedding_idx ON TABLE document FIELDS embedding
    MTREE DIMENSION 1536 DIST COSINE CAPACITY 40;

-- Overwrite existing index
DEFINE INDEX OVERWRITE email_idx ON TABLE person COLUMNS email UNIQUE;

-- Rebuild an index
REBUILD INDEX email_idx ON TABLE person;

-- Rebuild all indexes on a table
REBUILD INDEX ON TABLE person;
```

**HNSW distance metrics**: `COSINE`, `EUCLIDEAN`, `MANHATTAN`, `CHEBYSHEV`, `HAMMING`, `JACCARD`, `MINKOWSKI`, `PEARSON`.

**HNSW parameters**:
- `DIMENSION` -- Number of dimensions in the vector (required)
- `DIST` -- Distance metric (default: `COSINE`)
- `TYPE` -- Element type: `F32`, `F64`, `I16`, `I32`, `I64` (default: `F32`)
- `EFC` -- Size of dynamic candidate list during construction (default: 150)
- `M` -- Max number of connections per node per layer (default: 12)

### DEFINE ACCESS

Defines authentication and authorization access methods.

```surql
-- Record-based access (signup/signin for end users)
DEFINE ACCESS account ON DATABASE TYPE RECORD
    SIGNUP ( CREATE user SET email = $email, pass = crypto::argon2::generate($pass) )
    SIGNIN ( SELECT * FROM user WHERE email = $email AND crypto::argon2::compare(pass, $pass) )
    DURATION FOR TOKEN 15m, FOR SESSION 12h;

-- JWT access (external identity provider)
DEFINE ACCESS token_auth ON DATABASE TYPE JWT
    ALGORITHM HS256 KEY 'your-secret-key-here'
    DURATION FOR TOKEN 1h;

-- JWT with JWKS URL (for OAuth/OIDC providers)
DEFINE ACCESS oauth ON DATABASE TYPE JWT
    URL 'https://auth.example.com/.well-known/jwks.json'
    DURATION FOR TOKEN 1h, FOR SESSION 24h;

-- JWT with issuer key for token verification
DEFINE ACCESS api_auth ON NAMESPACE TYPE JWT
    ALGORITHM RS256 KEY '-----BEGIN PUBLIC KEY-----...'
    WITH ISSUER KEY '-----BEGIN PRIVATE KEY-----...';

-- Overwrite and IF NOT EXISTS
DEFINE ACCESS OVERWRITE account ON DATABASE TYPE RECORD
    SIGNUP ( CREATE user SET email = $email, pass = crypto::argon2::generate($pass) )
    SIGNIN ( SELECT * FROM user WHERE email = $email AND crypto::argon2::compare(pass, $pass) );

DEFINE ACCESS IF NOT EXISTS account ON DATABASE TYPE RECORD
    SIGNUP ( CREATE user SET email = $email, pass = crypto::argon2::generate($pass) )
    SIGNIN ( SELECT * FROM user WHERE email = $email AND crypto::argon2::compare(pass, $pass) );
```

### DEFINE ANALYZER

Defines text analyzers for full-text search indexes.

```surql
-- Basic analyzer with tokenizer and filters
DEFINE ANALYZER ascii TOKENIZERS blank, class FILTERS ascii, lowercase;

-- Snowball stemming analyzer for English
DEFINE ANALYZER english TOKENIZERS blank, class FILTERS ascii, snowball(english);

-- N-gram analyzer for autocomplete
DEFINE ANALYZER autocomplete TOKENIZERS blank FILTERS lowercase, ngram(2, 10);

-- Edge N-gram analyzer (prefix matching)
DEFINE ANALYZER prefix_search TOKENIZERS blank FILTERS lowercase, edgengram(1, 15);

-- Camel case tokenizer (splits camelCase words)
DEFINE ANALYZER code_search TOKENIZERS camel, blank FILTERS lowercase;

-- Custom multilingual analyzer
DEFINE ANALYZER multilingual TOKENIZERS blank, class FILTERS lowercase;
```

**Tokenizers**: `blank` (whitespace), `class` (character class boundaries), `camel` (camelCase split), `punct` (punctuation).

**Filters**: `ascii` (ASCII folding), `lowercase`, `uppercase`, `snowball(language)` (stemming), `ngram(min, max)`, `edgengram(min, max)`.

### DEFINE EVENT

Defines table events that trigger on record changes.

```surql
-- Event that fires on creation
DEFINE EVENT new_user ON TABLE user WHEN $event = "CREATE" THEN {
    CREATE log SET
        action = 'user_created',
        user = $after.id,
        timestamp = time::now();
};

-- Event that fires on update
DEFINE EVENT profile_change ON TABLE user WHEN $event = "UPDATE" THEN {
    CREATE audit_log SET
        table = 'user',
        record = $after.id,
        before = $before,
        after = $after,
        changed_at = time::now();
};

-- Event that fires on delete
DEFINE EVENT user_deleted ON TABLE user WHEN $event = "DELETE" THEN {
    -- Clean up related data
    DELETE session WHERE user = $before.id;
};

-- Event with conditional trigger
DEFINE EVENT stock_alert ON TABLE product
    WHEN $event = "UPDATE" AND $after.stock < 10
    THEN {
        CREATE notification SET
            type = 'low_stock',
            product = $after.id,
            stock = $after.stock;
    };

-- Event that sends HTTP webhook
DEFINE EVENT webhook ON TABLE order WHEN $event = "CREATE" THEN {
    http::post('https://hooks.example.com/orders', {
        order_id: $after.id,
        total: $after.total
    });
};
```

**Event variables**: `$event` (CREATE, UPDATE, DELETE), `$before` (record state before change), `$after` (record state after change).

### DEFINE FUNCTION

Defines reusable custom functions.

```surql
-- Simple function
DEFINE FUNCTION fn::greet($name: string) {
    RETURN string::concat('Hello, ', $name, '!');
};

-- Function with multiple parameters and return type
DEFINE FUNCTION fn::calculate_tax($amount: decimal, $rate: decimal) {
    RETURN $amount * $rate;
};

-- Function that queries the database
DEFINE FUNCTION fn::get_user_orders($user_id: record<person>) {
    RETURN SELECT * FROM order WHERE customer = $user_id ORDER BY created_at DESC;
};

-- Function with complex logic
DEFINE FUNCTION fn::full_name($person: record<person>) {
    LET $p = (SELECT name FROM ONLY $person);
    RETURN string::concat($p.name.first, ' ', $p.name.last);
};

-- Recursive-capable function
DEFINE FUNCTION fn::factorial($n: int) {
    IF $n <= 1 {
        RETURN 1;
    };
    RETURN $n * fn::factorial($n - 1);
};

-- Overwrite existing function
DEFINE FUNCTION OVERWRITE fn::greet($name: string) {
    RETURN string::concat('Hi, ', $name, '!');
};
```

### DEFINE MODULE

Defines WASM (WebAssembly) extension modules. New in SurrealDB v3. Allows extending SurrealDB with custom logic compiled to WASM.

```surql
-- Define a WASM module from a file
DEFINE MODULE my_module;

-- Modules provide custom functions that become available
-- as module::function_name() after loading
```

### DEFINE BUCKET

Defines file/object storage buckets. New in SurrealDB v3. Provides built-in file storage capabilities within SurrealDB.

```surql
-- Define a file storage bucket
DEFINE BUCKET images;

-- Define a bucket with configuration
DEFINE BUCKET documents COMMENT 'Document storage for user uploads';
```

### DEFINE USER

Defines system users with scoped access.

```surql
-- Root-level user (full system access)
DEFINE USER root_admin ON ROOT PASSWORD 'strong-password-here' ROLES OWNER;

-- Namespace-level user
DEFINE USER ns_admin ON NAMESPACE PASSWORD 'ns-password' ROLES OWNER;

-- Database-level user
DEFINE USER db_editor ON DATABASE PASSWORD 'db-password' ROLES EDITOR;

-- Database viewer
DEFINE USER db_viewer ON DATABASE PASSWORD 'viewer-password' ROLES VIEWER;

-- User with password hash (pre-hashed)
DEFINE USER admin ON ROOT PASSHASH '$argon2id$...' ROLES OWNER;

-- User with COMMENT
DEFINE USER admin ON DATABASE PASSWORD 'secret' ROLES OWNER
    COMMENT 'Primary database administrator';
```

**Roles**: `OWNER` (full access), `EDITOR` (read/write), `VIEWER` (read-only).

### DEFINE PARAM

Defines global parameters accessible across queries.

```surql
-- Define a parameter
DEFINE PARAM $app_name VALUE 'My Application';

-- Define a numeric parameter
DEFINE PARAM $max_results VALUE 100;

-- Define an object parameter
DEFINE PARAM $config VALUE {
    theme: 'dark',
    lang: 'en',
    version: 3
};

-- Use a defined parameter in queries
SELECT * FROM person LIMIT $max_results;
```

### DEFINE SEQUENCE

Defines an auto-incrementing sequence for generating sequential numeric IDs.

```surql
-- Define a sequence with defaults
DEFINE SEQUENCE order_seq;

-- Define with custom start and batch size
DEFINE SEQUENCE invoice_seq START 1000 BATCH 50;

-- Use OVERWRITE to redefine
DEFINE SEQUENCE OVERWRITE order_seq START 1 BATCH 100;

-- Use IF NOT EXISTS
DEFINE SEQUENCE IF NOT EXISTS order_seq;
```

Syntax: `DEFINE SEQUENCE [ OVERWRITE | IF NOT EXISTS ] @name [ BATCH @batch ] [ START @start ]`

### USE

Switches the active namespace and/or database.

```surql
-- Switch namespace
USE NS myapp;

-- Switch database
USE DB production;

-- Switch both
USE NS myapp DB production;
```

### INFO FOR

Returns schema information about the system, namespace, database, or table.

```surql
-- System-level info
INFO FOR ROOT;

-- Namespace-level info
INFO FOR NAMESPACE;
-- or
INFO FOR NS;

-- Database-level info
INFO FOR DATABASE;
-- or
INFO FOR DB;

-- Table-level info
INFO FOR TABLE person;
-- or
INFO FOR TABLE person STRUCTURE;
```

### LET

Binds values to variables for use in subsequent statements.

```surql
-- Bind a simple value
LET $name = 'Tobie';

-- Bind a query result
LET $adults = (SELECT * FROM person WHERE age >= 18);

-- Bind a computed value
LET $now = time::now();

-- Use variables in subsequent queries
LET $user = (CREATE person SET name = $name);
RELATE $user->wrote->article:first;
```

### BEGIN / COMMIT / CANCEL (Transactions)

Groups multiple statements into atomic transactions.

```surql
-- Basic transaction
BEGIN TRANSACTION;
    CREATE account:alice SET balance = 1000;
    CREATE account:bob SET balance = 500;
COMMIT TRANSACTION;

-- Transaction with transfer logic
BEGIN TRANSACTION;
    UPDATE account:alice SET balance -= 100;
    UPDATE account:bob SET balance += 100;
    CREATE transfer SET
        from = account:alice,
        to = account:bob,
        amount = 100,
        timestamp = time::now();
COMMIT TRANSACTION;

-- Cancel a transaction (rollback)
BEGIN TRANSACTION;
    UPDATE account:alice SET balance -= 10000;
    -- Oops, insufficient funds -- rollback
CANCEL TRANSACTION;
```

### RETURN

Returns a value from a block or function.

```surql
-- Return from a block
{
    LET $x = 10;
    LET $y = 20;
    RETURN $x + $y;
};

-- Return in function context
DEFINE FUNCTION fn::add($a: int, $b: int) {
    RETURN $a + $b;
};
```

### THROW

Throws a custom error, halting execution.

```surql
-- Throw a string error
THROW 'Something went wrong';

-- Throw conditionally
IF $balance < 0 {
    THROW 'Insufficient funds';
};

-- Throw with dynamic message
THROW string::concat('User ', $id, ' not found');
```

### SLEEP

Pauses execution for a specified duration. Primarily useful for testing.

```surql
SLEEP 1s;
SLEEP 500ms;
SLEEP 2m;
```

### IF / ELSE

Conditional branching.

```surql
-- Basic if/else
IF $age >= 18 {
    RETURN 'adult';
} ELSE {
    RETURN 'minor';
};

-- If/else if/else
IF $score >= 90 {
    RETURN 'A';
} ELSE IF $score >= 80 {
    RETURN 'B';
} ELSE IF $score >= 70 {
    RETURN 'C';
} ELSE {
    RETURN 'F';
};

-- If as an expression (inline)
LET $label = IF $active { 'Active' } ELSE { 'Inactive' };

-- If in UPDATE
UPDATE person SET status = IF age >= 18 { 'adult' } ELSE { 'minor' };
```

### FOR

Iterates over arrays or query results.

```surql
-- Iterate over an array
FOR $name IN ['Alice', 'Bob', 'Charlie'] {
    CREATE person SET name = $name;
};

-- Iterate over query results
FOR $user IN (SELECT * FROM person WHERE active = true) {
    UPDATE $user.id SET last_check = time::now();
};

-- Nested loops
FOR $i IN [1, 2, 3] {
    FOR $j IN ['a', 'b'] {
        CREATE item SET num = $i, letter = $j;
    };
};
```

### BREAK / CONTINUE

Controls loop execution flow.

```surql
-- Break out of a loop
FOR $item IN (SELECT * FROM product ORDER BY price ASC) {
    IF $item.price > 100 {
        BREAK;
    };
    UPDATE $item.id SET featured = true;
};

-- Skip iteration with CONTINUE
FOR $user IN (SELECT * FROM person) {
    IF $user.role = 'bot' {
        CONTINUE;
    };
    CREATE notification SET user = $user.id, message = 'System update';
};
```

### REMOVE

Removes schema definitions and data.

```surql
-- Remove a table and all its data
REMOVE TABLE person;

-- Remove a field definition
REMOVE FIELD email ON TABLE person;

-- Remove an index
REMOVE INDEX email_idx ON TABLE person;

-- Remove a namespace
REMOVE NAMESPACE myapp;

-- Remove a database
REMOVE DATABASE mydb;

-- Remove an event
REMOVE EVENT new_user ON TABLE user;

-- Remove a function
REMOVE FUNCTION fn::greet;

-- Remove a param
REMOVE PARAM $max_results;

-- Remove an analyzer
REMOVE ANALYZER english;

-- Remove an access method
REMOVE ACCESS account ON DATABASE;

-- Remove a user
REMOVE USER admin ON DATABASE;

-- Remove a module
REMOVE MODULE my_module;

-- Remove a bucket
REMOVE BUCKET images;
```

### REBUILD INDEX

Rebuilds indexes, useful after bulk data operations.

```surql
-- Rebuild a specific index
REBUILD INDEX email_idx ON TABLE person;

-- Rebuild all indexes on a table
REBUILD INDEX ON TABLE person;
```

### LIVE SELECT

Creates real-time subscriptions that push changes as they happen.

```surql
-- Live query on an entire table
LIVE SELECT * FROM person;

-- Live query with filtering
LIVE SELECT * FROM person WHERE age > 18;

-- Live query with DIFF (returns only changed fields)
LIVE SELECT DIFF FROM person;

-- Live query on specific fields
LIVE SELECT name, email FROM person;

-- Live query on a specific record
LIVE SELECT * FROM person:tobie;
```

Live queries return a UUID that can be used to cancel the subscription with `KILL`.

### KILL

Cancels an active live query.

```surql
-- Kill a live query by its UUID
KILL '1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d';

-- Typically used with the UUID returned by LIVE SELECT
LET $live_id = (LIVE SELECT * FROM person);
-- ... later ...
KILL $live_id;
```

### SHOW CHANGES FOR TABLE

Retrieves the change feed for a table (requires CHANGEFEED to be enabled on the table).

```surql
-- Show all changes since a timestamp
SHOW CHANGES FOR TABLE orders SINCE '2026-01-01T00:00:00Z';

-- Show limited changes
SHOW CHANGES FOR TABLE orders SINCE '2026-01-01T00:00:00Z' LIMIT 100;
```

### VERSION Clause (Time-Travel Queries)

When running on the SurrealKV storage engine, you can query historical data at a specific point in time.

```surql
-- Query data as it existed at a specific time
SELECT * FROM person VERSION d'2026-01-15T12:00:00Z';

-- Time-travel with filtering
SELECT * FROM person WHERE active = true VERSION d'2025-12-01T00:00:00Z';
```

---

## Data Types

### Primitive Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | UTF-8 text | `'hello'`, `"world"` |
| `int` | 64-bit signed integer | `42`, `-7` |
| `float` | 64-bit IEEE 754 floating point | `3.14`, `-0.5` |
| `decimal` | Arbitrary-precision decimal | `19.99dec`, `<decimal> 19.99` |
| `bool` | Boolean | `true`, `false` |
| `datetime` | ISO 8601 date and time | `d'2026-02-19T10:30:00Z'` |
| `duration` | Time duration | `1h30m`, `7d`, `500ms` |
| `bytes` | Binary data | `<bytes> "base64data"` |
| `uuid` | UUID value | `u'550e8400-e29b-41d4-a716-446655440000'` |
| `null` | Explicit null value | `null` |
| `none` | Absence of a value | `NONE` |
| `any` | Any type (no constraint) | -- |

### Complex Types

| Type | Description | Example |
|------|-------------|---------|
| `object` | Key-value map | `{ name: 'Tobie', age: 33 }` |
| `array` | Ordered list | `[1, 2, 3]` |
| `array<T>` | Typed array | `array<string>`, `array<int>` |
| `set` | Unique ordered list | -- |
| `set<T>` | Typed unique set | `set<string>` |
| `option<T>` | Nullable typed field | `option<string>` |
| `record` | Record link (any table) | `person:tobie` |
| `record<T>` | Record link (specific table) | `record<person>` |

### Geometry Types

| Type | Description |
|------|-------------|
| `geometry<point>` | GeoJSON Point |
| `geometry<line>` | GeoJSON LineString |
| `geometry<polygon>` | GeoJSON Polygon |
| `geometry<multipoint>` | GeoJSON MultiPoint |
| `geometry<multiline>` | GeoJSON MultiLineString |
| `geometry<multipolygon>` | GeoJSON MultiPolygon |
| `geometry<collection>` | GeoJSON GeometryCollection |

```surql
-- Geometry point (longitude, latitude)
CREATE place SET location = (-73.935242, 40.730610);

-- GeoJSON format
CREATE place SET location = {
    type: 'Point',
    coordinates: [-73.935242, 40.730610]
};

-- Polygon
CREATE zone SET area = {
    type: 'Polygon',
    coordinates: [[
        [-73.98, 40.75],
        [-73.97, 40.75],
        [-73.97, 40.76],
        [-73.98, 40.76],
        [-73.98, 40.75]
    ]]
};
```

### Record IDs

Record IDs are first-class citizens in SurrealDB, uniquely identifying every record.

```surql
-- String-based ID
person:tobie

-- Integer-based ID
person:100

-- UUID-based ID (auto-generated)
person:uuid()

-- ULID-based ID (time-sortable, auto-generated)
person:ulid()

-- Random ID
person:rand()

-- Complex/compound ID (using arrays or objects)
temperature:['London', d'2026-02-19T10:00:00Z']
city:[36.775, -122.4194]

-- Object-based compound ID
person:{ first: 'Tobie', last: 'Morgan' }
```

### Duration Literals

```surql
-- Duration components
1ns    -- nanoseconds
1us    -- microseconds
1ms    -- milliseconds
1s     -- seconds
1m     -- minutes
1h     -- hours
1d     -- days
1w     -- weeks
1y     -- years

-- Compound durations
1h30m
2d12h
1y6m3d
```

### Casting

Explicit type conversion using angle bracket syntax.

```surql
-- Cast to int
<int> '42'
<int> 3.14

-- Cast to float
<float> 42
<float> '3.14'

-- Cast to string
<string> 42
<string> true

-- Cast to bool
<bool> 'true'
<bool> 1

-- Cast to datetime
<datetime> '2026-02-19T10:00:00Z'

-- Cast to decimal
<decimal> 19.99
<decimal> '19.99'

-- Cast to duration
<duration> '1h30m'

-- Cast to record
<record> 'person:tobie'
```

---

## Operators

### Arithmetic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `1 + 2` returns `3` |
| `-` | Subtraction | `5 - 3` returns `2` |
| `*` | Multiplication | `4 * 3` returns `12` |
| `/` | Division | `10 / 3` returns `3` |
| `**` | Exponentiation | `2 ** 8` returns `256` |
| `%` | Modulo | `10 % 3` returns `1` |

### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals (loosely) | `1 = 1` |
| `!=` | Not equals | `1 != 2` |
| `==` | Exact equals (strict type) | `1 == 1` |
| `?=` | Any equals (for arrays) | `[1,2,3] ?= 2` |
| `*=` | All equals (for arrays) | `[1,1,1] *= 1` |
| `~` | Fuzzy match | `'hello' ~ 'helo'` |
| `!~` | Not fuzzy match | `'hello' !~ 'world'` |
| `?~` | Any fuzzy match | -- |
| `*~` | All fuzzy match | -- |
| `<` | Less than | `1 < 2` |
| `>` | Greater than | `2 > 1` |
| `<=` | Less than or equal | `1 <= 1` |
| `>=` | Greater than or equal | `2 >= 2` |

### Logical Operators

| Operator | Description |
|----------|-------------|
| `AND` / `&&` | Logical AND |
| `OR` / `\|\|` | Logical OR |
| `NOT` / `!` | Logical NOT |

### Containment Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `CONTAINS` | Value contains | `[1,2,3] CONTAINS 2` |
| `CONTAINSNOT` | Value does not contain | `[1,2,3] CONTAINSNOT 4` |
| `CONTAINSALL` | Contains all values | `[1,2,3] CONTAINSALL [1,2]` |
| `CONTAINSANY` | Contains any value | `[1,2,3] CONTAINSANY [2,4]` |
| `CONTAINSNONE` | Contains none of | `[1,2,3] CONTAINSNONE [4,5]` |

### Membership Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `IN` | Value is in | `2 IN [1,2,3]` |
| `NOT IN` | Value is not in | `4 NOT IN [1,2,3]` |
| `INSIDE` | Same as IN | `2 INSIDE [1,2,3]` |
| `NOTINSIDE` | Same as NOT IN | `4 NOTINSIDE [1,2,3]` |
| `ALLINSIDE` | All values are in | `[1,2] ALLINSIDE [1,2,3]` |
| `ANYINSIDE` | Any value is in | `[2,4] ANYINSIDE [1,2,3]` |
| `NONEINSIDE` | None of the values are in | `[4,5] NONEINSIDE [1,2,3]` |

### Pattern Matching

| Operator | Description | Example |
|----------|-------------|---------|
| `LIKE` | Wildcard pattern match | `name LIKE 'Tob%'` |
| `NOT LIKE` | Negative wildcard match | `name NOT LIKE '%bot%'` |

### Other Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `??` | Null coalescing | `$val ?? 'default'` |
| `?:` | Ternary | `$active ? 'yes' : 'no'` |
| `?.` | Optional chaining | `$user?.address?.city` |
| `..` | Range | `1..10` |

---

## Functions

### String Functions

```surql
string::concat('hello', ' ', 'world')       -- 'hello world'
string::contains('SurrealDB', 'real')        -- true
string::starts_with('SurrealDB', 'Surreal')  -- true
string::ends_with('SurrealDB', 'DB')         -- true
string::len('hello')                         -- 5
string::lowercase('HELLO')                   -- 'hello'
string::uppercase('hello')                   -- 'HELLO'
string::trim('  hello  ')                    -- 'hello'
string::trim::start('  hello  ')             -- 'hello  '
string::trim::end('  hello  ')              -- '  hello'
string::split('a,b,c', ',')                 -- ['a', 'b', 'c']
string::join(', ', 'a', 'b', 'c')           -- 'a, b, c'
string::slug('Hello World!')                 -- 'hello-world'
string::replace('hello world', 'world', 'DB') -- 'hello DB'
string::reverse('hello')                     -- 'olleh'
string::repeat('ab', 3)                      -- 'ababab'
string::slice('SurrealDB', 0, 7)             -- 'Surreal'

-- Validation functions
string::is::alphanum('abc123')               -- true
string::is::alpha('abc')                     -- true
string::is::ascii('hello')                   -- true
string::is::datetime('2026-01-01T00:00:00Z') -- true
string::is::domain('surrealdb.com')          -- true
string::is::email('tobie@surrealdb.com')     -- true
string::is::hexadecimal('ff00ab')            -- true
string::is::ip('192.168.1.1')               -- true
string::is::ipv4('192.168.1.1')             -- true
string::is::ipv6('::1')                      -- true
string::is::latitude('51.5074')              -- true
string::is::longitude('-0.1278')             -- true
string::is::numeric('12345')                 -- true
string::is::semver('1.2.3')                  -- true
string::is::url('https://surrealdb.com')     -- true
string::is::uuid('550e8400-e29b-41d4-a716-446655440000') -- true

-- Method syntax (on string values)
'hello world'.uppercase()                    -- 'HELLO WORLD'
'a,b,c'.split(',')                           -- ['a', 'b', 'c']
```

### Array Functions

```surql
array::add([1, 2], 3)                       -- [1, 2, 3] (no duplicates)
array::all([true, true, true])               -- true
array::any([false, true, false])             -- true
array::append([1, 2], 3)                     -- [1, 2, 3]
array::at([1, 2, 3], 1)                      -- 2
array::boolean_and([true, false], [true, true]) -- [true, false]
array::boolean_or([true, false], [false, true]) -- [true, true]
array::boolean_not([true, false])            -- [false, true]
array::boolean_xor([true, false], [false, true]) -- [true, true]
array::combine([1, 2], [3, 4])              -- [[1,3],[1,4],[2,3],[2,4]]
array::complement([1,2,3,4], [2,4])          -- [1, 3]
array::concat([1, 2], [3, 4])               -- [1, 2, 3, 4]
array::clump([1,2,3,4,5], 2)                -- [[1,2],[3,4],[5]]
array::difference([1,2,3], [2,3,4])          -- [1]
array::distinct([1, 2, 2, 3, 3])             -- [1, 2, 3]
array::find([1, 2, 3], 2)                    -- 2
array::find_index([1, 2, 3], 2)              -- 1
array::first([1, 2, 3])                      -- 1
array::flatten([[1, 2], [3, 4]])             -- [1, 2, 3, 4]
array::group([1,2,3,1,2])                    -- [1, 2, 3]
array::insert([1, 3], 2, 1)                  -- [1, 2, 3]
array::intersect([1,2,3], [2,3,4])           -- [2, 3]
array::join([1, 2, 3], ', ')                 -- '1, 2, 3'
array::last([1, 2, 3])                       -- 3
array::len([1, 2, 3])                        -- 3
array::logical_and([1, 0], [0, 1])           -- [0, 0]
array::logical_or([1, 0], [0, 1])            -- [1, 1]
array::logical_xor([1, 0], [0, 1])           -- [1, 1]
array::max([3, 1, 2])                        -- 3
array::min([3, 1, 2])                        -- 1
array::pop([1, 2, 3])                        -- [1, 2]
array::push([1, 2], 3)                       -- [1, 2, 3]
array::remove([1, 2, 3], 1)                  -- [1, 3]
array::reverse([1, 2, 3])                    -- [3, 2, 1]
array::shuffle([1, 2, 3])                    -- randomly shuffled
array::slice([1, 2, 3, 4], 1, 2)             -- [2, 3]
array::sort([3, 1, 2])                       -- [1, 2, 3]
array::sort::asc([3, 1, 2])                  -- [1, 2, 3]
array::sort::desc([3, 1, 2])                 -- [3, 2, 1]
array::transpose([[1,2],[3,4]])              -- [[1,3],[2,4]]
array::union([1, 2], [2, 3])                 -- [1, 2, 3]
array::windows([1,2,3,4], 2)                 -- [[1,2],[2,3],[3,4]]

-- Method syntax
[1, 2, 3].len()                              -- 3
[1, 2, 2, 3].distinct()                      -- [1, 2, 3]
[[1, 2], [3, 4]].flatten()                   -- [1, 2, 3, 4]
[3, 1, 2].sort()                             -- [1, 2, 3]
```

### Math Functions

```surql
math::abs(-42)                               -- 42
math::ceil(3.2)                              -- 4
math::floor(3.8)                             -- 3
math::round(3.5)                             -- 4
math::sqrt(16)                               -- 4.0
math::pow(2, 10)                             -- 1024
math::log(100, 10)                           -- 2.0
math::log2(8)                                -- 3.0
math::log10(1000)                            -- 3.0
math::max([1, 5, 3])                         -- 5
math::min([1, 5, 3])                         -- 1
math::mean([1, 2, 3, 4, 5])                  -- 3
math::median([1, 2, 3, 4, 5])               -- 3
math::sum([1, 2, 3, 4, 5])                   -- 15
math::product([2, 3, 4])                     -- 24
math::fixed(3.14159, 2)                      -- 3.14
math::clamp(15, 0, 10)                       -- 10
math::lerp(0, 10, 0.5)                       -- 5.0
math::spread([1, 5, 3])                      -- 4
math::variance([1, 2, 3, 4, 5])             -- 2.0
math::stddev([1, 2, 3, 4, 5])               -- ~1.414
math::nearestrank([1, 2, 3, 4, 5], 75)      -- 4
math::percentile([1, 2, 3, 4, 5], 50)       -- 3.0
math::interquartile([1, 2, 3, 4, 5])        -- 2.0
math::midhinge([1, 2, 3, 4, 5])             -- 3.0
math::trimean([1, 2, 3, 4, 5])              -- 3.0
math::mode([1, 2, 2, 3])                    -- 2
math::bottom([5, 1, 3, 2, 4], 3)            -- [1, 2, 3]
math::top([5, 1, 3, 2, 4], 3)               -- [3, 4, 5]

-- Constants
math::PI                                     -- 3.14159...
math::E                                      -- 2.71828...
math::TAU                                    -- 6.28318...
math::INF                                    -- Infinity
math::NEG_INF                                -- -Infinity
```

### Time Functions

```surql
time::now()                                  -- current UTC datetime
time::day(d'2026-02-19T10:00:00Z')          -- 19
time::hour(d'2026-02-19T10:30:00Z')         -- 10
time::minute(d'2026-02-19T10:30:00Z')       -- 30
time::second(d'2026-02-19T10:30:45Z')       -- 45
time::month(d'2026-02-19T10:00:00Z')        -- 2
time::year(d'2026-02-19T10:00:00Z')         -- 2026
time::wday(d'2026-02-19T10:00:00Z')         -- day of week (0=Sunday)
time::yday(d'2026-02-19T10:00:00Z')         -- day of year
time::week(d'2026-02-19T10:00:00Z')         -- ISO week number
time::unix(d'2026-02-19T10:00:00Z')         -- Unix timestamp (seconds)

-- Formatting
time::format(time::now(), '%Y-%m-%d')        -- '2026-02-19'

-- Grouping (truncate to period)
time::group(d'2026-02-19T10:30:45Z', 'hour') -- d'2026-02-19T10:00:00Z'
time::group(d'2026-02-19T10:30:45Z', 'day')  -- d'2026-02-19T00:00:00Z'
time::group(d'2026-02-19T10:30:45Z', 'month') -- d'2026-02-01T00:00:00Z'

-- Rounding
time::floor(d'2026-02-19T10:30:45Z', 1h)    -- d'2026-02-19T10:00:00Z'
time::ceil(d'2026-02-19T10:30:45Z', 1h)     -- d'2026-02-19T11:00:00Z'
time::round(d'2026-02-19T10:30:45Z', 1h)    -- d'2026-02-19T11:00:00Z'

-- From Unix timestamp
time::from::micros(1708344000000000)
time::from::millis(1708344000000)
time::from::nanos(1708344000000000000)
time::from::secs(1708344000)
time::from::unix(1708344000)

-- Timezone
time::timezone()                             -- server timezone
```

### Duration Functions

```surql
duration::days(90h)                          -- 3 (number of complete days)
duration::hours(2d12h)                       -- 60 (total hours)
duration::micros(1s)                         -- 1000000
duration::millis(1s)                         -- 1000
duration::mins(2h30m)                        -- 150
duration::nanos(1ms)                         -- 1000000
duration::secs(1h30m)                        -- 5400

-- From components
duration::from::days(7)                      -- 7d
duration::from::hours(24)                    -- 1d
duration::from::micros(1000000)              -- 1s
duration::from::millis(1000)                 -- 1s
duration::from::mins(60)                     -- 1h
duration::from::nanos(1000000000)            -- 1s
duration::from::secs(3600)                   -- 1h
```

### Type Functions

```surql
-- Type checking
type::is::array([1, 2])                     -- true
type::is::bool(true)                         -- true
type::is::bytes(<bytes> 'data')              -- true
type::is::datetime(time::now())              -- true
type::is::decimal(19.99dec)                  -- true
type::is::duration(1h)                       -- true
type::is::float(3.14)                        -- true
type::is::geometry((-73.9, 40.7))            -- true
type::is::int(42)                            -- true
type::is::null(null)                         -- true
type::is::none(NONE)                         -- true
type::is::number(42)                         -- true
type::is::object({ a: 1 })                  -- true
type::is::point((-73.9, 40.7))              -- true
type::is::record(person:tobie)               -- true
type::is::string('hello')                    -- true
type::is::uuid(rand::uuid())                 -- true

-- Type construction
type::thing('person', 'tobie')               -- person:tobie
type::field('name')                          -- field reference
type::fields(['name', 'age'])                -- field references
type::record('person', 'tobie')              -- person:tobie
```

### Crypto Functions

```surql
-- Hashing
crypto::md5('hello')
crypto::sha1('hello')
crypto::sha256('hello')
crypto::sha512('hello')

-- Password hashing (use for auth)
crypto::argon2::generate('MyPassword')
crypto::argon2::compare($hash, 'MyPassword')

crypto::bcrypt::generate('MyPassword')
crypto::bcrypt::compare($hash, 'MyPassword')

crypto::scrypt::generate('MyPassword')
crypto::scrypt::compare($hash, 'MyPassword')
```

### Geo Functions

```surql
-- Distance between two points (meters)
geo::distance((-0.04, 51.55), (30.46, -17.86))

-- Area of a polygon (square meters)
geo::area({
    type: 'Polygon',
    coordinates: [[
        [-73.98, 40.75], [-73.97, 40.75],
        [-73.97, 40.76], [-73.98, 40.76],
        [-73.98, 40.75]
    ]]
})

-- Bearing between two points (degrees)
geo::bearing((-0.04, 51.55), (30.46, -17.86))

-- Centroid of a geometry
geo::centroid({
    type: 'Polygon',
    coordinates: [[
        [0, 0], [10, 0], [10, 10], [0, 10], [0, 0]
    ]]
})

-- Geohash encoding/decoding
geo::hash::encode((-0.04, 51.55))              -- geohash string
geo::hash::encode((-0.04, 51.55), 6)           -- with precision
geo::hash::decode('gcpuuz')                     -- geometry point
```

### HTTP Functions

Make outbound HTTP requests (requires network capability to be enabled).

```surql
-- GET request
http::get('https://api.example.com/data')

-- GET with headers
http::get('https://api.example.com/data', {
    'Authorization': 'Bearer token123'
})

-- POST request with body
http::post('https://api.example.com/data', {
    name: 'Tobie',
    email: 'tobie@surrealdb.com'
})

-- POST with custom headers
http::post('https://api.example.com/data', { name: 'Tobie' }, {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token123'
})

-- PUT request
http::put('https://api.example.com/data/1', { name: 'Updated' })

-- PATCH request
http::patch('https://api.example.com/data/1', { age: 34 })

-- DELETE request
http::delete('https://api.example.com/data/1')

-- HEAD request
http::head('https://api.example.com/data')
```

### Meta / Record Functions

```surql
-- Extract the ID portion of a record ID
meta::id(person:tobie)                       -- 'tobie'
record::id(person:tobie)                     -- 'tobie'

-- Extract the table name from a record ID
meta::tb(person:tobie)                       -- 'person'
record::tb(person:tobie)                     -- 'person'
record::table(person:tobie)                  -- 'person'
```

### Parse Functions

```surql
-- Email parsing
parse::email::host('tobie@surrealdb.com')    -- 'surrealdb.com'
parse::email::user('tobie@surrealdb.com')    -- 'tobie'

-- URL parsing
parse::url::domain('https://surrealdb.com/docs')  -- 'surrealdb.com'
parse::url::host('https://surrealdb.com:8000')     -- 'surrealdb.com'
parse::url::path('https://surrealdb.com/docs')     -- '/docs'
parse::url::port('https://surrealdb.com:8000')     -- 8000
parse::url::query('https://example.com?a=1&b=2')   -- 'a=1&b=2'
parse::url::scheme('https://surrealdb.com')        -- 'https'
parse::url::fragment('https://example.com#section') -- 'section'
```

### Rand Functions

```surql
rand()                                       -- random float between 0 and 1
rand::bool()                                 -- random boolean
rand::enum('one', 'two', 'three')            -- random choice from values
rand::float()                                -- random float
rand::float(1.0, 100.0)                      -- random float in range
rand::guid()                                 -- random GUID string
rand::guid(20)                               -- random GUID of specific length
rand::int()                                  -- random integer
rand::int(1, 100)                            -- random integer in range
rand::string()                               -- random string
rand::string(10)                             -- random string of length
rand::string(5, 15)                          -- random string of length range
rand::time()                                 -- random datetime
rand::time(d'2020-01-01', d'2026-12-31')     -- random datetime in range
rand::uuid()                                 -- random UUID v7
rand::uuid::v4()                             -- random UUID v4
rand::uuid::v7()                             -- random UUID v7
rand::ulid()                                 -- random ULID
```

### Session Functions

```surql
session::db()                                -- current database name
session::id()                                -- current session ID
session::ip()                                -- client IP address
session::ns()                                -- current namespace name
session::origin()                            -- request origin
session::token()                             -- current auth token claims
```

### Object Functions

```surql
object::entries({ a: 1, b: 2 })             -- [['a', 1], ['b', 2]]
object::from_entries([['a', 1], ['b', 2]])   -- { a: 1, b: 2 }
object::keys({ a: 1, b: 2 })                -- ['a', 'b']
object::len({ a: 1, b: 2 })                 -- 2
object::values({ a: 1, b: 2 })              -- [1, 2]
```

### Count Function

```surql
-- Count all records
SELECT count() FROM person GROUP ALL;

-- Count with condition
SELECT count() AS total FROM person WHERE active = true GROUP ALL;

-- Count values (non-null)
count([1, null, 2, null, 3])                 -- 3
```

### Vector Functions

```surql
-- Arithmetic operations
vector::add([1, 2, 3], [4, 5, 6])           -- [5, 7, 9]
vector::subtract([4, 5, 6], [1, 2, 3])      -- [3, 3, 3]
vector::multiply([1, 2, 3], [4, 5, 6])      -- [4, 10, 18]
vector::divide([4, 10, 18], [4, 5, 6])      -- [1, 2, 3]

-- Geometric operations
vector::angle([1, 0], [0, 1])               -- angle in radians
vector::cross([1, 0, 0], [0, 1, 0])         -- [0, 0, 1]
vector::dot([1, 2, 3], [4, 5, 6])           -- 32
vector::magnitude([3, 4])                    -- 5.0
vector::normalize([3, 4])                    -- [0.6, 0.8]
vector::project([3, 4], [1, 0])             -- projection vector

-- Distance functions
vector::distance::chebyshev([1, 2], [4, 6])     -- 4
vector::distance::cosine([1, 2], [3, 4])         -- cosine distance
vector::distance::euclidean([1, 2], [4, 6])      -- 5.0
vector::distance::hamming([1, 0, 1], [1, 1, 0])  -- 2
vector::distance::manhattan([1, 2], [4, 6])      -- 7
vector::distance::jaccard([1, 2, 3], [2, 3, 4])  -- jaccard distance
vector::distance::minkowski([1, 2], [4, 6], 3)   -- minkowski with p=3
vector::distance::pearson([1, 2, 3], [4, 5, 6])  -- pearson distance

-- Similarity functions (1 - distance, higher = more similar)
vector::similarity::cosine([1, 2], [3, 4])       -- cosine similarity
vector::similarity::jaccard([1, 2, 3], [2, 3, 4]) -- jaccard similarity
vector::similarity::pearson([1, 2, 3], [4, 5, 6]) -- pearson similarity
```

### Search Functions

Used in full-text search queries with `SEARCH ANALYZER` indexes.

```surql
-- Highlight matching terms
SELECT search::highlight('<b>', '</b>', 1) AS highlighted
FROM article
WHERE content @1@ 'SurrealDB';

-- Get offsets of matching terms
SELECT search::offsets(1) AS offsets
FROM article
WHERE content @1@ 'SurrealDB';

-- Get BM25 score
SELECT search::score(1) AS score
FROM article
WHERE content @1@ 'SurrealDB'
ORDER BY score DESC;
```

The `@N@` operator is the match operator for full-text search, where `N` is the index reference number used with `search::score()`, `search::highlight()`, and `search::offsets()`.

### Value Functions

```surql
-- Compute JSON Merge Patch diff between two values
value::diff({ a: 1, b: 2 }, { a: 1, b: 3 })  -- returns diff

-- Apply a JSON Merge Patch to a value
value::patch({ a: 1, b: 2 }, [{ op: 'replace', path: '/b', value: 3 }])
```

---

## Subqueries and Expressions

### Subqueries

Any SurrealQL query can be used as a subquery within another query.

```surql
-- Subquery in WHERE clause
SELECT * FROM article
WHERE author IN (SELECT VALUE id FROM person WHERE role = 'editor');

-- Subquery in field projection
SELECT *,
    (SELECT VALUE count() FROM ->wrote->article GROUP ALL) AS article_count
FROM person;

-- Subquery in LET
LET $recent_articles = (
    SELECT * FROM article
    WHERE created_at > time::now() - 7d
    ORDER BY created_at DESC
    LIMIT 10
);
```

### Record Links

Records can directly link to other records using record IDs.

```surql
-- Create a record with a link
CREATE article SET
    title = 'Introduction to SurrealDB',
    author = person:tobie;

-- Query through the link
SELECT title, author.name FROM article;

-- Deep link traversal
SELECT title, author.company.name FROM article;
```

### Graph Traversal

Navigate graph relationships using arrow operators.

```surql
-- Forward traversal (outgoing edges)
SELECT ->wrote->article FROM person:tobie;

-- Backward traversal (incoming edges)
SELECT <-wrote<-person FROM article:surreal;

-- Multi-hop traversal
SELECT ->knows->person->wrote->article FROM person:tobie;

-- Bidirectional traversal
SELECT <->knows<->person FROM person:tobie;

-- Traversal with filtering
SELECT ->bought->product WHERE price > 100 FROM person:tobie;

-- Traversal with field selection
SELECT ->wrote->article.title FROM person:tobie;

-- Access edge properties during traversal
SELECT ->bought.quantity, ->bought->product.name FROM person:tobie;

-- Recursive traversal (ancestry)
-- Get parents
SELECT ->child_of->person FROM person:1;
-- Get grandparents
SELECT ->child_of->person->child_of->person FROM person:1;
-- All ancestors (variable depth)
SELECT ->child_of->person.* FROM person:1;
```

### Futures

Deferred computations that execute when queried.

```surql
-- Future value (recomputed on each read)
CREATE person SET
    name = 'Tobie',
    created = time::now(),
    age_display = <future> { string::concat(<string> age, ' years old') };
```

### Parameters

Variables prefixed with `$` used in queries.

```surql
-- User-defined parameters (via LET or API)
LET $name = 'Tobie';
SELECT * FROM person WHERE name = $name;

-- System parameters
$auth     -- Current authenticated user record
$session  -- Current session data
$token    -- Current JWT token claims
$before   -- Record state before event (in events/live queries)
$after    -- Record state after event (in events/live queries)
$value    -- Current field value (in ASSERT/VALUE expressions)
$this     -- Current record (in field expressions)
$parent   -- Parent record (in subqueries)
$event    -- Event type string: 'CREATE', 'UPDATE', 'DELETE' (in events)
$input    -- Input data (in ON DUPLICATE KEY UPDATE)
```

### Embedded JavaScript

SurrealDB supports inline JavaScript functions for complex logic.

```surql
-- Inline JavaScript function
CREATE person SET
    name = 'Tobie',
    name_slug = function() {
        return arguments[0].name.toLowerCase().replace(/\s+/g, '-');
    };

-- JavaScript in function definitions
DEFINE FUNCTION fn::slugify($text: string) {
    RETURN function($text) {
        return arguments[0].toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-');
    };
};
```

---

## Idioms and Patterns

### Record ID Syntax

```surql
-- Table:ID is the universal record identifier
person:tobie                 -- string ID
person:100                   -- numeric ID
person:uuid()                -- auto UUID
person:ulid()                -- auto ULID
person:rand()                -- auto random

-- Compound IDs
temperature:['London', '2026-02-19']    -- array compound key
user_session:{user: 'tobie', device: 'laptop'}  -- object compound key
```

### Destructuring and Nested Access

```surql
-- Access nested fields
SELECT name.first, name.last FROM person;

-- Access array elements
SELECT tags[0] FROM article;

-- Filter within arrays
SELECT emails[WHERE verified = true] FROM person;

-- Optional chaining for nullable fields
SELECT address?.city FROM person;
```

### Computed Table Views

```surql
-- Auto-updated aggregate view
DEFINE TABLE monthly_sales AS
    SELECT
        time::group(created_at, 'month') AS month,
        count() AS order_count,
        math::sum(total) AS revenue
    FROM order
    GROUP BY time::group(created_at, 'month');

-- Query the view like a regular table
SELECT * FROM monthly_sales ORDER BY month DESC;
```

### Changefeeds

```surql
-- Enable changefeed on a table
DEFINE TABLE orders CHANGEFEED 7d;

-- Read changes since a timestamp
SHOW CHANGES FOR TABLE orders SINCE '2026-02-01T00:00:00Z';

-- Changefeed with original data (for CDC patterns)
DEFINE TABLE orders CHANGEFEED 30d INCLUDE ORIGINAL;
```

---

## Best Practices

### SCHEMAFULL vs SCHEMALESS

- Use **SCHEMAFULL** when data integrity is paramount, for tables with well-known structures, user-facing data, and financial records. Every field must be defined before use. Provides compile-time-like safety for your data.
- Use **SCHEMALESS** for rapid prototyping, flexible metadata, log/event data, and when the schema is evolving frequently. Fields can be added without prior definition.
- Use **TYPE ANY** when a table may serve as both a normal document table and a graph edge table. Uncommon but useful in flexible schemas.
- Use **TYPE RELATION** for dedicated graph edge tables. Always specify `IN` and `OUT` types, and use `ENFORCED` to prevent edges from connecting incorrect record types.

### Transaction Patterns

```surql
-- Always wrap multi-step mutations in transactions
BEGIN TRANSACTION;
    LET $order = (CREATE order SET
        customer = $customer_id,
        total = $total,
        status = 'pending'
    );
    FOR $item IN $items {
        RELATE $order->contains->$item.product SET
            quantity = $item.qty,
            price = $item.price;
    };
    UPDATE customer:$customer_id SET last_order = time::now();
COMMIT TRANSACTION;
```

### Index Strategy

- Create indexes for fields used in `WHERE` clauses
- Use `UNIQUE` indexes for natural keys (email, username)
- Use full-text search indexes (`SEARCH ANALYZER`) for text search rather than `LIKE '%term%'`
- Use HNSW indexes for vector similarity search (faster, approximate)
- Use MTREE indexes when exact nearest-neighbor results are required
- Composite indexes should list the most selective column first
- Avoid over-indexing: each index adds write overhead
- Use `EXPLAIN` to verify index usage in queries

### Query Optimization

- Use `SELECT VALUE` when you need a flat array of single values
- Use `FETCH` to resolve record links in a single query instead of multiple round trips
- Use `LIMIT` and `START` for pagination
- Prefer `PARALLEL` for large table scans
- Use `TIMEOUT` to prevent runaway queries
- Use computed table views for frequently-accessed aggregations
- Use record links instead of JOIN-style subqueries when possible
- Pre-filter with indexes, then apply complex logic in application code when needed

### Common Pitfalls

- Record IDs are case-sensitive: `person:Tobie` and `person:tobie` are different records
- `=` is a loose comparison; use `==` for strict type-matching comparison
- `CONTENT` replaces the entire record; use `MERGE` or `SET` for partial updates
- `array::add` prevents duplicates; `array::append` does not
- Datetime literals require the `d'...'` prefix: `d'2026-01-01T00:00:00Z'`
- Duration values do not use quotes: `1h30m` not `'1h30m'`
- `NONE` and `null` are distinct: `NONE` means "field absent", `null` means "field present with null value"
- `option<T>` allows `NONE` (field absent); it does not allow arbitrary types
- `RETURN NONE` suppresses output; omitting `RETURN` returns the affected records by default
- `DELETE table` deletes all records; `REMOVE TABLE table` removes the table definition entirely
- Graph edges created with `RELATE` are themselves records in a table; they can be queried directly
- Indexes cannot be created on computed fields (enforced since v3.0.1)
- Durations can be multiplied/divided by numbers and incremented/decremented (since v3.0.1)

---

## v3.0.1 Patch Notes (2026-02-24)

Key fixes and changes in SurrealDB v3.0.1:

- **Duration arithmetic**: Durations can now be multiplied and divided by numbers, and incremented/decremented like numbers (`1h * 2` = `2h`, `30m + 15m` = `45m`)
- **Computed field index prevention**: Creating indexes on computed fields is now correctly rejected (prevents silent index corruption)
- **Record ID dereference fix**: Record IDs are now properly dereferenced when a field is computed on them
- **Error serialization fix**: Error objects are correctly serialized across all protocols
- **GraphQL string enum fix**: String enum literals now work correctly in GraphQL queries
- **Root user permission fix**: Permission check conditions for root users are now evaluated correctly
- **Parallel index compaction**: Index compaction now runs in parallel across distinct indexes (performance improvement)
- **WASM compatibility**: Improved compatibility for embedded WASM deployments
- **RouterFactory trait**: New `RouterFactory` trait exposed for embedders to compose custom HTTP routers (advanced)

### v3.1.0-alpha (in progress on main)

The main branch is tracking toward v3.1.0 with work on:
- **Non-existent record returns None** (#6978): `SELECT` on a record that does not exist now returns `NONE` instead of a confusing error. This is a behavior change from v3.0.x where `SELECT person:nonexistent` would raise an error. Code that catches errors on missing records should be updated to check for `NONE` instead.
- **Error chaining infrastructure** (#6969): Structured error chains for better debugging
- **SurrealValue derive convenience** (#6970): Simpler `#[derive(SurrealValue)]` for SDK embedders
- **wasmtime update** (#6973): Updated WASM runtime for extensions
- Code coverage for language tests
- Test fixtures for v3.0 compatibility
- Query planner deduplication and tidying
- Environment variable handling improvements
