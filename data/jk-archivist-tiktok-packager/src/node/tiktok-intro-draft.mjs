import { spawnSync } from "node:child_process";
import fs from "node:fs";
import { renderSlides } from "./render-slides.mjs";
import { loadPackagerSpec } from "./packager-spec.mjs";
import { postizUpload } from "./postiz-upload.mjs";
import { postizCreateDraft } from "./postiz-create-draft.mjs";
import { runPreflightChecks } from "./preflight-checks.mjs";
import { buildCaption } from "./write-caption.mjs";
import { preSlideRender } from "./hooks/pre-slide-render.mjs";
import { postCaptionBuild } from "./hooks/post-caption-build.mjs";
import { generateVariantSpecs } from "./variants/generator.mjs";
import { createRunLogger } from "./logger.mjs";
import {
  todayISO,
  ensureDir,
  writeText,
  writeJson,
  exists,
  optionalEnv,
  repoRoot,
  join,
} from "./utils.mjs";

function resolveFontPath() {
  const envFont = optionalEnv("TIKTOK_FONT_PATH");
  if (envFont && exists(envFont)) {
    return envFont;
  }
  if (envFont && !exists(envFont)) {
    throw new Error(
      `TIKTOK_FONT_PATH is set but file does not exist: ${envFont}`
    );
  }

  const fallback = "/System/Library/Fonts/Supplemental/Arial.ttf";
  if (exists(fallback)) {
    return fallback;
  }

  throw new Error(
    "No usable font found. Set TIKTOK_FONT_PATH to an absolute .ttf path."
  );
}

function verifySlides(slidesDir) {
  const result = spawnSync(
    "python3",
    ["scripts/verify_slides.py", "--dir", slidesDir],
    { stdio: "inherit" }
  );
  if (result.error) {
    throw new Error(`Failed to run slide verification: ${result.error.message}`);
  }
  if (result.status !== 0) {
    throw new Error(
      `Slide verification failed with status: ${result.status ?? "unknown"}`
    );
  }
}

function renderContactSheet(slidesDir, outFile) {
  const result = spawnSync(
    "python3",
    ["src/python/render_contact_sheet.py", "--slides-dir", slidesDir, "--out", outFile],
    { stdio: "inherit" }
  );
  if (result.error) {
    throw new Error(`Failed to run contact sheet renderer: ${result.error.message}`);
  }
  if (result.status !== 0) {
    throw new Error(`Contact sheet renderer failed with status: ${result.status ?? "unknown"}`);
  }
}

function parseArgs(argv = process.argv.slice(2)) {
  const args = {
    specPath: undefined,
    topic: undefined,
    template: undefined,
    stylePreset: undefined,
    enablePostiz: false,
    dryRun: false,
    postizOnly: false,
    noUpload: false,
    audience: undefined,
    ctaPack: undefined,
    hashtagPolicy: undefined,
    hashtagOverrides: [],
    locale: "en",
    abTest: undefined,
    resumeUpload: false,
    maxRetries: 3,
    timeoutMs: 15000,
    verbose: false,
  };
  for (let idx = 0; idx < argv.length; idx += 1) {
    const token = argv[idx];
    if (token === "--postiz") {
      args.enablePostiz = true;
      continue;
    }
    if (token === "--dry-run") {
      args.dryRun = true;
      continue;
    }
    if (token === "--postiz-only") {
      args.postizOnly = true;
      args.enablePostiz = true;
      continue;
    }
    if (token === "--no-upload") {
      args.noUpload = true;
      continue;
    }
    if (token === "--resume-upload") {
      args.resumeUpload = true;
      continue;
    }
    if (token === "--verbose") {
      args.verbose = true;
      continue;
    }
    if (token === "--spec") {
      args.specPath = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--topic") {
      args.topic = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--template") {
      args.template = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--style") {
      args.stylePreset = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--audience") {
      args.audience = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--cta-pack") {
      args.ctaPack = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--hashtag-policy") {
      args.hashtagPolicy = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--hashtag") {
      args.hashtagOverrides.push(argv[idx + 1]);
      idx += 1;
      continue;
    }
    if (token === "--locale") {
      args.locale = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--ab-test") {
      args.abTest = argv[idx + 1];
      idx += 1;
      continue;
    }
    if (token === "--max-retries") {
      args.maxRetries = Number.parseInt(argv[idx + 1], 10);
      idx += 1;
      continue;
    }
    if (token === "--timeout-ms") {
      args.timeoutMs = Number.parseInt(argv[idx + 1], 10);
      idx += 1;
      continue;
    }
  }
  return args;
}

