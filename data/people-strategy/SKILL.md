---
name: People-Strategy Agent Skill
description: A people relationship management agent skill that provides
  persistent graph-based storage using SQLite database. This skill enables AI
  agents to create, manage, and query a network of people and th...
---

# People-Strategy Agent Skill

## Overview

A people relationship management agent skill that provides persistent graph-based storage using SQLite database. This skill enables AI agents to create, manage, and query a network of people and their relationships, making it ideal for building personal CRMs, organizational charts, mentorship networks, and collaboration mapping.

## Capabilities

### Person Management
- **Create People**: Add new people with comprehensive information (name, role, relation, organization, character, notes)
- **Read People**: Retrieve individual people or search/filter across the database
- **Update People**: Modify any person's information
- **Delete People**: Remove people from the database (cascades to relationships)
- **Search**: Full-text search across names, roles, and organizations
- **Filter**: Filter by organization or relation type

### Relationship Management
- **Create Edges**: Establish directed relationships between people
- **Query Relationships**: Get incoming, outgoing, or all relationships for a person
- **Update Edges**: Modify relationship types and descriptions
- **Delete Edges**: Remove specific relationships
- **Bidirectional Support**: Track both directions of relationships

### Graph Operations
- **Full Graph Export**: Export entire network as JSON (nodes + edges)
- **Person Network**: Get complete network view for an individual
- **Relationship Types**: Support for custom relationship types (reports_to, mentors, works_with, etc.)

## Database Schema

### Tables

**people**
- `id`: INTEGER PRIMARY KEY
- `name`: TEXT NOT NULL
- `role`: TEXT
- `relation_to_me`: TEXT
- `organization`: TEXT
- `character`: TEXT
- `notes`: TEXT
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

**edges**
- `id`: INTEGER PRIMARY KEY
- `from_person_id`: INTEGER (FK to people.id)
- `to_person_id`: INTEGER (FK to people.id)
- `relationship_type`: TEXT NOT NULL
- `description`: TEXT
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP
- UNIQUE constraint on (from_person_id, to_person_id, relationship_type)

### Indexes
- `idx_people_name`: Index on people.name
- `idx_edges_from`: Index on edges.from_person_id
- `idx_edges_to`: Index on edges.to_person_id

## Usage Examples

### Command Line Interface

```bash
# Person operations
python people_skill.py add-person "Jane Doe" --role "CTO" --org "StartupXYZ" --relation "Mentor"
python people_skill.py get-person 1
python people_skill.py search "engineer"
python people_skill.py list-people --org "StartupXYZ"
python people_skill.py update-person 1 --notes "Coffee meeting scheduled"
python people_skill.py delete-person 1

# Relationship operations
python people_skill.py add-relationship 1 2 "mentors" --description "Tech career guidance"
python people_skill.py get-relationships 1
python people_skill.py list-relationships
python people_skill.py update-relationship 1 --type "coaches"
python people_skill.py delete-relationship 1

# Graph operations
python people_skill.py get-graph
python people_skill.py get-network 1
```

### Python API

```python
from database import PeopleDatabase
from people_skill import PeopleAgent

# Initialize
agent = PeopleAgent("people.db")

# Add people
result = agent.add_person(
    name="Alice Johnson",
    role="VP Engineering",
    relation_to_me="Former colleague",
    organization="TechCorp",
    character="Strategic thinker, empathetic leader",
    notes="Worked together 2020-2022"
)
person_id = result["person_id"]

# Add relationship
agent.add_relationship(
    from_person_id=1,
    to_person_id=2,
    relationship_type="manages",
    description="Direct manager relationship"
)

# Query network
network = agent.get_person_network(person_id)
print(f"Found {network['connections_count']} connections")

# Export graph
graph = agent.get_graph()
print(f"Graph: {graph['nodes_count']} nodes, {graph['edges_count']} edges")
```

## Common Relationship Types

- `reports_to`: Hierarchical reporting (subordinate → manager)
- `manages`: Hierarchical management (manager → subordinate)
- `works_with`: Peer collaboration
- `mentors`: Mentorship (mentor → mentee)
- `mentored_by`: Inverse mentorship (mentee → mentor)
- `friends_with`: Personal friendship
- `knows`: Acquaintance
- `collaborates_with`: Project collaboration
- `introduced_by`: Connection source

