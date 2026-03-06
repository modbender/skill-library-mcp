import "dotenv/config";
import { computeExec } from "./client.js";

const out = await computeExec({
  session_id: "demo",
  cmd: "echo hello"
});

console.log(out);