async function uploadToPostiz({
  caption,
  slidePaths,
  outDir,
  resumeUpload,
  maxRetries,
  timeoutMs,
  logger,
}) {
  const uploaded = [];
  const uploadStatePath = join(outDir, "upload_state.json");
  let uploadState = {
    uploaded: [],
  };
  if (resumeUpload && exists(uploadStatePath)) {
    try {
      uploadState = JSON.parse(fs.readFileSync(uploadStatePath, "utf8"));
    } catch {
      uploadState = { uploaded: [] };
    }
  }

  for (const path of slidePaths) {
    const existing = uploadState.uploaded.find((item) => item.path === path);
    if (existing) {
      uploaded.push(existing);
      logger.info("Reused uploaded slide from state", { path });
      continue;
    }
    const { mediaRef, raw } = await postizUpload({
      filePath: path,
      maxAttempts: maxRetries,
      timeoutMs,
    });
    uploaded.push({ path, mediaRef, uploadResponse: raw });
    uploadState.uploaded = uploaded;
    writeJson(uploadStatePath, uploadState);
  }
  const draftResponse = await postizCreateDraft({
    caption,
    mediaRefs: uploaded.map((item) => item.mediaRef),
    idempotencyKey: `${todayISO()}-${slidePaths.length}-${caption.length}-${slidePaths
      .join("|")
      .length}`,
    timeoutMs,
  });
  const responsePath = join(outDir, "postiz_response.json");
  writeJson(responsePath, {
    uploaded,
    draftResponse,
  });
  return responsePath;
}

