# SurrealDB Graph Queries

SurrealDB is a multi-model database with first-class graph capabilities. Unlike bolt-on graph layers, SurrealDB treats records as nodes and edge tables as typed, queryable relationships. Graph traversal uses arrow syntax (`->`, `<-`, `<->`) directly in SurrealQL, enabling complex relationship queries without separate graph query languages.

---

## RELATE Statement

The `RELATE` statement creates graph edges (relationships) between records. Each relationship is stored in an edge table with automatic `in` and `out` fields pointing to the source and target records.

### Basic Syntax

```surrealql
-- General form
RELATE @from->@edge->@to [SET | CONTENT | MERGE ...];

-- Create a simple relationship
RELATE person:alice->knows->person:bob;

-- The edge record is stored in the 'knows' table with:
--   in: person:alice
--   out: person:bob
SELECT * FROM knows;
-- Returns: [{ id: knows:..., in: person:alice, out: person:bob }]
```

### Setting Properties on Edges

Edge tables are full SurrealDB tables -- you can store arbitrary data on them.

```surrealql
-- Using SET for individual fields
RELATE person:alice->knows->person:bob SET
    since = d'2023-06-15',
    strength = 0.85,
    context = 'work';

-- Using CONTENT for full object replacement
RELATE person:alice->follows->person:charlie CONTENT {
    since: time::now(),
    notifications: true,
    tags: ['tech', 'surrealdb']
};

-- Using MERGE to add to existing properties
RELATE person:alice->knows->person:bob MERGE {
    last_interaction: time::now()
};
```

### Creating Multiple Relationships at Once

```surrealql
-- Relate multiple sources to one target
RELATE [person:alice, person:bob, person:charlie]->likes->post:123;

-- Relate one source to multiple targets
RELATE person:alice->follows->[person:bob, person:charlie, person:dave];

-- Relate multiple to multiple (creates cartesian product)
RELATE [person:alice, person:bob]->likes->[post:1, post:2];
-- Creates 4 edges: alice->post:1, alice->post:2, bob->post:1, bob->post:2
```

### Typed Edge Tables with Schema Enforcement

```surrealql
-- Define the edge table with typed in/out fields
DEFINE TABLE wrote SCHEMAFULL;
DEFINE FIELD in ON TABLE wrote TYPE record<person>;
DEFINE FIELD out ON TABLE wrote TYPE record<article>;
DEFINE FIELD written_at ON TABLE wrote TYPE datetime DEFAULT time::now();
DEFINE FIELD word_count ON TABLE wrote TYPE int;

-- Enforce unique relationships (one person can write an article only once)
DEFINE INDEX unique_author_article ON TABLE wrote COLUMNS in, out UNIQUE;

-- This succeeds
RELATE person:aristotle->wrote->article:metaphysics SET word_count = 45000;

-- This fails because of the UNIQUE index
RELATE person:aristotle->wrote->article:metaphysics SET word_count = 50000;

-- This also fails because 'in' must be a person record
RELATE article:foo->wrote->article:bar;
-- Error: Expected a record<person>, but found record<article>
```

### Bidirectional Edges

```surrealql
-- Some relationships are inherently bidirectional
-- Model friendship as a single edge, query from either direction
DEFINE TABLE friends_with SCHEMAFULL;
DEFINE FIELD in ON TABLE friends_with TYPE record<person>;
DEFINE FIELD out ON TABLE friends_with TYPE record<person>;
DEFINE FIELD since ON TABLE friends_with TYPE datetime;

RELATE person:alice->friends_with->person:bob SET since = d'2023-01-01';

-- Query from either side using <-> operator
SELECT *, <->friends_with<->person AS friends FROM person:alice;
SELECT *, <->friends_with<->person AS friends FROM person:bob;

-- Exclude self-references from results
SELECT *,
    array::complement(<->friends_with<->person, [id]) AS friends
FROM person;
```

### Self-Referential Edges

