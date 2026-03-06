/**
 * Core README generation logic.
 * Takes analysis results and assembles a complete, formatted README.
 */

const fs = require("fs");
const path = require("path");

/**
 * Load a template file from references/templates/ if it exists.
 * Falls back to the default template structure.
 */
function loadTemplate(projectType) {
  const templatePath = path.join(__dirname, "..", "references", "templates", `${projectType}.md`);
  if (fs.existsSync(templatePath)) {
    return fs.readFileSync(templatePath, "utf-8");
  }
  return null;
}

/**
 * Generate the title and description section.
 */
function generateHeader(analysis) {
  const { metadata } = analysis;
  const lines = [];

  lines.push(`# ${metadata.name}`);
  lines.push("");

  // Badges
  const badges = [];
  if (metadata.license) {
    badges.push(`![License](https://img.shields.io/badge/license-${encodeURIComponent(metadata.license)}-blue.svg)`);
  }
  badges.push(`![Stars](https://img.shields.io/github/stars/${metadata.fullName}.svg)`);
  badges.push(`![Forks](https://img.shields.io/github/forks/${metadata.fullName}.svg)`);
  if (metadata.language && metadata.language !== "Unknown") {
    badges.push(`![Language](https://img.shields.io/badge/language-${encodeURIComponent(metadata.language)}-brightgreen.svg)`);
  }

  lines.push(badges.join(" "));
  lines.push("");

  if (metadata.description) {
    lines.push(metadata.description);
    lines.push("");
  }

  if (metadata.homepage) {
    lines.push(`**Homepage:** ${metadata.homepage}`);
    lines.push("");
  }

  if (metadata.topics && metadata.topics.length > 0) {
    lines.push(`**Topics:** ${metadata.topics.join(", ")}`);
    lines.push("");
  }

  return lines.join("\n");
}

/**
 * Generate the table of contents.
 */
function generateTOC(analysis) {
  const sections = [
    "Installation",
    "Usage",
  ];

  if (analysis.apiSurface.length > 0) {
    sections.push("API Documentation");
  }

  if (analysis.scripts.length > 0) {
    sections.push("Available Scripts");
  }

  if (analysis.directoryStructure.topLevelDirs.length > 0) {
    sections.push("Project Structure");
  }

  if (analysis.dependencies.length > 0) {
    sections.push("Dependencies");
  }

  if (analysis.directoryStructure.hasDocker) {
    sections.push("Docker");
  }

  sections.push("Contributing", "License");

  const lines = ["## Table of Contents", ""];
  for (const section of sections) {
    const anchor = section.toLowerCase().replace(/\s+/g, "-");
    lines.push(`- [${section}](#${anchor})`);
  }
  lines.push("");

  return lines.join("\n");
}

/**
 * Generate the installation section.
 */
function generateInstallation(analysis) {
  const lines = ["## Installation", ""];

  // Prerequisites
  const prereqs = [];
  if (analysis.projectType === "nodejs") prereqs.push("Node.js (v14 or higher)", "npm or yarn");
  if (analysis.projectType === "python") prereqs.push("Python 3.7+", "pip");
  if (analysis.projectType === "go") prereqs.push("Go 1.16+");
  if (analysis.projectType === "rust") prereqs.push("Rust (stable)", "Cargo");
  if (analysis.directoryStructure.hasDocker) prereqs.push("Docker (optional)");

  if (prereqs.length > 0) {
    lines.push("### Prerequisites");
    lines.push("");
    for (const p of prereqs) {
      lines.push(`- ${p}`);
    }
    lines.push("");
  }

  lines.push("### Setup");
  lines.push("");
  lines.push(analysis.installInstructions);
  lines.push("");

  return lines.join("\n");
}

/**
 * Generate the usage section.
 */
