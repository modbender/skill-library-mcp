/**
 * GitHub API integration module.
 * Handles authenticated requests, repository metadata fetching,
 * and file content retrieval.
 */

const { Octokit } = require("octokit");

/**
 * Parse a GitHub URL into owner and repo components.
 * Supports formats:
 *   https://github.com/owner/repo
 *   https://github.com/owner/repo.git
 *   owner/repo
 */
function parseRepoUrl(url) {
  const shorthandMatch = url.match(/^([^/\s]+)\/([^/\s]+)$/);
  if (shorthandMatch) {
    return { owner: shorthandMatch[1], repo: shorthandMatch[2].replace(/\.git$/, "") };
  }

  const urlMatch = url.match(/github\.com\/([^/]+)\/([^/\s#?]+)/);
  if (urlMatch) {
    return { owner: urlMatch[1], repo: urlMatch[2].replace(/\.git$/, "") };
  }

  throw new Error(`Invalid GitHub repository URL: ${url}`);
}

/**
 * Create an Octokit client, optionally authenticated with GITHUB_TOKEN.
 */
function createClient(token) {
  const options = {};
  if (token) {
    options.auth = token;
  }
  return new Octokit(options);
}

/**
 * Fetch repository metadata from the GitHub API.
 */
async function fetchRepoMetadata(octokit, owner, repo) {
  const { data } = await octokit.rest.repos.get({ owner, repo });
  return {
    name: data.name,
    fullName: data.full_name,
    description: data.description || "",
    language: data.language || "Unknown",
    defaultBranch: data.default_branch,
    stars: data.stargazers_count,
    forks: data.forks_count,
    license: data.license ? data.license.spdx_id : null,
    topics: data.topics || [],
    homepage: data.homepage || null,
    createdAt: data.created_at,
    updatedAt: data.updated_at,
    openIssues: data.open_issues_count,
    isArchived: data.archived,
    htmlUrl: data.html_url,
  };
}

/**
 * Fetch the repository file tree (recursive, first level).
 * Returns an array of { path, type, size } objects.
 */
async function fetchRepoTree(octokit, owner, repo, branch) {
  const { data } = await octokit.rest.git.getTree({
    owner,
    repo,
    tree_sha: branch,
    recursive: "1",
  });
  return data.tree
    .filter((item) => item.type === "blob" || item.type === "tree")
    .map((item) => ({
      path: item.path,
      type: item.type === "blob" ? "file" : "dir",
      size: item.size || 0,
    }));
}

/**
 * Fetch a single file's content (UTF-8 decoded).
 * Returns null if the file doesn't exist or is too large.
 */
async function fetchFileContent(octokit, owner, repo, path) {
  try {
    const { data } = await octokit.rest.repos.getContent({ owner, repo, path });
    if (data.type !== "file" || !data.content) {
      return null;
    }
    return Buffer.from(data.content, "base64").toString("utf-8");
  } catch (err) {
    if (err.status === 404) {
      return null;
    }
    throw err;
  }
}

/**
 * High-level function: gather all repo information needed for README generation.
 */
async function gatherRepoData(repoUrl) {
  const token = process.env.GITHUB_TOKEN || null;
  const { owner, repo } = parseRepoUrl(repoUrl);
  const octokit = createClient(token);

  const metadata = await fetchRepoMetadata(octokit, owner, repo);
  const tree = await fetchRepoTree(octokit, owner, repo, metadata.defaultBranch);

  // Fetch key files that inform documentation
  const keyFiles = [
    "package.json",
    "requirements.txt",
    "setup.py",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    "LICENSE",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
  ];

  const fileContents = {};
  const existingFiles = tree.filter((f) => f.type === "file").map((f) => f.path);

  for (const keyFile of keyFiles) {
    if (existingFiles.includes(keyFile)) {
      const content = await fetchFileContent(octokit, owner, repo, keyFile);
      if (content !== null) {
        fileContents[keyFile] = content;
      }
    }
  }

  // Fetch up to 5 source files for API analysis (small files only)
  const sourceExtensions = [".js", ".ts", ".py", ".go", ".rs", ".java", ".rb"];
  const sourceFiles = tree
    .filter(
      (f) =>
        f.type === "file" &&
        f.size < 50000 &&
        sourceExtensions.some((ext) => f.path.endsWith(ext)) &&
        !f.path.includes("node_modules") &&
        !f.path.includes("vendor") &&
        !f.path.includes("dist") &&
        !f.path.includes(".min.")
    )
    .slice(0, 5);

  for (const sf of sourceFiles) {
    const content = await fetchFileContent(octokit, owner, repo, sf.path);
    if (content !== null) {
      fileContents[sf.path] = content;
    }
  }

  return { metadata, tree, fileContents };
}

module.exports = {
  parseRepoUrl,
  createClient,
  fetchRepoMetadata,
  fetchRepoTree,
  fetchFileContent,
  gatherRepoData,
};
