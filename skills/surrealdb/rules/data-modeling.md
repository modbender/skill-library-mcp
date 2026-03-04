# SurrealDB Data Modeling Guide

This guide covers data modeling patterns, schema design, and best practices for SurrealDB v3. SurrealDB is a multi-model database, meaning a single deployment can serve document, graph, relational, vector, time-series, geospatial, and full-text search use cases simultaneously.

---

## Core Concepts

### Namespace / Database / Table / Record Hierarchy

SurrealDB organizes data in a four-level hierarchy:

```
Root
  └── Namespace (organizational boundary, e.g., per-tenant)
        └── Database (application boundary)
              └── Table (collection of records)
                    └── Record (individual document, identified by table:id)
```

```surql
-- Define the hierarchy
DEFINE NAMESPACE mycompany;
USE NS mycompany;

DEFINE DATABASE production;
USE DB production;

DEFINE TABLE person SCHEMAFULL;

-- Create a record (table:id is the record's unique identity)
CREATE person:tobie SET name = 'Tobie', age = 33;
```

Namespaces are useful for multi-tenancy. Databases isolate application concerns within a namespace. Tables hold records. Every record has a globally unique identifier in the form `table:id`.

### Record IDs as First-Class Citizens

In SurrealDB, every record is uniquely identified by its record ID, which combines the table name and the record's identifier. Record IDs are not opaque surrogate keys; they are meaningful, typeable, and can be used directly in queries.

```surql
-- Various record ID forms
person:tobie                              -- string-based
person:100                                -- integer-based
person:uuid()                             -- auto-generated UUID v7
person:ulid()                             -- auto-generated ULID (time-sortable)
person:rand()                             -- auto-generated random

-- Compound record IDs (encode composite keys directly in the ID)
temperature:['London', d'2026-02-19T10:00:00Z']
route:{ from: 'LAX', to: 'JFK' }

-- Record IDs ARE the foreign key system
-- No separate FK columns needed; just reference the record ID
CREATE article SET title = 'Hello', author = person:tobie;

-- Traverse the link directly
SELECT author.name FROM article;
```

Record links are not strings. They are typed references resolved by the engine. You can traverse them with dot notation, and they participate in graph queries.

### Schema Modes

SurrealDB supports three schema enforcement modes:

| Mode | Description | Use When |
|------|-------------|----------|
| `SCHEMAFULL` | Only explicitly defined fields are allowed. Attempts to set undefined fields are silently ignored. | Data integrity is critical. Well-known stable schema. |
| `SCHEMALESS` | Any field can be added without prior definition. Defined fields still enforce their types. | Rapid prototyping. Flexible or evolving schemas. |
| `TYPE ANY` | Table can hold both normal documents and serve as graph edge endpoints. | Rare. Multi-purpose tables. |
| `TYPE NORMAL` | Explicit marker for standard document tables. | Clarity in schema definitions. Default behavior. |
| `TYPE RELATION` | Dedicated graph edge table. Requires `IN` and `OUT` (or `FROM`/`TO`). | Graph relationships with enforced types. |

```surql
-- Schemafull: strict, safe, predictable
DEFINE TABLE person SCHEMAFULL;
DEFINE FIELD name ON TABLE person TYPE string;
DEFINE FIELD age ON TABLE person TYPE int;
-- Inserting an undefined field like 'foo' is silently dropped.

-- Schemaless: flexible, fast iteration
DEFINE TABLE event SCHEMALESS;
-- Any field can appear on any record, no definition needed.
-- You can still define fields for validation:
DEFINE FIELD timestamp ON TABLE event TYPE datetime DEFAULT time::now();

-- Type Relation: graph edge table with enforcement
DEFINE TABLE purchased TYPE RELATION IN person OUT product ENFORCED;
-- ENFORCED means RELATE x->purchased->y will fail
-- unless x is a person record and y is a product record.
```

---

## Document Model Patterns

### Flat Documents

The simplest pattern. Each record is a single-level key-value document.

```surql
DEFINE TABLE product SCHEMAFULL;
DEFINE FIELD name ON TABLE product TYPE string;
DEFINE FIELD sku ON TABLE product TYPE string;
DEFINE FIELD price ON TABLE product TYPE decimal;
DEFINE FIELD stock ON TABLE product TYPE int DEFAULT 0;
DEFINE FIELD active ON TABLE product TYPE bool DEFAULT true;

CREATE product:widget SET
    name = 'Widget Pro',
    sku = 'WDG-PRO-001',
    price = 29.99dec,
    stock = 150,
    active = true;
```

### Nested Objects

SurrealDB supports arbitrary nesting. Define sub-fields using dot notation.

```surql
DEFINE TABLE person SCHEMAFULL;
DEFINE FIELD name ON TABLE person TYPE object;
DEFINE FIELD name.first ON TABLE person TYPE string;
DEFINE FIELD name.last ON TABLE person TYPE string;
DEFINE FIELD address ON TABLE person TYPE object;
DEFINE FIELD address.street ON TABLE person TYPE string;
DEFINE FIELD address.city ON TABLE person TYPE string;
DEFINE FIELD address.state ON TABLE person TYPE string;
DEFINE FIELD address.zip ON TABLE person TYPE string;
DEFINE FIELD address.country ON TABLE person TYPE string DEFAULT 'US';

CREATE person:tobie CONTENT {
    name: { first: 'Tobie', last: 'Morgan Hitchcock' },
    address: {
        street: '123 Main St',
        city: 'London',
        state: 'England',
        zip: 'EC1A 1BB',
        country: 'UK'
    }
};

-- Query nested fields directly
SELECT name.first, address.city FROM person;
```

### Arrays and Sets

```surql
DEFINE TABLE article SCHEMAFULL;
DEFINE FIELD title ON TABLE article TYPE string;
DEFINE FIELD tags ON TABLE article TYPE array<string>;
DEFINE FIELD categories ON TABLE article TYPE set<string>;  -- unique elements only
DEFINE FIELD scores ON TABLE article TYPE array<int>;

CREATE article:intro SET
    title = 'Getting Started',
    tags = ['tutorial', 'beginner', 'surrealdb'],
    categories = ['docs', 'tutorial'],
    scores = [95, 87, 92];

-- Filter within arrays
SELECT tags[WHERE $value LIKE 'surreal%'] FROM article;

-- Array aggregation
SELECT math::mean(scores) AS avg_score FROM article;
```

### Optional Fields

Fields that may or may not be present use `option<T>`.

```surql
DEFINE TABLE person SCHEMAFULL;
DEFINE FIELD name ON TABLE person TYPE string;
DEFINE FIELD email ON TABLE person TYPE string;
DEFINE FIELD phone ON TABLE person TYPE option<string>;      -- may be absent
DEFINE FIELD nickname ON TABLE person TYPE option<string>;
DEFINE FIELD bio ON TABLE person TYPE option<string>;

-- phone, nickname, bio can be omitted entirely
CREATE person:alice SET name = 'Alice', email = 'alice@example.com';

-- Or explicitly set to NONE
CREATE person:bob SET
    name = 'Bob',
    email = 'bob@example.com',
    phone = NONE;
```

### Default Values

```surql
DEFINE TABLE order SCHEMAFULL;
DEFINE FIELD status ON TABLE order TYPE string DEFAULT 'pending';
DEFINE FIELD created_at ON TABLE order TYPE datetime DEFAULT time::now();
DEFINE FIELD priority ON TABLE order TYPE int DEFAULT 0;
DEFINE FIELD currency ON TABLE order TYPE string DEFAULT 'USD';

-- Defaults are applied automatically
CREATE order:1 SET total = 99.99;
-- Result: { id: order:1, total: 99.99, status: 'pending', created_at: ..., priority: 0, currency: 'USD' }
```

### Computed Fields

Fields derived from other fields. These are recalculated on every read or write.

```surql
DEFINE TABLE person SCHEMAFULL;
DEFINE FIELD name ON TABLE person TYPE object;
DEFINE FIELD name.first ON TABLE person TYPE string;
DEFINE FIELD name.last ON TABLE person TYPE string;
DEFINE FIELD full_name ON TABLE person VALUE string::concat(name.first, ' ', name.last);
DEFINE FIELD initials ON TABLE person VALUE string::concat(
    string::slice(name.first, 0, 1),
    string::slice(name.last, 0, 1)
);

DEFINE TABLE product SCHEMAFULL;
DEFINE FIELD price ON TABLE product TYPE decimal;
DEFINE FIELD tax_rate ON TABLE product TYPE decimal DEFAULT 0.08dec;
DEFINE FIELD total ON TABLE product VALUE price + (price * tax_rate);

-- READONLY computed field: cannot be set manually
DEFINE FIELD updated_at ON TABLE product VALUE time::now() READONLY;
```

### Schema Evolution Strategies

SurrealDB handles schema evolution differently than traditional RDBMS:

