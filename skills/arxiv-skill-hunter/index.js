const fs = require("fs");
const path = require("path");

const CONFIG = {
  maxPapers: 1,
  categories: ["cs.AI", "cs.CL", "cs.SE"],
  workspaceRoot: path.resolve(__dirname, "../.."),
};

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

async function run() {
  console.log("[ArxivSkillHunter] Starting patrol...");
  try {
    const paperClient = require("../arxiv-paper-reviews/paper_client.js");
    const extractor = require("../arxiv-skill-extractor/index.js");
    const taskFile = path.join(CONFIG.workspaceRoot, "memory/evolution/pending_skill_task.json");

    console.log("[ArxivSkillHunter] Fetching latest papers via Node client...");
    const papers = await paperClient.listPapers({
      limit: Math.max(3, CONFIG.maxPapers),
      categories: CONFIG.categories.join(","),
    });

    if (!Array.isArray(papers) || papers.length === 0) {
      console.log("[ArxivSkillHunter] No papers found.");
      return { status: "idle", reason: "no_papers" };
    }

    const targetPaper = papers[0];
    const paperKey = targetPaper.paper_key;
    if (!paperKey) {
      throw new Error("paper list missing paper_key");
    }

    console.log(`[ArxivSkillHunter] Targeted paper: ${paperKey}`);
    const paperDetail = await paperClient.getPaper(paperKey);

    const taskData = {
      type: "skill_generation",
      source: "arxiv",
      paperKey,
      paperId: paperKey,
      paper: paperDetail,
      status: "pending",
      createdAt: new Date().toISOString(),
      categories: CONFIG.categories,
    };

    ensureDir(path.dirname(taskFile));
    fs.writeFileSync(taskFile, JSON.stringify(taskData, null, 2));
    console.log(`[ArxivSkillHunter] Task generated at ${taskFile}`);

    const extraction = await extractor.extractSkill(paperKey, { paper: paperDetail });
    taskData.status = "extracted";
    taskData.extractedAt = new Date().toISOString();
    taskData.generatedSkill = {
      name: extraction.skillName,
      path: extraction.skillPath,
      smokeTestCommand: extraction.smokeTestCommand,
    };
    fs.writeFileSync(taskFile, JSON.stringify(taskData, null, 2));
    console.log(`[ArxivSkillHunter] Generated skill: ${extraction.skillName}`);

    const today = new Date().toISOString().split("T")[0];
    const memoryFile = path.join(CONFIG.workspaceRoot, `memory/${today}.md`);
    if (fs.existsSync(memoryFile)) {
      fs.appendFileSync(
        memoryFile,
        `\n- [ArxivSkillHunter] Learned from ${paperKey} and generated ${extraction.skillName}.\n`,
      );
    }

    return {
      status: "ok",
      paperKey,
      skillName: extraction.skillName,
      skillPath: extraction.skillPath,
    };
  } catch (err) {
    console.error("[ArxivSkillHunter] Error:", err.message);
    throw err;
  }
}

async function main() {
  const result = await run();
  console.log(JSON.stringify(result, null, 2));
}

if (require.main === module) {
  main().catch(() => {
    process.exit(1);
  });
}

module.exports = { run, main };
