/**
 * Local Piper TTS Skill for OpenClaw
 *
 * Provides offline text-to-speech using Piper TTS with automatic language detection.
 * Includes self-contained setup: creates an isolated Python venv and installs piper-tts.
 * Language routing and voice selection are handled by the bundled piper-tts.sh script —
 * add more languages by installing .onnx models and the heuristics update automatically.
 */

const { execFile } = require('child_process');
const fs = require('fs');
const https = require('https');
const path = require('path');
const { promisify } = require('util');

const execFileAsync = promisify(execFile);

// Skill directory is the self-contained root: venv, voice models, and piper-tts.sh all live here
const PIPER_DIR    = __dirname;
const PIPER_SCRIPT = path.join(PIPER_DIR, 'piper-tts.sh');
const CONFIG_FILE  = path.join(PIPER_DIR, 'config.json');

/**
 * Load persisted skill config from config.json in the skill directory.
 * Returns {} if the file doesn't exist yet.
 * @returns {{ lengthScale?: number }}
 */
function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  } catch (err) {
    if (err.code === 'ENOENT') return {};
    // File exists but is not valid JSON — warn so corrupted config doesn't silently vanish
    console.error(`Warning: failed to parse ${CONFIG_FILE}: ${err.message}`);
    return {};
  }
}

/**
 * Save one or more config values to config.json in the skill directory.
 * Merges with existing config — does not overwrite unrelated keys.
 * @param {Object} updates - e.g. { lengthScale: 0.8 }
 */
function saveConfig(updates) {
  const current = loadConfig();
  const next = { ...current, ...updates };
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(next, null, 2) + '\n', 'utf8');
}

// Output directory
const WORKSPACE_DIR = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME, '.openclaw', 'workspace');
const OUTPUT_DIR    = path.join(WORKSPACE_DIR, 'tts');

/**
 * Resolve a voice stem to a safe, absolute .onnx path within PIPER_DIR.
 * Prevents path traversal: only models inside PIPER_DIR are accepted.
 * @param {string} voice - e.g. "en_US-ryan-high" or "en_US-ryan-high.onnx"
 * @returns {string} absolute path to the .onnx file
 */
function resolveVoice(voice) {
  // path.basename strips all directory components, preventing traversal
  const stem = path.basename(voice).replace(/\.onnx$/, '');
  const resolved = path.join(PIPER_DIR, stem + '.onnx');
  // Explicit bounds check as defence-in-depth
  if (!resolved.startsWith(PIPER_DIR + path.sep)) {
    throw new Error(`Invalid voice name: ${voice}`);
  }
  if (!fs.existsSync(resolved)) {
    throw new Error(`Voice model not found: ${stem} (expected at ${resolved})`);
  }
  return resolved;
}

/**
 * Download a single file from a URL, following redirects.
 * @param {string} url
 * @param {string} dest - absolute path to write to
 * @param {number} redirects - redirect budget
 * @returns {Promise<void>}
 */
function downloadFile(url, dest, redirects = 10) {
  return new Promise((resolve, reject) => {
    if (redirects === 0) { return reject(new Error('Too many redirects')); }
    if (!url.startsWith('https:')) { return reject(new Error(`Refusing non-HTTPS URL: ${url}`)); }
    const file = fs.createWriteStream(dest);
    let settled = false;
    const done = (err) => {
      if (settled) return;
      settled = true;
      file.close();
      if (err) { try { fs.unlinkSync(dest); } catch (_) {} reject(err); }
      else resolve();
    };
    const req = https.get(url, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        file.destroy();
        try { fs.unlinkSync(dest); } catch (_) {}
        settled = true;
        downloadFile(res.headers.location, dest, redirects - 1).then(resolve, reject);
        return;
      }
      if (res.statusCode !== 200) {
        return done(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      res.pipe(file);
      file.on('finish', () => done(null));
      file.on('error', done);
      res.on('error', done);
    });
    req.on('error', done);
    req.setTimeout(300000, () => { req.destroy(); done(new Error('Download timed out')); });
  });
}

/**
 * List voice model stems installed in PIPER_DIR.
 * Each stem can be passed directly as the `voice` parameter to tts().
 * @returns {string[]} sorted list of voice stems, e.g. ["en_US-ryan-high", "pl_PL-gosia-medium"]
 */