```surql
-- Strategy 1: Add new fields with defaults (non-breaking)
DEFINE FIELD new_field ON TABLE person TYPE option<string>;
-- Existing records automatically have new_field = NONE

-- Strategy 2: Rename via computed field (bridge period)
DEFINE FIELD display_name ON TABLE person VALUE
    IF name.full != NONE { name.full }
    ELSE { string::concat(name.first, ' ', name.last) };

-- Strategy 3: Backfill existing records
UPDATE person SET new_status = IF status = 'active' { 'enabled' } ELSE { 'disabled' };

-- Strategy 4: Use SCHEMALESS during migration, then switch to SCHEMAFULL
DEFINE TABLE OVERWRITE person SCHEMALESS;
-- ... migrate data ...
DEFINE TABLE OVERWRITE person SCHEMAFULL;

-- Strategy 5: Remove old field definition
REMOVE FIELD old_field ON TABLE person;
-- Existing data is not deleted but the field is no longer enforced
```

---

## Graph Model Patterns

### When to Use Graph Relationships vs Record Links

SurrealDB offers two ways to connect records:

**Record Links** (simple references):
- No metadata on the relationship itself
- One-directional by default
- Simpler queries with dot notation
- Use when the relationship is purely structural (e.g., `article.author`)

**Graph Edges** (via RELATE):
- Relationships are records themselves, stored in edge tables
- Can carry properties (timestamp, weight, role, etc.)
- Support bidirectional traversal with `->`, `<-`, `<->`
- Use when the relationship has meaning, attributes, or multiplicity

```surql
-- Record Link: simple, no relationship metadata
CREATE article SET title = 'Hello', author = person:tobie;
SELECT author.name FROM article;

-- Graph Edge: relationship has properties
RELATE person:tobie->wrote->article:hello SET
    published_at = time::now(),
    role = 'primary_author';
SELECT ->wrote->article FROM person:tobie;
-- Access edge properties
SELECT ->wrote.role, ->wrote->article.title FROM person:tobie;
```

### RELATE Syntax and Edge Tables

```surql
-- Define a typed edge table
DEFINE TABLE wrote TYPE RELATION IN person OUT article ENFORCED;
DEFINE FIELD published_at ON TABLE wrote TYPE datetime DEFAULT time::now();
DEFINE FIELD role ON TABLE wrote TYPE string DEFAULT 'author';

-- Create edges
RELATE person:tobie->wrote->article:surreal SET role = 'primary_author';
RELATE person:jaime->wrote->article:surreal SET role = 'co_author';

-- Edge records can be queried directly like any table
SELECT * FROM wrote;
SELECT * FROM wrote WHERE role = 'primary_author';

-- SET syntax for edge properties
RELATE person:alice->purchased->product:laptop SET
    quantity = 1,
    price = 1299.99,
    purchased_at = time::now();

-- CONTENT syntax for edge properties
RELATE person:bob->reviewed->product:laptop CONTENT {
    rating: 5,
    text: 'Excellent product',
    helpful_votes: 0
};
```

### Graph Traversal Patterns

```surql
-- Forward traversal: who did person:tobie write articles for?
SELECT ->wrote->article FROM person:tobie;

-- Backward traversal: who wrote article:surreal?
SELECT <-wrote<-person FROM article:surreal;

-- Multi-hop: find articles written by people that tobie knows
SELECT ->knows->person->wrote->article FROM person:tobie;

-- Bidirectional: all people connected to tobie via 'knows' (either direction)
SELECT <->knows<->person FROM person:tobie;

-- Filter on traversal
SELECT ->purchased->product WHERE price > 100 FROM person:tobie;

-- Select specific fields from traversed records
SELECT ->wrote->article.title AS articles FROM person:tobie;

-- Access edge properties during traversal
SELECT ->reviewed.rating, ->reviewed->product.name FROM person;

-- Count relationships
SELECT count(->wrote->article) AS article_count FROM person;

-- Traverse with conditions on intermediate edges
SELECT ->purchased[WHERE quantity > 1]->product FROM person:tobie;
```

### Recursive Graph Queries

```surql
-- Setup: family tree
CREATE person:alice, person:bob, person:charlie, person:diana;
RELATE person:bob->parent_of->person:alice;
RELATE person:charlie->parent_of->person:bob;
RELATE person:diana->parent_of->person:bob;

-- Parents (1 hop)
SELECT <-parent_of<-person AS parents FROM person:alice;

-- Grandparents (2 hops)
SELECT <-parent_of<-person<-parent_of<-person AS grandparents FROM person:alice;

-- All ancestors (chain traversals)
SELECT
    <-parent_of<-person AS parents,
    <-parent_of<-person<-parent_of<-person AS grandparents
FROM person:alice;

-- Descendants
SELECT ->parent_of->person AS children FROM person:charlie;
SELECT ->parent_of->person->parent_of->person AS grandchildren FROM person:charlie;
```

### Social Network Pattern

```surql
-- Tables
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD username ON TABLE user TYPE string;
DEFINE FIELD display_name ON TABLE user TYPE string;
DEFINE FIELD bio ON TABLE user TYPE option<string>;
DEFINE FIELD joined_at ON TABLE user TYPE datetime DEFAULT time::now();
DEFINE INDEX username_idx ON TABLE user COLUMNS username UNIQUE;

DEFINE TABLE follows TYPE RELATION IN user OUT user ENFORCED;
DEFINE FIELD created_at ON TABLE follows TYPE datetime DEFAULT time::now();

DEFINE TABLE post SCHEMAFULL;
DEFINE FIELD author ON TABLE post TYPE record<user>;
DEFINE FIELD content ON TABLE post TYPE string;
DEFINE FIELD created_at ON TABLE post TYPE datetime DEFAULT time::now();

DEFINE TABLE likes TYPE RELATION IN user OUT post ENFORCED;
DEFINE FIELD created_at ON TABLE likes TYPE datetime DEFAULT time::now();

-- Create users and relationships
CREATE user:alice SET username = 'alice', display_name = 'Alice';
CREATE user:bob SET username = 'bob', display_name = 'Bob';
RELATE user:alice->follows->user:bob;

-- Create a post
CREATE post:1 SET author = user:alice, content = 'Hello SurrealDB!';
RELATE user:bob->likes->post:1;

-- Feed query: posts from followed users, ordered by time
SELECT
    ->follows->user->wrote->post.* AS feed
FROM user:alice
ORDER BY feed.created_at DESC;

-- Alternative feed using record links
SELECT * FROM post
WHERE author IN (SELECT VALUE ->follows->user FROM user:alice)
ORDER BY created_at DESC
LIMIT 20;

-- Mutual follows
SELECT ->follows->user INTERSECT <-follows<-user AS mutual FROM user:alice;

-- Followers count
SELECT count(<-follows<-user) AS follower_count FROM user:alice;

-- Recommendations: friends of friends not already followed
SELECT ->follows->user->follows->user AS fof FROM user:alice
WHERE fof NOT IN (SELECT VALUE ->follows->user FROM user:alice)
AND fof != user:alice;
```

### Knowledge Graph Pattern

```surql
-- Entity tables
DEFINE TABLE concept SCHEMAFULL;
DEFINE FIELD name ON TABLE concept TYPE string;
DEFINE FIELD description ON TABLE concept TYPE option<string>;
DEFINE FIELD embedding ON TABLE concept TYPE array<float>;

-- Relationship edge tables
DEFINE TABLE is_a TYPE RELATION IN concept OUT concept;
DEFINE TABLE part_of TYPE RELATION IN concept OUT concept;
DEFINE TABLE related_to TYPE RELATION IN concept OUT concept;
DEFINE FIELD weight ON TABLE related_to TYPE float DEFAULT 1.0;

-- Vector index for semantic search
DEFINE INDEX concept_embedding ON TABLE concept FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE;

-- Build the knowledge graph
CREATE concept:database SET name = 'Database', description = 'A system for storing data';
CREATE concept:nosql SET name = 'NoSQL', description = 'Non-relational database';
CREATE concept:surrealdb SET name = 'SurrealDB', description = 'Multi-model database';

RELATE concept:nosql->is_a->concept:database;
RELATE concept:surrealdb->is_a->concept:nosql;

-- Traverse the ontology
SELECT ->is_a->concept.name AS parent_concepts FROM concept:surrealdb;
SELECT <-is_a<-concept.name AS child_concepts FROM concept:database;
```

### Supply Chain / Logistics Pattern

