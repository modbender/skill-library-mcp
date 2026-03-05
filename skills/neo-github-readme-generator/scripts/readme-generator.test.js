const { describe, it } = require("node:test");
const assert = require("node:assert/strict");

const {
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
} = require("./readme-generator");

function makeAnalysis(overrides = {}) {
  return {
    projectType: "nodejs",
    metadata: {
      name: "test-project",
      fullName: "owner/test-project",
      description: "A test project for unit tests",
      language: "JavaScript",
      license: "MIT",
      stars: 42,
      forks: 10,
      topics: ["testing", "example"],
      homepage: "https://example.com",
      htmlUrl: "https://github.com/owner/test-project",
    },
    installInstructions: "```bash\nnpm install\n```",
    dependencies: [
      { name: "express", version: "^4.18.0", dev: false },
      { name: "jest", version: "^29.0.0", dev: true },
    ],
    scripts: [
      { name: "start", command: "node index.js", run: "npm run start" },
      { name: "test", command: "jest", run: "npm run test" },
    ],
    apiSurface: [
      { file: "src/app.js", type: "function", name: "createApp", params: "config" },
      { file: "src/app.js", type: "class", name: "Application", params: "" },
    ],
    directoryStructure: {
      hasSrc: true,
      hasTests: true,
      hasDocs: false,
      hasDocker: false,
      hasCI: true,
      hasConfig: true,
      topLevelDirs: ["src", "test", ".github"],
      totalFiles: 15,
      totalDirs: 5,
    },
    tree: [
      { path: "src", type: "dir" },
      { path: "test", type: "dir" },
      { path: ".github", type: "dir" },
      { path: "package.json", type: "file" },
      { path: "README.md", type: "file" },
    ],
    fileContents: {
      "package.json": JSON.stringify({
        name: "test-project",
        main: "src/index.js",
        scripts: { start: "node src/index.js" },
      }),
    },
    ...overrides,
  };
}

describe("generateHeader", () => {
  it("includes project name as H1", () => {
    const result = generateHeader(makeAnalysis());
    assert.ok(result.startsWith("# test-project"));
  });

  it("includes badges", () => {
    const result = generateHeader(makeAnalysis());
    assert.ok(result.includes("img.shields.io"));
    assert.ok(result.includes("license-MIT"));
  });

  it("includes description", () => {
    const result = generateHeader(makeAnalysis());
    assert.ok(result.includes("A test project for unit tests"));
  });

  it("includes topics", () => {
    const result = generateHeader(makeAnalysis());
    assert.ok(result.includes("testing, example"));
  });

  it("includes homepage", () => {
    const result = generateHeader(makeAnalysis());
    assert.ok(result.includes("https://example.com"));
  });
});

describe("generateTOC", () => {
  it("includes basic sections", () => {
    const result = generateTOC(makeAnalysis());
    assert.ok(result.includes("Installation"));
    assert.ok(result.includes("Usage"));
    assert.ok(result.includes("Contributing"));
    assert.ok(result.includes("License"));
  });

  it("includes API Documentation when API surface exists", () => {
    const result = generateTOC(makeAnalysis());
    assert.ok(result.includes("API Documentation"));
  });

  it("excludes API Documentation when no API surface", () => {
    const result = generateTOC(makeAnalysis({ apiSurface: [] }));
    assert.ok(!result.includes("API Documentation"));
  });
});

describe("generateInstallation", () => {
  it("includes prerequisites for nodejs", () => {
    const result = generateInstallation(makeAnalysis());
    assert.ok(result.includes("Node.js"));
  });

  it("includes setup instructions", () => {
    const result = generateInstallation(makeAnalysis());
    assert.ok(result.includes("npm install"));
  });
});

describe("generateUsage", () => {
  it("uses npm start when start script exists", () => {
    const result = generateUsage(makeAnalysis());
    assert.ok(result.includes("npm start"));
  });

  it("falls back to node for generic nodejs projects", () => {
    const result = generateUsage(
      makeAnalysis({
        scripts: [],
        fileContents: { "package.json": JSON.stringify({ name: "test", main: "app.js" }) },
      })
    );
    assert.ok(result.includes("node app.js"));
  });
});