function generateUsage(analysis) {
  const lines = ["## Usage", ""];
  const { projectType, metadata, scripts: projectScripts } = analysis;

  if (projectType === "nodejs") {
    const startScript = projectScripts.find((s) => s.name === "start");
    if (startScript) {
      lines.push("```bash");
      lines.push("npm start");
      lines.push("```");
    } else {
      let pkg;
      try {
        pkg = analysis.fileContents["package.json"] ? JSON.parse(analysis.fileContents["package.json"]) : null;
      } catch {
        pkg = null;
      }
      if (pkg && pkg.main) {
        lines.push("```bash");
        lines.push(`node ${pkg.main}`);
        lines.push("```");
      } else {
        lines.push("```bash");
        lines.push(`# Run the project`);
        lines.push(`node index.js`);
        lines.push("```");
      }
    }
  } else if (projectType === "python") {
    lines.push("```bash");
    lines.push("python main.py");
    lines.push("```");
  } else if (projectType === "go") {
    lines.push("```bash");
    lines.push("go run .");
    lines.push("```");
  } else if (projectType === "rust") {
    lines.push("```bash");
    lines.push("cargo run");
    lines.push("```");
  } else {
    lines.push("Refer to the project documentation for usage instructions.");
  }

  lines.push("");

  // If .env.example exists, note env vars
  if (analysis.fileContents[".env.example"]) {
    lines.push("### Environment Variables");
    lines.push("");
    lines.push("Copy `.env.example` to `.env` and configure the required variables:");
    lines.push("");
    lines.push("```bash");
    lines.push("cp .env.example .env");
    lines.push("```");
    lines.push("");

    const envLines = analysis.fileContents[".env.example"].split("\n");
    const vars = envLines
      .filter((l) => l.trim() && !l.trim().startsWith("#"))
      .map((l) => l.split("=")[0].trim())
      .filter(Boolean);

    if (vars.length > 0) {
      lines.push("| Variable | Description |");
      lines.push("|----------|-------------|");
      for (const v of vars) {
        lines.push(`| \`${v}\` | Configure as needed |`);
      }
      lines.push("");
    }
  }

  return lines.join("\n");
}

/**
 * Generate API documentation section.
 */
function generateApiDocs(analysis) {
  if (analysis.apiSurface.length === 0) return "";

  const lines = ["## API Documentation", ""];

  // Group by file
  const byFile = {};
  for (const api of analysis.apiSurface) {
    if (!byFile[api.file]) byFile[api.file] = [];
    byFile[api.file].push(api);
  }

  for (const [file, apis] of Object.entries(byFile)) {
    lines.push(`### \`${file}\``);
    lines.push("");

    const classes = apis.filter((a) => a.type === "class");
    const functions = apis.filter((a) => a.type === "function");
    const exports = apis.filter((a) => a.type === "export");

    if (classes.length > 0) {
      lines.push("**Classes:**");
      lines.push("");
      for (const cls of classes) {
        lines.push(`- \`${cls.name}\``);
      }
      lines.push("");
    }

    if (functions.length > 0) {
      lines.push("**Functions:**");
      lines.push("");
      lines.push("| Function | Parameters |");
      lines.push("|----------|-----------|");
      for (const fn of functions) {
        const params = fn.params || "none";
        lines.push(`| \`${fn.name}\` | \`${params}\` |`);
      }
      lines.push("");
    }

    if (exports.length > 0) {
      lines.push("**Exports:**");
      lines.push("");
      for (const exp of exports) {
        lines.push(`- \`${exp.name}\``);
      }
      lines.push("");
    }
  }

  return lines.join("\n");
}

/**
 * Generate available scripts section.
 */
function generateScripts(analysis) {
  if (analysis.scripts.length === 0) return "";

  const lines = ["## Available Scripts", ""];
  lines.push("| Command | Description |");
  lines.push("|---------|-------------|");

  for (const script of analysis.scripts) {
    lines.push(`| \`${script.run}\` | ${script.command} |`);
  }

  lines.push("");
  return lines.join("\n");
}

/**
 * Generate project structure section.
 */
function generateProjectStructure(analysis) {
  const dirs = analysis.directoryStructure.topLevelDirs;
  if (dirs.length === 0) return "";

  const lines = ["## Project Structure", "", "```"];

  // Show top-level layout
  lines.push(`${analysis.metadata.name}/`);
  for (let i = 0; i < dirs.length; i++) {
    const prefix = i === dirs.length - 1 ? "└── " : "├── ";
    lines.push(`${prefix}${dirs[i]}/`);
  }

  // Show notable top-level files
  const topFiles = analysis.tree
    .filter((f) => f.type === "file" && !f.path.includes("/"))
    .map((f) => f.path)
    .sort();

  for (let i = 0; i < topFiles.length; i++) {
    const prefix = i === topFiles.length - 1 ? "└── " : "├── ";
    lines.push(`${prefix}${topFiles[i]}`);
  }

  lines.push("```", "");
  return lines.join("\n");
}