```surql
DEFINE TABLE facility SCHEMAFULL;
DEFINE FIELD name ON TABLE facility TYPE string;
DEFINE FIELD type ON TABLE facility TYPE string;  -- 'warehouse', 'factory', 'store'
DEFINE FIELD location ON TABLE facility TYPE geometry<point>;
DEFINE FIELD capacity ON TABLE facility TYPE int;

DEFINE TABLE ships_to TYPE RELATION IN facility OUT facility ENFORCED;
DEFINE FIELD transit_days ON TABLE ships_to TYPE int;
DEFINE FIELD cost_per_unit ON TABLE ships_to TYPE decimal;
DEFINE FIELD active ON TABLE ships_to TYPE bool DEFAULT true;

-- Build supply chain network
CREATE facility:factory_1 SET name = 'Main Factory', type = 'factory',
    location = (-73.9857, 40.7484), capacity = 10000;
CREATE facility:warehouse_east SET name = 'East Warehouse', type = 'warehouse',
    location = (-71.0589, 42.3601), capacity = 5000;
CREATE facility:store_nyc SET name = 'NYC Store', type = 'store',
    location = (-73.9857, 40.7484), capacity = 500;

RELATE facility:factory_1->ships_to->facility:warehouse_east SET
    transit_days = 2, cost_per_unit = 0.50dec;
RELATE facility:warehouse_east->ships_to->facility:store_nyc SET
    transit_days = 1, cost_per_unit = 0.25dec;

-- Find all facilities reachable from factory
SELECT ->ships_to->facility AS direct,
       ->ships_to->facility->ships_to->facility AS two_hop
FROM facility:factory_1;

-- Find cheapest path (manual approach)
SELECT ->ships_to.cost_per_unit AS leg1_cost,
       ->ships_to->facility->ships_to.cost_per_unit AS leg2_cost
FROM facility:factory_1;

-- Geospatial: find facilities within radius
SELECT * FROM facility
WHERE geo::distance(location, (-73.9857, 40.7484)) < 500000;
```

---

## Relational Patterns

### Foreign Key Equivalents (Record Links)

SurrealDB replaces traditional foreign keys with record links. A record link is a field whose value is a record ID, resolved automatically by the engine.

```surql
DEFINE TABLE author SCHEMAFULL;
DEFINE FIELD name ON TABLE author TYPE string;

DEFINE TABLE book SCHEMAFULL;
DEFINE FIELD title ON TABLE book TYPE string;
DEFINE FIELD author ON TABLE book TYPE record<author>;  -- typed record link

CREATE author:tolkien SET name = 'J.R.R. Tolkien';
CREATE book:lotr SET title = 'The Lord of the Rings', author = author:tolkien;

-- Automatic resolution via dot notation
SELECT title, author.name FROM book;
-- Returns: [{ title: 'The Lord of the Rings', author: { name: 'J.R.R. Tolkien' } }]

-- Or use FETCH for explicit resolution
SELECT * FROM book FETCH author;
```

### One-to-One Relationships

```surql
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD username ON TABLE user TYPE string;

DEFINE TABLE profile SCHEMAFULL;
DEFINE FIELD user ON TABLE profile TYPE record<user>;
DEFINE FIELD bio ON TABLE profile TYPE string;
DEFINE FIELD avatar_url ON TABLE profile TYPE option<string>;
DEFINE INDEX user_idx ON TABLE profile COLUMNS user UNIQUE;  -- enforces 1:1

CREATE user:alice SET username = 'alice';
CREATE profile:alice_profile SET user = user:alice, bio = 'Developer';

-- Query from user to profile
SELECT *, (SELECT * FROM profile WHERE user = $parent.id LIMIT 1) AS profile FROM user;

-- Or embed the profile directly in the user (simpler for 1:1)
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD username ON TABLE user TYPE string;
DEFINE FIELD profile ON TABLE user TYPE object;
DEFINE FIELD profile.bio ON TABLE user TYPE string;
DEFINE FIELD profile.avatar_url ON TABLE user TYPE option<string>;
```

### One-to-Many Relationships

```surql
-- Approach 1: Record link from child to parent (standard relational)
DEFINE TABLE department SCHEMAFULL;
DEFINE FIELD name ON TABLE department TYPE string;

DEFINE TABLE employee SCHEMAFULL;
DEFINE FIELD name ON TABLE employee TYPE string;
DEFINE FIELD department ON TABLE employee TYPE record<department>;

CREATE department:engineering SET name = 'Engineering';
CREATE employee:alice SET name = 'Alice', department = department:engineering;
CREATE employee:bob SET name = 'Bob', department = department:engineering;

-- Get employees in a department
SELECT * FROM employee WHERE department = department:engineering;

-- Get department with employees (subquery)
SELECT *, (SELECT * FROM employee WHERE department = $parent.id) AS employees
FROM department:engineering;

-- Approach 2: Array of record links from parent (embedded references)
DEFINE TABLE team SCHEMAFULL;
DEFINE FIELD name ON TABLE team TYPE string;
DEFINE FIELD members ON TABLE team TYPE array<record<employee>>;

CREATE team:alpha SET name = 'Alpha', members = [employee:alice, employee:bob];
SELECT members.*.name FROM team:alpha;
```

### Many-to-Many Relationships

```surql
-- Approach 1: Graph edges (preferred when relationship has properties)
DEFINE TABLE student SCHEMAFULL;
DEFINE FIELD name ON TABLE student TYPE string;

DEFINE TABLE course SCHEMAFULL;
DEFINE FIELD title ON TABLE course TYPE string;

DEFINE TABLE enrolled_in TYPE RELATION IN student OUT course ENFORCED;
DEFINE FIELD enrolled_at ON TABLE enrolled_in TYPE datetime DEFAULT time::now();
DEFINE FIELD grade ON TABLE enrolled_in TYPE option<string>;

RELATE student:alice->enrolled_in->course:math SET enrolled_at = time::now();
RELATE student:alice->enrolled_in->course:physics;
RELATE student:bob->enrolled_in->course:math;

-- Students in a course
SELECT <-enrolled_in<-student.name FROM course:math;

-- Courses for a student
SELECT ->enrolled_in->course.title FROM student:alice;

-- With edge properties
SELECT ->enrolled_in.grade, ->enrolled_in->course.title FROM student:alice;

-- Approach 2: Array of record links (simpler, no edge properties)
DEFINE TABLE article SCHEMAFULL;
DEFINE FIELD title ON TABLE article TYPE string;
DEFINE FIELD tags ON TABLE article TYPE array<record<tag>>;

DEFINE TABLE tag SCHEMAFULL;
DEFINE FIELD name ON TABLE tag TYPE string;

CREATE tag:rust SET name = 'Rust';
CREATE tag:database SET name = 'Database';
CREATE article:1 SET title = 'SurrealDB Internals', tags = [tag:rust, tag:database];

-- Articles with a specific tag
SELECT * FROM article WHERE tags CONTAINS tag:rust;
```

### Normalization vs Denormalization Trade-offs

**When to normalize (use record links / separate tables):**
- Data is updated independently (e.g., user profile changes should not require updating every order)
- Data integrity is critical (single source of truth)
- Many-to-many relationships exist
- Storage efficiency matters (avoid duplicating large objects)

**When to denormalize (embed data):**
- Data is always read together (e.g., order with line items)
- Read performance is critical and writes are infrequent
- The embedded data rarely changes
- The embedded data is specific to the parent (not shared)

```surql
-- Normalized: separate tables with record links
DEFINE TABLE order SCHEMAFULL;
DEFINE FIELD customer ON TABLE order TYPE record<customer>;
DEFINE FIELD total ON TABLE order TYPE decimal;

DEFINE TABLE order_item SCHEMAFULL;
DEFINE FIELD order ON TABLE order_item TYPE record<order>;
DEFINE FIELD product ON TABLE order_item TYPE record<product>;
DEFINE FIELD quantity ON TABLE order_item TYPE int;
DEFINE FIELD price ON TABLE order_item TYPE decimal;

-- Denormalized: embedded line items
DEFINE TABLE order SCHEMAFULL;
DEFINE FIELD customer ON TABLE order TYPE record<customer>;
DEFINE FIELD total ON TABLE order TYPE decimal;
DEFINE FIELD items ON TABLE order TYPE array<object>;
-- Each item: { product: record<product>, quantity: int, price: decimal, name: string }

CREATE order:1 CONTENT {
    customer: customer:alice,
    total: 149.97dec,
    items: [
        { product: product:widget, quantity: 3, price: 49.99dec, name: 'Widget' }
    ]
};
```

### When to Embed vs Link

| Criterion | Embed | Link |
|-----------|-------|------|
| Data read together? | Yes | Sometimes |
| Data changes independently? | No | Yes |
| Data shared across records? | No | Yes |
| Relationship has metadata? | No | Use RELATE |
| Unbounded growth? | No (keep arrays small) | Yes (separate table) |
| Needs independent queries? | No | Yes |

---

## Vector Data Patterns

### Storing Embeddings

```surql
DEFINE TABLE document SCHEMAFULL;
DEFINE FIELD title ON TABLE document TYPE string;
DEFINE FIELD content ON TABLE document TYPE string;
DEFINE FIELD embedding ON TABLE document TYPE array<float>;
DEFINE FIELD source ON TABLE document TYPE option<string>;
DEFINE FIELD created_at ON TABLE document TYPE datetime DEFAULT time::now();

-- Store a document with its embedding (e.g., from OpenAI text-embedding-3-large)
CREATE document:doc1 SET
    title = 'Introduction to SurrealDB',
    content = 'SurrealDB is a multi-model database...',
    embedding = [0.0123, -0.0456, 0.0789, ...];  -- 3072-dimensional vector
```

