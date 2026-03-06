/**
 * Repository structure parser and metadata extractor.
 * Analyzes file trees, package manifests, and source files
 * to extract structured data for README generation.
 */

/**
 * Detect the primary project type from repo metadata and file tree.
 * Returns one of: nodejs, python, go, rust, java, ruby, unknown
 */
function detectProjectType(metadata, tree) {
  const files = tree.filter((f) => f.type === "file").map((f) => f.path);

  if (files.includes("package.json")) return "nodejs";
  if (files.includes("requirements.txt") || files.includes("setup.py") || files.includes("pyproject.toml"))
    return "python";
  if (files.includes("go.mod")) return "go";
  if (files.includes("Cargo.toml")) return "rust";
  if (files.some((f) => f.endsWith(".java") || f === "pom.xml" || f === "build.gradle")) return "java";
  if (files.includes("Gemfile")) return "ruby";

  const langMap = {
    JavaScript: "nodejs",
    TypeScript: "nodejs",
    Python: "python",
    Go: "go",
    Rust: "rust",
    Java: "java",
    Ruby: "ruby",
  };
  return langMap[metadata.language] || "unknown";
}

/**
 * Extract installation instructions from project manifests.
 */
function extractInstallInstructions(projectType, fileContents) {
  const instructions = [];

  if (projectType === "nodejs" && fileContents["package.json"]) {
    let pkg;
    try {
      pkg = JSON.parse(fileContents["package.json"]);
    } catch {
      pkg = null;
    }

    instructions.push("```bash");
    if (pkg && pkg.name) {
      instructions.push(`# Clone the repository`);
      instructions.push(`git clone <repository-url>`);
      instructions.push(`cd ${pkg.name}`);
    }
    instructions.push("");
    instructions.push("# Install dependencies");
    instructions.push("npm install");

    if (pkg && pkg.scripts && pkg.scripts.build) {
      instructions.push("");
      instructions.push("# Build the project");
      instructions.push("npm run build");
    }
    instructions.push("```");
  } else if (projectType === "python") {
    instructions.push("```bash");
    instructions.push("# Clone the repository");
    instructions.push("git clone <repository-url>");
    instructions.push("cd <project-directory>");
    instructions.push("");
    instructions.push("# Create and activate virtual environment");
    instructions.push("python -m venv venv");
    instructions.push("source venv/bin/activate  # On Windows: venv\\Scripts\\activate");
    instructions.push("");

    if (fileContents["requirements.txt"]) {
      instructions.push("# Install dependencies");
      instructions.push("pip install -r requirements.txt");
    } else if (fileContents["setup.py"] || fileContents["pyproject.toml"]) {
      instructions.push("# Install the package");
      instructions.push("pip install -e .");
    }
    instructions.push("```");
  } else if (projectType === "go") {
    instructions.push("```bash");
    instructions.push("# Clone the repository");
    instructions.push("git clone <repository-url>");
    instructions.push("cd <project-directory>");
    instructions.push("");
    instructions.push("# Download dependencies");
    instructions.push("go mod download");
    instructions.push("");
    instructions.push("# Build");
    instructions.push("go build ./...");
    instructions.push("```");
  } else if (projectType === "rust") {
    instructions.push("```bash");
    instructions.push("# Clone the repository");
    instructions.push("git clone <repository-url>");
    instructions.push("cd <project-directory>");
    instructions.push("");
    instructions.push("# Build");
    instructions.push("cargo build --release");
    instructions.push("```");
  } else {
    instructions.push("```bash");
    instructions.push("# Clone the repository");
    instructions.push("git clone <repository-url>");
    instructions.push("cd <project-directory>");
    instructions.push("```");
    instructions.push("");
    instructions.push("Please refer to the project documentation for specific installation instructions.");
  }

  return instructions.join("\n");
}

/**
 * Extract dependencies from package manifests.
 */
function extractDependencies(projectType, fileContents) {
  const deps = [];

  if (projectType === "nodejs" && fileContents["package.json"]) {
    try {
      const pkg = JSON.parse(fileContents["package.json"]);
      if (pkg.dependencies) {
        for (const [name, version] of Object.entries(pkg.dependencies)) {
          deps.push({ name, version, dev: false });
        }
      }
      if (pkg.devDependencies) {
        for (const [name, version] of Object.entries(pkg.devDependencies)) {
          deps.push({ name, version, dev: true });
        }
      }
    } catch {
      // Invalid package.json
    }
  } else if (projectType === "python" && fileContents["requirements.txt"]) {
    const lines = fileContents["requirements.txt"].split("\n");
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith("#")) {
        const match = trimmed.match(/^([a-zA-Z0-9_-]+)([>=<~!]+.*)?$/);
        if (match) {
          deps.push({ name: match[1], version: match[2] || "*", dev: false });
        }
      }
    }
  }

  return deps;
}

/**
 * Extract script/command information from project manifests.
 */
