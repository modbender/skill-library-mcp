# OpenClaw+ 🚀

A modular super-skill for Claude that combines essential developer tools and web capabilities into a unified, powerful workflow.

## What is OpenClaw+?

OpenClaw+ is a comprehensive skill that integrates seven core capabilities:

### Developer Skills
- **run_python** - Execute Python code with proper environment management
- **git_status** - Check repository status and track changes  
- **git_commit** - Commit changes with meaningful messages
- **install_package** - Install Python packages with dependency handling

### Web Skills
- **fetch_url** - Retrieve web content with robust error handling
- **call_api** - Make API requests with authentication and response parsing

## Key Features

✅ **Modular Design** - Use only what you need, when you need it
✅ **Robust Error Handling** - Graceful failure recovery at every step
✅ **Workflow Composition** - Chain operations seamlessly
✅ **Production-Ready** - Follows industry best practices
✅ **Well-Documented** - Clear examples and patterns

## Common Use Cases

### Data Pipeline
```python
install_package("pandas requests")
data = call_api("https://api.example.com/dataset")
run_python("process_data.py")
git_commit("feat: add cleaned dataset")
```

### Web Scraping & Analysis
```python
install_package("beautifulsoup4 lxml")
html = fetch_url("https://example.com/data")
run_python("parse_and_analyze.py")
git_commit("chore: update scraped data")
```

### API Testing
```python
install_package("pytest requests")
run_python("test_api_endpoints.py")
git_commit("test: add API integration tests")
```

## When to Use

Use OpenClaw+ when your task involves:
- Running Python scripts or code snippets
- Installing Python packages
- Checking git repository status
- Committing code changes
- Fetching content from URLs
- Making API calls
- Combining any of the above in a workflow

## Installation

This skill is designed to be used with Claude's skill system. Simply reference it in your Claude configuration to enable all capabilities.

## Documentation

See [SKILL.md](./SKILL.md) for complete documentation including:
- Detailed capability reference
- Workflow patterns and examples
- Error handling guidelines
- Security considerations
- Best practices
- Integration with other skills

## License

MIT License - see [LICENSE.txt](./LICENSE.txt) for details.

## Contributing

OpenClaw+ is designed to be extensible. Contributions are welcome for:
- Additional capabilities
- Improved error handling
- More workflow patterns
- Better documentation

---

**Created for developers who need powerful, integrated workflows with Claude** 🚀