### HNSW Index Configuration

HNSW (Hierarchical Navigable Small World) is the recommended index for approximate nearest-neighbor vector search. It provides fast queries with tunable accuracy.

```surql
-- Basic HNSW index
DEFINE INDEX doc_embedding ON TABLE document FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE;

-- HNSW with full configuration
DEFINE INDEX doc_embedding ON TABLE document FIELDS embedding
    HNSW DIMENSION 3072    -- must match your embedding model's output dimension
    DIST COSINE            -- distance metric
    TYPE F32               -- element type (F32, F64, I16, I32, I64)
    EFC 200                -- ef_construction: higher = better recall, slower build
    M 16;                  -- max connections per layer: higher = better recall, more memory

-- Query using vector search with the <|K,EF|> operator
SELECT id, title,
    vector::similarity::cosine(embedding, $query_embedding) AS similarity
FROM document
WHERE embedding <|10,100|> $query_embedding
ORDER BY similarity DESC;
-- <|10,100|> means: return 10 nearest neighbors, using ef_search=100
```

**HNSW parameter guidance:**

| Parameter | Default | Low (fast, less accurate) | High (slower, more accurate) |
|-----------|---------|---------------------------|------------------------------|
| `EFC` | 150 | 100 | 300-500 |
| `M` | 12 | 8 | 24-48 |
| ef_search (in query) | 40 | 20 | 200-500 |

**Distance metrics**: `COSINE` (most common for text/image embeddings), `EUCLIDEAN` (L2 distance), `MANHATTAN` (L1 distance).

### MTREE Index

MTREE provides exact nearest-neighbor results (no approximation) but is slower than HNSW for large datasets.

```surql
DEFINE INDEX doc_embedding ON TABLE document FIELDS embedding
    MTREE DIMENSION 1536 DIST COSINE;

-- MTREE with capacity tuning
DEFINE INDEX doc_embedding ON TABLE document FIELDS embedding
    MTREE DIMENSION 1536 DIST EUCLIDEAN CAPACITY 40;

-- Query MTREE indexes similarly
SELECT id, title,
    vector::similarity::cosine(embedding, $query_embedding) AS similarity
FROM document
WHERE embedding <|10|> $query_embedding
ORDER BY similarity DESC;
```

### RAG (Retrieval-Augmented Generation) Pattern

```surql
-- Schema for a RAG system
DEFINE TABLE knowledge_chunk SCHEMAFULL;
DEFINE FIELD content ON TABLE knowledge_chunk TYPE string;
DEFINE FIELD embedding ON TABLE knowledge_chunk TYPE array<float>;
DEFINE FIELD source_doc ON TABLE knowledge_chunk TYPE record<source_document>;
DEFINE FIELD chunk_index ON TABLE knowledge_chunk TYPE int;
DEFINE FIELD token_count ON TABLE knowledge_chunk TYPE int;
DEFINE FIELD metadata ON TABLE knowledge_chunk FLEXIBLE TYPE object;

DEFINE TABLE source_document SCHEMAFULL;
DEFINE FIELD title ON TABLE source_document TYPE string;
DEFINE FIELD url ON TABLE source_document TYPE option<string>;
DEFINE FIELD ingested_at ON TABLE source_document TYPE datetime DEFAULT time::now();

-- Vector index for similarity search
DEFINE INDEX chunk_embedding ON TABLE knowledge_chunk FIELDS embedding
    HNSW DIMENSION 3072 DIST COSINE EFC 200 M 16;

-- Full-text index for keyword fallback
DEFINE ANALYZER english_analyzer TOKENIZERS blank, class
    FILTERS ascii, lowercase, snowball(english);
DEFINE INDEX chunk_content_ft ON TABLE knowledge_chunk COLUMNS content
    SEARCH ANALYZER english_analyzer BM25(1.2, 0.75) HIGHLIGHTS;

-- Ingest a chunk
CREATE knowledge_chunk SET
    content = 'SurrealDB supports HNSW indexes for vector similarity search...',
    embedding = $embedding_vector,
    source_doc = source_document:doc1,
    chunk_index = 0,
    token_count = 45,
    metadata = { section: 'indexes', heading: 'Vector Indexes' };

-- Semantic retrieval (vector search)
LET $query_emb = $query_embedding;
SELECT content, source_doc.title,
    vector::similarity::cosine(embedding, $query_emb) AS score
FROM knowledge_chunk
WHERE embedding <|5,150|> $query_emb
ORDER BY score DESC;
```

### Hybrid Search (Vector + Metadata Filtering)

Combine vector similarity with structured metadata filters for precise retrieval.

```surql
-- Hybrid query: semantic similarity + metadata filter
LET $query_emb = $query_embedding;

SELECT content, source_doc.title,
    vector::similarity::cosine(embedding, $query_emb) AS score
FROM knowledge_chunk
WHERE embedding <|20,200|> $query_emb
    AND metadata.section = 'security'
    AND token_count < 500
ORDER BY score DESC
LIMIT 5;

-- Hybrid: vector search + full-text search scoring
SELECT content,
    vector::similarity::cosine(embedding, $query_emb) AS vec_score,
    search::score(1) AS text_score
FROM knowledge_chunk
WHERE embedding <|20|> $query_emb
    OR content @1@ 'authentication security'
ORDER BY (vec_score * 0.7 + text_score * 0.3) DESC
LIMIT 10;
```

### Embedding Dimension Choices

| Model | Dimensions | Use Case |
|-------|-----------|----------|
| OpenAI text-embedding-3-small | 1536 | Cost-effective general purpose |
| OpenAI text-embedding-3-large | 3072 | High-accuracy retrieval |
| Cohere embed-v3 | 1024 | Multilingual search |
| BGE-large | 1024 | Open-source alternative |
| Nomic embed-text | 768 | Lightweight open-source |

Always set `DIMENSION` in the index to match your embedding model's output dimension exactly.

---

## Time-Series Patterns

### Timestamp-Ordered Records

```surql
-- Use compound record IDs for natural time-ordering
DEFINE TABLE sensor_reading SCHEMAFULL;
DEFINE FIELD sensor_id ON TABLE sensor_reading TYPE string;
DEFINE FIELD temperature ON TABLE sensor_reading TYPE float;
DEFINE FIELD humidity ON TABLE sensor_reading TYPE float;
DEFINE FIELD recorded_at ON TABLE sensor_reading TYPE datetime DEFAULT time::now();

DEFINE INDEX time_idx ON TABLE sensor_reading COLUMNS recorded_at;
DEFINE INDEX sensor_time_idx ON TABLE sensor_reading COLUMNS sensor_id, recorded_at;

-- Use compound IDs to encode time naturally
CREATE sensor_reading:['sensor_1', d'2026-02-19T10:00:00Z'] SET
    sensor_id = 'sensor_1',
    temperature = 22.5,
    humidity = 45.0;

-- Range query by time
SELECT * FROM sensor_reading
WHERE recorded_at >= d'2026-02-19T00:00:00Z'
    AND recorded_at < d'2026-02-20T00:00:00Z'
ORDER BY recorded_at ASC;

-- Latest reading per sensor
SELECT * FROM sensor_reading
WHERE sensor_id = 'sensor_1'
ORDER BY recorded_at DESC
LIMIT 1;
```

### Aggregated Views

```surql
-- Auto-aggregated hourly view
DEFINE TABLE hourly_sensor_avg AS
    SELECT
        sensor_id,
        time::group(recorded_at, 'hour') AS hour,
        math::mean(temperature) AS avg_temp,
        math::min(temperature) AS min_temp,
        math::max(temperature) AS max_temp,
        math::mean(humidity) AS avg_humidity,
        count() AS reading_count
    FROM sensor_reading
    GROUP BY sensor_id, time::group(recorded_at, 'hour');

-- Query the aggregated view
SELECT * FROM hourly_sensor_avg
WHERE sensor_id = 'sensor_1'
ORDER BY hour DESC
LIMIT 24;

-- Daily aggregation view
DEFINE TABLE daily_sensor_stats AS
    SELECT
        sensor_id,
        time::group(recorded_at, 'day') AS day,
        math::mean(temperature) AS avg_temp,
        math::stddev(temperature) AS temp_stddev,
        count() AS reading_count
    FROM sensor_reading
    GROUP BY sensor_id, time::group(recorded_at, 'day');
```

### Retention Policies

SurrealDB does not have built-in TTL. Use scheduled cleanup or the DROP table option:

```surql
-- Approach 1: Periodic cleanup
DELETE sensor_reading WHERE recorded_at < time::now() - 90d;

-- Approach 2: DROP table (records are deleted as soon as written -- write-only audit)
DEFINE TABLE ephemeral_log DROP;
-- Records vanish after being processed by events

-- Approach 3: Event-driven cleanup
DEFINE EVENT cleanup ON TABLE sensor_reading
    WHEN $event = "CREATE"
    THEN {
        DELETE sensor_reading WHERE recorded_at < time::now() - 30d LIMIT 100;
    };
```

