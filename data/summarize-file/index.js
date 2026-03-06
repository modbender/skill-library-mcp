import fs from "fs";

export async function run(params) {
  const filename = params.filename || "example.txt";
  const path = `C:\\Users\\user\\.openclaw\\workspace\\${filename}`;

  if (!fs.existsSync(path)) {
    return `File ${filename} does not exist in workspace.`;
  }

  const content = fs.readFileSync(path, "utf-8");
  const summary = content.slice(0, 500) + (content.length > 500 ? "..." : "");
  return summary;
}