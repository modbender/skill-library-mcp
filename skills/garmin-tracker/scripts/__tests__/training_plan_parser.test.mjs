import assert from "node:assert/strict";
import fs from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { normalizeWeek, parseCalendarUpcomingFromLines } from "../training_plan_parser.mjs";

const fixturePath = path.resolve(
  process.cwd(),
  "skills/garmin-tracker/scripts/__tests__/fixtures/training-plan-lines.json",
);

test("normalizeWeek parses short and textual formats", () => {
  assert.equal(normalizeWeek("W6"), "W06");
  assert.equal(normalizeWeek("Week 12"), "W12");
  assert.equal(normalizeWeek("Semana 3"), "W03");
  assert.equal(normalizeWeek("No week here"), null);
});

test("parseCalendarUpcomingFromLines extracts upcoming workouts with inferred week", async () => {
  const fixture = JSON.parse(await fs.readFile(fixturePath, "utf8"));
  const parsed = parseCalendarUpcomingFromLines(fixture.lines, fixture.today);

  assert.equal(parsed.inferredWeek, "W06");
  assert.deepEqual(parsed.upcoming, [
    { date: "2026-02-17", scheduled: "W06D2-Easy Run" },
    { date: "2026-02-19", scheduled: "W06D4-Steady Run" },
    { date: "2026-02-22", scheduled: "W06D7-Long Run" },
    { date: "2026-02-24", scheduled: "W07D2-Steady Run" },
    { date: "2026-02-26", scheduled: "W07D4-Intervals" },
  ]);
});
