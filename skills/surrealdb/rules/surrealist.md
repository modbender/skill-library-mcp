# Surrealist -- SurrealDB IDE and Management Interface

Surrealist is the official graphical management interface for SurrealDB. It is available as a web application at app.surrealdb.com and as a standalone desktop application built with Tauri.

Current version: **v3.7.2** (2026-02-21). Fixes migration exports and miscellaneous UI issues.

---

## Overview

Surrealist provides a comprehensive interface for managing SurrealDB instances, including query authoring, data exploration, schema design, and cloud instance management. It supports connections to local, remote, and cloud-hosted SurrealDB instances.

---

## Views and Features

### Query View

The primary interface for writing and executing SurrealQL queries.

**Capabilities:**
- Full SurrealQL syntax highlighting with autocomplete
- Multiple query tabs for working on several queries simultaneously
- Saved queries library for frequently used queries
- Query history with search
- Multiple result display modes:
  - Table view for tabular results
  - JSON view for raw response data
  - Graph visualization for relationship queries (displays nodes and edges interactively)
- Query execution timing and statistics
- Variable binding panel for parameterized queries
- Query formatting and validation

**Usage Patterns:**

```surrealql
-- Write queries with syntax highlighting and autocomplete
SELECT * FROM person WHERE age > 25 ORDER BY name;

-- Use the variable panel to bind parameters
-- Set $min_age = 25 in the variables panel, then:
SELECT * FROM person WHERE age > $min_age;

-- Graph queries are visualized as interactive node-edge diagrams
SELECT *, ->knows->person AS friends FROM person;
```

### Explorer View

Browse and inspect database records interactively.

**Capabilities:**
- Table listing with record counts
- Record browsing with pagination
- Individual record inspection and editing
- Follow record links and graph edges to navigate between related records
- Inline record creation and deletion
- Field-level filtering and sorting
- Export selected records

### Designer View

Visual schema design and entity relationship diagrams.

**Capabilities:**
- Visual entity-relationship diagrams showing tables and their fields
- Table relationship visualization (record links, graph edges)
- Schema definition viewing and editing
- Field type information display
- Index visualization
- Access rule overview
- Event and changefeed display

### GraphQL View

Execute GraphQL queries against SurrealDB's built-in GraphQL endpoint.

**Capabilities:**
- GraphQL syntax highlighting
- Query variable panel
- Response viewer
- Schema introspection

### Cloud Panel

Manage SurrealDB Cloud instances directly from Surrealist.

**Capabilities:**
- Provision new cloud database instances
- View and manage existing instances
- Monitor instance health and metrics
- Scale instance resources
- Manage billing and usage

---

## Key Features

### Surreal Sidekick

AI-powered assistant integrated into Surrealist that helps with query writing and schema design.

**What it does:**
- Suggests SurrealQL queries based on natural language descriptions
- Explains existing queries
- Recommends schema improvements
- Helps debug query errors
- Suggests index optimizations

### One-Click Local Database (Desktop Only)

The desktop application can start a local SurrealDB instance with a single click, without requiring a separate server installation. This is useful for development and testing.

### Sandbox Environment

A built-in sandbox environment for learning SurrealQL without connecting to any database. It provides an in-memory database instance where you can experiment freely.

### Command Palette

Quick navigation and action system accessible via keyboard shortcut:
- Switch between views
- Open saved queries
- Connect to different databases
- Execute common actions
- Search across the interface

### SurrealML Model Upload

Upload and manage SurrealML machine learning models through the interface. This integrates with SurrealDB's built-in ML capabilities.

### Auto-Generated API Documentation

View auto-generated REST and WebSocket API documentation for your database schema, including available tables, fields, and access rules.

### Access Rule Management

Visual interface for managing SurrealDB access rules:
- Define and edit access methods
- Configure record-level access
- Set up namespace and database authentication
- Manage user permissions

### Connection Management

Manage multiple database connections:
- Save connection profiles with authentication credentials
- Switch between connections quickly
- Support for local, remote, and cloud connections
- Connection health indicators
- WebSocket and HTTP connection options

---

## Configuration

### Connection Strings

Surrealist accepts standard SurrealDB connection strings:

```
# WebSocket (recommended)
ws://localhost:8000
wss://your-server.example.com:8000

# HTTP
http://localhost:8000
https://your-server.example.com:8000

# Cloud
wss://your-instance.surrealdb.cloud
```

### Authentication Setup

When connecting to a SurrealDB instance, configure authentication in the connection dialog:

- **Root credentials**: Username and password for root-level access
- **Namespace credentials**: For namespace-scoped access
- **Database credentials**: For database-scoped access
- **Token-based**: Paste an existing authentication token
- **Access method**: Use a defined access method for record-level authentication

### Namespace and Database Selection

After connecting, select the target namespace and database from the dropdowns in the toolbar, or specify them in the connection configuration.

---

## Desktop Application

The desktop version of Surrealist is built with Tauri and provides additional capabilities over the web version:

- **Local database serving**: Start an embedded SurrealDB instance without installing the server separately
- **File system access**: Import and export files directly
- **Native performance**: Runs as a native application
- **Offline mode**: Work with local databases without internet access
- **System tray integration**: Keep Surrealist running in the background

### Installation

Download the desktop application from the SurrealDB website or the Surrealist GitHub releases page. Available for macOS, Windows, and Linux.

---

## Web Application

Access the web version at app.surrealdb.com. The web application provides the same core functionality as the desktop version except for local database serving and file system access.

No installation required -- works in any modern browser.

---

## Keyboard Shortcuts

Common keyboard shortcuts for efficient navigation:

| Action | Shortcut |
|--------|----------|
| Execute query | Ctrl/Cmd + Enter |
| New query tab | Ctrl/Cmd + T |
| Close query tab | Ctrl/Cmd + W |
| Format query | Ctrl/Cmd + Shift + F |
| Command palette | Ctrl/Cmd + K |
| Toggle sidebar | Ctrl/Cmd + B |
| Save query | Ctrl/Cmd + S |
| Switch to Query view | Ctrl/Cmd + 1 |
| Switch to Explorer view | Ctrl/Cmd + 2 |
| Switch to Designer view | Ctrl/Cmd + 3 |

---

## Tips

- Use the graph visualization in Query View to understand relationships between records. Execute queries that include graph traversals and the results will render as an interactive node-edge diagram.
- The Explorer View is the fastest way to inspect individual records and navigate relationships by following record links.
- Save frequently used queries in the saved queries library. Organize them with descriptive names for quick retrieval.
- Use the sandbox to test destructive operations (DELETE, REMOVE TABLE) safely before running them on production data.
- The command palette provides the fastest way to navigate between views and execute common actions without leaving the keyboard.