```surrealql
-- A person can manage themselves (e.g., solo founder)
DEFINE TABLE manages SCHEMAFULL;
DEFINE FIELD in ON TABLE manages TYPE record<person>;
DEFINE FIELD out ON TABLE manages TYPE record<person>;
DEFINE FIELD role ON TABLE manages TYPE string;

-- Hierarchical management
RELATE person:ceo->manages->person:vp_eng SET role = 'direct_report';
RELATE person:vp_eng->manages->person:lead_1 SET role = 'direct_report';
RELATE person:vp_eng->manages->person:lead_2 SET role = 'direct_report';
RELATE person:lead_1->manages->person:dev_1 SET role = 'direct_report';
RELATE person:lead_1->manages->person:dev_2 SET role = 'direct_report';

-- Self-referential: person references themselves
RELATE person:freelancer->manages->person:freelancer SET role = 'self';
```

---

## Graph Traversal

SurrealDB uses arrow operators for graph traversal directly within `SELECT` statements or as standalone expressions.

### Forward Traversal (`->`)

Follow edges from a record outward through the `out` direction.

```surrealql
-- Find all articles written by Aristotle
SELECT ->wrote->article FROM person:aristotle;
-- Returns: [{ "->wrote->article": [article:metaphysics, article:on_sleep] }]

-- Get specific fields from traversed records
SELECT ->wrote->article.title FROM person:aristotle;

-- Standalone expression (no SELECT needed)
RETURN person:aristotle->wrote->article;

-- Destructured form with aliases
person:aristotle.{ name, articles: ->wrote->article.title };
```

### Reverse Traversal (`<-`)

Follow edges backward through the `in` direction.

```surrealql
-- Find who wrote a specific article
SELECT <-wrote<-person FROM article:metaphysics;

-- Find all users who liked a post
SELECT <-likes<-person.name AS liked_by FROM post:123;

-- Standalone expression
RETURN article:metaphysics<-wrote<-person;

-- Find all followers of a person
SELECT <-follows<-person.name AS followers FROM person:alice;
```

### Bidirectional Traversal (`<->`)

Follow edges in both directions simultaneously.

```surrealql
-- Find all friends (regardless of who initiated the relationship)
SELECT <->friends_with<->person AS friends FROM person:alice;

-- Exclude self from results
SELECT
    array::complement(<->friends_with<->person, [id]) AS friends
FROM person:alice;

-- Works across any relationship
SELECT <->knows<->person AS connections FROM person:bob;
```

### Multi-Hop Traversal

Chain arrow operators to traverse multiple relationship levels.

```surrealql
-- Friends of friends
SELECT ->knows->person->knows->person AS friends_of_friends
FROM person:alice;

-- Author -> articles -> topics
SELECT ->wrote->article->tagged_with->topic AS interests
FROM person:aristotle;

-- User -> orders -> products -> categories
SELECT ->placed->order->contains->product->belongs_to->category
FROM user:customer_1;

-- Multi-hop with field selection at each level
SELECT
    ->manages->person.name AS direct_reports,
    ->manages->person->manages->person.name AS skip_level_reports
FROM person:ceo;

-- Traversal through different edge types
SELECT
    ->likes->post<-wrote<-person AS liked_same_posts
FROM person:alice;
```

### Filtered Traversal

Apply WHERE conditions during traversal to filter intermediate results.

```surrealql
-- Only traverse 'knows' edges created after 2020
SELECT ->(knows WHERE since > d'2020-01-01')->person.name AS recent_contacts
FROM person:alice;

-- Filter on edge properties
SELECT ->(rated WHERE score >= 4.0)->movie.title AS highly_rated
FROM user:alice;

-- Filter on target node properties
SELECT ->knows->(person WHERE age > 30).name AS older_contacts
FROM person:alice;

-- Combine edge and node filters
SELECT
    ->(knows WHERE strength > 0.7)->(person WHERE active = true).name
    AS strong_active_contacts
FROM person:alice;

-- Multi-hop with filters at each level
SELECT
    ->(manages WHERE role = 'direct_report')
    ->person
    ->(manages WHERE role = 'direct_report')
    ->person.name AS skip_level_reports
FROM person:ceo;
```

### Aliased Traversal

Use `AS` to alias intermediate results for later reference.