function listVoices() {
  if (!fs.existsSync(PIPER_DIR)) return [];
  return fs.readdirSync(PIPER_DIR)
    .filter(f => f.endsWith('.onnx') && !f.endsWith('.onnx.tmp'))
    .map(f => f.replace(/\.onnx$/, ''))
    .sort();
}

/**
 * Return detailed status of the Piper installation.
 * Use this before any tts() call to determine what action is needed.
 * @returns {Promise<{ ready: boolean, stage: string, message: string, voices?: string[] }>}
 */
async function status() {
  // piper-tts.sh is always present (bundled); check venv to detect missing setup
  const venvPath = path.join(PIPER_DIR, 'venv');
  if (!fs.existsSync(venvPath)) {
    return {
      ready: false,
      stage: 'not-setup',
      message: 'Piper is not set up. Ask the user for confirmation, then call setup().'
    };
  }

  const venvPiper = path.join(PIPER_DIR, 'venv', 'bin', 'piper');
  if (!fs.existsSync(venvPiper)) {
    return {
      ready: false,
      stage: 'no-piper',
      message: 'piper binary missing from venv. Ask the user for confirmation, then call setup() to reinstall.'
    };
  }

  const voices = listVoices();
  if (voices.length === 0) {
    return {
      ready: false,
      stage: 'no-model',
      message: `No voice models installed in ${PIPER_DIR}. Ask the user which language/voice they want, then download the .onnx + .onnx.json from https://github.com/rhasspy/piper/blob/master/VOICES.md`
    };
  }

  return { ready: true, stage: 'ready', voices };
}

/**
 * Check if Piper TTS is fully ready to use.
 * @returns {Promise<boolean>}
 */
async function isAvailable() {
  const s = await status();
  return s.ready;
}

/**
 * Set up the Piper TTS environment.
 * Creates an isolated Python venv inside the skill directory and installs piper-tts.
 * Everything stays self-contained — nothing is written outside the skill directory.
 *
 * IMPORTANT: Always ask the user for confirmation before calling this.
 * It installs piper-tts from PyPI into a venv inside the skill directory.
 *
 * @returns {Promise<{ success: boolean, steps: string[] }>}
 */
async function setup() {
  const steps = [];

  // 1. Verify Python 3 is available
  try {
    await execFileAsync('python3', ['--version'], { timeout: 10000 });
    steps.push('Python 3 found');
  } catch {
    throw new Error('Python 3 is required but not found on PATH. Please install Python 3.8+ first.');
  }

  // 2. Create venv inside skill directory (skip if already exists)
  const venvPath = path.join(PIPER_DIR, 'venv');
  if (!fs.existsSync(venvPath)) {
    await execFileAsync('python3', ['-m', 'venv', venvPath], { timeout: 60000 });
    steps.push('Python virtual environment created');
  } else {
    steps.push('Python virtual environment already exists');
  }

  // 3. Verify pip is present in venv
  const pipPath = path.join(venvPath, 'bin', 'pip');
  if (!fs.existsSync(pipPath)) {
    throw new Error('pip not found in venv — venv creation may have failed. Check your Python installation.');
  }

  // 4. Install piper-tts and its dependencies into the isolated venv (not system Python)
  // pathvalidate is listed as a piper-tts dependency but is occasionally missed by pip
  await execFileAsync(pipPath, ['install', '--quiet', 'piper-tts', 'pathvalidate'], { timeout: 300000 });
  steps.push('piper-tts installed into venv');

  // 5. Ensure piper-tts.sh is executable (may be lost on cp-based installs)
  if (!fs.existsSync(PIPER_SCRIPT)) {
    throw new Error('piper-tts.sh not found in skill directory — skill installation may be incomplete.');
  }
  fs.chmodSync(PIPER_SCRIPT, 0o755);
  steps.push('piper-tts.sh marked executable');

  // 6. Check for espeak-ng (required by Piper for phonemization, but varies by platform)
  let hasEspeak = false;
  for (const bin of ['espeak-ng', 'espeak']) {
    try {
      await execFileAsync('which', [bin], { timeout: 5000 });
      hasEspeak = true;
      break;
    } catch (_) {}
  }
  if (!hasEspeak) {
    steps.push('WARNING: espeak-ng not found — Piper requires it for phonemization. Install it: sudo apt install espeak-ng (Debian/Ubuntu), sudo dnf install espeak-ng (Fedora), brew install espeak (macOS)');
  } else {
    steps.push('espeak-ng found');
  }

  return { success: true, steps };
}