## Use Cases

### 1. Personal CRM
Track professional contacts, their roles, organizations, and how you know them. Add notes about conversations, meetings, or follow-ups.

```bash
python people_skill.py add-person "Sarah Chen" \
  --role "Product Director" \
  --org "InnovateCo" \
  --relation "Met at conference" \
  --notes "Interested in API collaboration, follow up Q2"
```

### 2. Organizational Mapping
Build and maintain organizational charts with reporting relationships.

```bash
# Add team members
python people_skill.py add-person "Mike Lead" --role "Team Lead" --org "Engineering"
python people_skill.py add-person "Dev One" --role "Engineer" --org "Engineering"
python people_skill.py add-person "Dev Two" --role "Engineer" --org "Engineering"

# Create reporting structure
python people_skill.py add-relationship 2 1 "reports_to"
python people_skill.py add-relationship 3 1 "reports_to"
```

### 3. Mentorship Network
Track mentorship relationships and career guidance connections.

```bash
python people_skill.py add-relationship 5 3 "mentors" \
  --description "Career guidance in ML/AI"
```

### 4. Collaboration Tracking
Map who works with whom on projects.

```bash
python people_skill.py add-relationship 1 2 "works_with" \
  --description "Project Phoenix collaboration"
```

### 5. Network Analysis
Analyze your professional network to identify key connections.

```bash
# View someone's complete network
python people_skill.py get-network 1

# Export for visualization
python people_skill.py get-graph > network.json
```

## Advanced Features

### Bidirectional Relationship Queries
The system automatically handles both directions:
```python
# Get all relationships for a person
edges = db.get_all_edges_for_person(person_id)
# Returns: {"outgoing": [...], "incoming": [...]}
```

### Cascade Deletion
Deleting a person automatically removes all associated relationships.

### Duplicate Prevention
The UNIQUE constraint prevents duplicate relationships between the same two people with the same type.

### Search Flexibility
Search works across multiple fields:
```bash
python people_skill.py search "engineer"
# Matches: names, roles, organizations
```

## Integration Examples

### Export to Visualization Tools
```bash
# Export graph for tools like D3.js, Cytoscape, Gephi
python people_skill.py get-graph > graph.json
```

### Import from CSV
```python
import csv
from people_skill import PeopleAgent

agent = PeopleAgent()
with open('contacts.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        agent.add_person(
            name=row['name'],
            role=row['role'],
            organization=row['org'],
            relation_to_me=row['relation']
        )
```

## Best Practices

1. **Consistent Naming**: Use consistent naming conventions for relationship types
2. **Rich Notes**: Add contextual notes to remember important details
3. **Regular Updates**: Keep information current with update commands
4. **Character Tracking**: Use the character field to remember personality traits
5. **Relationship Descriptions**: Add context to relationships for clarity
6. **Search First**: Before adding, search to avoid duplicates

## API Reference

See [people_skill.py](people_skill.py) for complete API documentation.

### Key Classes
- `PeopleDatabase`: Low-level database operations
- `PeopleAgent`: High-level agent interface with result dictionaries

### Return Format
All agent methods return dictionaries with:
- `success`: Boolean indicating success/failure
- `message`: Human-readable status message (on errors)
- Data fields specific to the operation

## Error Handling

The skill includes comprehensive error handling:
- Foreign key constraints prevent invalid relationships
- Unique constraints prevent duplicate relationships
- Cascade deletion maintains referential integrity
- Try-catch blocks in CLI provide user-friendly errors

## Performance

- Indexed queries for fast lookups
- Efficient graph traversal
- Suitable for networks of thousands of people
- SQLite handles concurrent reads

## Future Enhancements

Potential extensions:
- Graph visualization generation
- Shortest path finding between people
- Influence/centrality scoring
- Duplicate person detection
- Export to various formats (GraphML, DOT)
- Import from LinkedIn, contact lists
- Time-based relationship tracking
- Strength/confidence scoring for relationships

## License

MIT