```surrealql
-- Alias the intermediate edge
SELECT
    ->(knows WHERE since > d'2023-01-01' AS recent_connections)->person.name
FROM person:alice;

-- Alias nodes at different traversal levels
SELECT
    ->wrote->(article AS authored_articles)->tagged_with->topic.name AS topics
FROM person:aristotle;
```

### Recursive Traversal Patterns

SurrealDB does not have a built-in recursive traversal keyword, but you can implement recursive patterns using subqueries and multi-hop chains.

```surrealql
-- Fixed-depth hierarchy (3 levels of management)
SELECT
    name,
    ->manages->person.name AS level_1,
    ->manages->person->manages->person.name AS level_2,
    ->manages->person->manages->person->manages->person.name AS level_3
FROM person:ceo;

-- Collect all descendants up to N levels using array functions
SELECT
    name,
    array::flatten([
        ->manages->person,
        ->manages->person->manages->person,
        ->manages->person->manages->person->manages->person
    ]) AS all_reports
FROM person:ceo;

-- Recursive-like pattern using a subquery approach
-- Find all ancestors (who manages my manager?)
SELECT
    name,
    <-manages<-person AS manager,
    <-manages<-person<-manages<-person AS skip_manager,
    <-manages<-person<-manages<-person<-manages<-person AS exec
FROM person:dev_1;
```

---

## Advanced Graph Patterns

### Shortest Path Queries

SurrealDB does not have a native shortest-path function, but you can implement BFS-like patterns.

```surrealql
-- Check if a direct connection exists (depth 1)
SELECT ->knows->person
FROM person:alice
WHERE person:dave IN ->knows->person;

-- Check depth 2
SELECT ->knows->person->knows->person
FROM person:alice
WHERE person:dave IN ->knows->person->knows->person;

-- Find shortest path by testing increasing depths
-- Depth 1
LET $depth1 = SELECT VALUE ->knows->person FROM person:alice;
-- Depth 2
LET $depth2 = SELECT VALUE ->knows->person->knows->person FROM person:alice;
-- Depth 3
LET $depth3 = SELECT VALUE ->knows->person->knows->person->knows->person FROM person:alice;

-- Check which depth first contains the target
RETURN {
    depth_1: person:dave IN array::flatten($depth1),
    depth_2: person:dave IN array::flatten($depth2),
    depth_3: person:dave IN array::flatten($depth3)
};

-- BFS-like approach using a SurrealDB function
DEFINE FUNCTION fn::find_path($from: record, $to: record, $edge: string) {
    -- Check direct connection
    LET $d1 = SELECT VALUE out FROM type::table($edge) WHERE in = $from;
    IF $to IN $d1 { RETURN { depth: 1, found: true } };

    -- Check depth 2
    LET $d2 = SELECT VALUE out FROM type::table($edge) WHERE in IN $d1;
    IF $to IN $d2 { RETURN { depth: 2, found: true } };

    -- Check depth 3
    LET $d3 = SELECT VALUE out FROM type::table($edge) WHERE in IN $d2;
    IF $to IN $d3 { RETURN { depth: 3, found: true } };

    RETURN { depth: -1, found: false };
};

RETURN fn::find_path(person:alice, person:dave, 'knows');
```

### Degree Centrality Calculations

```surrealql
-- Out-degree: number of outgoing relationships
SELECT
    id,
    name,
    count(->knows->person) AS out_degree
FROM person
ORDER BY out_degree DESC;

-- In-degree: number of incoming relationships
SELECT
    id,
    name,
    count(<-knows<-person) AS in_degree
FROM person
ORDER BY in_degree DESC;

-- Total degree (bidirectional)
SELECT
    id,
    name,
    count(->knows->person) AS out_degree,
    count(<-knows<-person) AS in_degree,
    count(->knows->person) + count(<-knows<-person) AS total_degree
FROM person
ORDER BY total_degree DESC;

-- Weighted centrality using edge properties
SELECT
    id,
    name,
    math::sum(->knows.strength) AS weighted_out_degree,
    math::sum(<-knows.strength) AS weighted_in_degree
FROM person
ORDER BY weighted_out_degree DESC;
```

### Community Detection Patterns

