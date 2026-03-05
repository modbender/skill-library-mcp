---
name: exa-researcher
description: "Comprehensive research capabilities using Exa AI MCP tools. Use when you need to conduct web research, gather company information, find people, extract code context, or perform deep research tasks. Specifically triggers for: web searches, company research, people search, code context extraction, web crawling, and deep researcher workflows. Perfect for market research, competitive analysis, technical research, news gathering, and any knowledge-intensive research needs."
---

# Exa Researcher

## Overview

Exa Researcher provides powerful research capabilities through Exa AI's MCP tools, including web searches (basic and advanced), company and people research, code context extraction, web crawling, and deep research workflows.

## Core Capabilities

### 1. Web Search (Basic & Advanced)

**Basic Web Search** (`web_search_exa`)
- Quick web searches for general information
- Ideal for: factual queries, news, quick facts

**Advanced Web Search** (`web_search_advanced_exa`)
- More sophisticated search with filters and ranking
- Ideal for: detailed research, finding specific content types, narrowing results by freshness, region, etc.

### 2. Company Research (`company_research_exa`)
- Gather comprehensive information about companies
- Ideal for: competitive analysis, partner research, due diligence
- Use cases: company overview, financial data, recent news, leadership, products/services

### 3. People Search (`people_search_exa`)
- Find information about people by name or query
- Ideal for: background research, networking, finding experts
- Use cases: professional backgrounds, expertise areas, recent activity

### 4. Code Context (`get_code_context_exa`)
- Extract code context and technical information
- Ideal for: technical research, understanding codebases, finding code examples
- Use cases: understanding APIs, finding implementation patterns, technical documentation research

### 5. Web Crawling (`crawling_exa`)
- Systematic web crawling for comprehensive information gathering
- Ideal for: in-depth site research, content extraction, archiving
- Use cases: website analysis, content aggregation, research from specific domains

### 6. Deep Research (`deep_researcher_start`, `deep_researcher_check`)
- Long-running research workflows with progress tracking
- Ideal for: comprehensive multi-source research, trend analysis, information synthesis
- Use cases: research papers, market reports, feasibility studies, competitive intelligence

## Usage Guidelines

### When to Use Each Tool

| Task | Recommended Tool | Reason |
|------|------------------|--------|
| Quick facts, news | `web_search_exa` | Fast, simple queries |
| Detailed research with filters | `web_search_advanced_exa` | More control, better results |
| Company analysis | `company_research_exa` | Structured company data |
| Finding people/experts | `people_search_exa` | People-focused search |
| Technical/code research | `get_code_context_exa` | Code and API focused |
| Researching websites/domains | `crawling_exa` | Systematic site exploration |
| Long-term research projects | `deep_researcher_start` → `deep_researcher_check` | Multi-source, time-consuming |

### Research Workflow

1. **Identify the research goal** - What information do you need?
2. **Select the appropriate tool** - Match the task to the tool above
3. **Execute the search/research** - Call the Exa AI tool
4. **Analyze results** - Synthesize findings
5. **Iterate if needed** - Refine queries or use additional tools

## Advanced Use Cases

### Competitive Analysis
- Use `company_research_exa` for multiple competitors
- Combine with `web_search_advanced_exa` for recent news
- Document findings in structured format

### Market Research
- `web_search_advanced_exa` for market trends
- `crawling_exa` for industry reports and whitepapers
- Synthesize findings into market overview

### Technical Documentation Research
- `get_code_context_exa` for API documentation
- Find code examples and implementation patterns
- Extract technical specifications

### Background Research (People/Companies)
- `people_search_exa` for expertise matching
- `company_research_exa` for organizational context
- Combine for comprehensive profiles

### Long-Form Research Projects
- Use `deep_researcher_start` to initiate workflow
- Monitor progress with `deep_researcher_check`
- Let it run for complex, multi-source research needs

## Tips for Best Results

- **Be specific with queries** - More precise queries yield better results
- **Combine tools** - Multiple tools can provide comprehensive coverage
- **Use filters wisely** - Especially with advanced search (date ranges, regions, etc.)
- **Iterate** - Refine queries based on initial results
- **Store important findings** - Save significant research to memory
- **Consider search volume** - Complex searches may take longer