import { describe, it, expect } from "vitest";
import { expandHome, parseTodos, markDone, editTodo, removeTodo, addTodo, searchTodos, extractTags, extractPriority, extractDueDate, cleanText, isOverdue, isDueToday, sortByDueDate, type TodoItem } from "./index.js";
import os from "node:os";
import path from "node:path";

// ---------------------------------------------------------------------------
// expandHome
// ---------------------------------------------------------------------------
describe("expandHome", () => {
  it("returns empty string for empty input", () => {
    expect(expandHome("")).toBe("");
  });

  it("expands bare ~ to home directory", () => {
    expect(expandHome("~")).toBe(os.homedir());
  });

  it("expands ~/path to home + path", () => {
    const result = expandHome("~/foo/bar");
    expect(result).toBe(path.join(os.homedir(), "foo/bar"));
  });

  it("leaves absolute paths unchanged", () => {
    expect(expandHome("/usr/local/bin")).toBe("/usr/local/bin");
  });

  it("leaves relative paths unchanged", () => {
    expect(expandHome("relative/path")).toBe("relative/path");
  });
});

// ---------------------------------------------------------------------------
// parseTodos
// ---------------------------------------------------------------------------
describe("parseTodos", () => {
  it("returns empty array for empty string", () => {
    expect(parseTodos("")).toEqual([]);
  });

  it("returns empty array for markdown without todos", () => {
    const md = "# Notes\n\nSome text here.\n";
    expect(parseTodos(md)).toEqual([]);
  });

  it("parses a single open todo", () => {
    const md = "- [ ] Buy milk";
    const result = parseTodos(md);
    expect(result).toHaveLength(1);
    expect(result[0]).toEqual({
      lineNo: 0,
      raw: "- [ ] Buy milk",
      done: false,
      text: "Buy milk",
      tags: [],
      priority: null,
      dueDate: null,
    });
  });

  it("parses a single done todo", () => {
    const md = "- [x] Buy milk";
    const result = parseTodos(md);
    expect(result).toHaveLength(1);
    expect(result[0].done).toBe(true);
    expect(result[0].text).toBe("Buy milk");
  });

  it("handles uppercase X as done", () => {
    const md = "- [X] Done task";
    const result = parseTodos(md);
    expect(result).toHaveLength(1);
    expect(result[0].done).toBe(true);
  });

  it("parses mixed open and done todos", () => {
    const md = [
      "# TODO",
      "",
      "- [ ] Open task",
      "- [x] Done task",
      "- [ ] Another open",
    ].join("\n");
    const result = parseTodos(md);
    expect(result).toHaveLength(3);
    expect(result[0]).toMatchObject({ done: false, text: "Open task", lineNo: 2 });
    expect(result[1]).toMatchObject({ done: true, text: "Done task", lineNo: 3 });
    expect(result[2]).toMatchObject({ done: false, text: "Another open", lineNo: 4 });
  });

  it("handles indented todos", () => {
    const md = "  - [ ] Indented task";
    const result = parseTodos(md);
    expect(result).toHaveLength(1);
    expect(result[0].text).toBe("Indented task");
  });

  it("ignores lines that look similar but are not todos", () => {
    const md = [
      "- Regular list item",
      "- [] Missing space",
      "- [a] Wrong character",
      "Some - [ ] inline text",
    ].join("\n");
    const result = parseTodos(md);
    expect(result).toHaveLength(0);
  });

  it("preserves correct line numbers with blank lines", () => {
    const md = [
      "# Header",   // 0
      "",            // 1
      "- [ ] First", // 2
      "",            // 3
      "- [x] Second", // 4
    ].join("\n");
    const result = parseTodos(md);
    expect(result[0].lineNo).toBe(2);
    expect(result[1].lineNo).toBe(4);
  });

  it("trims whitespace from todo text", () => {
    const md = "- [ ]   Lots of spaces   ";
    const result = parseTodos(md);
    expect(result[0].text).toBe("Lots of spaces");
  });
});