function extractScripts(projectType, fileContents) {
  const scripts = [];

  if (projectType === "nodejs" && fileContents["package.json"]) {
    try {
      const pkg = JSON.parse(fileContents["package.json"]);
      if (pkg.scripts) {
        for (const [name, command] of Object.entries(pkg.scripts)) {
          scripts.push({ name, command, run: `npm run ${name}` });
        }
      }
    } catch {
      // Invalid package.json
    }
  }

  if (fileContents["Makefile"]) {
    const lines = fileContents["Makefile"].split("\n");
    for (const line of lines) {
      const match = line.match(/^([a-zA-Z_][a-zA-Z0-9_-]*):/);
      if (match && !match[1].startsWith(".")) {
        scripts.push({ name: match[1], command: `make ${match[1]}`, run: `make ${match[1]}` });
      }
    }
  }

  return scripts;
}

/**
 * Extract exported functions/classes from source files for API documentation.
 */
function extractApiSurface(fileContents, projectType) {
  const apis = [];

  for (const [filePath, content] of Object.entries(fileContents)) {
    if (projectType === "nodejs" && (filePath.endsWith(".js") || filePath.endsWith(".ts"))) {
      // Match exported functions
      const funcRegex = /(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)/g;
      let match;
      while ((match = funcRegex.exec(content)) !== null) {
        apis.push({
          file: filePath,
          type: "function",
          name: match[1],
          params: match[2].trim(),
        });
      }

      // Match module.exports assignments
      const exportRegex = /module\.exports\s*=\s*\{([^}]+)\}/;
      const exportMatch = exportRegex.exec(content);
      if (exportMatch) {
        const exported = exportMatch[1].split(",").map((s) => s.trim().split(/\s/)[0]);
        for (const name of exported) {
          if (name && !apis.some((a) => a.name === name)) {
            apis.push({ file: filePath, type: "export", name, params: "" });
          }
        }
      }

      // Match class declarations
      const classRegex = /(?:export\s+)?class\s+(\w+)/g;
      while ((match = classRegex.exec(content)) !== null) {
        apis.push({ file: filePath, type: "class", name: match[1], params: "" });
      }
    }

    if (projectType === "python" && filePath.endsWith(".py")) {
      // Match function definitions
      const defRegex = /def\s+(\w+)\s*\(([^)]*)\):/g;
      let match;
      while ((match = defRegex.exec(content)) !== null) {
        if (!match[1].startsWith("_")) {
          apis.push({ file: filePath, type: "function", name: match[1], params: match[2].trim() });
        }
      }

      // Match class definitions
      const classRegex = /class\s+(\w+)(?:\([^)]*\))?:/g;
      while ((match = classRegex.exec(content)) !== null) {
        apis.push({ file: filePath, type: "class", name: match[1], params: "" });
      }
    }
  }

  return apis;
}

/**
 * Analyze directory structure to identify key directories.
 */
function analyzeDirectoryStructure(tree) {
  const dirs = tree.filter((f) => f.type === "dir").map((f) => f.path);
  const files = tree.filter((f) => f.type === "file").map((f) => f.path);

  const structure = {
    hasSrc: dirs.some((d) => d === "src" || d.startsWith("src/")),
    hasTests: dirs.some((d) => ["test", "tests", "__tests__", "spec"].includes(d) || d.startsWith("test/")),
    hasDocs: dirs.some((d) => d === "docs" || d.startsWith("docs/")),
    hasDocker: files.includes("Dockerfile") || files.includes("docker-compose.yml") || files.includes("docker-compose.yaml"),
    hasCI: dirs.some((d) => d === ".github" || d.startsWith(".github/")),
    hasConfig: files.some((f) => f.startsWith(".") && (f.endsWith("rc") || f.endsWith(".json") || f.endsWith(".yml"))),
    topLevelDirs: dirs.filter((d) => !d.includes("/")).sort(),
    totalFiles: files.length,
    totalDirs: dirs.length,
  };

  return structure;
}

/**
 * Main analysis function: run all analyzers on gathered repo data.
 */
function analyzeRepo(repoData) {
  const { metadata, tree, fileContents } = repoData;

  const projectType = detectProjectType(metadata, tree);
  const installInstructions = extractInstallInstructions(projectType, fileContents);
  const dependencies = extractDependencies(projectType, fileContents);
  const scripts = extractScripts(projectType, fileContents);
  const apiSurface = extractApiSurface(fileContents, projectType);
  const directoryStructure = analyzeDirectoryStructure(tree);

  return {
    projectType,
    metadata,
    installInstructions,
    dependencies,
    scripts,
    apiSurface,
    directoryStructure,
    tree,
    fileContents,
  };
}

module.exports = {
  detectProjectType,
  extractInstallInstructions,
  extractDependencies,
  extractScripts,
  extractApiSurface,
  analyzeDirectoryStructure,
  analyzeRepo,
};
