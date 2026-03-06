// Search Raysurfer cache. Usage: bun search.ts "task description"
const task = process.argv[2] ?? "Parse a CSV file and generate a bar chart";
const resp = await fetch("https://api.raysurfer.com/api/retrieve/search", {
  method: "POST",
  headers: { Authorization: `Bearer ${process.env.RAYSURFER_API_KEY}`, "Content-Type": "application/json" },
  body: JSON.stringify({ task, top_k: 5, min_verdict_score: 0.3 }),
});
console.log(JSON.stringify(await resp.json(), null, 2));
