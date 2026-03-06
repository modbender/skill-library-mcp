# People-Strategy Agent Skill

A relationship management agent skill that provides persistent graph-based storage for people and their relationships using SQLite database.

## Features

- **Person Management**: Store and manage information about people including name, role, relation to you, organization, character traits, and notes
- **Relationship Graph**: Create directed edges between people to represent relationships (reports_to, works_with, mentors, etc.)
- **Search & Filter**: Search people by name, role, or organization; filter by organization or relation
- **Network Analysis**: View a person's complete network including all connections and relationships
- **Graph Export**: Export the entire relationship graph in JSON format

## Installation

```bash
cd people-strategy
pip install -r requirements.txt  # No external dependencies needed
```

## Usage

### Person Management

```bash
# Add a person
python people_skill.py add-person "John Doe" --role "Senior Engineer" --relation "Colleague" --org "Acme Corp" --character "Collaborative, detail-oriented" --notes "Met at conference 2024"

# Get a person by ID
python people_skill.py get-person 1

# Search for people
python people_skill.py search "engineer"

# List all people
python people_skill.py list-people

# Filter by organization
python people_skill.py list-people --org "Acme Corp"

# Filter by relation
python people_skill.py list-people --relation "Colleague"

# Update a person
python people_skill.py update-person 1 --role "Lead Engineer" --notes "Promoted in Q1 2025"

# Delete a person
python people_skill.py delete-person 1
```

### Relationship Management

```bash
# Add a relationship (edge)
python people_skill.py add-relationship 1 2 "reports_to" --description "Direct manager"

# Get all relationships for a person
python people_skill.py get-relationships 1

# Get only outgoing relationships
python people_skill.py get-relationships 1 --direction outgoing

# Get only incoming relationships
python people_skill.py get-relationships 1 --direction incoming

# List all relationships
python people_skill.py list-relationships

# Update a relationship
python people_skill.py update-relationship 1 --type "works_with" --description "Team member"

# Delete a relationship
python people_skill.py delete-relationship 1
```

### Graph Operations

```bash
# Export entire graph
python people_skill.py get-graph

# Get a person's complete network
python people_skill.py get-network 1
```

## Database Schema

### People Table
- `id`: Unique identifier
- `name`: Person's name
- `role`: Their role/position
- `relation_to_me`: How they relate to you
- `organization`: Their organization
- `character`: Character traits/description
- `notes`: Additional notes
- `created_at`, `updated_at`: Timestamps

### Edges Table
- `id`: Unique identifier
- `from_person_id`: Source person
- `to_person_id`: Target person
- `relationship_type`: Type of relationship (e.g., "reports_to", "mentors", "works_with")
- `description`: Additional description
- `created_at`, `updated_at`: Timestamps

## Common Relationship Types

- `reports_to`: Direct reporting relationship
- `manages`: Management relationship
- `works_with`: Collaboration/peer relationship
- `mentors`: Mentorship relationship
- `friends_with`: Personal relationship
- `knows`: Acquaintance

## Use Cases

1. **Professional Network Management**: Track colleagues, managers, and professional contacts
2. **Organizational Mapping**: Visualize org charts and reporting structures
3. **Mentorship Tracking**: Maintain mentor/mentee relationships
4. **Collaboration Networks**: Identify collaboration patterns and connections
5. **Personal CRM**: Keep notes and track relationships with people you know

## Example Workflow

```bash
# Add team members
python people_skill.py add-person "Alice Smith" --role "Engineering Manager" --org "TechCorp" --relation "Manager"
python people_skill.py add-person "Bob Jones" --role "Senior Engineer" --org "TechCorp" --relation "Colleague"
python people_skill.py add-person "Carol White" --role "Product Manager" --org "TechCorp" --relation "Colleague"

# Create relationships
python people_skill.py add-relationship 2 1 "reports_to" --description "Direct report"
python people_skill.py add-relationship 3 1 "reports_to" --description "Direct report"
python people_skill.py add-relationship 2 3 "works_with" --description "Project Alpha collaboration"

# View Alice's network
python people_skill.py get-network 1

# Search for engineers
python people_skill.py search "Engineer"
```

## License

MIT
