const { describe, it } = require("node:test");
const assert = require("node:assert/strict");

const {
  parseHeadings,
  checkRequiredSections,
  checkRecommendedSections,
  checkTitle,
  checkCodeBlocks,
  checkMinimumLength,
  checkImageAltText,
  validate,
} = require("./validator");

describe("parseHeadings", () => {
  it("parses headings from markdown", () => {
    const content = "# Title\n\n## Section One\n\n### Sub Section\n\n## Section Two";
    const headings = parseHeadings(content);
    assert.equal(headings.length, 4);
    assert.equal(headings[0].level, 1);
    assert.equal(headings[0].text, "Title");
    assert.equal(headings[1].level, 2);
    assert.equal(headings[1].text, "Section One");
    assert.equal(headings[2].level, 3);
    assert.equal(headings[3].text, "Section Two");
  });

  it("returns empty array for no headings", () => {
    const headings = parseHeadings("Just some text without headings.");
    assert.equal(headings.length, 0);
  });

  it("includes line numbers", () => {
    const content = "# Title\n\nSome text\n\n## Usage";
    const headings = parseHeadings(content);
    assert.equal(headings[0].line, 1);
    assert.equal(headings[1].line, 5);
  });
});

describe("checkRequiredSections", () => {
  it("returns no errors for complete README", () => {
    const content = [
      "# My Project",
      "## Installation",
      "## Usage",
      "## Contributing",
      "## License",
    ].join("\n");
    const errors = checkRequiredSections(content);
    assert.equal(errors.length, 0);
  });

  it("reports missing sections", () => {
    const content = "# My Project\n## Installation\n## Usage";
    const errors = checkRequiredSections(content);
    assert.ok(errors.length > 0);
    assert.ok(errors.some((e) => e.includes("Contributing")));
    assert.ok(errors.some((e) => e.includes("License")));
  });
});

describe("checkTitle", () => {
  it("passes with H1 heading", () => {
    const errors = checkTitle("# My Project\n\nSome content");
    assert.equal(errors.length, 0);
  });

  it("fails without H1 heading", () => {
    const errors = checkTitle("## Not a title\n\nSome content");
    assert.equal(errors.length, 1);
  });
});

describe("checkCodeBlocks", () => {
  it("passes with properly closed code blocks", () => {
    const content = "```bash\nnpm install\n```\n\n```js\nconsole.log('hi')\n```";
    const errors = checkCodeBlocks(content);
    assert.equal(errors.length, 0);
  });

  it("detects unclosed code blocks", () => {
    const content = "```bash\nnpm install\n\nSome more text";
    const errors = checkCodeBlocks(content);
    assert.equal(errors.length, 1);
    assert.ok(errors[0].includes("Unclosed"));
  });
});

describe("checkMinimumLength", () => {
  it("passes for sufficient content", () => {
    const lines = Array(15).fill("Some meaningful content line.").join("\n");
    const errors = checkMinimumLength(lines);
    assert.equal(errors.length, 0);
  });

  it("fails for very short content", () => {
    const errors = checkMinimumLength("# Title\n\nShort.");
    assert.equal(errors.length, 1);
    assert.ok(errors[0].includes("too short"));
  });
});

describe("checkImageAltText", () => {
  it("passes with proper alt text", () => {
    const content = "![License](https://img.shields.io/badge/license-MIT-blue.svg)";
    const warnings = checkImageAltText(content);
    assert.equal(warnings.length, 0);
  });

  it("warns about empty alt text", () => {
    const content = "![](https://example.com/image.png)";
    const warnings = checkImageAltText(content);
    assert.equal(warnings.length, 1);
  });
});

describe("validate", () => {
  it("returns valid for a complete README", () => {
    const content = [
      "# My Project",
      "",
      "![License](https://img.shields.io/badge/license-MIT-blue.svg)",
      "",
      "A great project description.",
      "",
      "## Installation",
      "",
      "```bash",
      "npm install",
      "```",
      "",
      "## Usage",
      "",
      "```bash",
      "npm start",
      "```",
      "",
      "## API Documentation",
      "",
      "Some API docs here.",
      "",
      "## Project Structure",
      "",
      "```",
      "src/",
      "```",
      "",
      "## Dependencies",
      "",
      "express, lodash",
      "",
      "## Contributing",
      "",
      "Fork and submit a PR.",
      "",
      "## License",
      "",
      "MIT",
    ].join("\n");

    const result = validate(content);
    assert.equal(result.valid, true);
    assert.equal(result.errors.length, 0);
    assert.equal(result.score, 100);
  });

  it("returns invalid for an incomplete README", () => {
    const result = validate("## Just a section\n\nNo title, no nothing.");
    assert.equal(result.valid, false);
    assert.ok(result.errors.length > 0);
    assert.ok(result.score < 100);
  });

  it("calculates score based on errors and warnings", () => {
    const content = [
      "# Title",
      "",
      "Line 1", "Line 2", "Line 3", "Line 4", "Line 5",
      "Line 6", "Line 7", "Line 8", "Line 9", "Line 10",
      "",
      "## Installation",
      "## Usage",
      "## Contributing",
      "## License",
    ].join("\n");
    const result = validate(content);
    assert.equal(result.valid, true);
    // Should have warnings for missing recommended sections
    assert.ok(result.warnings.length > 0);
    assert.ok(result.score > 0);
    assert.ok(result.score <= 100);
  });
});