```surrealql
-- Find clusters by shared connections (common neighbors)
SELECT
    p1.name AS person_a,
    p2.name AS person_b,
    array::intersect(
        p1->knows->person,
        p2->knows->person
    ) AS common_friends,
    count(array::intersect(
        p1->knows->person,
        p2->knows->person
    )) AS overlap_count
FROM person AS p1, person AS p2
WHERE p1.id != p2.id
ORDER BY overlap_count DESC;

-- Find tightly connected subgroups
-- People who all know each other (triads)
SELECT
    a.name AS person_a,
    b.name AS person_b,
    c.name AS person_c
FROM person AS a, person AS b, person AS c
WHERE
    a.id != b.id AND b.id != c.id AND a.id != c.id
    AND b IN a->knows->person
    AND c IN a->knows->person
    AND c IN b->knows->person;

-- Neighborhood overlap for community strength
DEFINE FUNCTION fn::jaccard_similarity($a: record<person>, $b: record<person>) {
    LET $neighbors_a = SELECT VALUE ->knows->person FROM ONLY $a;
    LET $neighbors_b = SELECT VALUE ->knows->person FROM ONLY $b;
    LET $intersection = array::intersect($neighbors_a, $neighbors_b);
    LET $union = array::union($neighbors_a, $neighbors_b);
    RETURN IF count($union) > 0 {
        count($intersection) / count($union)
    } ELSE {
        0.0
    };
};
```

### Recommendation Engine Using Graph Traversal

```surrealql
-- Collaborative filtering: "users who liked X also liked Y"
SELECT
    ->likes->product AS also_liked,
    count() AS frequency
FROM person
WHERE id IN (
    SELECT VALUE <-likes<-person FROM product:target_product
)
AND ->likes->product != product:target_product
GROUP BY also_liked
ORDER BY frequency DESC
LIMIT 10;

-- Content-based with graph enrichment:
-- Find products in categories the user has shown interest in
SELECT
    p.id,
    p.name,
    p.price
FROM product AS p
WHERE p->belongs_to->category IN (
    SELECT VALUE ->purchased->product->belongs_to->category
    FROM user:current_user
)
AND p.id NOT IN (
    SELECT VALUE ->purchased->product FROM user:current_user
)
ORDER BY p.rating DESC
LIMIT 20;

-- Hybrid: People with similar taste who liked other things
LET $my_likes = SELECT VALUE ->likes->product FROM ONLY user:alice;
LET $similar_users = SELECT
    id,
    count(->likes->product INTERSECT $my_likes) AS overlap
FROM user
WHERE id != user:alice
ORDER BY overlap DESC
LIMIT 10;

SELECT
    ->likes->product AS recommended,
    count() AS score
FROM $similar_users
WHERE ->likes->product NOT IN $my_likes
GROUP BY recommended
ORDER BY score DESC
LIMIT 10;
```

### Access Control Graphs