### IoT Data Pattern

```surql
DEFINE TABLE device SCHEMAFULL;
DEFINE FIELD name ON TABLE device TYPE string;
DEFINE FIELD type ON TABLE device TYPE string;
DEFINE FIELD location ON TABLE device TYPE geometry<point>;
DEFINE FIELD status ON TABLE device TYPE string DEFAULT 'active';
DEFINE FIELD last_heartbeat ON TABLE device TYPE option<datetime>;

DEFINE TABLE telemetry SCHEMAFULL;
DEFINE FIELD device ON TABLE telemetry TYPE record<device>;
DEFINE FIELD payload ON TABLE telemetry FLEXIBLE TYPE object;
DEFINE FIELD recorded_at ON TABLE telemetry TYPE datetime DEFAULT time::now();

DEFINE INDEX telemetry_device_time ON TABLE telemetry COLUMNS device, recorded_at;

-- Event: update device heartbeat on new telemetry
DEFINE EVENT heartbeat ON TABLE telemetry WHEN $event = "CREATE" THEN {
    UPDATE $after.device SET last_heartbeat = time::now();
};

-- Ingest telemetry
CREATE telemetry SET
    device = device:sensor_42,
    payload = { temperature: 22.5, battery: 85, signal: -67 };

-- Find offline devices (no heartbeat in 5 minutes)
SELECT * FROM device
WHERE last_heartbeat < time::now() - 5m
    OR last_heartbeat IS NONE;
```

### Event Sourcing Pattern

```surql
-- Immutable event log
DEFINE TABLE account_event SCHEMAFULL;
DEFINE FIELD account ON TABLE account_event TYPE record<account>;
DEFINE FIELD type ON TABLE account_event TYPE string;
DEFINE FIELD amount ON TABLE account_event TYPE decimal;
DEFINE FIELD balance_after ON TABLE account_event TYPE decimal;
DEFINE FIELD metadata ON TABLE account_event FLEXIBLE TYPE object;
DEFINE FIELD occurred_at ON TABLE account_event TYPE datetime DEFAULT time::now();

DEFINE INDEX event_account_time ON TABLE account_event COLUMNS account, occurred_at;

-- Materialized current state
DEFINE TABLE account SCHEMAFULL;
DEFINE FIELD name ON TABLE account TYPE string;
DEFINE FIELD balance ON TABLE account TYPE decimal DEFAULT 0dec;

-- Record an event and update state in a transaction
BEGIN TRANSACTION;
    LET $acct = (SELECT * FROM ONLY account:alice);
    LET $new_balance = $acct.balance + 100dec;
    UPDATE account:alice SET balance = $new_balance;
    CREATE account_event SET
        account = account:alice,
        type = 'deposit',
        amount = 100dec,
        balance_after = $new_balance;
COMMIT TRANSACTION;

-- Replay events to reconstruct state
SELECT type, amount, balance_after, occurred_at
FROM account_event
WHERE account = account:alice
ORDER BY occurred_at ASC;
```

---

## Geospatial Patterns

### GeoJSON Storage

SurrealDB stores geospatial data as GeoJSON-compatible geometry types.

```surql
DEFINE TABLE place SCHEMAFULL;
DEFINE FIELD name ON TABLE place TYPE string;
DEFINE FIELD location ON TABLE place TYPE geometry<point>;
DEFINE FIELD boundary ON TABLE place TYPE option<geometry<polygon>>;

-- Point (longitude, latitude) -- NOTE: longitude first, per GeoJSON spec
CREATE place:nyc SET
    name = 'New York City',
    location = (-73.935242, 40.730610);

-- Full GeoJSON syntax
CREATE place:london SET
    name = 'London',
    location = {
        type: 'Point',
        coordinates: [-0.1278, 51.5074]
    };

-- Polygon
CREATE place:central_park SET
    name = 'Central Park',
    boundary = {
        type: 'Polygon',
        coordinates: [[
            [-73.981, 40.768], [-73.958, 40.800],
            [-73.949, 40.797], [-73.973, 40.764],
            [-73.981, 40.768]
        ]]
    };
```

### Proximity Queries

```surql
-- Find places within 10km of a point
SELECT * FROM place
WHERE geo::distance(location, (-73.935242, 40.730610)) < 10000;

-- Find nearest places, ordered by distance
SELECT *, geo::distance(location, (-73.935242, 40.730610)) AS distance
FROM place
ORDER BY distance ASC
LIMIT 10;

-- Find places within a bounding polygon
SELECT * FROM place
WHERE location INSIDE {
    type: 'Polygon',
    coordinates: [[
        [-74.0, 40.7], [-73.9, 40.7],
        [-73.9, 40.8], [-74.0, 40.8],
        [-74.0, 40.7]
    ]]
};
```

### Geofencing Pattern

```surql
DEFINE TABLE geofence SCHEMAFULL;
DEFINE FIELD name ON TABLE geofence TYPE string;
DEFINE FIELD boundary ON TABLE geofence TYPE geometry<polygon>;
DEFINE FIELD alert_type ON TABLE geofence TYPE string;  -- 'enter', 'exit', 'both'

DEFINE TABLE device_location SCHEMAFULL;
DEFINE FIELD device ON TABLE device_location TYPE record<device>;
DEFINE FIELD position ON TABLE device_location TYPE geometry<point>;
DEFINE FIELD timestamp ON TABLE device_location TYPE datetime DEFAULT time::now();

-- Check if a device is inside any geofence
SELECT * FROM geofence
WHERE position INSIDE boundary;

-- Event-based geofence checking
DEFINE EVENT geofence_check ON TABLE device_location
    WHEN $event = "CREATE"
    THEN {
        LET $inside = (
            SELECT id, name FROM geofence
            WHERE $after.position INSIDE boundary
        );
        IF array::len($inside) > 0 {
            CREATE geofence_alert SET
                device = $after.device,
                geofences = $inside,
                position = $after.position,
                triggered_at = time::now();
        };
    };
```

### Location-Based Service Pattern

```surql
DEFINE TABLE restaurant SCHEMAFULL;
DEFINE FIELD name ON TABLE restaurant TYPE string;
DEFINE FIELD cuisine ON TABLE restaurant TYPE string;
DEFINE FIELD location ON TABLE restaurant TYPE geometry<point>;
DEFINE FIELD rating ON TABLE restaurant TYPE float;
DEFINE FIELD price_level ON TABLE restaurant TYPE int;  -- 1-4

-- Find nearby restaurants of a specific cuisine
SELECT name, cuisine, rating,
    geo::distance(location, $user_location) AS distance
FROM restaurant
WHERE cuisine = 'Italian'
    AND geo::distance(location, $user_location) < 5000
ORDER BY rating DESC
LIMIT 20;

-- Bearing and distance for navigation
SELECT name,
    geo::distance(location, $user_location) AS distance_m,
    geo::bearing($user_location, location) AS bearing_deg
FROM restaurant
ORDER BY distance_m ASC
LIMIT 5;
```

---

## Full-Text Search Patterns

### Analyzer Configuration

Analyzers define how text is tokenized and filtered for search indexes.

```surql
-- ASCII + lowercase analyzer (good default for English)
DEFINE ANALYZER ascii_lower TOKENIZERS blank, class FILTERS ascii, lowercase;

-- English stemming analyzer (reduces words to root form)
DEFINE ANALYZER english TOKENIZERS blank, class FILTERS ascii, lowercase, snowball(english);

-- N-gram analyzer (substring matching, good for autocomplete)
DEFINE ANALYZER autocomplete TOKENIZERS blank FILTERS lowercase, ngram(2, 8);

-- Edge n-gram (prefix matching)
DEFINE ANALYZER prefix TOKENIZERS blank FILTERS lowercase, edgengram(1, 10);

-- Code search analyzer (splits camelCase and snake_case)
DEFINE ANALYZER code TOKENIZERS camel, blank, class FILTERS lowercase;

-- Minimal analyzer (full word match only)
DEFINE ANALYZER exact TOKENIZERS blank FILTERS lowercase;
```

### Search Index Creation

```surql
-- Basic search index
DEFINE INDEX article_search ON TABLE article COLUMNS title, content
    SEARCH ANALYZER ascii_lower BM25;

-- Search index with custom BM25 parameters
DEFINE INDEX article_search ON TABLE article COLUMNS content
    SEARCH ANALYZER english BM25(1.2, 0.75);

-- Search index with highlights support
DEFINE INDEX article_search ON TABLE article COLUMNS content
    SEARCH ANALYZER english BM25(1.2, 0.75) HIGHLIGHTS;

-- Separate indexes for different fields (independent scoring)
DEFINE INDEX title_search ON TABLE article COLUMNS title
    SEARCH ANALYZER english BM25;
DEFINE INDEX content_search ON TABLE article COLUMNS content
    SEARCH ANALYZER english BM25 HIGHLIGHTS;
```