async function runSingleFlow({ cliArgs, variantSpec, outDir, variantLabel, logger }) {
  const slidesDir = join(outDir, "slides");
  const captionPath = join(outDir, "caption.txt");
  const reviewDir = join(outDir, "review");
  const reviewPath = join(reviewDir, "review.md");
  const contactSheetPath = join(reviewDir, "contact_sheet.png");
  const runLogPath = join(outDir, "run_log.json");

  ensureDir(slidesDir);
  ensureDir(reviewDir);
  const staged = preSlideRender({ slides: variantSpec.slides, spec: variantSpec });
  const slides = staged.slides;
  const diagnostics = runPreflightChecks({
    slides,
    caption: variantSpec.captionOverride || "temporary",
  });

  let slidePaths = Array.from({ length: 6 }, (_, idx) =>
    join(slidesDir, `slide_${String(idx + 1).padStart(2, "0")}.png`)
  );
  let specPath = join(outDir, "_slide_spec.json");
  if (!cliArgs.postizOnly) {
    const fontPath = resolveFontPath();
    const renderResult = renderSlides({
      slidesDir,
      fontPath,
      slides,
      style: variantSpec.style,
      dryRun: cliArgs.dryRun,
    });
    slidePaths = renderResult.produced;
    specPath = renderResult.specPath;
  }

  const captionBase =
    variantSpec.captionOverride ||
    (variantSpec.template === "jk-default" &&
    !variantSpec.topic &&
    (!variantSpec.hashtagOverrides || variantSpec.hashtagOverrides.length === 0)
      ? buildCaption()
      : buildCaption({
          template: variantSpec.template,
          topic: variantSpec.topic,
          slides,
          ctaPack: variantSpec.ctaPack,
          hashtagPolicy: variantSpec.hashtagPolicy,
          hashtagOverrides: variantSpec.hashtagOverrides,
          locale: variantSpec.locale,
        }));
  const caption = postCaptionBuild({ caption: captionBase, spec: variantSpec }).caption;
  writeText(captionPath, `${caption}\n`);

  writeText(
    reviewPath,
    [
      "# Review",
      "",
      `Variant: ${variantLabel || "primary"}`,
      `Source: ${variantSpec.source}`,
      `Template: ${variantSpec.template}`,
      `Style preset: ${variantSpec.stylePreset}`,
      `Audience: ${variantSpec.audience}`,
      `Locale: ${variantSpec.locale}`,
      "",
      "## Slides",
      ...slides.map((line, idx) => `${idx + 1}. ${line}`),
      "",
      "## Caption",
      caption,
      "",
      "## Checks",
      `- dry_run: ${cliArgs.dryRun}`,
      `- postiz_only: ${cliArgs.postizOnly}`,
      `- upload_enabled: ${cliArgs.enablePostiz && !cliArgs.noUpload && !cliArgs.dryRun}`,
      `- spec_path: ${specPath}`,
      `- readability_score: ${diagnostics.readability_score}`,
      `- avg_slide_chars: ${diagnostics.avg_slide_chars}`,
      `- max_slide_chars: ${diagnostics.max_slide_chars}`,
      `- caption_chars: ${diagnostics.caption_chars}`,
    ].join("\n")
  );

  if (slidePaths.length !== 6) {
    throw new Error(`Expected 6 slides, got: ${slidePaths.length}`);
  }
  if (!cliArgs.dryRun) {
    verifySlides(slidesDir);
    renderContactSheet(slidesDir, contactSheetPath);
  }

  let postizResponsePath;
  if (cliArgs.enablePostiz && !cliArgs.noUpload && !cliArgs.dryRun) {
    postizResponsePath = await uploadToPostiz({
      caption,
      slidePaths,
      outDir,
      resumeUpload: cliArgs.resumeUpload,
      maxRetries: cliArgs.maxRetries,
      timeoutMs: cliArgs.timeoutMs,
      logger,
    });
  }

  logger.flush({
    variant: variantLabel || "primary",
    source: variantSpec.source,
    output_folder: outDir,
  });
  return {
    outDir,
    specPath,
    slidePaths,
    caption,
    postizResponsePath,
    runLogPath,
    variantLabel: variantLabel || "primary",
  };
}

export async function runDraftFlow(cliArgs = parseArgs()) {
  const root = repoRoot();
  const day = todayISO();
  const baseOutDir = join(root, "outbox", "tiktok", "intro", day);
  const packagerSpec = loadPackagerSpec(cliArgs);
  const strategy =
    typeof packagerSpec.abTest === "string"
      ? packagerSpec.abTest
      : packagerSpec.abTest?.strategy || cliArgs.abTest;
  const variants = generateVariantSpecs(packagerSpec, strategy);
  const results = [];

  for (const variantSpec of variants) {
    const variantOutDir =
      variants.length > 1
        ? join(baseOutDir, variantSpec.variantLabel || variantSpec.template)
        : baseOutDir;
    ensureDir(variantOutDir);
    const logger = createRunLogger({
      runLogPath: join(variantOutDir, "run_log.json"),
      verbose: cliArgs.verbose,
    });
    logger.info("Starting variant run", {
      variant: variantSpec.variantLabel || "primary",
      source: variantSpec.source,
    });
    const result = await runSingleFlow({
      cliArgs,
      variantSpec,
      outDir: variantOutDir,
      variantLabel: variantSpec.variantLabel,
      logger,
    });
    results.push(result);
  }

  console.log("");
  console.log("Draft generation complete.");
  for (const result of results) {
    console.log(`Output folder: ${result.outDir}`);
    if (result.postizResponsePath) {
      console.log(`Postiz: enabled (response written to ${result.postizResponsePath})`);
    }
    console.log(`Run log: ${result.runLogPath}`);
  }
}

export async function main() {
  try {
    const args = parseArgs();
    await runDraftFlow(args);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Error: ${message}`);
    process.exit(1);
  }
}