describe("generateApiDocs", () => {
  it("generates API docs grouped by file", () => {
    const result = generateApiDocs(makeAnalysis());
    assert.ok(result.includes("src/app.js"));
    assert.ok(result.includes("createApp"));
    assert.ok(result.includes("Application"));
  });

  it("returns empty string when no APIs", () => {
    const result = generateApiDocs(makeAnalysis({ apiSurface: [] }));
    assert.equal(result, "");
  });
});

describe("generateScripts", () => {
  it("generates script table", () => {
    const result = generateScripts(makeAnalysis());
    assert.ok(result.includes("npm run start"));
    assert.ok(result.includes("npm run test"));
  });

  it("returns empty string when no scripts", () => {
    const result = generateScripts(makeAnalysis({ scripts: [] }));
    assert.equal(result, "");
  });
});

describe("generateProjectStructure", () => {
  it("shows top-level directories", () => {
    const result = generateProjectStructure(makeAnalysis());
    assert.ok(result.includes("src/"));
    assert.ok(result.includes("test/"));
  });

  it("returns empty for no dirs", () => {
    const result = generateProjectStructure(
      makeAnalysis({
        directoryStructure: { ...makeAnalysis().directoryStructure, topLevelDirs: [] },
      })
    );
    assert.equal(result, "");
  });
});

describe("generateDependencies", () => {
  it("separates production and dev dependencies", () => {
    const result = generateDependencies(makeAnalysis());
    assert.ok(result.includes("Production"));
    assert.ok(result.includes("Development"));
    assert.ok(result.includes("express"));
    assert.ok(result.includes("jest"));
  });

  it("returns empty when no dependencies", () => {
    const result = generateDependencies(makeAnalysis({ dependencies: [] }));
    assert.equal(result, "");
  });
});

describe("generateDocker", () => {
  it("generates docker section when Dockerfile exists", () => {
    const analysis = makeAnalysis({
      directoryStructure: { ...makeAnalysis().directoryStructure, hasDocker: true },
      fileContents: {
        ...makeAnalysis().fileContents,
        Dockerfile: "FROM node:18",
      },
    });
    const result = generateDocker(analysis);
    assert.ok(result.includes("docker build"));
    assert.ok(result.includes("docker run"));
  });

  it("returns empty when no Docker", () => {
    const result = generateDocker(makeAnalysis());
    assert.equal(result, "");
  });
});

describe("generateContributing", () => {
  it("generates default contributing section", () => {
    const result = generateContributing(makeAnalysis());
    assert.ok(result.includes("Pull Request"));
    assert.ok(result.includes("Fork"));
  });

  it("references CONTRIBUTING.md if it exists", () => {
    const result = generateContributing(
      makeAnalysis({
        fileContents: { ...makeAnalysis().fileContents, "CONTRIBUTING.md": "# Contributing guide" },
      })
    );
    assert.ok(result.includes("CONTRIBUTING.md"));
  });
});

describe("generateLicense", () => {
  it("shows license type", () => {
    const result = generateLicense(makeAnalysis());
    assert.ok(result.includes("MIT"));
  });

  it("falls back when no license", () => {
    const result = generateLicense(
      makeAnalysis({ metadata: { ...makeAnalysis().metadata, license: null } })
    );
    assert.ok(result.includes("LICENSE"));
  });
});

describe("generateReadme", () => {
  it("produces a complete README with all sections", () => {
    const readme = generateReadme(makeAnalysis());
    assert.ok(readme.includes("# test-project"));
    assert.ok(readme.includes("## Installation"));
    assert.ok(readme.includes("## Usage"));
    assert.ok(readme.includes("## API Documentation"));
    assert.ok(readme.includes("## Contributing"));
    assert.ok(readme.includes("## License"));
  });

  it("generated README passes validation", () => {
    const { validate } = require("./validator");
    const readme = generateReadme(makeAnalysis());
    const result = validate(readme);
    assert.equal(result.valid, true);
    assert.equal(result.errors.length, 0);
  });
});
