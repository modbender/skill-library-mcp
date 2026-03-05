/**
 * Desktop-Sandbox Installer
 * Downloads and installs AtlasCore Desktop Sandbox from GitHub releases
 */

const fs = require('fs');
const path = require('path');
const { spawn, spawnSync } = require('child_process');
const https = require('https');
const http = require('http');
const os = require('os');

const REPO_OWNER = 'AtlasCore-tech';
const REPO_NAME = 'desktop-sandbox-openclaw';

const platform = os.platform();
const args = process.argv.slice(2);
const version = args.find(a => a.startsWith('--version='))?.replace('--version=', '') || '';

function writeLog(message, level = 'INFO') {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    console.log(`[${timestamp}] [${level}] ${message}`);
}

function fileExists(filePath) {
    try {
        return fs.existsSync(filePath) && fs.statSync(filePath).isFile();
    } catch {
        return false;
    }
}

function dirExists(dirPath) {
    try {
        return fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
    } catch {
        return false;
    }
}

function getTempPath() {
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').substring(0, 15);
    const random = Math.floor(Math.random() * 9000) + 1000;
    return path.join(os.tmpdir(), `desktop-sandbox_${timestamp}_${random}`);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function isPkgInstalled(pkgId) {
    try {
        const result = spawnSync('pkgutil', ['--pkg-info', pkgId], { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
        if (result.status !== 0) {
            return false;
        }
        const output = result.stdout || '';
        return output.includes('package-id:') && output.includes(pkgId);
    } catch {
        return false;
    }
}

function verifyInstallation(pkgId) {
    const pkgFiles = spawnSync('pkgutil', ['--files', pkgId], { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
    if (pkgFiles.status !== 0 || !pkgFiles.stdout.trim()) {
        return false;
    }
    const files = pkgFiles.stdout.trim().split('\n');
    return files.length > 0 && files.every(f => {
        const fullPath = path.join('/', f);
        return fileExists(fullPath) || dirExists(fullPath);
    });
}

function isAppInstalledInApplications(appName) {
    const appPath = path.join('/Applications', appName);
    return dirExists(appPath);
}

async function waitForPkgInstall(pkgIds, timeoutMs = 30 * 60 * 1000, intervalMs = 2000) {
    const start = Date.now();
    let lastStatus = false;
    while (Date.now() - start < timeoutMs) {
        const allInstalled = pkgIds.every(id => isPkgInstalled(id));
        if (allInstalled) {
            const verified = pkgIds.every(id => verifyInstallation(id));
            if (verified || lastStatus) {
                return { installed: true, durationSec: (Date.now() - start) / 1000 };
            }
        }
        lastStatus = allInstalled;
        await sleep(intervalMs);
    }
    return { installed: false, durationSec: (Date.now() - start) / 1000 };
}

function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function downloadFile(url, dest) {
    return new Promise((resolve, reject) => {
        console.log(`Downloading to: ${dest}`);

        const file = fs.createWriteStream(dest);
        const protocol = url.startsWith('https') ? https : http;

        let downloadedBytes = 0;
        let totalBytes = 0;
        let lastTime = Date.now();
        let lastBytes = 0;

        const request = protocol.get(url, { headers: { 'User-Agent': 'Desktop-Sandbox-Installer/1.0' } }, (response) => {
            if (response.statusCode === 302 || response.statusCode === 301) {
                file.close();
                downloadFile(response.headers.location, dest).then(resolve).catch(reject);
                return;
            }

            if (response.statusCode !== 200) {
                file.close();
                fs.unlink(dest, () => {});
                reject(`Download failed with status: ${response.statusCode}`);
                return;
            }

            totalBytes = parseInt(response.headers['content-length'], 10) || 0;
            console.log(`Total size: ${formatSize(totalBytes)}`);

            response.pipe(file);

            response.on('data', (chunk) => {
                downloadedBytes += chunk.length;
                const now = Date.now();
                if (now - lastTime >= 300) {
                    const speed = Math.round((downloadedBytes - lastBytes) / ((now - lastTime) / 1000));
                    const percent = totalBytes > 0 ? ((downloadedBytes / totalBytes) * 100).toFixed(1) : 0;
                    const line = `Progress: ${formatSize(downloadedBytes)} / ${formatSize(totalBytes)} (${percent}%) - ${formatSize(speed)}/s`;
                    process.stdout.write('\r\x1b[K' + line);
                    lastTime = now;
                    lastBytes = downloadedBytes;
                }
            });

            file.on('finish', () => {
                const percent = totalBytes > 0 ? ((downloadedBytes / totalBytes) * 100).toFixed(1) : 100;
                process.stdout.write('\r\x1b[K');
                console.log(`Download complete: ${formatSize(downloadedBytes)} (${percent}%)`);
                resolve();
            });

            file.on('error', (err) => {
                process.stdout.write('\r\x1b[K');
                fs.unlink(dest, () => {});
                reject(`Failed to write file: ${err.message}`);
            });
        });

        request.on('error', (err) => {
            process.stdout.write('\r\x1b[K');
            file.close();
            fs.unlink(dest, () => {});
            reject(`Failed to download: ${err.message}`);
        });
    });
}

async function fetchGitHubRelease(owner, repo, specificVersion = '') {
    const apiUrl = specificVersion
        ? `https://api.github.com/repos/${owner}/${repo}/releases/tags/${specificVersion}`
        : `https://api.github.com/repos/${owner}/${repo}/releases/latest`;

    writeLog(`Fetching from: ${apiUrl}`);

    return new Promise((resolve, reject) => {
        const req = https.get(apiUrl, {
            headers: {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Desktop-Sandbox-Installer/1.0'
            }
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(`Failed to parse GitHub API response: ${e.message}`);
                }
            });
        });

        req.on('error', err => reject(`Failed to fetch release info: ${err.message}`));
        req.end();
    });
}

function findInstaller(assets) {
    const platformMap = {
        darwin: { pattern: /\.pkg$/i, name: 'macOS' },
        win32: { pattern: /\.exe$/i, name: 'Windows' }
    };

    const config = platformMap[platform];
    if (!config) {
        throw new Error(`Unsupported platform: ${platform}`);
    }

    for (const asset of assets) {
        const name = asset.name || '';
        if (config.pattern.test(name)) {
            return asset;
        }
    }

    return null;
}

function runInstaller(installerPath) {
    return new Promise((resolve) => {
        writeLog(`Starting installer: ${installerPath}`);

        if (!fileExists(installerPath)) {
            resolve({ success: false, exitCode: -1, message: `Installer not found: ${installerPath}` });
            return;
        }

        const startTime = Date.now();

        if (platform === 'darwin') {
            (async () => {
                writeLog(`Running installer with open -W...`);

                const proc = spawn('open', ['-n', '-W', installerPath], { stdio: 'inherit' });

                proc.on('error', err => {
                    resolve({ success: false, exitCode: -1, message: `Failed to execute installer: ${err.message}` });
                });

                proc.on('close', code => {
                    const duration = (Date.now() - startTime) / 1000;
                    const success = code === 0;
                    resolve({
                        success,
                        exitCode: code,
                        message: success ? 'Installation completed successfully' : `Installer exited with code: ${code}`,
                        duration
                    });
                });
            })().catch(err => {
                resolve({ success: false, exitCode: -1, message: `Installer flow failed: ${err.message}` });
            });
        } else {
            const psScript = `Start-Process -FilePath '${installerPath}' -ArgumentList '/S', '/D=C:\\Program Files\\' -WindowStyle Hidden -Wait`;
            const proc = spawn('powershell.exe', ['-Command', psScript], { stdio: 'inherit' });

            proc.on('close', code => {
                const duration = (Date.now() - startTime) / 1000;
                resolve({
                    success: code === 0, exitCode: code,
                    message: code === 0 ? 'Installation completed successfully' : `Exit code: ${code}`,
                    duration
                });
            });

            proc.on('error', err => {
                resolve({ success: false, exitCode: -1, message: `Failed to execute installer: ${err.message}` });
            });
        }
    });
}

function cleanupPath(dirPath) {
    try {
        if (dirExists(dirPath)) {
            fs.rmSync(dirPath, { recursive: true, force: true });
            writeLog(`Cleaned up directory: ${dirPath}`);
        }
    } catch (err) {
        writeLog(`Failed to cleanup directory: ${err.message}`, 'WARNING');
    }
}

async function main() {
    try {
        writeLog(`=== Desktop-Sandbox Installer Started (${platform}) ===`);

        const releaseInfo = await fetchGitHubRelease(REPO_OWNER, REPO_NAME, version);
        writeLog(`Release version: ${releaseInfo.tag_name || 'unknown'}`);

        const assets = releaseInfo.assets || [];
        const asset = findInstaller(assets);

        if (!asset) {
            throw new Error(`No matching installer found for ${platform}`);
        }

        writeLog(`Found asset: ${asset.name}`);
        writeLog(`Download URL: ${asset.browser_download_url}`);

        const targetDir = getTempPath();
        fs.mkdirSync(targetDir, { recursive: true });

        const downloadPath = path.join(targetDir, asset.name);
        await downloadFile(asset.browser_download_url, downloadPath);

        if (!fileExists(downloadPath)) {
            throw new Error(`Download failed: ${downloadPath}`);
        }

        const result = await runInstaller(downloadPath);

        if (result.success) {
            writeLog('Installation successful, cleaning up...');
            const delay = result.deferCleanupMs || 0;
            if (delay > 0) {
                setTimeout(() => cleanupPath(targetDir), delay);
            } else {
                cleanupPath(targetDir);
            }
        } else {
            const delay = result.deferCleanupMs || 5000;
            setTimeout(() => cleanupPath(targetDir), delay);
        }

        writeLog(`=== Desktop-Sandbox Installer Completed ===`);
        console.log(JSON.stringify(result));

        process.exit(result.success ? 0 : 1);

    } catch (err) {
        writeLog(`Fatal error: ${err.message}`, 'ERROR');
        console.log(JSON.stringify({ success: false, message: err.message }));
        process.exit(999);
    }
}

main();