/**
 * Generate speech using local Piper TTS.
 * @param {string} text - Text to synthesize
 * @param {string|null} outputFilename - Optional output filename
 * @param {string|null} voice - Optional voice stem, e.g. "en_US-amy-medium"
 * @returns {Promise<string>} - Path to generated WAV file
 */
async function synthesize(text, outputFilename = null, voice = null, lengthScale = null) {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // path.basename prevents directory traversal in user-supplied filenames
  const safeBase = outputFilename || `piper-${Date.now()}.wav`;
  const filename = path.basename(safeBase);
  const outputPath = path.join(OUTPUT_DIR, filename);

  if (!fs.existsSync(PIPER_SCRIPT)) {
    throw new Error('Piper TTS not set up. Call setup() first.');
  }

  // Inherit env; optionally pin a specific voice model and speed
  const env = { ...process.env };
  if (voice) {
    env.PIPER_VOICE_MODEL = resolveVoice(voice);
  }
  if (lengthScale !== null) {
    env.PIPER_LENGTH_SCALE = String(lengthScale);
  }

  try {
    await execFileAsync(PIPER_SCRIPT, [text, outputPath],
      { timeout: 30000, maxBuffer: 1024 * 1024, env }
    );

    if (!fs.existsSync(outputPath)) {
      throw new Error('Piper TTS failed to create output file');
    }

    return outputPath;
  } catch (error) {
    throw new Error(`Piper TTS synthesis failed: ${error.message}`);
  }
}

/**
 * Remove a voice model from the skill directory.
 * Deletes both the .onnx and .onnx.json files for the given stem.
 * @param {string} stem - Voice stem to remove, e.g. "en_US-ryan-medium"
 * @returns {{ removed: string, filesDeleted: string[] }}
 */
function removeVoice(stem) {
  const safeStem = path.basename(stem).replace(/\.onnx$/, '');
  const onnxPath = path.join(PIPER_DIR, safeStem + '.onnx');
  const jsonPath = path.join(PIPER_DIR, safeStem + '.onnx.json');

  if (!onnxPath.startsWith(PIPER_DIR + path.sep)) {
    throw new Error(`Invalid voice name: ${stem}`);
  }
  if (!fs.existsSync(onnxPath)) {
    throw new Error(`Voice not installed: ${safeStem}. Use listVoices() to see installed voices.`);
  }

  const deleted = [];
  fs.unlinkSync(onnxPath);
  deleted.push(safeStem + '.onnx');
  try { fs.unlinkSync(jsonPath); deleted.push(safeStem + '.onnx.json'); } catch (_) {}

  return { removed: safeStem, filesDeleted: deleted };
}

/**
 * Convert WAV to OGG/Opus format.
 * @param {string} inputPath - Path to WAV file
 * @param {string|null} outputPath - Path for OGG output
 * @returns {Promise<string>} - Path to OGG file
 */
async function convertToOgg(inputPath, outputPath = null) {
  if (!outputPath) {
    outputPath = inputPath.replace(/\.wav$/, '.ogg');
  }

  try {
    await execFileAsync('ffmpeg', ['-y', '-i', inputPath, '-c:a', 'libopus', '-b:a', '64k', outputPath],
      { timeout: 30000 }
    );

    if (!fs.existsSync(outputPath)) {
      throw new Error('FFmpeg conversion failed');
    }

    return outputPath;
  } catch (error) {
    throw new Error(`OGG conversion failed: ${error.message}`);
  }
}

/**
 * Download Piper voice models from HuggingFace (rhasspy/piper-voices).
 * Downloads both .onnx and .onnx.json for each requested stem.
 *
 * Stem format: {lang_region}-{name}-{quality}
 * Examples: "en_US-ryan-medium", "en_US-amy-medium", "pl_PL-gosia-medium"
 *
 * @param {string[]} voices - Voice stems to download
 * @returns {Promise<{ downloaded: string[], failed: Array<{stem: string, error: string}> }>}
 */
