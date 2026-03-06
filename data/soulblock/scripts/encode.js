const MAX_FRAGMENT_SIZE = 2048;

const content = process.argv.slice(2).join(" ");

if (!content) {
  console.error('Usage: node scripts/encode.js "Your fragment content"');
  process.exit(1);
}

const bytes = Buffer.from(content, "utf8");

if (bytes.length === 0) {
  console.error("Error: Content is empty.");
  process.exit(1);
}

if (bytes.length > MAX_FRAGMENT_SIZE) {
  console.error(
    `Error: Content is ${bytes.length} bytes, exceeds ${MAX_FRAGMENT_SIZE} byte limit.`,
  );
  process.exit(1);
}

const decoded = bytes.toString("utf8");
if (decoded !== content) {
  console.error("Warning: Content may contain characters that do not round-trip cleanly.");
}

console.log(`0x${bytes.toString("hex")}`);
