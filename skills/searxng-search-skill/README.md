# SearXNG Advanced Search Skill

A comprehensive Python library for interacting with SearXNG instances with advanced features including retry logic, timeout handling, and support for both local and remote instances.

## Features

- ✅ Comprehensive retry logic with exponential backoff
- ✅ Timeout handling
- ✅ Local and remote instance support
- ✅ Multiple search categories
- ✅ Advanced search operators
- ✅ Structured result objects
- ✅ Health checking
- ✅ Autocomplete support
- ✅ Engine-specific searches
- ✅ Multi-category searches
- ✅ Safe search filtering
- ✅ Time range filtering

## Installation

```bash
pip install searxng-skill # Not yet ready
```

## Or install from source:

```bash
git clone https://github.com/mouaad-ops/searxng-search-skill.git
cd searxng-skill
pip install -e .
```

## Quick Start

```python
from searxng_skill import SearXNGSkill, SearchCategory, TimeRange

# Initialize with local instance
skill = SearXNGSkill(instance_url="http://localhost:8080")

# Basic search
results = skill.search("Python programming")

# Category search
news = skill.news_search("AI", time_range=TimeRange.DAY)

# Advanced search
advanced = skill.advanced_search(
    query="machine learning",
    exact_phrase="deep learning",
    exclude_words=["tutorial"],
    site="github.com"
)
```