### Scoring and Ranking

```surql
-- Basic search with BM25 scoring
SELECT id, title,
    search::score(1) AS relevance
FROM article
WHERE content @1@ 'SurrealDB multi-model database'
ORDER BY relevance DESC
LIMIT 10;

-- Multi-field scoring with weighted combination
SELECT id, title,
    search::score(1) AS title_score,
    search::score(2) AS content_score,
    (search::score(1) * 2.0 + search::score(2)) AS combined_score
FROM article
WHERE title @1@ 'SurrealDB' OR content @2@ 'SurrealDB'
ORDER BY combined_score DESC;

-- Highlighted results
SELECT id, title,
    search::highlight('<mark>', '</mark>', 1) AS highlighted_content,
    search::score(1) AS score
FROM article
WHERE content @1@ 'vector search'
ORDER BY score DESC;
```

### Faceted Search Pattern

```surql
-- Product search with faceted filtering
DEFINE TABLE product SCHEMAFULL;
DEFINE FIELD name ON TABLE product TYPE string;
DEFINE FIELD description ON TABLE product TYPE string;
DEFINE FIELD category ON TABLE product TYPE string;
DEFINE FIELD brand ON TABLE product TYPE string;
DEFINE FIELD price ON TABLE product TYPE decimal;
DEFINE FIELD in_stock ON TABLE product TYPE bool;

DEFINE ANALYZER product_search TOKENIZERS blank, class FILTERS ascii, lowercase, snowball(english);
DEFINE INDEX product_name_ft ON TABLE product COLUMNS name SEARCH ANALYZER product_search BM25;
DEFINE INDEX product_desc_ft ON TABLE product COLUMNS description SEARCH ANALYZER product_search BM25 HIGHLIGHTS;

-- Faceted search: text search + structured filters
SELECT id, name, price, category, brand,
    search::score(1) AS relevance
FROM product
WHERE description @1@ 'wireless bluetooth headphones'
    AND category = 'electronics'
    AND price >= 50 AND price <= 200
    AND in_stock = true
ORDER BY relevance DESC
LIMIT 20;

-- Category facet counts after search
SELECT category, count() AS count
FROM product
WHERE description @1@ 'wireless bluetooth headphones'
GROUP BY category
ORDER BY count DESC;
```

### Multilingual Search

```surql
-- Per-language analyzers
DEFINE ANALYZER english_search TOKENIZERS blank, class FILTERS ascii, lowercase, snowball(english);
DEFINE ANALYZER french_search TOKENIZERS blank, class FILTERS ascii, lowercase, snowball(french);
DEFINE ANALYZER german_search TOKENIZERS blank, class FILTERS ascii, lowercase, snowball(german);

-- Multi-language content table
DEFINE TABLE content SCHEMAFULL;
DEFINE FIELD title ON TABLE content TYPE string;
DEFINE FIELD body_en ON TABLE content TYPE option<string>;
DEFINE FIELD body_fr ON TABLE content TYPE option<string>;
DEFINE FIELD body_de ON TABLE content TYPE option<string>;
DEFINE FIELD language ON TABLE content TYPE string;

-- Per-language search indexes
DEFINE INDEX content_en_ft ON TABLE content COLUMNS body_en SEARCH ANALYZER english_search BM25;
DEFINE INDEX content_fr_ft ON TABLE content COLUMNS body_fr SEARCH ANALYZER french_search BM25;
DEFINE INDEX content_de_ft ON TABLE content COLUMNS body_de SEARCH ANALYZER german_search BM25;

-- Search in a specific language
SELECT * FROM content WHERE body_en @1@ 'database performance' ORDER BY search::score(1) DESC;
SELECT * FROM content WHERE body_fr @1@ 'performance de base de donnees' ORDER BY search::score(1) DESC;
```

---

## Multi-Model Combinations

### Document + Graph (Social Network with Rich Profiles)

```surql
-- Rich user profiles (document model)
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD username ON TABLE user TYPE string;
DEFINE FIELD profile ON TABLE user TYPE object;
DEFINE FIELD profile.display_name ON TABLE user TYPE string;
DEFINE FIELD profile.bio ON TABLE user TYPE option<string>;
DEFINE FIELD profile.interests ON TABLE user TYPE array<string>;
DEFINE FIELD profile.location ON TABLE user TYPE option<geometry<point>>;
DEFINE FIELD joined_at ON TABLE user TYPE datetime DEFAULT time::now();

-- Graph relationships
DEFINE TABLE follows TYPE RELATION IN user OUT user ENFORCED;
DEFINE TABLE blocked TYPE RELATION IN user OUT user ENFORCED;
DEFINE TABLE member_of TYPE RELATION IN user OUT group ENFORCED;
DEFINE FIELD role ON TABLE member_of TYPE string DEFAULT 'member';

-- Query: nearby users with shared interests, excluding blocked
LET $me = user:alice;
LET $my_interests = (SELECT VALUE profile.interests FROM ONLY $me);
LET $my_blocked = (SELECT VALUE ->blocked->user FROM ONLY $me);

SELECT username, profile.display_name, profile.interests,
    geo::distance(profile.location, $my_location) AS distance
FROM user
WHERE id != $me
    AND id NOT IN $my_blocked
    AND profile.interests CONTAINSANY $my_interests
    AND geo::distance(profile.location, $my_location) < 50000
ORDER BY distance ASC
LIMIT 20;
```

### Vector + Document (Semantic Search Over Structured Data)

```surql
-- Products with embeddings for semantic search
DEFINE TABLE product SCHEMAFULL;
DEFINE FIELD name ON TABLE product TYPE string;
DEFINE FIELD description ON TABLE product TYPE string;
DEFINE FIELD category ON TABLE product TYPE string;
DEFINE FIELD price ON TABLE product TYPE decimal;
DEFINE FIELD embedding ON TABLE product TYPE array<float>;

DEFINE INDEX product_vec ON TABLE product FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE;
DEFINE INDEX product_category ON TABLE product COLUMNS category;

-- Semantic search: "comfortable office chair under $500"
LET $query_emb = $embedding_for_query;
SELECT name, description, price, category,
    vector::similarity::cosine(embedding, $query_emb) AS relevance
FROM product
WHERE embedding <|20|> $query_emb
    AND category = 'furniture'
    AND price <= 500
ORDER BY relevance DESC
LIMIT 10;
```

### Graph + Vector (Knowledge Graph with Embeddings)

```surql
-- Concepts with embeddings and graph relationships
DEFINE TABLE concept SCHEMAFULL;
DEFINE FIELD name ON TABLE concept TYPE string;
DEFINE FIELD description ON TABLE concept TYPE string;
DEFINE FIELD embedding ON TABLE concept TYPE array<float>;

DEFINE INDEX concept_vec ON TABLE concept FIELDS embedding
    HNSW DIMENSION 768 DIST COSINE;

DEFINE TABLE related_to TYPE RELATION IN concept OUT concept;
DEFINE FIELD weight ON TABLE related_to TYPE float DEFAULT 1.0;
DEFINE FIELD relation_type ON TABLE related_to TYPE string;

-- Find semantically similar concepts, then explore graph neighbors
LET $similar = (
    SELECT id, name,
        vector::similarity::cosine(embedding, $query_emb) AS score
    FROM concept
    WHERE embedding <|5|> $query_emb
    ORDER BY score DESC
);

-- For each similar concept, get graph neighbors
SELECT name,
    ->related_to->concept.name AS related,
    <-related_to<-concept.name AS referenced_by
FROM $similar;
```

### Time-Series + Geospatial (Fleet Tracking)

```surql
DEFINE TABLE vehicle SCHEMAFULL;
DEFINE FIELD name ON TABLE vehicle TYPE string;
DEFINE FIELD type ON TABLE vehicle TYPE string;
DEFINE FIELD status ON TABLE vehicle TYPE string DEFAULT 'active';

DEFINE TABLE position SCHEMAFULL;
DEFINE FIELD vehicle ON TABLE position TYPE record<vehicle>;
DEFINE FIELD location ON TABLE position TYPE geometry<point>;
DEFINE FIELD speed ON TABLE position TYPE float;
DEFINE FIELD heading ON TABLE position TYPE float;
DEFINE FIELD recorded_at ON TABLE position TYPE datetime DEFAULT time::now();

DEFINE INDEX pos_vehicle_time ON TABLE position COLUMNS vehicle, recorded_at;

-- Live tracking: event to update vehicle's current location
DEFINE EVENT update_vehicle_pos ON TABLE position WHEN $event = "CREATE" THEN {
    UPDATE $after.vehicle SET
        current_location = $after.location,
        current_speed = $after.speed,
        last_seen = $after.recorded_at;
};

-- Find vehicles near a location
SELECT *, geo::distance(current_location, $center) AS distance
FROM vehicle
WHERE status = 'active'
    AND geo::distance(current_location, $center) < 10000
ORDER BY distance ASC;

-- Historical route for a vehicle
SELECT location, speed, recorded_at
FROM position
WHERE vehicle = vehicle:truck_1
    AND recorded_at >= d'2026-02-19T00:00:00Z'
    AND recorded_at < d'2026-02-20T00:00:00Z'
ORDER BY recorded_at ASC;
```