// ---------------------------------------------------------------------------
// markDone
// ---------------------------------------------------------------------------
describe("markDone", () => {
  it("marks an open item as done", () => {
    const md = "- [ ] Buy milk";
    const item: TodoItem = { lineNo: 0, raw: "- [ ] Buy milk", done: false, text: "Buy milk", tags: [], priority: null, dueDate: null };
    const result = markDone(md, item);
    expect(result).toBe("- [x] Buy milk");
  });

  it("marks the correct item in a multi-line document", () => {
    const md = [
      "# TODO",
      "- [ ] First",
      "- [ ] Second",
      "- [ ] Third",
    ].join("\n");
    const item: TodoItem = { lineNo: 2, raw: "- [ ] Second", done: false, text: "Second", tags: [], priority: null, dueDate: null };
    const result = markDone(md, item);
    const lines = result.split("\n");
    expect(lines[1]).toBe("- [ ] First");
    expect(lines[2]).toBe("- [x] Second");
    expect(lines[3]).toBe("- [ ] Third");
  });

  it("does not affect already-done items on other lines", () => {
    const md = [
      "- [x] Already done",
      "- [ ] To mark",
    ].join("\n");
    const item: TodoItem = { lineNo: 1, raw: "- [ ] To mark", done: false, text: "To mark", tags: [], priority: null, dueDate: null };
    const result = markDone(md, item);
    const lines = result.split("\n");
    expect(lines[0]).toBe("- [x] Already done");
    expect(lines[1]).toBe("- [x] To mark");
  });

  it("handles indented items", () => {
    const md = "  - [ ] Indented";
    const item: TodoItem = { lineNo: 0, raw: "  - [ ] Indented", done: false, text: "Indented", tags: [], priority: null, dueDate: null };
    const result = markDone(md, item);
    expect(result).toBe("- [x] Indented");
  });
});

// ---------------------------------------------------------------------------
// editTodo
// ---------------------------------------------------------------------------
describe("editTodo", () => {
  it("replaces the text of an open item", () => {
    const md = "- [ ] Buy milk";
    const item: TodoItem = { lineNo: 0, raw: "- [ ] Buy milk", done: false, text: "Buy milk", tags: [], priority: null, dueDate: null };
    const result = editTodo(md, item, "Buy oat milk");
    expect(result).toBe("- [ ] Buy oat milk");
  });

  it("replaces the text of a done item", () => {
    const md = "- [x] Buy milk";
    const item: TodoItem = { lineNo: 0, raw: "- [x] Buy milk", done: true, text: "Buy milk", tags: [], priority: null, dueDate: null };
    const result = editTodo(md, item, "Buy oat milk");
    expect(result).toBe("- [x] Buy oat milk");
  });

  it("edits the correct item in a multi-line document", () => {
    const md = [
      "# TODO",
      "- [ ] First",
      "- [ ] Second",
      "- [ ] Third",
    ].join("\n");
    const item: TodoItem = { lineNo: 2, raw: "- [ ] Second", done: false, text: "Second", tags: [], priority: null, dueDate: null };
    const result = editTodo(md, item, "Updated second");
    const lines = result.split("\n");
    expect(lines[1]).toBe("- [ ] First");
    expect(lines[2]).toBe("- [ ] Updated second");
    expect(lines[3]).toBe("- [ ] Third");
  });

  it("preserves done state when editing", () => {
    const md = [
      "- [x] Done task",
      "- [ ] Open task",
    ].join("\n");
    const item: TodoItem = { lineNo: 0, raw: "- [x] Done task", done: true, text: "Done task", tags: [], priority: null, dueDate: null };
    const result = editTodo(md, item, "Edited done task");
    const lines = result.split("\n");
    expect(lines[0]).toBe("- [x] Edited done task");
    expect(lines[1]).toBe("- [ ] Open task");
  });

  it("handles indented items", () => {
    const md = "  - [ ] Indented task";
    const item: TodoItem = { lineNo: 0, raw: "  - [ ] Indented task", done: false, text: "Indented task", tags: [], priority: null, dueDate: null };
    const result = editTodo(md, item, "New text");
    expect(result).toBe("  - [ ] New text");
  });
});

