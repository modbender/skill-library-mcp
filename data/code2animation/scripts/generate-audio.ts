import fs from 'fs';
import path from 'path';
import { MsEdgeTTS, OUTPUT_FORMAT } from 'msedge-tts';

const SCRIPT_JSON_PATH = path.resolve(process.cwd(), 'public', 'script', 'index.json');

function loadProjectsFromScriptJson() {
    if (!fs.existsSync(SCRIPT_JSON_PATH)) {
        throw new Error(`Script JSON not found: ${SCRIPT_JSON_PATH}`);
    }
    const raw = fs.readFileSync(SCRIPT_JSON_PATH, 'utf-8');
    const data = JSON.parse(raw);
    
    const projects: Record<string, any> = {};

    // 1. Load inline projects
    if (data.projects && typeof data.projects === 'object') {
        Object.assign(projects, data.projects);
    }

    // 2. Load referenced entries
    if (Array.isArray(data.entries)) {
        const scriptDir = path.dirname(SCRIPT_JSON_PATH);
        for (const entry of data.entries) {
            const entryPath = path.join(scriptDir, entry);
            if (fs.existsSync(entryPath)) {
                try {
                    const entryRaw = fs.readFileSync(entryPath, 'utf-8');
                    const entryData = JSON.parse(entryRaw);
                    if (entryData.projects) {
                        Object.assign(projects, entryData.projects);
                    }
                } catch (e) {
                    console.warn(`Failed to load project entry ${entry}:`, e);
                }
            }
        }
    }

    if (Object.keys(projects).length === 0) {
        // As a fallback, try to find a file named after the projectId if we could pass it here,
        // but since we don't have projectId argument, we can only rely on index.json entries.
        // Or we could scan the directory for .json files that contain "projects" key.
        // For now, assume index.json is correct.
        console.warn(`No projects found in ${SCRIPT_JSON_PATH} or its entries.`);
    }

    return projects;
}

const OUTPUT_DIR = path.resolve(process.cwd(), 'public/audio');

async function ensureDir(dir: string) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

async function generateAudioForProject(projectId: string) {
    const projects = loadProjectsFromScriptJson();
    const project = projects[projectId as keyof typeof projects];
    if (!project) {
        console.error(`Project ${projectId} not found`);
        return;
    }

    console.log(`Generating audio for project: ${project.name} (${projectId})`);
    const projectDir = path.join(OUTPUT_DIR, projectId);
    await ensureDir(projectDir);

    const tts = new MsEdgeTTS();

    for (let i = 0; i < project.clips.length; i++) {
        const clip = project.clips[i];
        if (!clip.speech) {
            console.log(`Skipping clip ${i + 1} (no speech)`);
            continue;
        }

        // Determine voice for this clip
        const isChinese = /[\u4e00-\u9fa5]/.test(clip.speech);
        const voice = clip.voice || (isChinese ? 'zh-CN-YunjianNeural' : 'en-US-GuyNeural');

        console.log(`Generating clip ${i + 1}/${project.clips.length} using voice: ${voice}...`);

        await tts.setMetadata(
            voice,
            OUTPUT_FORMAT.AUDIO_24KHZ_48KBITRATE_MONO_MP3,
            {
                wordBoundaryEnabled: true,
            }
        );

        const audioPath = path.join(projectDir, `${i}.mp3`);
        const metaPath = path.join(projectDir, `${i}.json`);

        try {
            const { audioStream, metadataStream } = tts.toStream(clip.speech);

            const audioFile = fs.createWriteStream(audioPath);
            const metadata: any[] = [];

            metadataStream.on('data', (data) => {
                let content = data;
                if (Buffer.isBuffer(data)) {
                    content = data.toString('utf8');
                }

                if (typeof content === 'string') {
                    try {
                        const parsed = JSON.parse(content);
                        metadata.push(parsed);
                    } catch (e) {
                        // Ignore non-json chunks
                    }
                } else {
                    metadata.push(content);
                }
            });

            await new Promise((resolve, reject) => {
                audioStream.pipe(audioFile);
                audioStream.on('end', resolve);
                audioStream.on('error', reject);
            });

            fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2));
            console.log(`Saved: ${audioPath}`);

        } catch (err) {
            console.error(`Error generating audio for clip ${i}:`, err);
        }
    }
}

async function main() {
    const args = process.argv.slice(2);
    const targetProject = args[0];

    const projects = loadProjectsFromScriptJson();

    if (targetProject) {
        await generateAudioForProject(targetProject);
    } else {
        console.log('No project specified, generating for all projects...');
        for (const projectId of Object.keys(projects)) {
            await generateAudioForProject(projectId);
        }
    }

    console.log('Audio generation complete.');
}

main().catch(console.error);