### Full-Text + Document (Content Management)

```surql
DEFINE TABLE article SCHEMAFULL;
DEFINE FIELD title ON TABLE article TYPE string;
DEFINE FIELD slug ON TABLE article TYPE string;
DEFINE FIELD content ON TABLE article TYPE string;
DEFINE FIELD author ON TABLE article TYPE record<user>;
DEFINE FIELD tags ON TABLE article TYPE array<string>;
DEFINE FIELD status ON TABLE article TYPE string DEFAULT 'draft';
DEFINE FIELD published_at ON TABLE article TYPE option<datetime>;
DEFINE FIELD views ON TABLE article TYPE int DEFAULT 0;

DEFINE ANALYZER content_analyzer TOKENIZERS blank, class
    FILTERS ascii, lowercase, snowball(english);

DEFINE INDEX article_title_ft ON TABLE article COLUMNS title
    SEARCH ANALYZER content_analyzer BM25;
DEFINE INDEX article_content_ft ON TABLE article COLUMNS content
    SEARCH ANALYZER content_analyzer BM25 HIGHLIGHTS;
DEFINE INDEX article_slug ON TABLE article COLUMNS slug UNIQUE;
DEFINE INDEX article_status ON TABLE article COLUMNS status;

-- Full-text search on published articles
SELECT id, title, slug,
    search::highlight('<b>', '</b>', 1) AS excerpt,
    search::score(1) AS relevance,
    author.name AS author_name,
    tags, published_at, views
FROM article
WHERE content @1@ 'vector database performance'
    AND status = 'published'
ORDER BY relevance DESC
LIMIT 10;

-- Related articles by shared tags
SELECT * FROM article
WHERE tags CONTAINSANY (SELECT VALUE tags FROM ONLY article:current)
    AND id != article:current
    AND status = 'published'
ORDER BY published_at DESC
LIMIT 5;
```

---

## Schema Design Best Practices

### Naming Conventions

- **Tables**: lowercase singular nouns (`person`, `article`, `order`)
- **Edge tables**: lowercase verb phrases (`wrote`, `purchased`, `follows`, `enrolled_in`)
- **Fields**: lowercase snake_case (`first_name`, `created_at`, `order_total`)
- **Indexes**: descriptive names with suffix pattern (`email_idx`, `name_search_ft`, `embedding_vec`)
- **Analyzers**: descriptive names (`english`, `autocomplete`, `code_search`)
- **Functions**: namespaced with `fn::` prefix (`fn::calculate_tax`, `fn::full_name`)
- **Parameters**: `$` prefix, lowercase snake_case (`$max_results`, `$app_name`)

### Record ID Strategies

| Strategy | Example | Use When |
|----------|---------|----------|
| Auto UUID | `person:uuid()` | General purpose, globally unique, no coordination needed |
| Auto ULID | `person:ulid()` | Need time-sortable IDs, useful for time-ordered data |
| Auto random | `person:rand()` | Simple random IDs, no time ordering needed |
| Meaningful string | `person:tobie` | Natural keys exist (usernames, slugs, codes) |
| Integer | `person:100` | Sequential data, legacy system compatibility |
| Compound array | `reading:['sensor_1', d'2026-02-19']` | Composite natural keys (sensor+time, route segments) |
| Compound object | `config:{ env: 'prod', key: 'db_url' }` | Named composite keys |

Best practice: prefer `uuid()` or `ulid()` for most tables. Use meaningful string IDs only when a natural key exists and is stable.

### Access Control Design

```surql
-- Layered access control pattern

-- 1. System users for service-to-service auth
DEFINE USER api_service ON DATABASE PASSWORD 'strong-service-password' ROLES EDITOR;

-- 2. Record access for end-user authentication
DEFINE ACCESS user_auth ON DATABASE TYPE RECORD
    SIGNUP (
        CREATE user SET
            email = $email,
            pass = crypto::argon2::generate($pass),
            role = 'user',
            created_at = time::now()
    )
    SIGNIN (
        SELECT * FROM user
        WHERE email = $email
            AND crypto::argon2::compare(pass, $pass)
    )
    DURATION FOR TOKEN 15m, FOR SESSION 24h;

-- 3. Table-level permissions based on auth context
DEFINE TABLE post SCHEMALESS
    PERMISSIONS
        FOR select FULL
        FOR create WHERE $auth.id != NONE
        FOR update WHERE author = $auth.id
        FOR delete WHERE author = $auth.id OR $auth.role = 'admin';

DEFINE TABLE user SCHEMAFULL
    PERMISSIONS
        FOR select WHERE id = $auth.id OR $auth.role = 'admin'
        FOR update WHERE id = $auth.id
        FOR delete WHERE $auth.role = 'admin';

-- 4. Field-level permissions for sensitive data
DEFINE FIELD email ON TABLE user TYPE string
    PERMISSIONS
        FOR select WHERE id = $auth.id OR $auth.role = 'admin';

DEFINE FIELD pass ON TABLE user TYPE string
    PERMISSIONS
        FOR select NONE;  -- never expose password hash
```

### Anti-Patterns to Avoid

**1. Storing record IDs as strings instead of record links**
```surql
-- BAD: string reference
DEFINE FIELD author ON TABLE article TYPE string;
CREATE article SET author = 'person:tobie';  -- string, not a link

-- GOOD: typed record link
DEFINE FIELD author ON TABLE article TYPE record<person>;
CREATE article SET author = person:tobie;  -- actual record reference
```

**2. Over-nesting instead of using separate tables**
```surql
-- BAD: deeply nested orders within user records
CREATE user SET orders = [
    { items: [...], total: 99.99, ... },
    { items: [...], total: 149.99, ... }
];
-- Cannot query orders independently, unbounded array growth

-- GOOD: separate order table with record link
CREATE order SET customer = user:alice, total = 99.99;
```

**3. Using RELATE for simple references**
```surql
-- BAD: graph edge for a simple belongs-to relationship
RELATE article:1->written_by->person:tobie;

-- GOOD: record link (no edge metadata needed)
CREATE article:1 SET author = person:tobie;

-- GOOD: graph edge when the relationship has properties
RELATE person:tobie->wrote->article:1 SET role = 'primary', drafted_at = time::now();
```

**4. Missing indexes on filtered fields**
```surql
-- BAD: no index on frequently filtered field
SELECT * FROM user WHERE email = 'alice@example.com';  -- full table scan

-- GOOD: index on the field
DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;
```

**5. Using CONTENT when you mean MERGE**
```surql
-- BAD: CONTENT replaces the entire record
UPDATE person:tobie CONTENT { age: 34 };
-- Result: all other fields are gone

-- GOOD: SET or MERGE for partial updates
UPDATE person:tobie SET age = 34;
UPDATE person:tobie MERGE { age: 34 };
```

**6. Unbounded arrays**
```surql
-- BAD: comments stored in article array (can grow to millions)
DEFINE FIELD comments ON TABLE article TYPE array<object>;

-- GOOD: separate table with record link
DEFINE TABLE comment SCHEMAFULL;
DEFINE FIELD article ON TABLE comment TYPE record<article>;
DEFINE FIELD text ON TABLE comment TYPE string;
```

---

## Migration from Other Databases

### From PostgreSQL (Relational Mapping)

| PostgreSQL | SurrealDB |
|------------|-----------|
| Schema | Namespace + Database |
| Table | Table (SCHEMAFULL) |
| Row | Record |
| Primary key | Record ID (`table:id`) |
| Foreign key | Record link (`TYPE record<table>`) |
| JOIN | Record link traversal (dot notation) or subquery |
| Serial/sequence | `uuid()`, `ulid()`, or DEFINE SEQUENCE |
| ENUM | `ASSERT $value IN [...]` |
| JSON/JSONB column | Nested object fields or FLEXIBLE TYPE object |
| INDEX | DEFINE INDEX |
| VIEW | DEFINE TABLE ... AS SELECT |
| TRIGGER | DEFINE EVENT |
| FUNCTION | DEFINE FUNCTION |
| Row-level security | Table/field PERMISSIONS |

