---
name: scholargraph
description: Academic literature intelligence toolkit with AI-powered multi-source search (11 sources including arXiv, Semantic Scholar, OpenAlex, PubMed, CrossRef, DBLP, IEEE, CORE, Google Scholar), complementary search strategy with domain auto-detection, PDF download, concept learning, gap detection, progress tracking, paper analysis, knowledge graph building, review detection, concept extraction, and SQLite-based persistent storage across 15+ AI providers.
metadata:
  {
    "openclaw": {
      "emoji": "📚",
      "requires": {
        "bins": ["bun"],
        "env": ["AI_PROVIDER"]
      }
    }
  }
---

# ScholarGraph - Academic Literature Intelligence Toolkit

## Overview

ScholarGraph is a comprehensive academic literature intelligence toolkit that helps researchers efficiently search, analyze, and manage academic papers using AI-powered tools. Features 11 academic search sources with intelligent domain-based source selection and PDF download capabilities.

## Features

### Core Modules (6)

1. **Literature Search** - Multi-source academic paper discovery (11 sources)
   - **Free sources**: arXiv, Semantic Scholar, OpenAlex (250M+), PubMed (biomedical), CrossRef (150M+ DOI), DBLP (CS), Web Search
   - **API-key sources**: IEEE Xplore, CORE, Google Scholar (SerpAPI), Unpaywall (OA PDF)
   - Adapter-based plugin architecture for easy extension
   - Complementary search strategy with auto domain detection (biomedical/cs/engineering/physics)
   - Priority-based source selection per domain
   - Query expansion for better search results
   - PDF download with multi-strategy URL resolution

2. **Concept Learner** - Rapid knowledge framework construction
   - Generate structured learning cards
   - Include code examples and related papers
   - Support beginner/intermediate/advanced depth levels

3. **Knowledge Gap Detector** - Proactive blind spot identification
   - Analyze knowledge coverage in specific domains
   - Identify critical, recommended, and optional gaps
   - Provide learning recommendations and time estimates

4. **Progress Tracker** - Real-time field monitoring
   - Track research topics and keywords
   - Generate daily/weekly/monthly reports
   - Monitor trending papers and topics

5. **Paper Analyzer** - Deep paper analysis
   - Extract key contributions and insights
   - Support quick/standard/deep analysis modes
   - Generate structured analysis reports

6. **Knowledge Graph Builder** - Concept relationship visualization
   - Build interactive knowledge graphs
   - Support Mermaid and JSON output formats
   - Find learning paths between concepts
   - SQLite-based persistent storage
   - Bidirectional concept-paper indexing

### Advanced Features (9)

7. **Review Detector** - Automatic review paper identification
   - Multi-dimensional scoring (title 30% + citations 25% + abstract 25% + AI 20%)
   - Chinese and English keyword support
   - Confidence-based filtering with user confirmation

8. **Concept Extractor** - Extract concepts from review papers
   - AI-powered extraction of 15-30 core concepts
   - Four-level categorization (foundation/core/advanced/application)
   - Importance scoring and relationship identification
   - Cross-review deduplication and merging

9. **Review-to-Graph Workflow** - End-to-end pipeline
   - Search reviews -> Detect -> Confirm -> Analyze -> Extract concepts
   - Build knowledge graph -> Enrich with key papers -> Index -> Store
   - Interactive or automatic confirmation mode

10. **Knowledge Graph Query** - Bidirectional literature indexing
    - Concept -> papers: find papers related to a concept
    - Paper -> concepts: find concepts covered by a paper
    - Paper recommendations based on multiple concepts
    - SQLite-optimized high-performance queries

11. **Compare Concepts** - Compare two concepts
    - Identify similarities and differences
    - Provide use case recommendations

12. **Compare Papers** - Compare multiple papers
    - Find common themes and differences
    - Generate synthesis analysis

13. **Critique** - Critical paper analysis
    - Identify strengths and weaknesses
    - Find research gaps and improvement suggestions
    - Support custom focus areas

14. **Learning Path** - Find optimal learning paths
    - Discover paths between concepts
    - Generate topological learning order
    - Visualize with Mermaid diagrams

15. **Graph Management** - Manage persistent knowledge graphs
    - List all saved graphs
    - View graph statistics
    - Export graphs to JSON
    - Visualize with Mermaid

## Technical Features

