import puppeteer from 'puppeteer-core';
import { spawn, execSync, spawnSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import os from 'os';

// Logger with levels
const LOG_LEVEL = process.env.LOG_LEVEL || 'info'; // debug, info, warn, error
const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
const currentLevel = LEVELS[LOG_LEVEL] || LEVELS.info;

const log = {
  debug: (...args) => currentLevel <= LEVELS.debug && console.log('[DEBUG]', ...args),
  info: (...args) => currentLevel <= LEVELS.info && console.log('[INFO]', ...args),
  warn: (...args) => currentLevel <= LEVELS.warn && console.warn('[WARN]', ...args),
  error: (...args) => currentLevel <= LEVELS.error && console.error('[ERROR]', ...args),
};

const args = process.argv.slice(2);
const projectId = args.find(arg => !arg.startsWith('--'));
const forceAudio = args.includes('--force-audio');
const useGpu = args.includes('--gpu');

function getArgValue(name) {
  const withEq = args.find(arg => arg.startsWith(`--${name}=`));
  if (withEq) return withEq.slice(`--${name}=`.length) || null;
  const idx = args.indexOf(`--${name}`);
  if (idx !== -1) return args[idx + 1] || null;
  return null;
}

if (!projectId) {
  log.error('Please specify a project ID');
  process.exit(1);
}

const scriptName = getArgValue('script') || projectId;

const WIDTH = 1920;
const HEIGHT = 1080;
const FPS = 30;
const FRAME_MS = 1000 / FPS;

const BASE_PORT = 5175;

const OUTPUT_DIR = path.resolve(process.cwd(), 'public', 'video');
const FRAMES_DIR = path.join(OUTPUT_DIR, `frames-${projectId}`);
const FINAL_VIDEO = path.join(OUTPUT_DIR, `render-${projectId}.mp4`);

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

if (fs.existsSync(FRAMES_DIR)) {
  fs.rmSync(FRAMES_DIR, { recursive: true, force: true });
}
fs.mkdirSync(FRAMES_DIR, { recursive: true });

function detectBrowserExecutable() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) return process.env.PUPPETEER_EXECUTABLE_PATH;
  
  const candidates = os.platform() === 'darwin'
    ? [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
      ]
    : ['google-chrome', 'chromium', 'brave-browser'];

  for (const p of candidates) {
    if (os.platform() === 'darwin') {
      if (fs.existsSync(p)) return p;
    } else {
      try {
        const result = execSync(`which ${p}`, { encoding: 'utf-8' }).trim();
        if (result) return result;
      } catch {}
    }
  }
  return null;
}

function probeDurationSeconds(filePath) {
  const result = spawnSync('ffprobe', [
    '-v', 'error', '-show_entries', 'format=duration',
    '-of', 'default=noprint_wrappers=1:nokey=1', filePath
  ], { encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] });
  
  if (result.status !== 0) return null;
  const value = Number.parseFloat(String(result.stdout || '').trim());
  return (Number.isFinite(value) && value > 0) ? value : null;
}

function getDurationFromJson(jsonPath) {
  const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  if (!Array.isArray(data)) return 0;

  let maxEndSeconds = 0;
  for (const entry of data) {
    if (!entry || typeof entry !== 'object') continue;
    
    const candidates = [entry, ...(Array.isArray(entry.Metadata) ? entry.Metadata : [])];
    for (const c of candidates) {
      if (c?.Type !== 'WordBoundary') continue;
      const dataObj = c.Data || c;
      const offset = Number(dataObj.Offset);
      const dur = Number(dataObj.Duration);
      if (Number.isFinite(offset) && Number.isFinite(dur)) {
        maxEndSeconds = Math.max(maxEndSeconds, (offset + dur) / 10000000);
      }
    }
  }
  return maxEndSeconds > 0 ? maxEndSeconds + 0.6 : 0;
}