```surrealql
-- Model RBAC as a graph
DEFINE TABLE role SCHEMAFULL;
DEFINE FIELD name ON TABLE role TYPE string;

DEFINE TABLE permission SCHEMAFULL;
DEFINE FIELD resource ON TABLE permission TYPE string;
DEFINE FIELD action ON TABLE permission TYPE string;

DEFINE TABLE has_role SCHEMAFULL;
DEFINE FIELD in ON TABLE has_role TYPE record<user>;
DEFINE FIELD out ON TABLE has_role TYPE record<role>;

DEFINE TABLE grants SCHEMAFULL;
DEFINE FIELD in ON TABLE grants TYPE record<role>;
DEFINE FIELD out ON TABLE grants TYPE record<permission>;

DEFINE TABLE inherits SCHEMAFULL;
DEFINE FIELD in ON TABLE inherits TYPE record<role>;
DEFINE FIELD out ON TABLE inherits TYPE record<role>;

-- Setup hierarchy
CREATE role:admin SET name = 'Admin';
CREATE role:editor SET name = 'Editor';
CREATE role:viewer SET name = 'Viewer';

-- Role inheritance: admin inherits editor inherits viewer
RELATE role:admin->inherits->role:editor;
RELATE role:editor->inherits->role:viewer;

-- Assign permissions
CREATE permission:read_posts SET resource = 'posts', action = 'read';
CREATE permission:write_posts SET resource = 'posts', action = 'write';
CREATE permission:delete_posts SET resource = 'posts', action = 'delete';

RELATE role:viewer->grants->permission:read_posts;
RELATE role:editor->grants->permission:write_posts;
RELATE role:admin->grants->permission:delete_posts;

-- Assign user to role
RELATE user:alice->has_role->role:editor;

-- Check all permissions for a user (including inherited via role hierarchy)
SELECT
    ->has_role->role AS direct_roles,
    ->has_role->role->grants->permission AS direct_permissions,
    ->has_role->role->inherits->role AS inherited_roles,
    ->has_role->role->inherits->role->grants->permission AS inherited_permissions,
    array::flatten([
        ->has_role->role->grants->permission,
        ->has_role->role->inherits->role->grants->permission,
        ->has_role->role->inherits->role->inherits->role->grants->permission
    ]) AS all_permissions
FROM user:alice;

-- Check if user has a specific permission
DEFINE FUNCTION fn::has_permission($user: record<user>, $resource: string, $action: string) {
    LET $all_perms = array::flatten([
        SELECT VALUE ->has_role->role->grants->permission FROM ONLY $user,
        SELECT VALUE ->has_role->role->inherits->role->grants->permission FROM ONLY $user,
        SELECT VALUE ->has_role->role->inherits->role->inherits->role->grants->permission FROM ONLY $user
    ]);
    LET $matching = SELECT * FROM array::flatten($all_perms) WHERE resource = $resource AND action = $action;
    RETURN count($matching) > 0;
};
```

### Hierarchical Data (Org Charts, Categories)

```surrealql
-- Category tree
DEFINE TABLE category SCHEMAFULL;
DEFINE FIELD name ON TABLE category TYPE string;
DEFINE FIELD description ON TABLE category TYPE option<string>;

DEFINE TABLE subcategory_of SCHEMAFULL;
DEFINE FIELD in ON TABLE subcategory_of TYPE record<category>;
DEFINE FIELD out ON TABLE subcategory_of TYPE record<category>;

-- Build category hierarchy
CREATE category:electronics SET name = 'Electronics';
CREATE category:computers SET name = 'Computers';
CREATE category:laptops SET name = 'Laptops';
CREATE category:desktops SET name = 'Desktops';
CREATE category:gaming_laptops SET name = 'Gaming Laptops';

RELATE category:computers->subcategory_of->category:electronics;
RELATE category:laptops->subcategory_of->category:computers;
RELATE category:desktops->subcategory_of->category:computers;
RELATE category:gaming_laptops->subcategory_of->category:laptops;

-- Find all children of a category
SELECT <-subcategory_of<-category.name AS children FROM category:electronics;

-- Find parent chain (breadcrumb)
SELECT
    name,
    ->subcategory_of->category.name AS parent,
    ->subcategory_of->category->subcategory_of->category.name AS grandparent
FROM category:gaming_laptops;

-- Find all descendants (up to 3 levels)
SELECT
    name,
    array::flatten([
        <-subcategory_of<-category,
        <-subcategory_of<-category<-subcategory_of<-category,
        <-subcategory_of<-category<-subcategory_of<-category<-subcategory_of<-category
    ]) AS all_descendants
FROM category:electronics;

-- Org chart example
DEFINE TABLE employee SCHEMAFULL;
DEFINE FIELD name ON TABLE employee TYPE string;
DEFINE FIELD title ON TABLE employee TYPE string;
DEFINE FIELD department ON TABLE employee TYPE string;

DEFINE TABLE reports_to SCHEMAFULL;
DEFINE FIELD in ON TABLE reports_to TYPE record<employee>;
DEFINE FIELD out ON TABLE reports_to TYPE record<employee>;

-- Build org chart
CREATE employee:ceo SET name = 'Jane', title = 'CEO', department = 'Executive';
CREATE employee:cto SET name = 'John', title = 'CTO', department = 'Engineering';
CREATE employee:lead SET name = 'Sam', title = 'Tech Lead', department = 'Engineering';
CREATE employee:dev SET name = 'Alex', title = 'Developer', department = 'Engineering';

RELATE employee:cto->reports_to->employee:ceo;
RELATE employee:lead->reports_to->employee:cto;
RELATE employee:dev->reports_to->employee:lead;

-- Full reporting chain upward
SELECT
    name, title,
    ->reports_to->employee.name AS manager,
    ->reports_to->employee->reports_to->employee.name AS skip_manager,
    ->reports_to->employee->reports_to->employee->reports_to->employee.name AS exec
FROM employee:dev;
```

