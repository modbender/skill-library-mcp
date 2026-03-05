# Mermaid Diagrams Skill

Generate beautiful diagrams from text using [Mermaid](https://mermaid.js.org/). Perfect for flowcharts, sequence diagrams, Gantt charts, and more.

## Quick Start

### Prerequisites

Install the Mermaid CLI globally:

```bash
npm install -g @mermaid-js/mermaid-cli
```

### Installation

```bash
clawhub install mermaid
```

### Usage

The skill uses the `mmdc` command to convert `.mmd` text files into images:

```bash
mmdc -i diagram.mmd -o diagram.png -t dark -b transparent -s 2
```

## Example Diagrams

### 1. Flowchart - Decision Tree

```mermaid
graph TD
    A[User Request] --> B{Authenticated?}
    B -->|Yes| C[Check Permissions]
    B -->|No| D[Show Login]
    C --> E{Has Access?}
    E -->|Yes| F[Process Request]
    E -->|No| G[403 Forbidden]
    D --> H[Redirect to OAuth]
    F --> I[Return Response]
```

**Use case:** System architecture, decision logic, user flows

### 2. Sequence Diagram - API Interaction

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Auth
    participant DB
    
    User->>API: POST /api/data
    API->>Auth: Verify Token
    Auth-->>API: Token Valid
    API->>DB: Query Data
    DB-->>API: Result Set
    API-->>User: JSON Response
```

**Use case:** API documentation, debugging async flows, microservice interactions

### 3. Gantt Chart - Project Timeline

```mermaid
gantt
    title Project Development Timeline
    dateFormat YYYY-MM-DD
    section Planning
    Requirements     :done, req, 2024-01-01, 2024-01-14
    Design          :done, des, 2024-01-15, 2024-01-28
    section Development
    Backend API     :active, dev1, 2024-01-29, 2024-02-25
    Frontend UI     :dev2, 2024-02-12, 2024-03-10
    section Testing
    Integration     :test1, 2024-03-11, 2024-03-24
    User Acceptance :test2, 2024-03-25, 2024-04-07
```

**Use case:** Project planning, sprint visualization, milestone tracking

### 4. Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string email
        string name
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int user_id FK
        date created_at
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
    }
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    PRODUCT {
        int id PK
        string name
        decimal price
    }
```

**Use case:** Database schema design, understanding data relationships

## Common Options

| Flag | Description | Example |
|------|-------------|---------|
| `-i` | Input `.mmd` file | `-i diagram.mmd` |
| `-o` | Output file (PNG/SVG/PDF) | `-o output.png` |
| `-t` | Theme | `-t dark` (default, dark, forest, neutral) |
| `-b` | Background | `-b transparent` |
| `-s` | Scale factor | `-s 2` (for retina displays) |
| `-w` | Width in pixels | `-w 1200` |

## Supported Diagram Types

- **Flowchart** (`graph TD` / `graph LR`) - Process flows, decision trees
- **Sequence** (`sequenceDiagram`) - API calls, async interactions
- **Class** (`classDiagram`) - Object-oriented design
- **State** (`stateDiagram-v2`) - State machines, workflows
- **ER** (`erDiagram`) - Database schemas
- **Gantt** (`gantt`) - Project timelines
- **Pie** (`pie`) - Data visualization
- **Mindmap** (`mindmap`) - Brainstorming, concept maps
- **Git Graph** (`gitGraph`) - Branch visualization
- **Timeline** (`timeline`) - Historical events

## Tips

1. **Use dark theme with transparency** for best results: `-t dark -b transparent`
2. **Scale for retina displays**: `-s 2` or `-s 3` for sharp images
3. **Keep labels concise** - Detail belongs in documentation, not the diagram
4. **Use subgraphs** to group related nodes in flowcharts
5. **Always use `pty: false`** when calling `mmdc` in scripts

## Testing

Run the included test script:

```bash
./generate-test.sh
```

This creates a sample flowchart and verifies the Mermaid CLI is working correctly.

## Documentation

- [Official Mermaid Docs](https://mermaid.js.org/)
- [Live Editor](https://mermaid.live/) - Test diagrams in your browser
- [Syntax Reference](https://mermaid.js.org/intro/syntax-reference.html)

## Troubleshooting

**Issue:** `mmdc: command not found`  
**Solution:** Install globally: `npm install -g @mermaid-js/mermaid-cli`

**Issue:** Diagram renders but text is cut off  
**Solution:** Increase width with `-w 1200` or use `-s 2` for better scaling

**Issue:** Colors look wrong  
**Solution:** Try different themes with `-t` flag or create custom theme config

## License

This skill is a wrapper around the open-source Mermaid project. See [Mermaid's license](https://github.com/mermaid-js/mermaid/blob/develop/LICENSE) for details.
