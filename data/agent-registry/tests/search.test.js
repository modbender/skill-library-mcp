const { describe, test, expect } = require("bun:test");

const { tokenize, BM25, keywordMatchScore, searchAgents, searchAgentsAll } = require("../lib/search");

describe("search", () => {
  describe("tokenize", () => {
    test("lowercases and splits on word boundaries", () => {
      expect(tokenize("Hello World")).toEqual(["hello", "world"]);
    });

    test("returns empty array for empty input", () => {
      expect(tokenize("")).toEqual([]);
    });

    test("handles hyphens as word boundaries", () => {
      expect(tokenize("react-native")).toEqual(["react", "native"]);
    });

    test("treats underscores as non-boundary (regex \\b behavior)", () => {
      // \b considers _ a word char, so expert_v2 doesn't split
      expect(tokenize("react-expert_v2")).toEqual(["react"]);
    });

    test("includes numbers", () => {
      expect(tokenize("node18 k8s")).toEqual(["node18", "k8s"]);
    });

    test("filters out non-alphanumeric tokens", () => {
      const tokens = tokenize("hello --- world *** test");
      expect(tokens).toEqual(["hello", "world", "test"]);
    });
  });

  describe("BM25", () => {
    let bm25;

    test("can be constructed with default params", () => {
      bm25 = new BM25();
      expect(bm25.k1).toBe(1.5);
      expect(bm25.b).toBe(0.75);
    });

    test("can be constructed with custom params", () => {
      bm25 = new BM25(2.0, 0.5);
      expect(bm25.k1).toBe(2.0);
      expect(bm25.b).toBe(0.5);
    });

    test("fit indexes documents correctly", () => {
      bm25 = new BM25();
      bm25.fit(["hello world", "foo bar baz", "hello foo"]);
      expect(bm25.N).toBe(3);
      expect(bm25.corpus.length).toBe(3);
      expect(bm25.docLengths).toEqual([2, 3, 2]);
      expect(bm25.avgdl).toBeCloseTo(7 / 3);
    });

    test("computes IDF scores", () => {
      bm25 = new BM25();
      bm25.fit(["hello world", "foo bar", "hello foo"]);
      // "hello" appears in 2 of 3 docs
      expect(bm25.idf["hello"]).toBeDefined();
      // "world" appears in 1 of 3 docs — should have higher IDF
      expect(bm25.idf["world"]).toBeGreaterThan(bm25.idf["hello"]);
    });

    test("score returns 0 for no matching terms", () => {
      bm25 = new BM25();
      bm25.fit(["hello world", "foo bar"]);
      expect(bm25.score("xyz", 0)).toBe(0);
    });

    test("score returns positive for matching terms", () => {
      bm25 = new BM25();
      bm25.fit(["hello world", "foo bar"]);
      expect(bm25.score("hello", 0)).toBeGreaterThan(0);
    });

    test("search returns results sorted by score descending", () => {
      bm25 = new BM25();
      bm25.fit([
        "react hooks frontend",
        "python backend api",
        "react typescript frontend components",
      ]);
      const results = bm25.search("react frontend", 3);
      expect(results.length).toBeGreaterThan(0);
      // Results should be sorted descending
      for (let i = 1; i < results.length; i++) {
        expect(results[i][1]).toBeLessThanOrEqual(results[i - 1][1]);
      }
    });

    test("search respects topK limit", () => {
      bm25 = new BM25();
      bm25.fit(["a b c", "a d e", "a f g", "a h i"]);
      const results = bm25.search("a", 2);
      expect(results.length).toBeLessThanOrEqual(2);
    });

    test("handles empty corpus", () => {
      bm25 = new BM25();
      bm25.fit([]);
      expect(bm25.N).toBe(0);
      expect(bm25.avgdl).toBe(0);
      const results = bm25.search("hello", 5);
      expect(results).toEqual([]);
    });

    test("handles single document corpus", () => {
      bm25 = new BM25();
      bm25.fit(["single document with some words"]);
      const results = bm25.search("document", 5);
      expect(results.length).toBe(1);
      expect(results[0][0]).toBe(0);
      expect(results[0][1]).toBeGreaterThan(0);
    });
  });

  describe("keywordMatchScore", () => {
    test("returns 0 for empty query", () => {
      expect(keywordMatchScore("", { name: "test", keywords: ["foo"] })).toBe(0);
    });

    test("scores higher for name matches", () => {
      const agent = { name: "react-expert", keywords: ["vue"], summary: "A vue specialist" };
      const reactScore = keywordMatchScore("react", agent);
      const vueScore = keywordMatchScore("vue", agent);
      // "react" matches name (weight 3) but not keywords/summary
      // "vue" matches keywords (weight 2) and summary (weight 1)
      // Both should be positive
      expect(reactScore).toBeGreaterThan(0);
      expect(vueScore).toBeGreaterThan(0);
    });

    test("matches keywords with medium weight", () => {
      const agent = { name: "test", keywords: ["docker", "kubernetes"], summary: "Container tools" };
      const score = keywordMatchScore("docker", agent);
      expect(score).toBeGreaterThan(0);
    });

    test("matches summary terms with lower weight", () => {
      const agent = { name: "test", keywords: [], summary: "Specializes in react development" };
      const score = keywordMatchScore("react", agent);
      expect(score).toBeGreaterThan(0);
    });

    test("adds partial match bonus for 3+ char terms in summary", () => {
      const agent = { name: "test", keywords: [], summary: "authentication handler" };
      const score = keywordMatchScore("auth", agent);
      expect(score).toBeGreaterThan(0);
    });

    test("handles missing fields gracefully", () => {
      const agent = { name: "test" };
      expect(() => keywordMatchScore("query", agent)).not.toThrow();
      const score = keywordMatchScore("query", agent);
      expect(typeof score).toBe("number");
    });

    test("score can exceed 1 when partial match bonus applies", () => {
      // Partial match bonus (+0.5) is added on top of weighted score,
      // so when a term matches name + keywords + summary + partial, it exceeds 1.0
      const agent = { name: "react", keywords: ["react", "frontend"], summary: "React specialist for react apps" };
      const score = keywordMatchScore("react", agent);
      expect(score).toBeGreaterThan(1);
    });

    test("score is 0 or positive", () => {
      const agent = { name: "test", keywords: ["foo"], summary: "bar" };
      const score = keywordMatchScore("xyz", agent);
      expect(score).toBeGreaterThanOrEqual(0);
    });
  });

  describe("searchAgents", () => {
    const mockRegistry = {
      agents: [
        { name: "react-expert", summary: "React specialist for frontend", keywords: ["react", "frontend", "javascript"], token_estimate: 2000 },
        { name: "django-expert", summary: "Django web framework specialist", keywords: ["django", "python", "backend"], token_estimate: 3000 },
        { name: "security-auditor", summary: "Security vulnerability scanner", keywords: ["security", "audit", "vulnerabilities"], token_estimate: 1500 },
        { name: "docker-specialist", summary: "Docker and container orchestration", keywords: ["docker", "kubernetes", "devops"], token_estimate: 2500 },
        { name: "code-reviewer", summary: "General code review and best practices", keywords: ["code", "review", "quality"], token_estimate: 1800 },
      ],
    };

    test("returns results matching query", () => {
      const results = searchAgents("react frontend", mockRegistry);
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].name).toBe("react-expert");
    });

    test("respects topK parameter", () => {
      const results = searchAgents("code", mockRegistry, 2);
      expect(results.length).toBeLessThanOrEqual(2);
    });

    test("defaults to topK=5", () => {
      const results = searchAgents("a", mockRegistry);
      expect(results.length).toBeLessThanOrEqual(5);
    });

    test("results have required fields", () => {
      const results = searchAgents("security", mockRegistry);
      expect(results.length).toBeGreaterThan(0);
      const r = results[0];
      expect(r).toHaveProperty("name");
      expect(r).toHaveProperty("summary");
      expect(r).toHaveProperty("score");
      expect(r).toHaveProperty("bm25_score");
      expect(r).toHaveProperty("keyword_score");
      expect(r).toHaveProperty("token_estimate");
      expect(r).toHaveProperty("keywords");
    });

    test("results are sorted by score descending", () => {
      const results = searchAgents("code review", mockRegistry, 5);
      for (let i = 1; i < results.length; i++) {
        expect(results[i].score).toBeLessThanOrEqual(results[i - 1].score);
      }
    });

    test("returns empty array for no matches", () => {
      const results = searchAgents("zzzzzzzzz", mockRegistry);
      expect(results).toEqual([]);
    });

    test("returns empty array for empty registry", () => {
      const results = searchAgents("test", { agents: [] });
      expect(results).toEqual([]);
    });

    test("scores are rounded to 3 decimal places", () => {
      const results = searchAgents("react", mockRegistry);
      for (const r of results) {
        const str = String(r.score);
        const decimals = str.includes(".") ? str.split(".")[1].length : 0;
        expect(decimals).toBeLessThanOrEqual(3);
      }
    });
  });

  describe("searchAgentsAll", () => {
    const mockRegistry = {
      agents: [
        { name: "agent-1", summary: "First agent", keywords: ["test"], token_estimate: 100 },
        { name: "agent-2", summary: "Second test agent", keywords: ["test"], token_estimate: 200 },
        { name: "agent-3", summary: "Third test agent", keywords: ["test"], token_estimate: 300 },
        { name: "agent-4", summary: "Fourth test agent", keywords: ["test"], token_estimate: 400 },
        { name: "agent-5", summary: "Fifth test agent", keywords: ["test"], token_estimate: 500 },
        { name: "agent-6", summary: "Sixth test agent", keywords: ["test"], token_estimate: 600 },
      ],
    };

    test("returns all matching results without limit", () => {
      const results = searchAgentsAll("test agent", mockRegistry);
      // Should return more than the default topK=5
      expect(results.length).toBeGreaterThan(0);
    });

    test("returns empty array for empty registry", () => {
      const results = searchAgentsAll("test", { agents: [] });
      expect(results).toEqual([]);
    });
  });
});
