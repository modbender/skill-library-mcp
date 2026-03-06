const { describe, it } = require("node:test");
const assert = require("node:assert/strict");

const { parseRepoUrl } = require("./github-api");

describe("parseRepoUrl", () => {
  it("parses full HTTPS URL", () => {
    const result = parseRepoUrl("https://github.com/octokit/octokit.js");
    assert.equal(result.owner, "octokit");
    assert.equal(result.repo, "octokit.js");
  });

  it("parses HTTPS URL with .git suffix", () => {
    const result = parseRepoUrl("https://github.com/owner/repo.git");
    assert.equal(result.owner, "owner");
    assert.equal(result.repo, "repo");
  });

  it("parses shorthand format", () => {
    const result = parseRepoUrl("expressjs/express");
    assert.equal(result.owner, "expressjs");
    assert.equal(result.repo, "express");
  });

  it("parses shorthand with .git suffix", () => {
    const result = parseRepoUrl("owner/repo.git");
    assert.equal(result.owner, "owner");
    assert.equal(result.repo, "repo");
  });

  it("throws for invalid URL", () => {
    assert.throws(() => parseRepoUrl("not-a-valid-url"), /Invalid GitHub repository URL/);
  });

  it("throws for empty string", () => {
    assert.throws(() => parseRepoUrl(""), /Invalid GitHub repository URL/);
  });

  it("handles URL with trailing path elements", () => {
    const result = parseRepoUrl("https://github.com/owner/repo/tree/main");
    assert.equal(result.owner, "owner");
    assert.equal(result.repo, "repo");
  });
});
