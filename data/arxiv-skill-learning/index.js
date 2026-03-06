const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

// Path to track learned papers to avoid duplicates
const WORKSPACE_ROOT = path.resolve(__dirname, '../..');
const LEARNED_DB_PATH = path.join(WORKSPACE_ROOT, 'memory/evolution/learned_papers.json');

// Ensure DB exists
if (!fs.existsSync(LEARNED_DB_PATH)) {
  const dir = path.dirname(LEARNED_DB_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(LEARNED_DB_PATH, JSON.stringify([], null, 2));
}

// Helper to load learned papers
function loadLearnedPapers() {
  try {
    return JSON.parse(fs.readFileSync(LEARNED_DB_PATH, 'utf8'));
  } catch (e) {
    return [];
  }
}

// Helper to save learned paper
function recordLearnedPaper(paperKey, skillName, result) {
  const db = loadLearnedPapers();
  if (!db.find(p => p.paperKey === paperKey)) {
    db.push({
      paperKey,
      skillName,
      learnedAt: new Date().toISOString(),
      testStatus: result.testStatus || 'unknown',
      outcome: result.outcome || 'unknown'
    });
    fs.writeFileSync(LEARNED_DB_PATH, JSON.stringify(db, null, 2));
  }
}

exports.main = async () => {
  console.log('[ArXiv Skill Learning] Starting learning cycle...');
  const result = { status: 'failed', paper: null, skill: null, testStatus: 'pending' };

  try {
    // 1. Load paper_client safely with absolute path resolution
    let paperClient;
    try {
      const paperClientPath = path.resolve(__dirname, '../arxiv-paper-reviews/paper_client');
      paperClient = require(paperClientPath);
    } catch (err) {
      console.error('[ArXiv Skill Learning] Failed to load paper_client:', err.message);
      return { status: 'failed', reason: 'dependency_missing_paper_client', error: err.message };
    }

    // 2. Fetch recent papers
    console.error('[ArXiv Skill Learning] Fetching candidate papers...');
    
    // Expanded category list and fallback logic
    const primaryCategories = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.RO', 'cs.SE', 'cs.CY', 'cs.MA'].sort(() => 0.5 - Math.random());
    let targetPaper = null;
    
    // Load learned papers once
    const learnedDb = loadLearnedPapers();
    const learnedKeys = new Set(learnedDb.map(p => p.paperKey));

    // Try primary categories first
    for (const cat of primaryCategories) {
      console.error(`[ArXiv Skill Learning] Trying category: ${cat}`);
      try {
        const papers = await paperClient.listPapers({ limit: 15, categories: cat }); // Increased limit
        if (papers && papers.length > 0) {
          const candidates = papers.filter(p => !learnedKeys.has(p.paper_key));
          if (candidates.length > 0) {
            targetPaper = candidates[0];
            console.error(`[ArXiv Skill Learning] Found fresh candidate in ${cat}: ${targetPaper.title}`);
            break; 
          } else {
             console.error(`[ArXiv Skill Learning] Category ${cat} returned papers, but all are already learned.`);
          }
        }
      } catch (e) {
        console.warn(`[ArXiv Skill Learning] Failed to fetch category ${cat}:`, e.message);
      }
    }
    
    // Fallback: Try fetching without category (general recent) if still null
    if (!targetPaper) {
       console.error('[ArXiv Skill Learning] Primary categories exhausted. Trying general fetch...');
       try {
         const papers = await paperClient.listPapers({ limit: 20 });
         if (papers && papers.length > 0) {
            const candidates = papers.filter(p => !learnedKeys.has(p.paper_key));
            if (candidates.length > 0) {
              targetPaper = candidates[0];
              console.error(`[ArXiv Skill Learning] Found fresh candidate in general fetch: ${targetPaper.title}`);
            }
         }
       } catch (e) {
         console.warn(`[ArXiv Skill Learning] General fetch failed:`, e.message);
       }
    }

    if (!targetPaper) {
      console.error('[ArXiv Skill Learning] No fresh unlearned papers found after trying all methods.');
      return { status: 'skipped', reason: 'all_candidates_learned' };
    }

    result.paper = targetPaper.title;
    console.error(`[ArXiv Skill Learning] Selected target: ${targetPaper.title} (${targetPaper.paper_key})`);

    // 4. Extract skill using arxiv-skill-extractor safely
    console.error('[ArXiv Skill Learning] Invoking extractor...');
    let extractor;
    try {
      const extractorPath = path.resolve(__dirname, '../arxiv-skill-extractor/index');
      extractor = require(extractorPath);
    } catch (err) {
       console.error('[ArXiv Skill Learning] Failed to load extractor:', err.message);
       return { status: 'failed', reason: 'dependency_missing_extractor', error: err.message };
    }
    
    let extractionResult;
    try {
      extractionResult = await extractor.extractSkill(targetPaper.paper_key, { paper: targetPaper });
    } catch (err) {
       console.error('[ArXiv Skill Learning] Extraction failed:', err.message);
       return { status: 'failed', reason: 'extraction_failed', error: err.message };
    }

    if (!extractionResult || !extractionResult.skillName) {
       console.error('[ArXiv Skill Learning] Extraction returned invalid result.');
       return { status: 'failed', reason: 'extraction_invalid_result' };
    }

    result.skill = extractionResult.skillName;
    console.error(`[ArXiv Skill Learning] Extracted skill: ${extractionResult.skillName} at ${extractionResult.skillPath}`);

    // 5. Verify (Smoke Test)
    console.error('[ArXiv Skill Learning] Running smoke test...');
    if (extractionResult.smokeTestCommand) {
      try {
        console.error(`[ArXiv Skill Learning] Executing: ${extractionResult.smokeTestCommand}`);
        // Ensure we run in workspace root to resolve paths correctly
        const { stdout, stderr } = await execAsync(extractionResult.smokeTestCommand, { 
          encoding: 'utf8', 
          timeout: 60000, // Increased timeout to 60s
          cwd: WORKSPACE_ROOT 
        });
        const smokeTestOutput = stdout;
        console.error('[ArXiv Skill Learning] Smoke test passed:\n', smokeTestOutput.trim());
        if (stderr) console.warn('[ArXiv Skill Learning] Smoke test stderr:', stderr);
        result.testStatus = 'passed';
      } catch (err) {
        console.error('[ArXiv Skill Learning] Smoke test FAILED:', err.message);
        if (err.stdout) console.error('Stdout:', err.stdout);
        if (err.stderr) console.error('Stderr:', err.stderr);
        result.testStatus = 'failed';
        result.testError = err.message;
        // Continue to record success of learning, but note test failure
      }
    } else {
      console.warn('[ArXiv Skill Learning] No smoke test command provided by extractor.');
      result.testStatus = 'skipped';
    }

    // 6. Record success
    result.status = 'success';
    recordLearnedPaper(targetPaper.paper_key, extractionResult.skillName, result);

    return result;

  } catch (error) {
    console.error('[ArXiv Skill Learning] Cycle failed unhandled:', error);
    return { status: 'error', message: error.message };
  }
};

if (require.main === module) {
  exports.main().then(res => console.log(JSON.stringify(res, null, 2))).catch(err => {
    console.error(err);
    process.exit(1);
  });
}
