import { spawnSync } from "node:child_process";
import { join, writeJson, exists } from "./utils.mjs";
import { DEFAULT_SLIDES } from "./slide-copy.mjs";

export function renderSlides({
  slidesDir,
  fontPath,
  slides = DEFAULT_SLIDES,
  style,
  dryRun = false,
}) {
  if (!Array.isArray(slides) || slides.length !== 6) {
    throw new Error("renderSlides requires exactly 6 slide lines.");
  }
  const outDir = join(slidesDir, "..");
  const specPath = join(outDir, "_slide_spec.json");
  writeJson(specPath, { slides, style });

  if (dryRun) {
    return {
      produced: Array.from({ length: 6 }, (_, idx) =>
        join(slidesDir, `slide_${String(idx + 1).padStart(2, "0")}.png`)
      ),
      specPath,
      skipped: true,
    };
  }

  const result = spawnSync(
    "python3",
    [
      "scripts/render_slides_pillow.py",
      "--spec",
      specPath,
      "--out",
      slidesDir,
      "--font",
      fontPath,
    ],
    { stdio: "inherit" }
  );

  if (result.error) {
    throw new Error(`Failed to run python renderer: ${result.error.message}`);
  }
  if (result.status !== 0) {
    throw new Error(
      `Slide renderer exited with non-zero status: ${result.status ?? "unknown"}`
    );
  }

  const produced = Array.from({ length: 6 }, (_, idx) =>
    join(slidesDir, `slide_${String(idx + 1).padStart(2, "0")}.png`)
  );
  for (const filePath of produced) {
    if (!exists(filePath)) {
      throw new Error(`Expected slide missing after render: ${filePath}`);
    }
  }
  return {
    produced,
    specPath,
    skipped: false,
  };
}

export { DEFAULT_SLIDES as EXACT_SLIDES };
