# Architecture Diagram: Conversation-Driven Recommendations

## System Architecture

```mermaid
graph TB
    A[User Conversation in OpenClaw] --> B[Session JSONL Files]
    B --> C[OpenClaw Session Reader]

    C --> D[Conversation Analysis]
    D --> E[Topics Extraction]
    D --> F[Interests Detection]
    D --> G[Preferences Identification]

    E --> H[Data Collector]
    F --> H
    G --> H

    H --> I[Personality Analyzer]

    I --> J[Calculate Conviction]
    I --> K[Calculate Intuition]
    I --> L[Calculate Contribution]

    J --> M[2x2 Quadrant Classification]
    K --> M
    L --> M

    M --> N{Contribution > 65?}
    N -->|Yes| O[The Cultivator]
    N -->|No| P[2x2 Classification]

    P --> Q{Conviction ≥ 50?}
    Q -->|Yes| R{Intuition ≥ 50?}
    Q -->|No| S{Intuition ≥ 50?}

    R -->|Yes| T[The Visionary]
    R -->|No| U[The Optimizer]
    S -->|Yes| V[The Explorer]
    S -->|No| W[The Innovator]

    T --> X[Detected Categories]
    U --> X
    V --> X
    W --> X
    O --> X

    F --> X

    X --> Y[Skill Discovery]
    Y --> Z[ClawHub Search]

    Z --> AA[Category Match 30pts]
    Z --> AB[Personality Match 20pts]
    Z --> AC[Conversation Align 15pts]
    Z --> AD[Dimension Bonus 15pts]

    AA --> AE[Final Recommendations]
    AB --> AE
    AC --> AE
    AD --> AE

    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#fff4e1
    style H fill:#fff4e1
    style I fill:#ffe1f5
    style M fill:#ffe1f5
    style X fill:#e1ffe1
    style Y fill:#e1ffe1
    style AE fill:#e1ffe1
```

## Data Flow: Before vs After

### Before (Mock Data)
```mermaid
graph LR
    A[User ID] --> B[Data Collector]
    B --> C[MOCK DATA]
    C --> D[Personality Analyzer]
    D --> E[Fixed Category Mapping]
    E --> F[Recommendations]

    style C fill:#ffcccc
    style E fill:#ffcccc
```

### After (Real Data)
```mermaid
graph LR
    A[User ID] --> B[Session Reader]
    B --> C[Real Conversation]
    C --> D[Extract Insights]
    D --> E[Personality Analyzer]
    E --> F[Detected Categories]
    F --> G[Recommendations]

    style C fill:#ccffcc
    style F fill:#ccffcc
```

## Recommendation Scoring

```mermaid
graph TD
    A[Skill Candidate] --> B{Category Match?}
    B -->|Yes| C[+30 points]
    B -->|No| D[Max 65 points]

    A --> E{Personality Match?}
    E -->|5 keywords| F[+20 points]

    A --> G{Conversation Align?}
    G -->|3 keywords| H[+15 points]

    A --> I{High Conviction?}
    I -->|≥70| J[+5 points]

    A --> K{High Intuition?}
    K -->|≥70| L[+5 points]

    A --> M{High Contribution?}
    M -->|≥65| N[+5 points]

    C --> O[Total Score]
    D --> O
    F --> O
    H --> O
    J --> O
    L --> O
    N --> O

    O --> P{Score ≥ 60?}
    P -->|Yes| Q[Recommended]
    P -->|No| R[Filtered Out]

    style C fill:#90ee90
    style F fill:#90ee90
    style H fill:#90ee90
    style Q fill:#90ee90
```

## Personality Classification (2x2 + Override)

```mermaid
graph TD
    A[Calculate Dimensions] --> B{Contribution > 65?}
    B -->|Yes| C[🩵 The Cultivator]
    B -->|No| D{Conviction ≥ 50?}

    D -->|Yes| E{Intuition ≥ 50?}
    D -->|No| F{Intuition ≥ 50?}

    E -->|Yes| G[💜 The Visionary<br/>High Conviction<br/>High Intuition]
    E -->|No| H[🧡 The Optimizer<br/>High Conviction<br/>Low Intuition]

    F -->|Yes| I[💚 The Explorer<br/>Low Conviction<br/>High Intuition]
    F -->|No| J[💙 The Innovator<br/>Low Conviction<br/>Low Intuition]

    style C fill:#add8e6
    style G fill:#dda0dd
    style H fill:#ffa07a
    style I fill:#90ee90
    style J fill:#87ceeb
```