function loadRenderTimings(audioDir) {
  if (!fs.existsSync(audioDir)) return [];

  const indices = new Set();
  for (const f of fs.readdirSync(audioDir)) {
    const ext = path.extname(f).toLowerCase();
    if (ext === '.mp3' || ext === '.json') {
      const idx = Number.parseInt(path.basename(f, ext), 10);
      if (Number.isFinite(idx)) indices.add(idx);
    }
  }

  const timings = [];
  let currentStart = 0;
  
  for (const index of Array.from(indices).sort((a, b) => a - b)) {
    let duration = 4; // default
    try {
      const mp3Path = path.join(audioDir, `${index}.mp3`);
      duration = fs.existsSync(mp3Path) ? probeDurationSeconds(mp3Path) : null;
      
      if (!duration) {
        const jsonPath = path.join(audioDir, `${index}.json`);
        duration = getDurationFromJson(jsonPath) || 4;
      }
    } catch (e) {
      log.debug(`Failed to get duration for index ${index}:`, e.message);
    }
    
    timings.push({ start: currentStart, end: currentStart + duration, duration });
    currentStart += duration;
  }
  return timings;
}

function projectHasSpeech(projectId) {
  const checkProject = (data) => {
    const project = data?.projects?.[projectId];
    const clips = Array.isArray(project?.clips) ? project.clips : [];
    return clips.some(c => c?.speech?.trim());
  };

  try {
    const projectPath = path.resolve(process.cwd(), 'public', 'script', `${projectId}.json`);
    if (fs.existsSync(projectPath)) {
      return checkProject(JSON.parse(fs.readFileSync(projectPath, 'utf-8')));
    }

    const indexPath = path.resolve(process.cwd(), 'public', 'script', 'index.json');
    if (fs.existsSync(indexPath)) {
      return checkProject(JSON.parse(fs.readFileSync(indexPath, 'utf-8')));
    }
  } catch (e) {
    log.debug('Error checking speech:', e.message);
  }
  return true; // default to true if uncertain
}

async function findFreePort(startPort) {
  const { createServer } = await import('net');
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.listen(startPort, () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
    server.on('error', () => {
      findFreePort(startPort + 1).then(resolve).catch(reject);
    });
  });
}

async function waitForHttpOk(url, timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start <= timeoutMs) {
    try {
      const res = await fetch(url, { method: 'GET' });
      if (res.ok) return;
    } catch {
    }
    await sleep(200);
  }
  throw new Error(`Server not reachable: ${url}`);
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function waitForViteReady(server, port, timeoutMs = 20000) {
  let serverStarted = false;
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => !serverStarted && reject(new Error('Server start timeout')), timeoutMs);

    const cleanup = () => {
      clearTimeout(timeout);
      server.stdout?.removeAllListeners?.('data');
      server.stderr?.removeAllListeners?.('data');
      server.removeAllListeners?.('error');
      server.removeAllListeners?.('exit');
    };

    server.stdout.on('data', (data) => {
      const text = data.toString();
      log.debug(text.trim());
      if (text.includes('Local:') || text.includes('ready in')) {
        serverStarted = true;
        cleanup();
        resolve();
      }
    });

    server.stderr.on('data', (data) => {
      const msg = data.toString();
      log.debug(msg.trim());
      if (msg.includes('EADDRINUSE')) {
        cleanup();
        reject(new Error(`Port ${port} is already in use`));
      }
    });

    server.on('error', (err) => { cleanup(); reject(err); });
    server.on('exit', (code) => { cleanup(); reject(new Error(`Server exited with code ${code ?? 'unknown'}`)); });
  });
}