### Dependency Graphs

```surrealql
-- Package dependency management
DEFINE TABLE package SCHEMAFULL;
DEFINE FIELD name ON TABLE package TYPE string;
DEFINE FIELD version ON TABLE package TYPE string;

DEFINE TABLE depends_on SCHEMAFULL;
DEFINE FIELD in ON TABLE depends_on TYPE record<package>;
DEFINE FIELD out ON TABLE depends_on TYPE record<package>;
DEFINE FIELD version_constraint ON TABLE depends_on TYPE string;

-- Create packages and dependencies
CREATE package:app SET name = 'my-app', version = '1.0.0';
CREATE package:framework SET name = 'web-framework', version = '3.2.1';
CREATE package:orm SET name = 'orm-lib', version = '2.1.0';
CREATE package:db_driver SET name = 'db-driver', version = '1.5.0';
CREATE package:logger SET name = 'logger', version = '0.8.0';

RELATE package:app->depends_on->package:framework SET version_constraint = '^3.0.0';
RELATE package:app->depends_on->package:orm SET version_constraint = '^2.0.0';
RELATE package:orm->depends_on->package:db_driver SET version_constraint = '^1.0.0';
RELATE package:framework->depends_on->package:logger SET version_constraint = '^0.5.0';
RELATE package:orm->depends_on->package:logger SET version_constraint = '^0.7.0';

-- Find all transitive dependencies of a package
SELECT
    name,
    ->depends_on->package.name AS direct_deps,
    ->depends_on->package->depends_on->package.name AS transitive_deps,
    array::distinct(array::flatten([
        ->depends_on->package,
        ->depends_on->package->depends_on->package,
        ->depends_on->package->depends_on->package->depends_on->package
    ])) AS all_deps
FROM package:app;

-- Find reverse dependencies (what depends on this package?)
SELECT
    name,
    <-depends_on<-package.name AS depended_on_by,
    <-depends_on<-package<-depends_on<-package.name AS transitive_dependents
FROM package:logger;
-- Shows that both framework and orm (and transitively, app) depend on logger
```

### Workflow and State Machine Patterns

```surrealql
-- State machine for order processing
DEFINE TABLE state SCHEMAFULL;
DEFINE FIELD name ON TABLE state TYPE string;
DEFINE FIELD description ON TABLE state TYPE string;

DEFINE TABLE transition SCHEMAFULL;
DEFINE FIELD in ON TABLE transition TYPE record<state>;
DEFINE FIELD out ON TABLE transition TYPE record<state>;
DEFINE FIELD action ON TABLE transition TYPE string;
DEFINE FIELD guard ON TABLE transition TYPE option<string>;

-- Define states
CREATE state:draft SET name = 'Draft', description = 'Order not yet submitted';
CREATE state:pending SET name = 'Pending', description = 'Awaiting approval';
CREATE state:approved SET name = 'Approved', description = 'Order approved';
CREATE state:shipped SET name = 'Shipped', description = 'Order in transit';
CREATE state:delivered SET name = 'Delivered', description = 'Order received';
CREATE state:cancelled SET name = 'Cancelled', description = 'Order cancelled';

-- Define transitions
RELATE state:draft->transition->state:pending SET action = 'submit';
RELATE state:pending->transition->state:approved SET action = 'approve', guard = 'role:manager';
RELATE state:pending->transition->state:cancelled SET action = 'cancel';
RELATE state:approved->transition->state:shipped SET action = 'ship';
RELATE state:shipped->transition->state:delivered SET action = 'deliver';
RELATE state:approved->transition->state:cancelled SET action = 'cancel';

-- Find valid transitions from current state
SELECT
    ->transition->state.name AS next_states,
    ->transition.action AS available_actions
FROM state:pending;

-- Check if a transition is valid
DEFINE FUNCTION fn::can_transition($current: record<state>, $action: string) {
    LET $valid = SELECT * FROM transition
        WHERE in = $current AND action = $action;
    RETURN count($valid) > 0;
};

-- Apply a state transition to an order
DEFINE FUNCTION fn::apply_transition($order: record<order>, $action: string) {
    LET $current_state = (SELECT VALUE current_state FROM ONLY $order);
    LET $next = SELECT VALUE out FROM transition
        WHERE in = $current_state AND action = $action
        LIMIT 1;
    IF count($next) = 0 {
        THROW "Invalid transition: cannot " + $action + " from current state";
    };
    UPDATE $order SET
        current_state = $next[0],
        updated_at = time::now();
};
```

