const { describe, it } = require("node:test");
const assert = require("node:assert/strict");

const {
  detectProjectType,
  extractInstallInstructions,
  extractDependencies,
  extractScripts,
  extractApiSurface,
  analyzeDirectoryStructure,
  analyzeRepo,
} = require("./analyzer");

describe("detectProjectType", () => {
  it("detects nodejs from package.json", () => {
    const metadata = { language: "JavaScript" };
    const tree = [{ path: "package.json", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "nodejs");
  });

  it("detects python from requirements.txt", () => {
    const metadata = { language: "Python" };
    const tree = [{ path: "requirements.txt", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "python");
  });

  it("detects python from setup.py", () => {
    const metadata = { language: "Python" };
    const tree = [{ path: "setup.py", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "python");
  });

  it("detects python from pyproject.toml", () => {
    const metadata = { language: "Python" };
    const tree = [{ path: "pyproject.toml", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "python");
  });

  it("detects go from go.mod", () => {
    const metadata = { language: "Go" };
    const tree = [{ path: "go.mod", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "go");
  });

  it("detects rust from Cargo.toml", () => {
    const metadata = { language: "Rust" };
    const tree = [{ path: "Cargo.toml", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "rust");
  });

  it("detects java from .java files", () => {
    const metadata = { language: "Java" };
    const tree = [{ path: "src/Main.java", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "java");
  });

  it("detects ruby from Gemfile", () => {
    const metadata = { language: "Ruby" };
    const tree = [{ path: "Gemfile", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "ruby");
  });

  it("falls back to language map when no manifest files", () => {
    const metadata = { language: "TypeScript" };
    const tree = [{ path: "index.ts", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "nodejs");
  });

  it("returns unknown for unrecognized language", () => {
    const metadata = { language: "Haskell" };
    const tree = [{ path: "Main.hs", type: "file" }];
    assert.equal(detectProjectType(metadata, tree), "unknown");
  });
});

describe("extractInstallInstructions", () => {
  it("generates nodejs instructions from package.json", () => {
    const result = extractInstallInstructions("nodejs", {
      "package.json": JSON.stringify({ name: "my-app", scripts: { build: "tsc" } }),
    });
    assert.ok(result.includes("npm install"));
    assert.ok(result.includes("npm run build"));
    assert.ok(result.includes("my-app"));
  });

  it("generates python instructions with requirements.txt", () => {
    const result = extractInstallInstructions("python", {
      "requirements.txt": "flask==2.0\nrequests>=2.28",
    });
    assert.ok(result.includes("pip install -r requirements.txt"));
    assert.ok(result.includes("python -m venv"));
  });

  it("generates python instructions with setup.py", () => {
    const result = extractInstallInstructions("python", {
      "setup.py": "from setuptools import setup",
    });
    assert.ok(result.includes("pip install -e ."));
  });

  it("generates go instructions", () => {
    const result = extractInstallInstructions("go", {});
    assert.ok(result.includes("go mod download"));
    assert.ok(result.includes("go build"));
  });

  it("generates rust instructions", () => {
    const result = extractInstallInstructions("rust", {});
    assert.ok(result.includes("cargo build --release"));
  });

  it("generates generic instructions for unknown type", () => {
    const result = extractInstallInstructions("unknown", {});
    assert.ok(result.includes("git clone"));
  });
});

describe("extractDependencies", () => {
  it("extracts nodejs dependencies", () => {
    const deps = extractDependencies("nodejs", {
      "package.json": JSON.stringify({
        dependencies: { express: "^4.18.0" },
        devDependencies: { jest: "^29.0.0" },
      }),
    });
    assert.equal(deps.length, 2);
    assert.equal(deps[0].name, "express");
    assert.equal(deps[0].dev, false);
    assert.equal(deps[1].name, "jest");
    assert.equal(deps[1].dev, true);
  });

  it("extracts python dependencies from requirements.txt", () => {
    const deps = extractDependencies("python", {
      "requirements.txt": "flask==2.0.1\nrequests>=2.28.0\n# comment\n\nnumpy",
    });
    assert.equal(deps.length, 3);
    assert.equal(deps[0].name, "flask");
    assert.equal(deps[2].name, "numpy");
  });

  it("returns empty array for unknown project type", () => {
    const deps = extractDependencies("go", {});
    assert.equal(deps.length, 0);
  });

  it("handles invalid package.json gracefully", () => {
    const deps = extractDependencies("nodejs", {
      "package.json": "not valid json{{{",
    });
    assert.equal(deps.length, 0);
  });
});

describe("extractScripts", () => {
  it("extracts npm scripts", () => {
    const scripts = extractScripts("nodejs", {
      "package.json": JSON.stringify({
        scripts: { start: "node index.js", test: "jest" },
      }),
    });
    assert.equal(scripts.length, 2);
    assert.equal(scripts[0].name, "start");
    assert.equal(scripts[0].run, "npm run start");
  });

  it("extracts Makefile targets", () => {
    const scripts = extractScripts("go", {
      Makefile: "build:\n\tgo build\ntest:\n\tgo test\n.PHONY: build test",
    });
    assert.ok(scripts.some((s) => s.name === "build"));
    assert.ok(scripts.some((s) => s.name === "test"));
    assert.ok(!scripts.some((s) => s.name === ".PHONY"));
  });
});

describe("extractApiSurface", () => {
  it("extracts JavaScript functions", () => {
    const apis = extractApiSurface(
      { "index.js": "function hello(name) { return name; }\nasync function fetchData(url, options) {}" },
      "nodejs"
    );
    assert.equal(apis.length, 2);
    assert.equal(apis[0].name, "hello");
    assert.equal(apis[0].params, "name");
    assert.equal(apis[1].name, "fetchData");
  });

  it("extracts JavaScript classes", () => {
    const apis = extractApiSurface(
      { "app.js": "class MyApp {\n  constructor() {}\n}\nexport class Router {}" },
      "nodejs"
    );
    const classes = apis.filter((a) => a.type === "class");
    assert.equal(classes.length, 2);
  });

  it("extracts module.exports", () => {
    const apis = extractApiSurface(
      { "lib.js": "module.exports = { foo, bar, baz };" },
      "nodejs"
    );
    const exports = apis.filter((a) => a.type === "export");
    assert.equal(exports.length, 3);
  });

  it("extracts Python functions", () => {
    const apis = extractApiSurface(
      { "app.py": "def handle_request(req):\n    pass\ndef _private():\n    pass\nclass Server:" },
      "python"
    );
    const fns = apis.filter((a) => a.type === "function");
    assert.equal(fns.length, 1); // _private is excluded
    assert.equal(fns[0].name, "handle_request");
  });

  it("extracts Python classes", () => {
    const apis = extractApiSurface(
      { "models.py": "class User(Base):\n    pass\nclass Order:\n    pass" },
      "python"
    );
    const classes = apis.filter((a) => a.type === "class");
    assert.equal(classes.length, 2);
  });
});

describe("analyzeDirectoryStructure", () => {
  it("identifies key directories", () => {
    const tree = [
      { path: "src", type: "dir" },
      { path: "test", type: "dir" },
      { path: "docs", type: "dir" },
      { path: ".github", type: "dir" },
      { path: "Dockerfile", type: "file" },
      { path: ".eslintrc", type: "file" },
    ];
    const result = analyzeDirectoryStructure(tree);
    assert.equal(result.hasSrc, true);
    assert.equal(result.hasTests, true);
    assert.equal(result.hasDocs, true);
    assert.equal(result.hasCI, true);
    assert.equal(result.hasDocker, true);
    assert.equal(result.hasConfig, true);
  });

  it("handles empty tree", () => {
    const result = analyzeDirectoryStructure([]);
    assert.equal(result.hasSrc, false);
    assert.equal(result.totalFiles, 0);
    assert.equal(result.totalDirs, 0);
  });
});

describe("analyzeRepo", () => {
  it("produces complete analysis from repo data", () => {
    const repoData = {
      metadata: { name: "test-repo", fullName: "owner/test-repo", language: "JavaScript" },
      tree: [
        { path: "package.json", type: "file", size: 100 },
        { path: "src", type: "dir", size: 0 },
        { path: "src/index.js", type: "file", size: 200 },
      ],
      fileContents: {
        "package.json": JSON.stringify({
          name: "test-repo",
          dependencies: { express: "^4.18.0" },
          scripts: { start: "node src/index.js" },
        }),
      },
    };

    const analysis = analyzeRepo(repoData);
    assert.equal(analysis.projectType, "nodejs");
    assert.ok(analysis.installInstructions.includes("npm install"));
    assert.equal(analysis.dependencies.length, 1);
    assert.equal(analysis.scripts.length, 1);
  });
});
