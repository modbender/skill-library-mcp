// Upload code to Raysurfer cache. Usage: bun upload.ts "task description" path/to/file.py
import { readFileSync } from "node:fs";
import { basename } from "node:path";

const [task, filepath] = [process.argv[2], process.argv[3]];
if (!task || !filepath) { console.error("Usage: bun upload.ts <task> <file>"); process.exit(1); }
const content = readFileSync(filepath, "utf-8");
const resp = await fetch("https://api.raysurfer.com/api/store/execution-result", {
  method: "POST",
  headers: { Authorization: `Bearer ${process.env.RAYSURFER_API_KEY}`, "Content-Type": "application/json" },
  body: JSON.stringify({ task, file_written: { path: basename(filepath), content }, succeeded: true, auto_vote: true }),
});
console.log(JSON.stringify(await resp.json(), null, 2));