---

## Performance Considerations

### Graph Index Strategies

```surrealql
-- Index edge table fields for faster traversal
DEFINE INDEX idx_knows_in ON TABLE knows COLUMNS in;
DEFINE INDEX idx_knows_out ON TABLE knows COLUMNS out;
DEFINE INDEX idx_knows_in_out ON TABLE knows COLUMNS in, out UNIQUE;

-- Index edge properties used in filtered traversals
DEFINE INDEX idx_knows_since ON TABLE knows COLUMNS since;
DEFINE INDEX idx_knows_strength ON TABLE knows COLUMNS strength;

-- Composite index for common filter patterns
DEFINE INDEX idx_manages_role ON TABLE manages COLUMNS in, role;
```

### Traversal Depth Limits

Deep traversals can be expensive. Limit depth and result sets.

```surrealql
-- Limit results at each hop
SELECT ->(knows LIMIT 10)->person FROM person:alice;

-- Use LIMIT on the outer query
SELECT ->knows->person->knows->person AS fof
FROM person:alice
LIMIT 50;

-- Avoid unbounded multi-hop chains in production
-- BAD: unlimited depth chain
-- SELECT ->knows->person->knows->person->knows->person->knows->person->... FROM person:alice;

-- GOOD: bounded depth with explicit limits
SELECT
    ->knows->(person LIMIT 20) AS depth_1
FROM person:alice;
```

### Caching Patterns for Frequent Traversals

```surrealql
-- Precompute common graph aggregates
DEFINE EVENT update_friend_count ON TABLE knows WHEN $event = "CREATE" THEN {
    UPDATE $after.in SET friend_count += 1;
};

DEFINE EVENT decrement_friend_count ON TABLE knows WHEN $event = "DELETE" THEN {
    UPDATE $before.in SET friend_count -= 1;
};

-- Materialized view pattern: store computed traversal results
DEFINE TABLE user_stats SCHEMAFULL;
DEFINE FIELD user ON TABLE user_stats TYPE record<person>;
DEFINE FIELD friend_count ON TABLE user_stats TYPE int;
DEFINE FIELD follower_count ON TABLE user_stats TYPE int;
DEFINE FIELD following_count ON TABLE user_stats TYPE int;

-- Periodically refresh with a function
DEFINE FUNCTION fn::refresh_user_stats($user: record<person>) {
    UPSERT user_stats SET
        user = $user,
        friend_count = count((SELECT ->friends_with->person FROM ONLY $user)),
        follower_count = count((SELECT <-follows<-person FROM ONLY $user)),
        following_count = count((SELECT ->follows->person FROM ONLY $user));
};
```

### General Tips

- Index the `in` and `out` columns on edge tables for faster traversal lookups.
- For large graphs, prefer shallow traversals (1-2 hops) and use application logic or stored functions for deeper searches.
- Use `LIMIT` within filtered traversals to cap intermediate result sets.
- Avoid cartesian explosions: chaining multiple multi-target traversals can produce exponentially large intermediate results.
- Use SCHEMAFULL edge tables with typed `in`/`out` fields to prevent invalid relationships and improve query planning.
- Consider precomputing and caching graph metrics (degree, centrality) on the node records themselves if they are queried frequently.
- Use `EXPLAIN` (covered in the performance rules) to understand traversal query plans.