## Session File Structure

```mermaid
graph TD
    A[~/.openclaw/agents/main/sessions/] --> B[sessions.json]
    A --> C[sessionId.jsonl]

    B --> D[Session Metadata]
    D --> E[agent:main:userId]
    E --> F[sessionId: abc123...]

    C --> G[JSONL Events]
    G --> H[Line 1: User message]
    G --> I[Line 2: Assistant response]
    G --> J[Line 3: User message]
    G --> K[...]

    H --> L[Parse JSON]
    I --> L
    J --> L

    L --> M[Extract text content]
    M --> N[Analyze conversation]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#fff4e1
    style N fill:#e1ffe1
```

## Error Handling Flow

```mermaid
graph TD
    A[Read Session] --> B{File exists?}
    B -->|No| C[Return empty data]
    B -->|Yes| D{Valid JSON?}

    D -->|No| E[Skip line, continue]
    D -->|Yes| F{Message type?}

    F -->|message| G[Extract text]
    F -->|other| E

    G --> H{Has content?}
    H -->|Yes| I[Add to messages]
    H -->|No| E

    I --> J{All lines parsed?}
    J -->|No| D
    J -->|Yes| K[Analyze conversation]

    K --> L{Has messages?}
    L -->|Yes| M[Return analysis]
    L -->|No| C

    C --> N[Use fallback categories]
    M --> O[Use detected categories]

    style C fill:#ffcccc
    style E fill:#ffffcc
    style N fill:#ffcccc
    style O fill:#ccffcc
```

## Component Interaction

```mermaid
sequenceDiagram
    participant U as User
    participant S as Session Reader
    participant D as Data Collector
    participant P as Personality Analyzer
    participant R as Recommender
    participant C as ClawHub

    U->>S: Start skill with userId
    S->>S: Find active session
    S->>S: Read JSONL file
    S->>S: Extract topics/interests
    S-->>D: Return conversation analysis

    D->>D: Collect Twitter data
    D->>D: Collect Wallet data
    D->>D: Include conversation memory
    D-->>P: Return user data

    P->>P: Calculate Conviction
    P->>P: Calculate Intuition
    P->>P: Calculate Contribution
    P->>P: Classify personality (2x2)
    P->>P: Detect categories from data
    P-->>R: Return identity data

    R->>C: Search by detected categories
    C-->>R: Return skill candidates
    R->>R: Score by category match
    R->>R: Score by personality match
    R->>R: Score by conversation align
    R-->>U: Return top recommendations
```

## Key Decision Points

```mermaid
graph TD
    A[Start] --> B{Has session data?}
    B -->|Yes| C[Use detected categories]
    B -->|No| D[Use personality-based categories]

    C --> E{Category detected?}
    E -->|Yes| F[Primary: Detected]
    E -->|No| D

    F --> G[Match skills]
    D --> G

    G --> H{Enough matches?}
    H -->|Yes| I[Return top 10]
    H -->|No| J[Expand search]

    J --> K[Include sub-categories]
    K --> L[Return best available]

    I --> M[End]
    L --> M

    style C fill:#90ee90
    style F fill:#90ee90
    style D fill:#ffcccc
```

## Testing Flow

```mermaid
graph TD
    A[npm run test:conversation] --> B[Create test user ID]
    B --> C[Read session history]

    C --> D{Session found?}
    D -->|Yes| E[Display messages count]
    D -->|No| F[Skip to data collector]

    E --> G[Display topics]
    E --> H[Display interests]
    E --> I[Display preferences]

    G --> J[Collect user data]
    H --> J
    I --> J
    F --> J

    J --> K[Analyze personality]
    K --> L[Display 2x2 metrics]
    K --> M[Display personality type]
    K --> N[Display detected categories]

    L --> O[Verify recommendation logic]
    M --> O
    N --> O

    O --> P{Test passed?}
    P -->|Yes| Q[✅ Success]
    P -->|No| R[❌ Failed]

    style Q fill:#90ee90
    style R fill:#ffcccc
```