```surql
-- PostgreSQL:
-- CREATE TABLE users (
--   id SERIAL PRIMARY KEY,
--   email VARCHAR(255) UNIQUE NOT NULL,
--   name VARCHAR(100) NOT NULL,
--   created_at TIMESTAMP DEFAULT NOW()
-- );
-- CREATE TABLE posts (
--   id SERIAL PRIMARY KEY,
--   author_id INTEGER REFERENCES users(id),
--   title VARCHAR(255) NOT NULL,
--   body TEXT
-- );

-- SurrealDB equivalent:
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD email ON TABLE user TYPE string ASSERT string::is::email($value);
DEFINE FIELD name ON TABLE user TYPE string;
DEFINE FIELD created_at ON TABLE user TYPE datetime DEFAULT time::now();
DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;

DEFINE TABLE post SCHEMAFULL;
DEFINE FIELD author ON TABLE post TYPE record<user>;
DEFINE FIELD title ON TABLE post TYPE string;
DEFINE FIELD body ON TABLE post TYPE option<string>;

-- PostgreSQL JOIN:
-- SELECT p.title, u.name FROM posts p JOIN users u ON p.author_id = u.id;

-- SurrealDB:
SELECT title, author.name FROM post;
```

### From MongoDB (Document Mapping)

| MongoDB | SurrealDB |
|---------|-----------|
| Database | Database |
| Collection | Table (SCHEMALESS) |
| Document | Record |
| `_id` (ObjectId) | Record ID (`table:id`) |
| Embedded document | Nested object |
| DBRef / manual reference | Record link (`TYPE record<table>`) |
| Aggregation pipeline | SELECT with GROUP BY, subqueries |
| Change streams | LIVE SELECT, CHANGEFEED |
| Atlas Search | DEFINE INDEX ... SEARCH ANALYZER |
| Atlas Vector Search | DEFINE INDEX ... HNSW |

```surql
-- MongoDB:
-- db.users.insertOne({
--   name: { first: "Tobie", last: "Morgan" },
--   email: "tobie@surrealdb.com",
--   tags: ["admin", "developer"],
--   address: { city: "London", country: "UK" }
-- });

-- SurrealDB (schemaless, closest to MongoDB):
DEFINE TABLE user SCHEMALESS;
CREATE user SET
    name = { first: 'Tobie', last: 'Morgan' },
    email = 'tobie@surrealdb.com',
    tags = ['admin', 'developer'],
    address = { city: 'London', country: 'UK' };

-- MongoDB $lookup (JOIN equivalent):
-- db.orders.aggregate([{ $lookup: { from: "users", localField: "userId", ... } }])

-- SurrealDB: just use record links
SELECT *, customer.name FROM order FETCH customer;
```

### From Neo4j (Graph Mapping)

| Neo4j | SurrealDB |
|-------|-----------|
| Node | Record (in a table) |
| Node label | Table name |
| Relationship | Edge record (via RELATE) |
| Relationship type | Edge table name |
| `MATCH (n:Person)` | `SELECT * FROM person` |
| `CREATE (n:Person)` | `CREATE person SET ...` |
| `MATCH (a)-[:KNOWS]->(b)` | `SELECT ->knows->person FROM person:a` |
| `(a)-[:KNOWS*1..3]->(b)` | Chain traversals: `->knows->person->knows->person...` |
| Cypher | SurrealQL |
| APOC | DEFINE FUNCTION + built-in functions |

```surql
-- Neo4j Cypher:
-- CREATE (alice:Person {name: 'Alice'})-[:KNOWS {since: 2020}]->(bob:Person {name: 'Bob'})

-- SurrealDB:
CREATE person:alice SET name = 'Alice';
CREATE person:bob SET name = 'Bob';
RELATE person:alice->knows->person:bob SET since = 2020;

-- Neo4j:
-- MATCH (p:Person {name: 'Alice'})-[:KNOWS]->(friend)-[:KNOWS]->(fof)
-- RETURN fof.name

-- SurrealDB:
SELECT ->knows->person->knows->person.name AS friends_of_friends
FROM person:alice;

-- Neo4j:
-- MATCH (p:Person)-[r:KNOWS]->(other) WHERE r.since > 2019 RETURN p, other

-- SurrealDB:
SELECT <-knows[WHERE since > 2019]<-person AS recent_connections
FROM person;
```

### From Redis (Caching Patterns)

| Redis | SurrealDB |
|-------|-----------|
| SET key value | `CREATE cache:key SET value = ...` |
| GET key | `SELECT value FROM ONLY cache:key` |
| HSET | Nested object fields |
| LPUSH/RPUSH | Array fields with `array::push` |
| EXPIRE | No native TTL; use DELETE with time conditions |
| PUB/SUB | LIVE SELECT |

```surql
-- Key-value cache pattern
DEFINE TABLE cache SCHEMALESS;
DEFINE FIELD value ON TABLE cache FLEXIBLE TYPE any;
DEFINE FIELD expires_at ON TABLE cache TYPE option<datetime>;

-- Set a cache entry
UPSERT cache:session_abc123 SET
    value = { user_id: 'alice', role: 'admin' },
    expires_at = time::now() + 1h;

-- Get a cache entry (with expiration check)
SELECT value FROM ONLY cache:session_abc123
WHERE expires_at > time::now() OR expires_at IS NONE;

-- Periodic cleanup
DELETE cache WHERE expires_at < time::now();

-- Pub/Sub via LIVE SELECT
LIVE SELECT * FROM cache;
```

### From Elasticsearch (Search Mapping)

| Elasticsearch | SurrealDB |
|---------------|-----------|
| Index | Table |
| Document | Record |
| Mapping | DEFINE FIELD + DEFINE INDEX |
| Analyzer | DEFINE ANALYZER |
| Full-text query | `WHERE field @N@ 'query'` |
| Highlighting | `search::highlight()` |
| Score | `search::score()` |
| Aggregation | SELECT ... GROUP BY |

```surql
-- Elasticsearch-style search schema
DEFINE TABLE article SCHEMAFULL;
DEFINE FIELD title ON TABLE article TYPE string;
DEFINE FIELD body ON TABLE article TYPE string;
DEFINE FIELD author ON TABLE article TYPE string;
DEFINE FIELD published_at ON TABLE article TYPE datetime;
DEFINE FIELD tags ON TABLE article TYPE array<string>;

DEFINE ANALYZER article_analyzer TOKENIZERS blank, class
    FILTERS ascii, lowercase, snowball(english);
DEFINE INDEX title_ft ON TABLE article COLUMNS title SEARCH ANALYZER article_analyzer BM25;
DEFINE INDEX body_ft ON TABLE article COLUMNS body SEARCH ANALYZER article_analyzer BM25 HIGHLIGHTS;

-- Elasticsearch: { "query": { "match": { "body": "vector search" } } }
-- SurrealDB:
SELECT title,
    search::highlight('<em>', '</em>', 1) AS snippet,
    search::score(1) AS score
FROM article
WHERE body @1@ 'vector search'
ORDER BY score DESC
LIMIT 10;

-- Elasticsearch aggregation equivalent
SELECT tags, count() AS doc_count
FROM article
WHERE body @1@ 'vector search'
SPLIT tags
GROUP BY tags
ORDER BY doc_count DESC;
```

### From Pinecone/Weaviate (Vector Mapping)

| Vector DB | SurrealDB |
|-----------|-----------|
| Collection/Index | Table + HNSW/MTREE index |
| Vector + metadata | Record with embedding field + other fields |
| Upsert | UPSERT |
| Query (top-K) | `WHERE embedding <\|K\|> $query_vec` |
| Metadata filter | Standard WHERE clauses |
| Namespace | Namespace or Database |

```surql
-- Pinecone-style vector store
DEFINE TABLE vectors SCHEMAFULL;
DEFINE FIELD embedding ON TABLE vectors TYPE array<float>;
DEFINE FIELD metadata ON TABLE vectors FLEXIBLE TYPE object;
DEFINE FIELD text ON TABLE vectors TYPE option<string>;

DEFINE INDEX vec_idx ON TABLE vectors FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE EFC 200 M 16;

-- Pinecone: index.upsert([("id1", [0.1, 0.2, ...], {"category": "tech"})])
-- SurrealDB:
UPSERT vectors:id1 SET
    embedding = [0.1, 0.2, ...],
    metadata = { category: 'tech' },
    text = 'Original text content';

-- Pinecone: index.query(vector=[0.1, ...], top_k=5, filter={"category": "tech"})
-- SurrealDB:
SELECT id, text, metadata,
    vector::similarity::cosine(embedding, $query_vec) AS score
FROM vectors
WHERE embedding <|5|> $query_vec
    AND metadata.category = 'tech'
ORDER BY score DESC;
```

---

## Summary

SurrealDB's multi-model architecture means you choose the right model for each part of your application rather than forcing everything into a single paradigm. The key guidelines are:

1. **Start with your access patterns.** Design your schema around how you query data, not how you store it.
2. **Use record links for structural references** and graph edges for relationships with properties.
3. **Use SCHEMAFULL for core business data** and SCHEMALESS for flexible or evolving data.
4. **Combine models freely.** A single table can have vector indexes, full-text search, and participate in graph traversals.
5. **Index strategically.** Create indexes for fields in WHERE clauses, but avoid over-indexing.
6. **Leverage computed table views** for frequently-accessed aggregations instead of running expensive queries repeatedly.
7. **Use transactions** for multi-step mutations that must be atomic.
8. **Use compound record IDs** to encode natural composite keys directly in the record identifier.