// ---------------------------------------------------------------------------
// editTodo + parseTodos round-trip
// ---------------------------------------------------------------------------
describe("editTodo + parseTodos round-trip", () => {
  it("edits an item and re-parses correctly", () => {
    const md = [
      "# TODO",
      "- [ ] Task A",
      "- [ ] Task B",
      "- [ ] Task C",
    ].join("\n");

    const todos = parseTodos(md);
    const updated = editTodo(md, todos[1], "Task B edited");
    const reParsed = parseTodos(updated);

    expect(reParsed).toHaveLength(3);
    expect(reParsed[0].text).toBe("Task A");
    expect(reParsed[1].text).toBe("Task B edited");
    expect(reParsed[2].text).toBe("Task C");
    expect(reParsed.every((t) => !t.done)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// removeTodo
// ---------------------------------------------------------------------------
describe("removeTodo", () => {
  it("removes a single item from a one-item document", () => {
    const md = "- [ ] Only task";
    const item: TodoItem = { lineNo: 0, raw: "- [ ] Only task", done: false, text: "Only task", tags: [], priority: null, dueDate: null };
    const result = removeTodo(md, item);
    expect(result).toBe("");
  });

  it("removes the correct item from a multi-line document", () => {
    const md = [
      "# TODO",
      "- [ ] First",
      "- [ ] Second",
      "- [ ] Third",
    ].join("\n");
    const item: TodoItem = { lineNo: 2, raw: "- [ ] Second", done: false, text: "Second", tags: [], priority: null, dueDate: null };
    const result = removeTodo(md, item);
    const lines = result.split("\n");
    expect(lines).toHaveLength(3);
    expect(lines[0]).toBe("# TODO");
    expect(lines[1]).toBe("- [ ] First");
    expect(lines[2]).toBe("- [ ] Third");
  });

  it("removes the first item", () => {
    const md = [
      "- [ ] First",
      "- [ ] Second",
    ].join("\n");
    const item: TodoItem = { lineNo: 0, raw: "- [ ] First", done: false, text: "First", tags: [], priority: null, dueDate: null };
    const result = removeTodo(md, item);
    expect(result).toBe("- [ ] Second");
  });

  it("removes the last item", () => {
    const md = [
      "- [ ] First",
      "- [ ] Second",
    ].join("\n");
    const item: TodoItem = { lineNo: 1, raw: "- [ ] Second", done: false, text: "Second", tags: [], priority: null, dueDate: null };
    const result = removeTodo(md, item);
    expect(result).toBe("- [ ] First");
  });

  it("removes a done item", () => {
    const md = [
      "- [ ] Open",
      "- [x] Done",
    ].join("\n");
    const item: TodoItem = { lineNo: 1, raw: "- [x] Done", done: true, text: "Done", tags: [], priority: null, dueDate: null };
    const result = removeTodo(md, item);
    expect(result).toBe("- [ ] Open");
  });

  it("preserves surrounding non-todo lines", () => {
    const md = [
      "# TODO",
      "",
      "- [ ] Task",
      "",
      "Some notes",
    ].join("\n");
    const item: TodoItem = { lineNo: 2, raw: "- [ ] Task", done: false, text: "Task", tags: [], priority: null, dueDate: null };
    const result = removeTodo(md, item);
    const lines = result.split("\n");
    expect(lines).toEqual(["# TODO", "", "", "Some notes"]);
  });
});

// ---------------------------------------------------------------------------
// removeTodo + parseTodos round-trip
// ---------------------------------------------------------------------------
describe("removeTodo + parseTodos round-trip", () => {
  it("removes an item and re-parses correctly", () => {
    const md = [
      "# TODO",
      "- [ ] Task A",
      "- [ ] Task B",
      "- [ ] Task C",
    ].join("\n");

    const todos = parseTodos(md);
    const updated = removeTodo(md, todos[1]); // remove Task B
    const reParsed = parseTodos(updated);

    expect(reParsed).toHaveLength(2);
    expect(reParsed[0].text).toBe("Task A");
    expect(reParsed[1].text).toBe("Task C");
  });
});

// ---------------------------------------------------------------------------
// addTodo
// ---------------------------------------------------------------------------
describe("addTodo", () => {
  it("appends to an empty document", () => {
    const result = addTodo("", "New task");
    expect(result).toContain("- [ ] New task");
  });

  it("appends after existing todos when no section header", () => {
    const md = [
      "# TODO",
      "",
      "- [ ] Existing task",
    ].join("\n");
    const result = addTodo(md, "New task");
    const lines = result.split("\n");
    const existingIdx = lines.indexOf("- [ ] Existing task");
    const newIdx = lines.indexOf("- [ ] New task");
    expect(newIdx).toBeGreaterThan(existingIdx);
  });

  it("inserts under section header when provided", () => {
    const md = [
      "# TODO",
      "",
      "- [ ] Existing task",
      "",
      "## Done",
      "",
      "- [x] Finished",
    ].join("\n");
    const result = addTodo(md, "New task", "# TODO");
    const lines = result.split("\n");
    // Should be inserted near the top, under the header
    const headerIdx = lines.findIndex((l) => l === "# TODO");
    const newIdx = lines.indexOf("- [ ] New task");
    expect(newIdx).toBeGreaterThan(headerIdx);
  });

  it("is case-insensitive for section header matching", () => {
    const md = [
      "# TODO",
      "",
      "- [ ] Existing",
    ].join("\n");
    const result = addTodo(md, "New task", "# todo");
    expect(result).toContain("- [ ] New task");
  });

  it("falls back to last todo position when header not found", () => {
    const md = [
      "# Tasks",
      "",
      "- [ ] First",
      "- [ ] Second",
    ].join("\n");
    const result = addTodo(md, "Third", "# Nonexistent Header");
    const lines = result.split("\n");
    const secondIdx = lines.indexOf("- [ ] Second");
    const thirdIdx = lines.indexOf("- [ ] Third");
    expect(thirdIdx).toBeGreaterThan(secondIdx);
  });

  it("appends at end when no todos and no header match", () => {
    const md = "# Notes\n\nSome text.";
    const result = addTodo(md, "First task", "# Nonexistent");
    const lines = result.split("\n");
    expect(lines[lines.length - 1]).toBe("- [ ] First task");
  });

  it("skips blank lines after header before inserting", () => {
    const md = [
      "# TODO",
      "",
      "",
      "- [ ] Existing",
    ].join("\n");
    const result = addTodo(md, "New task", "# TODO");
    const lines = result.split("\n");
    const newIdx = lines.indexOf("- [ ] New task");
    // Should skip past blank lines, inserting right before existing items
    expect(newIdx).toBeGreaterThanOrEqual(2);
  });

  it("handles document with only a header", () => {
    const md = "# TODO\n";
    const result = addTodo(md, "First task", "# TODO");
    expect(result).toContain("- [ ] First task");
  });

  it("adds multiple todos sequentially", () => {
    let md = "# TODO\n";
    md = addTodo(md, "First", "# TODO");
    md = addTodo(md, "Second", "# TODO");
    md = addTodo(md, "Third", "# TODO");
    const todos = parseTodos(md).filter((t) => !t.done);
    expect(todos).toHaveLength(3);
    // All three should be present
    const texts = todos.map((t) => t.text);
    expect(texts).toContain("First");
    expect(texts).toContain("Second");
    expect(texts).toContain("Third");
  });
});

// ---------------------------------------------------------------------------
// Integration: parseTodos + markDone round-trip
// ---------------------------------------------------------------------------
describe("parseTodos + markDone round-trip", () => {
  it("marks an item done and re-parses correctly", () => {
    const md = [
      "# TODO",
      "- [ ] Task A",
      "- [ ] Task B",
      "- [ ] Task C",
    ].join("\n");

    const todos = parseTodos(md);
    expect(todos.filter((t) => !t.done)).toHaveLength(3);

    const updated = markDone(md, todos[1]); // mark Task B done
    const reParsed = parseTodos(updated);

    expect(reParsed.filter((t) => !t.done)).toHaveLength(2);
    expect(reParsed.filter((t) => t.done)).toHaveLength(1);
    expect(reParsed.find((t) => t.done)!.text).toBe("Task B");
  });
});

// ---------------------------------------------------------------------------
// Integration: addTodo + parseTodos round-trip
// ---------------------------------------------------------------------------
describe("addTodo + parseTodos round-trip", () => {
  it("adds a todo and parses it back", () => {
    const md = "# TODO\n\n- [ ] Existing\n";
    const updated = addTodo(md, "New item");
    const todos = parseTodos(updated);
    const texts = todos.map((t) => t.text);
    expect(texts).toContain("Existing");
    expect(texts).toContain("New item");
    expect(todos.every((t) => !t.done)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// extractTags
// ---------------------------------------------------------------------------
describe("extractTags", () => {
  it("returns empty array for text without tags", () => {
    expect(extractTags("Buy milk")).toEqual([]);
  });

  it("extracts a single tag", () => {
    expect(extractTags("Buy milk #groceries")).toEqual(["groceries"]);
  });

  it("extracts multiple tags", () => {
    expect(extractTags("Fix login #dev #backend #urgent")).toEqual(["dev", "backend", "urgent"]);
  });

  it("lowercases tags", () => {
    expect(extractTags("Task #DevOps #CI")).toEqual(["devops", "ci"]);
  });

  it("deduplicates tags", () => {
    expect(extractTags("Fix #dev and test #dev")).toEqual(["dev"]);
  });

  it("supports hyphenated tags", () => {
    expect(extractTags("Deploy #front-end")).toEqual(["front-end"]);
  });

  it("does not match bare # without word chars", () => {
    expect(extractTags("Issue # 42")).toEqual([]);
  });

  it("extracts tags alongside priority markers", () => {
    expect(extractTags("Task #dev !high #ops")).toEqual(["dev", "ops"]);
  });
});

// ---------------------------------------------------------------------------
// extractPriority
// ---------------------------------------------------------------------------
describe("extractPriority", () => {
  it("returns null for text without priority", () => {
    expect(extractPriority("Buy milk")).toBeNull();
  });

  it("extracts !high", () => {
    expect(extractPriority("Fix bug !high")).toBe("high");
  });

  it("extracts !medium", () => {
    expect(extractPriority("Review PR !medium")).toBe("medium");
  });

  it("extracts !low", () => {
    expect(extractPriority("Update docs !low")).toBe("low");
  });

  it("is case-insensitive", () => {
    expect(extractPriority("Task !HIGH")).toBe("high");
    expect(extractPriority("Task !Medium")).toBe("medium");
  });

  it("returns first priority if multiple are present", () => {
    expect(extractPriority("Task !high !low")).toBe("high");
  });

  it("does not match !other words", () => {
    expect(extractPriority("Task !important")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// extractDueDate
// ---------------------------------------------------------------------------
describe("extractDueDate", () => {
  it("returns null if no due date is present", () => {
    expect(extractDueDate("Buy milk")).toBeNull();
  });

  it("extracts a valid due date", () => {
    expect(extractDueDate("Buy milk @due(2023-12-31)")).toBe("2023-12-31");
  });

  it("ignores invalid due date formats", () => {
    expect(extractDueDate("Buy milk @due(31-12-2023)")).toBeNull();
  });

  it("is case-insensitive", () => {
    expect(extractDueDate("Task @DUE(2024-01-15)")).toBe("2024-01-15");
  });

  it("extracts due date alongside tags and priority", () => {
    expect(extractDueDate("Fix bug #dev !high @due(2024-03-01)")).toBe("2024-03-01");
  });
});

// ---------------------------------------------------------------------------
// isOverdue
// ---------------------------------------------------------------------------
describe("isOverdue", () => {
  it("returns true when due date is before today", () => {
    expect(isOverdue("2024-01-01", "2024-01-02")).toBe(true);
  });

  it("returns false when due date is today", () => {
    expect(isOverdue("2024-01-01", "2024-01-01")).toBe(false);
  });

  it("returns false when due date is in the future", () => {
    expect(isOverdue("2024-01-02", "2024-01-01")).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// isDueToday
// ---------------------------------------------------------------------------
describe("isDueToday", () => {
  it("returns true when due date matches today", () => {
    expect(isDueToday("2024-01-01", "2024-01-01")).toBe(true);
  });

  it("returns false when due date is different", () => {
    expect(isDueToday("2024-01-01", "2024-01-02")).toBe(false);
    expect(isDueToday("2024-01-02", "2024-01-01")).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// cleanText
// ---------------------------------------------------------------------------
describe("cleanText", () => {
  it("returns text unchanged when no markers", () => {
    expect(cleanText("Buy milk")).toBe("Buy milk");
  });

  it("removes tags", () => {
    expect(cleanText("Buy milk #groceries")).toBe("Buy milk");
  });

  it("removes priority", () => {
    expect(cleanText("Fix bug !high")).toBe("Fix bug");
  });

  it("removes both tags and priority", () => {
    expect(cleanText("Fix login #dev !high #backend")).toBe("Fix login");
  });

  it("collapses extra whitespace", () => {
    expect(cleanText("#dev Fix bug !high #backend")).toBe("Fix bug");
  });

  it("removes due date annotations", () => {
    expect(cleanText("Buy milk @due(2023-12-31)")).toBe("Buy milk");
  });

  it("removes all markers together", () => {
    expect(cleanText("Fix bug #dev !high @due(2024-03-01)")).toBe("Fix bug");
  });
});

// ---------------------------------------------------------------------------
// parseTodos with tags/priority
// ---------------------------------------------------------------------------
describe("parseTodos with tags/priority", () => {
  it("parses tags from todo text", () => {
    const md = "- [ ] Fix login #dev #backend";
    const result = parseTodos(md);
    expect(result[0].tags).toEqual(["dev", "backend"]);
  });

  it("parses priority from todo text", () => {
    const md = "- [ ] Fix crash !high";
    const result = parseTodos(md);
    expect(result[0].priority).toBe("high");
  });

  it("parses both tags and priority", () => {
    const md = "- [ ] Deploy service #ops !medium #infra";
    const result = parseTodos(md);
    expect(result[0].tags).toEqual(["ops", "infra"]);
    expect(result[0].priority).toBe("medium");
  });

  it("returns empty tags and null priority for plain text", () => {
    const md = "- [ ] Plain task";
    const result = parseTodos(md);
    expect(result[0].tags).toEqual([]);
    expect(result[0].priority).toBeNull();
  });

  it("preserves full text including markers", () => {
    const md = "- [ ] Fix bug #dev !high";
    const result = parseTodos(md);
    expect(result[0].text).toBe("Fix bug #dev !high");
  });
});

// ---------------------------------------------------------------------------
// parseTodos with due dates
// ---------------------------------------------------------------------------
describe("parseTodos with due dates", () => {
  it("parses a todo with a due date", () => {
    const md = "- [ ] Buy milk @due(2023-12-31)";
    const result = parseTodos(md);
    expect(result).toHaveLength(1);
    expect(result[0].dueDate).toBe("2023-12-31");
    expect(result[0].text).toContain("@due(2023-12-31)");
  });

  it("parses a todo without a due date", () => {
    const md = "- [ ] Buy milk";
    const result = parseTodos(md);
    expect(result).toHaveLength(1);
    expect(result[0].dueDate).toBeNull();
  });

  it("handles multiple todos with and without due dates", () => {
    const md = [
      "- [ ] Task one",
      "- [ ] Task two @due(2023-12-31)",
      "- [ ] Task three",
    ].join("\n");
    const result = parseTodos(md);
    expect(result).toHaveLength(3);
    expect(result[0].dueDate).toBeNull();
    expect(result[1].dueDate).toBe("2023-12-31");
    expect(result[2].dueDate).toBeNull();
  });

  it("parses due date alongside tags and priority", () => {
    const md = "- [ ] Fix bug #dev !high @due(2024-03-01)";
    const result = parseTodos(md);
    expect(result[0].dueDate).toBe("2024-03-01");
    expect(result[0].tags).toEqual(["dev"]);
    expect(result[0].priority).toBe("high");
  });
});

// ---------------------------------------------------------------------------
// sortByDueDate
// ---------------------------------------------------------------------------
describe("sortByDueDate", () => {
  const today = "2024-06-15";

  const items: TodoItem[] = [
    { lineNo: 0, raw: "", done: false, text: "No due date", tags: [], priority: null, dueDate: null },
    { lineNo: 1, raw: "", done: false, text: "Future", tags: [], priority: null, dueDate: "2024-07-01" },
    { lineNo: 2, raw: "", done: false, text: "Overdue", tags: [], priority: null, dueDate: "2024-06-01" },
    { lineNo: 3, raw: "", done: false, text: "Due today", tags: [], priority: null, dueDate: "2024-06-15" },
  ];

  it("sorts overdue items first", () => {
    const sorted = sortByDueDate(items, today);
    expect(sorted[0].text).toBe("Overdue");
  });

  it("sorts due-today items second", () => {
    const sorted = sortByDueDate(items, today);
    expect(sorted[1].text).toBe("Due today");
  });

  it("sorts future due dates third", () => {
    const sorted = sortByDueDate(items, today);
    expect(sorted[2].text).toBe("Future");
  });

  it("sorts items without due dates last", () => {
    const sorted = sortByDueDate(items, today);
    expect(sorted[3].text).toBe("No due date");
  });

  it("sorts multiple overdue items by date ascending", () => {
    const overdueItems: TodoItem[] = [
      { lineNo: 0, raw: "", done: false, text: "Later overdue", tags: [], priority: null, dueDate: "2024-06-10" },
      { lineNo: 1, raw: "", done: false, text: "Earlier overdue", tags: [], priority: null, dueDate: "2024-05-01" },
    ];
    const sorted = sortByDueDate(overdueItems, today);
    expect(sorted[0].text).toBe("Earlier overdue");
    expect(sorted[1].text).toBe("Later overdue");
  });

  it("does not mutate the original array", () => {
    const original = [...items];
    sortByDueDate(items, today);
    expect(items).toEqual(original);
  });
});

// ---------------------------------------------------------------------------
// searchTodos
// ---------------------------------------------------------------------------
describe("searchTodos", () => {
  const sampleMd = [
    "- [ ] Fix login page #dev #frontend !high",
    "- [ ] Update README #docs !low",
    "- [ ] Review PR #backend #dev",
    "- [ ] Buy coffee",
    "- [x] Done task #dev !medium",
  ].join("\n");

  const allItems = parseTodos(sampleMd);
  const openItems = allItems.filter((t) => !t.done);

  it("returns all items for empty query parts (after trim)", () => {
    const result = searchTodos(openItems, "   ");
    expect(result).toHaveLength(openItems.length);
  });

  it("matches by text substring (case-insensitive)", () => {
    const result = searchTodos(openItems, "login");
    expect(result).toHaveLength(1);
    expect(result[0].text).toContain("login");
  });

  it("matches by text substring case-insensitively", () => {
    const result = searchTodos(openItems, "README");
    expect(result).toHaveLength(1);
    expect(result[0].text).toContain("README");
  });

  it("filters by single tag", () => {
    const result = searchTodos(openItems, "#dev");
    expect(result).toHaveLength(2); // Fix login, Review PR
    expect(result.every((t) => t.tags.includes("dev"))).toBe(true);
  });

  it("filters by multiple tags (AND logic)", () => {
    const result = searchTodos(openItems, "#dev #frontend");
    expect(result).toHaveLength(1);
    expect(result[0].text).toContain("login");
  });

  it("filters by priority", () => {
    const result = searchTodos(openItems, "!high");
    expect(result).toHaveLength(1);
    expect(result[0].priority).toBe("high");
  });

  it("combines tag and text filters", () => {
    const result = searchTodos(openItems, "#dev login");
    expect(result).toHaveLength(1);
    expect(result[0].text).toContain("login");
  });

  it("combines tag and priority filters", () => {
    const result = searchTodos(openItems, "#dev !high");
    expect(result).toHaveLength(1);
    expect(result[0].text).toContain("login");
  });

  it("returns empty array when no matches", () => {
    const result = searchTodos(openItems, "nonexistent");
    expect(result).toHaveLength(0);
  });

  it("returns empty when tag filter does not match", () => {
    const result = searchTodos(openItems, "#zzz");
    expect(result).toHaveLength(0);
  });

  it("returns empty when priority does not match any item", () => {
    const result = searchTodos(openItems, "!medium");
    // Only the done task has !medium, and openItems excludes done tasks
    expect(result).toHaveLength(0);
  });

  it("handles mixed case priority filter", () => {
    const result = searchTodos(openItems, "!HIGH");
    expect(result).toHaveLength(1);
  });

  it("matches text with multiple words", () => {
    const result = searchTodos(openItems, "Buy coffee");
    expect(result).toHaveLength(1);
    expect(result[0].text).toBe("Buy coffee");
  });
});

// ---------------------------------------------------------------------------
// searchTodos with due date filters
// ---------------------------------------------------------------------------
describe("searchTodos with due date filters", () => {
  const today = "2024-06-15";

  const sampleMd = [
    "- [ ] Overdue task @due(2024-06-01)",
    "- [ ] Due today task @due(2024-06-15)",
    "- [ ] Future task @due(2024-07-01)",
    "- [ ] No due date task",
  ].join("\n");

  const items = parseTodos(sampleMd);

  it("@due filters to items with any due date", () => {
    const result = searchTodos(items, "@due", today);
    expect(result).toHaveLength(3);
    expect(result.every((t) => t.dueDate !== null)).toBe(true);
  });

  it("@overdue filters to only overdue items", () => {
    const result = searchTodos(items, "@overdue", today);
    expect(result).toHaveLength(1);
    expect(result[0].text).toContain("Overdue");
  });

  it("@today filters to items due today", () => {
    const result = searchTodos(items, "@today", today);
    expect(result).toHaveLength(1);
    expect(result[0].text).toContain("Due today");
  });

  it("combines @overdue with text filter", () => {
    const result = searchTodos(items, "@overdue task", today);
    expect(result).toHaveLength(1);
    expect(result[0].dueDate).toBe("2024-06-01");
  });

  it("@overdue returns empty when nothing is overdue", () => {
    const result = searchTodos(items, "@overdue", "2024-01-01");
    expect(result).toHaveLength(0);
  });
});