async function downloadVoices(voices) {
  if (!fs.existsSync(PIPER_DIR)) {
    fs.mkdirSync(PIPER_DIR, { recursive: true });
  }

  const downloaded = [];
  const failed = [];

  for (const stem of voices) {
    // Strip directory components — prevents path traversal via crafted stems
    const safeStem = path.basename(stem);

    // Parse stem: first segment is lang_region (e.g. en_US), last is quality, middle is name
    const parts = safeStem.split('-');
    if (parts.length < 3) {
      failed.push({ stem, error: `Invalid voice stem format: ${stem}` });
      continue;
    }
    const lang_region = parts[0];                    // e.g. "en_US"
    const lang = lang_region.split('_')[0];          // e.g. "en"
    const quality = parts[parts.length - 1];         // e.g. "medium"
    const name = parts.slice(1, -1).join('-');        // e.g. "ryan" (handles hyphenated names)

    // Validate URL path components to prevent traversal in the constructed URL
    if (!/^[a-z]{2}_[A-Z]{2}$/.test(lang_region) ||
        !/^[a-z]{2}$/.test(lang) ||
        !/^[a-zA-Z0-9_-]+$/.test(name) ||
        !/^[a-z]+$/.test(quality)) {
      failed.push({ stem, error: `Voice stem contains invalid characters: ${stem}` });
      continue;
    }

    const base = `https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/${lang}/${lang_region}/${name}/${quality}/${safeStem}`;
    const onnxDest = path.join(PIPER_DIR, `${safeStem}.onnx`);
    const jsonDest = path.join(PIPER_DIR, `${safeStem}.onnx.json`);
    const onnxTmp  = onnxDest + '.tmp';
    const jsonTmp  = jsonDest + '.tmp';

    try {
      // Download to .tmp files first — rename on success for crash safety
      await downloadFile(`${base}.onnx`,      onnxTmp);
      await downloadFile(`${base}.onnx.json`, jsonTmp);
      fs.renameSync(onnxTmp, onnxDest);
      fs.renameSync(jsonTmp, jsonDest);
      downloaded.push(safeStem);
    } catch (err) {
      // Clean up partial / temp downloads
      try { fs.unlinkSync(onnxTmp);  } catch (_) {}
      try { fs.unlinkSync(jsonTmp);  } catch (_) {}
      try { fs.unlinkSync(onnxDest); } catch (_) {}
      try { fs.unlinkSync(jsonDest); } catch (_) {}
      failed.push({ stem, error: err.message });
    }
  }

  return { downloaded, failed };
}

/**
 * Main TTS function for OpenClaw integration.
 * @param {Object} options
 * @param {string} options.text - Text to synthesize
 * @param {string} [options.format='ogg'] - Output format: 'ogg' or 'wav'
 * @param {string} [options.voice] - Voice stem, e.g. "en_US-amy-medium". Omit for auto-detect.
 * @param {number} [options.lengthScale] - Speech speed. 1.0 = normal, <1.0 = faster, >1.0 = slower. Default: 1.0.
 * @returns {Promise<{ path: string, format: string, size: number }>}
 */
async function tts(options) {
  const { text, format = 'ogg', voice = null } = options;
  const lengthScale = options.lengthScale ?? loadConfig().lengthScale ?? null;

  if (!text || text.trim().length === 0) {
    throw new Error('No text provided for TTS');
  }

  const wavPath = await synthesize(text, null, voice, lengthScale);

  if (format === 'ogg') {
    const oggPath = await convertToOgg(wavPath);
    // Remove intermediate WAV — only the OGG is needed
    try { fs.unlinkSync(wavPath); } catch (_) {}
    const stats = fs.statSync(oggPath);
    return { path: oggPath, format: 'ogg', size: stats.size };
  }

  const stats = fs.statSync(wavPath);
  return { path: wavPath, format: 'wav', size: stats.size };
}

module.exports = {
  tts,
  synthesize,
  convertToOgg,
  isAvailable,
  listVoices,
  status,
  setup,
  downloadVoices,
  removeVoice,
  loadConfig,
  saveConfig,

  meta: {
    name: 'local-piper-tts-multilang-secure',
    version: '1.1.0',
    description: 'Local offline Piper TTS with self-contained setup, automatic language detection, and per-call voice selection. Add languages by installing .onnx models.',
    license: 'MIT',
    features: ['offline', 'multilingual', 'auto-detect', 'voice-select', 'self-setup', 'workspace-output']
  }
};