- **11 Academic Search Sources**: arXiv, Semantic Scholar, OpenAlex, PubMed, CrossRef, DBLP, IEEE Xplore, CORE, Google Scholar, Unpaywall, Web Search
- **Complementary Search Strategy**: Auto-detects query domain and selects optimal source combination
- **Adapter Pattern**: Plugin-based search source architecture for easy extension
- **PDF Download**: Multi-strategy URL resolution (direct, Unpaywall, OpenAlex OA, CORE)
- **Multi-AI Provider Support**: 15+ AI providers including OpenAI, Anthropic, DeepSeek, Qwen, Zhipu AI, etc.
- **SQLite Persistence**: Knowledge graphs stored in SQLite database via bun:sqlite
- **Bidirectional Indexing**: Concept-paper and paper-concept bidirectional query support
- **Rate Limiting**: Per-source rate limiting with automatic retry and delay
- **Multiple Output Formats**: Markdown, JSON, Mermaid
- **TypeScript + Bun**: Fast and type-safe runtime
- **CLI + API**: Both command-line and programmatic interfaces

## Installation

```bash
# Clone repository
git clone https://github.com/Josephyb97/ScholarGraph.git
cd ScholarGraph

# Install dependencies
bun install

# Initialize configuration
bun run cli.ts config init
```

## Configuration

Set up your AI provider:

```bash
# Using OpenAI
export AI_PROVIDER=openai
export OPENAI_API_KEY="your-api-key"

# Using DeepSeek
export AI_PROVIDER=deepseek
export DEEPSEEK_API_KEY="your-api-key"

# Using Qwen (通义千问)
export AI_PROVIDER=qwen
export QWEN_API_KEY="your-api-key"
```

### Academic Source API Keys (optional, expand search coverage)

```bash
export NCBI_API_KEY="your-key"           # PubMed high-speed access (10 req/s)
export IEEE_API_KEY="your-key"           # IEEE Xplore engineering papers
export CORE_API_KEY="your-key"           # CORE open access full text
export UNPAYWALL_EMAIL="your@email.com"  # Unpaywall OA PDF resolver
export CROSSREF_MAILTO="your@email.com"  # CrossRef polite pool (higher rate)
export SERPAPI_KEY="your-key"            # Google Scholar (via SerpAPI)
export SERPER_API_KEY="your-key"         # Web search via Serper
```

## Usage Examples

### Search Literature
```bash
# Auto-select best sources based on query domain
lit search "transformer attention" --limit 20

# Specify domain for optimized source selection
lit search "CRISPR gene editing" --domain biomedical

# Use specific sources (comma-separated)
lit search "deep learning" --source semantic_scholar,arxiv,openalex --sort citations

# Search and download PDFs
lit search "attention is all you need" --download --limit 3
```

### Download PDFs
```bash
# Search and download PDFs
lit download "transformer" --limit 5 --output ./papers
```

### Learn Concepts
```bash
lit learn "BERT" --depth advanced --papers --code --output bert-card.md
```

### Detect Knowledge Gaps
```bash
lit detect --domain "Deep Learning" --known "CNN,RNN" --output gaps.md
```

### Analyze Papers
```bash
lit analyze "https://arxiv.org/abs/1706.03762" --mode deep --output analysis.md
```

### Build Knowledge Graph
```bash
lit graph transformer attention BERT GPT --format mermaid --output graph.md
```

### Compare Concepts
```bash
lit compare concepts CNN RNN --output comparison.md
```

### Compare Papers
```bash
lit compare papers "url1" "url2" "url3" --output comparison.md
```

### Critical Analysis
```bash
lit critique "paper-url" --focus "novelty,scalability" --output critique.md
```

### Find Learning Path
```bash
lit path "Machine Learning" "Deep Learning" --concepts "Neural Networks" --output path.md
```

### Search Review Papers
```bash
lit review-search "attention mechanism" --limit 10
```

### Build Knowledge Graph from Reviews
```bash
# From search query (interactive mode)
lit review-graph "deep learning" --output dl-graph --enrich

# From specific URL
lit review-graph "https://arxiv.org/abs/xxxx" --output my-graph --enrich

# Auto-confirm mode (non-interactive)
lit review-graph "transformer" --output tf-graph --enrich --auto-confirm
```

### Query Knowledge Graph
```bash
# Find papers by concept
lit query concept "transformer" --graph dl-graph --limit 20

# Find concepts by paper
lit query paper "https://arxiv.org/abs/1706.03762" --graph dl-graph
```

### Manage Knowledge Graphs
```bash
# List all graphs
lit graph-list

# View graph statistics
lit graph-stats dl-graph

# Visualize graph
lit graph-viz dl-graph --format mermaid --output graph.md

# Export graph
lit graph-export dl-graph --output dl-graph.json
```

## Use Cases

### 1. Quick Field Onboarding
- Learn core concepts
- Detect prerequisite gaps
- Build knowledge graph
- Plan learning path