async function main() {
  const audioDir = path.resolve(process.cwd(), 'public', 'audio', projectId);
  const hasSpeech = projectHasSpeech(projectId);
  
  if (hasSpeech) {
    const needsAudio = forceAudio || !fs.existsSync(audioDir) || 
                       fs.readdirSync(audioDir).filter(f => f.endsWith('.mp3')).length === 0;
    if (needsAudio) {
      log.info(`Generating TTS audio for ${projectId}...`);
      execSync(`npx tsx scripts/generate-audio.ts ${projectId}`, { 
        stdio: currentLevel <= LEVELS.debug ? 'inherit' : 'ignore' 
      });
    } else {
      log.debug('Audio files already exist');
    }
  } else {
    log.info(`No speech in ${projectId}, skipping audio generation`);
  }

  const renderTimings = loadRenderTimings(audioDir);
  const portOverride = getArgValue('port');
  const portStart = portOverride ? Number.parseInt(portOverride, 10) : BASE_PORT;
  const startPort = Number.isFinite(portStart) ? portStart : BASE_PORT;
  let server = null;
  let browser = null;
  let userDataDir = null;
  let baseUrl = null;

  try {
    let attemptStart = startPort;
    for (let attempt = 0; attempt < 5; attempt++) {
      const port = await findFreePort(attemptStart);
      baseUrl = `http://127.0.0.1:${port}/?record=true&project=${encodeURIComponent(projectId)}&script=${encodeURIComponent(scriptName)}`;

      log.info(`Starting Vite server on port ${port}...`);
      server = spawn('pnpm', ['exec', 'vite', '--port', String(port), '--strictPort', '--host', '127.0.0.1'], {
        stdio: ['ignore', 'pipe', 'pipe'],
        shell: true
      });

      try {
        await waitForViteReady(server, port);
        await waitForHttpOk(baseUrl);
        break;
      } catch (e) {
        server.kill('SIGINT');
        server = null;
        attemptStart = port + 1;
        if (attempt === 4) throw e;
      }
    }

    log.info('Launching browser...');
    const executablePath = detectBrowserExecutable();
    if (!executablePath) {
      throw new Error('Chrome/Chromium not found. Set PUPPETEER_EXECUTABLE_PATH.');
    }
    log.debug(`Using browser: ${executablePath}`);
    
    const browserLaunchArgs = [
      `--window-size=${WIDTH},${HEIGHT}`,
      '--hide-scrollbars',
      '--mute-audio',
      '--disable-dev-shm-usage',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-gpu-compositing',
      '--enable-logging=stderr',
      '--v=1'
    ];

    if (useGpu) {
      browserLaunchArgs.push('--use-gl=desktop');
    }

    userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), `c2a-render-${projectId}-`));
    browserLaunchArgs.push(
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-crash-reporter',
      '--disable-breakpad',
      '--no-crashpad'
    );
    browserLaunchArgs.push('--disable-rlz');
    browserLaunchArgs.push('--disable-features=Crashpad');
    browserLaunchArgs.push(`--crash-dumps-dir=${userDataDir}`);

    browser = await puppeteer.launch({
      headless: 'new',
      executablePath,
      args: browserLaunchArgs,
      userDataDir,
      defaultViewport: null,
      protocolTimeout: 240000,
      timeout: 60000,
      dumpio: currentLevel <= LEVELS.debug,
      env: {
        ...process.env,
        HOME: userDataDir,
      },
    });

    const page = await browser.newPage();
    await page.evaluateOnNewDocument(() => {
      window.suppressTTS = true;
      window.__renderTickAll = (timeSeconds) => {
        try {
          if (typeof window.__renderTick === 'function') {
            window.__renderTick(timeSeconds);
          }
        } catch {
        }

        try {
          const iframes = document.querySelectorAll('iframe');
          for (const iframe of iframes) {
            try {
              const w = iframe && iframe.contentWindow;
              if (w && typeof w.__renderTick === 'function') {
                w.__renderTick(timeSeconds);
              }
            } catch {
            }
          }
        } catch {
        }
      };

      try {
        if (!(typeof location?.pathname === 'string' && location.pathname.startsWith('/footage/'))) return;

        let nowMs = 0;
        let rafId = 0;
        const rafCallbacks = new Map();

        let timerId = 0;
        const timeoutIdToEntry = new Map();
        const intervalIdToEntry = new Map();

        const realDateNow = Date.now.bind(Date);
        const timeOrigin = realDateNow();

        const runRafOnce = (timeMs) => {
          const entries = Array.from(rafCallbacks.entries());
          rafCallbacks.clear();
          for (const [, cb] of entries) {
            try {
              cb(timeMs);
            } catch {
            }
          }
        };

        const runTimersOnce = (timeMs) => {
          for (const [id, entry] of Array.from(timeoutIdToEntry.entries())) {
            if (timeMs < entry.atMs) continue;
            timeoutIdToEntry.delete(id);
            try {
              entry.cb(...entry.args);
            } catch {
            }
          }

          for (const entry of Array.from(intervalIdToEntry.values())) {
            const intervalMs = Math.max(1, entry.intervalMs);
            while (timeMs >= entry.nextAtMs) {
              entry.nextAtMs += intervalMs;
              try {
                entry.cb(...entry.args);
              } catch {
              }
            }
          }
        };

        const syncCssAnimations = (timeMs) => {
          try {
            const animations = document.getAnimations();
            for (const anim of animations) {
              try {
                anim.pause();
                anim.currentTime = timeMs;
              } catch {
              }
            }
          } catch {
          }
        };

        window.__renderTick = (timeSeconds) => {
          const nextNowMs = Math.max(0, Number(timeSeconds) * 1000);
          const deltaMs = nextNowMs - nowMs;
          const stepMs = 1000 / 60;
          const steps = Math.max(1, Math.round(deltaMs / stepMs));

          syncCssAnimations(nextNowMs);

          for (let s = 1; s <= steps; s++) {
            const tMs = nowMs + (deltaMs * s) / steps;
            runTimersOnce(tMs);
            runRafOnce(tMs);
          }

          nowMs = nextNowMs;
        };

        window.requestAnimationFrame = (cb) => {
          rafId += 1;
          rafCallbacks.set(rafId, cb);
          return rafId;
        };
        window.cancelAnimationFrame = (id) => {
          rafCallbacks.delete(id);
        };

        window.setTimeout = (cb, delayMs, ...args) => {
          timerId += 1;
          const atMs = nowMs + Math.max(0, Number(delayMs) || 0);
          timeoutIdToEntry.set(timerId, { cb, atMs, args });
          return timerId;
        };
        window.clearTimeout = (id) => {
          timeoutIdToEntry.delete(id);
        };

        window.setInterval = (cb, intervalMs, ...args) => {
          timerId += 1;
          const ms = Math.max(1, Number(intervalMs) || 0);
          intervalIdToEntry.set(timerId, { cb, intervalMs: ms, nextAtMs: nowMs + ms, args });
          return timerId;
        };
        window.clearInterval = (id) => {
          intervalIdToEntry.delete(id);
        };

        Date.now = () => timeOrigin + nowMs;
        if (typeof performance?.now === 'function') {
          performance.now = () => nowMs;
        }
      } catch {
      }
    });
    await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: 1 });
    await page.goto(baseUrl, { waitUntil: 'networkidle0' });
    await sleep(1000);

    let frameIndex = 0;
    const digits = 6;
    const LOG_EVERY_N_FRAMES = 30;
    const formatPct = (value) => `${Math.round(value * 100)}%`;

    if (renderTimings.length === 0) {
      const duration = 10;
      const totalFrames = Math.round(duration * FPS);
      log.info(`Rendering ${totalFrames} frames (no audio)`);
      
      for (let i = 0; i < totalFrames; i++) {
        await page.evaluate((time) => {
          if (window.seekTo) window.seekTo(time);
          if (window.__renderTickAll) window.__renderTickAll(time);
        }, i / FPS);
        await page.evaluate(() => new Promise(requestAnimationFrame));
        await page.screenshot({ 
          path: path.join(FRAMES_DIR, `frame-${String(frameIndex++).padStart(digits, '0')}.png`), 
          type: 'png' 
        });
        
        if (i === 0 || (i + 1) % LOG_EVERY_N_FRAMES === 0 || i === totalFrames - 1) {
          log.info(`Progress: ${i + 1}/${totalFrames} (${formatPct((i + 1) / totalFrames)})`);
        }
      }
    } else {
      const totalFramesAll = renderTimings.reduce((acc, t) => acc + Math.max(1, Math.round(t.duration * FPS)), 0);
      log.info(`Rendering ${renderTimings.length} clips, ${totalFramesAll} total frames`);
      
      for (let clipIndex = 0; clipIndex < renderTimings.length; clipIndex++) {
        const timing = renderTimings[clipIndex];
        const clipFrames = Math.max(1, Math.round(timing.duration * FPS));

        log.debug(`Clip ${clipIndex + 1}/${renderTimings.length}: ${timing.duration.toFixed(2)}s, ${clipFrames} frames`);

        await page.evaluate((index) => window.setClipIndex?.(index), clipIndex);
        await sleep(300);

        for (let i = 0; i < clipFrames; i++) {
          await page.evaluate((time) => {
            if (window.seekTo) window.seekTo(time);
            if (window.__renderTickAll) window.__renderTickAll(time);
          }, i / FPS);
          await page.evaluate(() => new Promise(requestAnimationFrame));
          await page.screenshot({ 
            path: path.join(FRAMES_DIR, `frame-${String(frameIndex++).padStart(digits, '0')}.png`), 
            type: 'png' 
          });
          
          if (i === 0 || (i + 1) % LOG_EVERY_N_FRAMES === 0 || i === clipFrames - 1) {
            log.info(`Clip ${clipIndex + 1}/${renderTimings.length} | Overall ${frameIndex}/${totalFramesAll} (${formatPct(frameIndex / totalFramesAll)})`);
          }
        }
      }
    }

    log.info('Combining frames with ffmpeg...');

    const audioFiles = hasSpeech && fs.existsSync(audioDir)
      ? fs.readdirSync(audioDir).filter(f => f.endsWith('.mp3')).sort((a, b) => {
        const ia = Number.parseInt(path.basename(a, '.mp3'), 10);
        const ib = Number.parseInt(path.basename(b, '.mp3'), 10);
        return Number.isNaN(ia) || Number.isNaN(ib) ? a.localeCompare(b) : ia - ib;
      })
      : [];

    let combinedAudio = null;
    if (audioFiles.length > 0) {
      log.debug(`Concatenating ${audioFiles.length} audio files`);
      const concatListPath = path.join(OUTPUT_DIR, `audio-${projectId}-concat.txt`);
      const tempAudioPath = path.join(OUTPUT_DIR, `audio-${projectId}.mp3`);

      fs.writeFileSync(concatListPath, audioFiles
        .map(f => `file '${path.join(audioDir, f).replace(/'/g, "'\\''")}'`)
        .join('\n'));

      const result = spawnSync('ffmpeg', ['-y', '-f', 'concat', '-safe', '0', '-i', concatListPath, '-c', 'copy', tempAudioPath], {
        stdio: currentLevel <= LEVELS.debug ? 'inherit' : 'pipe'
      });

      if (result.status === 0) {
        combinedAudio = tempAudioPath;
      } else {
        log.warn('Audio concatenation failed, continuing without audio');
      }
    }

    const ffmpegArgs = ['-y', '-framerate', String(FPS), '-i', path.join(FRAMES_DIR, 'frame-%06d.png')];
    if (combinedAudio) ffmpegArgs.push('-i', combinedAudio);

    if (useGpu && os.platform() === 'darwin') {
      log.info('Using GPU acceleration (h264_videotoolbox)');
      ffmpegArgs.push('-c:v', 'h264_videotoolbox', '-b:v', '5000k');
    } else {
      ffmpegArgs.push('-c:v', 'libx264');
    }

    ffmpegArgs.push('-pix_fmt', 'yuv420p', '-r', String(FPS));
    if (combinedAudio) ffmpegArgs.push('-c:a', 'aac', '-shortest');
    ffmpegArgs.push(FINAL_VIDEO);

    const ffmpegResult = spawnSync('ffmpeg', ffmpegArgs, { 
      stdio: currentLevel <= LEVELS.debug ? 'inherit' : 'pipe' 
    });
    if (ffmpegResult.status !== 0) {
      log.error(`ffmpeg failed with exit code ${ffmpegResult.status}`);
      process.exitCode = ffmpegResult.status || 1;
    } else {
      log.info(`✓ Render complete: ${FINAL_VIDEO}`);
      
      log.debug('Cleaning up temporary files...');
      if (fs.existsSync(FRAMES_DIR)) {
        fs.rmSync(FRAMES_DIR, { recursive: true, force: true });
      }
      
      const concatListPath = path.join(OUTPUT_DIR, `audio-${projectId}-concat.txt`);
      const tempAudioPath = path.join(OUTPUT_DIR, `audio-${projectId}.mp3`);
      [concatListPath, tempAudioPath].forEach(p => {
        if (fs.existsSync(p)) fs.unlinkSync(p);
      });
      log.debug('Cleanup complete');
    }
  } finally {
    await browser?.close?.().catch(() => {});
    server?.kill?.('SIGINT');
    if (userDataDir && fs.existsSync(userDataDir)) {
      fs.rmSync(userDataDir, { recursive: true, force: true });
    }
  }
}

main().catch(err => {
  log.error(err);
  process.exit(1);
});
