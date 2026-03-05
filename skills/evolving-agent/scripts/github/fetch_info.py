import sys
import json
import subprocess
import re
import urllib.request
import os

def extract_file_tree(readme: str) -> list:
    """
    Extract file tree structure from README by looking for directory listings.
    Returns a list of top-level directory paths.
    """
    file_tree = []

    # Pattern 1: Tree structure in README (e.g., src/, components/, etc.)
    tree_patterns = [
        r'([a-zA-Z0-9_-]+/)',  # Matches "src/", "components/", etc.
        r'`([a-zA-Z0-9_-]+)`',   # Matches `src`, `components`
    ]

    for pattern in tree_patterns:
        matches = re.findall(pattern, readme)
        for match in matches:
            if '/' in match or len(match) > 3:  # Only include actual directories
                if match not in file_tree:
                    file_tree.append(match)

        if file_tree:  # Stop if we found directories
            break

    # If no tree found, try extracting from code blocks
    if not file_tree:
        code_block_pattern = r'```.*?\n((?:.|\n)*?)```'
        blocks = re.findall(code_block_pattern, readme)
        for block in blocks:
            for pattern in tree_patterns:
                matches = re.findall(pattern, block)
                for match in matches:
                    if match not in file_tree:
                        file_tree.append(match)

    return file_tree[:50]  # Limit to first 50 entries


def get_repo_info(url):
    """
    Fetches repository information using git ls-remote and direct HTTP requests.
    Returns a dictionary with name, description, latest_hash, and readme content.
    """
    
    # Normalize URL (remove .git suffix if present)
    clean_url = url.rstrip('/')
    if clean_url.endswith('.git'):
        clean_url = clean_url[:-4]
        
    repo_name = clean_url.split('/')[-1]
    
    # 1. Get Latest Commit Hash (using git ls-remote to avoid full clone)
    try:
        result = subprocess.run(
            ['git', 'ls-remote', url, 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        # Output format: <hash>\tHEAD
        latest_hash = result.stdout.split()[0]
    except subprocess.TimeoutExpired:
        print(f"Error: Git command timed out for {url}", file=sys.stderr)
        latest_hash = "unknown"
    except subprocess.CalledProcessError as e:
        print(f"Error: Git command failed with exit code {e.returncode} for {url}", file=sys.stderr)
        if e.stderr:
            print(f"Git stderr: {e.stderr.strip()}", file=sys.stderr)
        latest_hash = "unknown"
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH", file=sys.stderr)
        latest_hash = "unknown"
    except IndexError:
        print(f"Error: Unexpected git ls-remote output format for {url}", file=sys.stderr)
        latest_hash = "unknown"
    except Exception as e:
        print(f"Unexpected error fetching git info: {type(e).__name__}: {e}", file=sys.stderr)
        latest_hash = "unknown"

    # 2. Fetch README (Try main, then master)
    readme_content = ""
    readme_url_base = clean_url.replace("github.com", "raw.githubusercontent.com")
    
    for branch in ["main", "master"]:
        try:
            readme_url = f"{readme_url_base}/{branch}/README.md"
            with urllib.request.urlopen(readme_url) as response:
                readme_content = response.read().decode('utf-8')
                break
        except Exception:
            continue
            
    if not readme_content:
        # Try lowercase readme
        for branch in ["main", "master"]:
            try:
                readme_url = f"{readme_url_base}/{branch}/readme.md"
                with urllib.request.urlopen(readme_url) as response:
                    readme_content = response.read().decode('utf-8')
                    break
            except Exception:
                continue

    # 3. Extract File Tree from README
    file_tree = extract_file_tree(readme_content)

    # 4. Construct Result
    return {
        "name": repo_name,
        "url": url,
        "latest_hash": latest_hash,
        "readme": readme_content[:10000], # Truncate if too huge to avoid context blowup
        "file_tree": file_tree
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_github_info.py <github_url>")
        sys.exit(1)
        
    url = sys.argv[1]
    info = get_repo_info(url)
    print(json.dumps(info, indent=2))