### 2. Deep Paper Understanding
- Analyze paper in depth
- Perform critical analysis
- Learn new concepts from paper
- Compare with related papers

### 3. Research Progress Tracking
- Monitor research topics
- Track latest papers
- Generate progress reports

### 4. Concept Comparison
- Compare technical approaches
- Evaluate different models
- Build comparison graphs

### 5. Review-Driven Knowledge Building
- Search and identify review papers
- Extract concepts from reviews
- Build persistent knowledge graphs
- Query concept-paper relationships

## Project Structure

```
ScholarGraph/
├── cli.ts                      # Unified CLI entry
├── config.ts                   # Configuration management
├── README.md                   # Project documentation
├── CHANGELOG.md                # Version history
├── SKILL.md                    # This file
│
├── shared/                     # Shared modules
│   ├── ai-provider.ts          # AI provider abstraction
│   ├── types.ts                # Type definitions
│   ├── validators.ts           # Parameter validation
│   ├── errors.ts               # Error handling
│   └── utils.ts                # Utility functions
│
├── literature-search/          # Literature search module
│   └── scripts/
│       ├── search.ts           # Search engine core
│       ├── types.ts            # Type definitions
│       ├── query-expander.ts   # Query expansion
│       ├── search-strategy.ts  # Complementary search strategy
│       ├── pdf-downloader.ts   # PDF download module
│       └── adapters/           # Search source adapters
│           ├── base.ts         # Adapter interface & base class
│           ├── registry.ts     # Adapter registry
│           ├── index.ts        # Barrel export
│           ├── arxiv-adapter.ts
│           ├── semantic-scholar-adapter.ts
│           ├── web-adapter.ts
│           ├── openalex-adapter.ts
│           ├── pubmed-adapter.ts
│           ├── crossref-adapter.ts
│           ├── dblp-adapter.ts
│           ├── ieee-adapter.ts
│           ├── core-adapter.ts
│           ├── unpaywall-adapter.ts
│           └── google-scholar-adapter.ts
│
├── concept-learner/            # Concept learning module
├── knowledge-gap-detector/     # Gap detection module
├── progress-tracker/           # Progress tracking module
├── paper-analyzer/             # Paper analysis module
│
├── review-detector/            # Review paper identification
│   └── scripts/
│       ├── detect.ts           # Multi-dimensional scoring
│       └── types.ts
│
├── concept-extractor/          # Concept extraction from reviews
│   └── scripts/
│       ├── extract.ts          # AI-powered extraction
│       └── types.ts
│
├── knowledge-graph/            # Knowledge graph module
│   └── scripts/
│       ├── graph.ts            # Graph building core
│       ├── indexer.ts          # Bidirectional indexing
│       ├── storage.ts          # SQLite persistence
│       └── enricher.ts         # Key paper association
│
├── workflows/                  # End-to-end workflows
│   └── review-to-graph.ts      # Review to graph pipeline
│
├── data/                       # Data directory (auto-created)
│   └── knowledge-graphs.db     # SQLite database
│
├── downloads/                  # PDF downloads (auto-created)
│   └── pdfs/
│       └── metadata.json       # Download index
│
└── test/                       # Tests and documentation
    ├── ADVANCED_FEATURES.md
    ├── TEST_RESULTS.md
    └── scripts/
```

## Supported AI Providers

### International
- OpenAI
- Anthropic (Claude)
- Azure OpenAI
- Groq
- Together AI
- Ollama (local)

### China
- 通义千问 (Qwen/DashScope)
- DeepSeek
- 智谱 AI (GLM)
- MiniMax
- Moonshot (Kimi)
- 百川 AI (Baichuan)
- 零一万物 (Yi)
- 豆包 (Doubao)

## Output Formats

### Markdown Reports
- Concept cards with definitions, components, history, applications
- Gap reports with analysis and recommendations
- Progress reports with trending topics
- Paper analyses with methods, experiments, contributions
- Comparison analyses with similarities and differences
- Critical analyses with strengths, weaknesses, and suggestions

### JSON Data
Structured data for programmatic processing

### Mermaid Diagrams
Interactive knowledge graphs and learning paths

## Requirements

- Bun 1.3+ or Node.js 18+
- AI provider API key
- Internet connection for paper search

## License

MIT License

## Links

- GitHub: https://github.com/Josephyb97/ScholarGraph
- Issues: https://github.com/Josephyb97/ScholarGraph/issues
- Discussions: https://github.com/Josephyb97/ScholarGraph/discussions

## Version

Current version: 1.0.0

## Author

ScholarGraph Team

---

*For detailed documentation, see README.md*
*For advanced features, see test/ADVANCED_FEATURES.md*
*For test results, see test/TEST_RESULTS.md*