/**
 * Generate dependencies section.
 */
function generateDependencies(analysis) {
  if (analysis.dependencies.length === 0) return "";

  const lines = ["## Dependencies", ""];
  const prodDeps = analysis.dependencies.filter((d) => !d.dev);
  const devDeps = analysis.dependencies.filter((d) => d.dev);

  if (prodDeps.length > 0) {
    lines.push("### Production");
    lines.push("");
    lines.push("| Package | Version |");
    lines.push("|---------|---------|");
    for (const dep of prodDeps) {
      lines.push(`| ${dep.name} | ${dep.version} |`);
    }
    lines.push("");
  }

  if (devDeps.length > 0) {
    lines.push("### Development");
    lines.push("");
    lines.push("| Package | Version |");
    lines.push("|---------|---------|");
    for (const dep of devDeps) {
      lines.push(`| ${dep.name} | ${dep.version} |`);
    }
    lines.push("");
  }

  return lines.join("\n");
}

/**
 * Generate Docker section.
 */
function generateDocker(analysis) {
  if (!analysis.directoryStructure.hasDocker) return "";

  const lines = ["## Docker", ""];

  if (analysis.fileContents["Dockerfile"]) {
    lines.push("### Build");
    lines.push("");
    lines.push("```bash");
    lines.push(`docker build -t ${analysis.metadata.name} .`);
    lines.push("```");
    lines.push("");
    lines.push("### Run");
    lines.push("");
    lines.push("```bash");
    lines.push(`docker run -p 3000:3000 ${analysis.metadata.name}`);
    lines.push("```");
    lines.push("");
  }

  if (analysis.fileContents["docker-compose.yml"] || analysis.fileContents["docker-compose.yaml"]) {
    lines.push("### Docker Compose");
    lines.push("");
    lines.push("```bash");
    lines.push("docker-compose up -d");
    lines.push("```");
    lines.push("");
  }

  return lines.join("\n");
}

/**
 * Generate contributing section.
 */
function generateContributing(analysis) {
  const lines = ["## Contributing", ""];

  if (analysis.fileContents["CONTRIBUTING.md"]) {
    lines.push("Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.");
  } else {
    lines.push("Contributions are welcome! Please feel free to submit a Pull Request.");
    lines.push("");
    lines.push("1. Fork the repository");
    lines.push("2. Create your feature branch (`git checkout -b feature/amazing-feature`)");
    lines.push("3. Commit your changes (`git commit -m 'Add some amazing feature'`)");
    lines.push("4. Push to the branch (`git push origin feature/amazing-feature`)");
    lines.push("5. Open a Pull Request");
  }

  lines.push("");
  return lines.join("\n");
}

/**
 * Generate license section.
 */
function generateLicense(analysis) {
  const lines = ["## License", ""];

  if (analysis.metadata.license) {
    lines.push(`This project is licensed under the ${analysis.metadata.license} License - see the [LICENSE](LICENSE) file for details.`);
  } else {
    lines.push("See the [LICENSE](LICENSE) file for details.");
  }

  lines.push("");
  return lines.join("\n");
}

/**
 * Assemble all sections into a complete README.
 */
function generateReadme(analysis) {
  const sections = [
    generateHeader(analysis),
    generateTOC(analysis),
    generateInstallation(analysis),
    generateUsage(analysis),
    generateApiDocs(analysis),
    generateScripts(analysis),
    generateProjectStructure(analysis),
    generateDependencies(analysis),
    generateDocker(analysis),
    generateContributing(analysis),
    generateLicense(analysis),
  ];

  // Filter out empty sections and join
  return sections.filter((s) => s.trim().length > 0).join("\n");
}

module.exports = {
  loadTemplate,
  generateHeader,
  generateTOC,
  generateInstallation,
  generateUsage,
  generateApiDocs,
  generateScripts,
  generateProjectStructure,
  generateDependencies,
  generateDocker,
  generateContributing,
  generateLicense,
  generateReadme,
};
