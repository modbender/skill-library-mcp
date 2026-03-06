# Solid Protocol Primer

This document explains the core Solid concepts you need to understand when using this Skill.

## What is Solid?

Solid (Social Linked Data) is a W3C specification that lets people and agents store their data in personal online datastores called **Pods**. The key idea: you control your data, not the application.

## Key Concepts

### Pod

A Pod is a personal data store — think of it as a private web server for your data. Each agent gets its own Pod with a URL like `http://localhost:3000/myagent/`.

Inside a Pod, data is organized into **containers** (like folders) and **resources** (like files):

```
/myagent/
├── profile/card          ← Your WebID profile document
├── memory/               ← Container for private data
│   ├── notes.ttl
│   └── preferences.ttl
├── shared/               ← Container for shared data
│   └── report.ttl
└── conversations/        ← Container for conversation logs
```

### WebID

A WebID is a URL that uniquely identifies an agent. It looks like:

```
http://localhost:3000/myagent/profile/card#me
```

The `#me` fragment points to the specific entity described in the profile document. When another agent or server needs to verify who you are, they dereference your WebID to read your profile.

### Turtle (RDF)

Turtle is the primary data format for Solid. It's a way to express linked data as subject-predicate-object triples:

```turtle
@prefix foaf: <http://xmlns.com/foaf/0.1/>.

<#me> a foaf:Agent;
  foaf:name "My Agent".
```

This says: "The entity `#me` is a `foaf:Agent` and its name is 'My Agent'."

You can also store non-RDF data (plain text, JSON, etc.) — Solid doesn't require Turtle for everything.

### Web Access Control (WAC)

WAC is how Solid handles permissions. Each resource can have an Access Control List (ACL) that specifies who can do what:

- **Read** — View the resource
- **Write** — Modify or replace the resource
- **Append** — Add to the resource without modifying existing content
- **Control** — Manage the ACL itself

ACL rules are expressed in Turtle:

```turtle
@prefix acl: <http://www.w3.org/ns/auth/acl#>.

<#rule1>
    a acl:Authorization;
    acl:agent <http://localhost:3000/other/profile/card#me>;
    acl:accessTo <http://localhost:3000/myagent/shared/report.ttl>;
    acl:mode acl:Read.
```

This grants the agent `other` read access to `report.ttl`.

### Linked Data Platform (LDP)

Solid builds on LDP, a W3C standard for read-write linked data on the web. Key operations:

- **GET** a resource → read its contents
- **PUT** a resource → create or replace it
- **DELETE** a resource → remove it
- **POST** to a container → create a new resource inside it

All of these are standard HTTP operations, which is why Solid works with any HTTP client.

## Common Prefixes

When writing Turtle data, these prefixes are commonly used:

| Prefix | URI | Used for |
|--------|-----|----------|
| `foaf:` | `http://xmlns.com/foaf/0.1/` | People, agents, names |
| `schema:` | `http://schema.org/` | General-purpose metadata |
| `acl:` | `http://www.w3.org/ns/auth/acl#` | Access control |
| `solid:` | `http://www.w3.org/ns/solid/terms#` | Solid-specific terms |
| `ldp:` | `http://www.w3.org/ns/ldp#` | Linked Data Platform |
