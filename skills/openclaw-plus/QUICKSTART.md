# OpenClaw+ Quick Start Guide

Get up and running with OpenClaw+ in minutes!

## Installation

OpenClaw+ is a skill for Claude. To use it, simply enable it in your Claude skills configuration.

## Basic Usage

### 1. Running Python Code

The simplest operation - execute Python code directly:

```
User: "Run Python code to calculate the first 10 Fibonacci numbers"

Claude will:
1. Use run_python capability
2. Execute the code
3. Display results
```

### 2. Installing Packages

Before using external packages:

```
User: "Install numpy and create a random 3x3 matrix"

Claude will:
1. Install numpy using install_package
2. Run Python code to create and display the matrix
```

### 3. Git Operations

Track and commit your work:

```
User: "Create a file called notes.txt, check git status, and commit it"

Claude will:
1. Create the file
2. Use git_status to check changes
3. Use git_commit to save changes
```

### 4. Fetching Web Content

Get data from the web:

```
User: "Fetch the HTML from example.com and show me the title"

Claude will:
1. Use fetch_url to get the page
2. Parse and extract the title
3. Display the result
```

### 5. Calling APIs

Interact with web services:

```
User: "Get the first post from JSONPlaceholder API"

Claude will:
1. Use call_api to fetch data
2. Parse JSON response
3. Display the post information
```

## Common Workflows

### Data Analysis Pipeline

```
User: "Install pandas, create a sample sales dataset, analyze it, and save the results"
```

OpenClaw+ will orchestrate:
1. Package installation (install_package)
2. Data creation and analysis (run_python)
3. File saving
4. Git operations to track changes (git_status, git_commit)

### Web Scraping

```
User: "Install beautifulsoup4, scrape product data from example-shop.com, and save to a JSON file"
```

OpenClaw+ will handle:
1. Installing required packages
2. Fetching the webpage
3. Parsing and extracting data
4. Saving results
5. Committing to git

### API Integration Testing

```
User: "Test our API endpoints and create a report of which ones are working"
```

OpenClaw+ will execute:
1. Make API calls to each endpoint
2. Track successes and failures
3. Generate a report
4. Save and commit the report

## Tips & Tricks

### 1. Chain Operations

OpenClaw+ excels at multi-step workflows:

```
"Install matplotlib, generate a chart, create a README explaining it, and commit both files"
```

### 2. Error Handling

OpenClaw+ handles errors gracefully:

```
"Try to install package-that-doesnt-exist and let me know if it fails"
```

### 3. Combine with Other Skills

OpenClaw+ works great with other Claude skills:

```
"Fetch sales data from the API, process it with Python, and create an Excel report"
```
(This uses OpenClaw+ for data fetching/processing and xlsx skill for the report)

## Environment Notes

### Python Environment

- Default Python version: Check with `python --version`
- Package manager: pip with `--break-system-packages` flag
- Supported: Virtual environments (when needed)

### Git Environment

- Requires existing git repository
- Commit messages follow conventional commit format
- Supports staging specific files or all changes

### Network Access

- HTTP/HTTPS requests supported
- Timeouts configurable (default 30s)
- Authentication via headers or tokens

## Troubleshooting

### "Package installation failed"

- Check package name spelling
- Verify internet connectivity
- Some packages require system dependencies

### "Not a git repository"

- Initialize git first: `git init`
- Or work in an existing repository

### "Network error"

- Check URL is correct
- Verify internet connectivity
- Try with longer timeout

### "Python execution error"

- Check for syntax errors
- Ensure required packages are installed
- Review the full error message

## Next Steps

1. Review the [full documentation](SKILL.md)
2. Check out the [examples](evals/evals.json)
3. Try the [example implementation](scripts/implementation.py)
4. Explore workflow patterns for your use case

## Need Help?

- Review error messages carefully
- Check the documentation for specific capabilities
- Try breaking complex workflows into smaller steps
- Refer to example workflows in SKILL.md

---

Happy coding with OpenClaw+! 🚀
