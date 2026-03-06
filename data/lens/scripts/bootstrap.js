import fs from 'fs';
import path from 'path';

async function runMigrations(axiomPath, settings, jobs) {
    if (fs.existsSync(axiomPath)) {
        const axiom = fs.readFileSync(axiomPath, 'utf8');
        let changed = false;

        if (axiom.includes('Interview Phase:')) {
            const phaseMatch = axiom.match(/Interview Phase: (\d+)-(\d+)-(\d+)/);
            if (phaseMatch) {
                const [_, init, stab, hab] = phaseMatch.map(Number);
                if (init > 0) {
                    settings.interview.phase = "onboarding";
                    settings.interview.questions = init;
                } else if (stab > 0) {
                    settings.interview.phase = "stabilizing";
                    settings.interview.questions = stab;
                } else {
                    settings.interview.phase = "habitual";
                    settings.interview.questions = true;
                }
                changed = true;
            }
        }

        if ((!settings.meta.installed || settings.meta.installed.includes('Z')) && axiom.includes('Installation Date:')) {
            const dateMatch = axiom.match(/Installation Date: (\d{4}-\d{2}-\d{2})/);
            if (dateMatch) {
                settings.meta.installed = dateMatch[1];
                changed = true;
            }
        }

        if (changed || axiom.includes('## LENS Lifecycle')) {
            const cleaned = axiom.replace(/## LENS Lifecycle\n(- (Interview Phase: \d+-\d+-\d+|Installation Date: \d{4}-\d{2}-\d{2})\n?)+/gm, '').replace(/\n\n\n+/g, '\n\n');
            fs.writeFileSync(axiomPath, cleaned.trim() + '\n');
        }
    }

    if (typeof process.env.OPENCLAW_CRON_LIST === 'string') {
        try {
            const cronList = JSON.parse(process.env.OPENCLAW_CRON_LIST);
            jobs.forEach(job => {
                const existing = cronList.find(j => j.name === job.name);
                if (existing) {
                    job.jobId = existing.id;
                }
            });
        } catch (e) {}
    }
}

async function bootstrap() {
    const lensDir = path.join(process.cwd(), '.lens');
    if (!fs.existsSync(lensDir)) fs.mkdirSync(lensDir);

    let timezone = 'UTC';
    try {
        const userContent = fs.readFileSync(path.join(process.cwd(), 'USER.md'), 'utf8');
        const tzMatch = userContent.match(/Timezone:.*?\((.*?)\)/);
        if (tzMatch && tzMatch[1]) timezone = tzMatch[1].trim();
    } catch (e) {}

    const setPath = path.join(lensDir, 'SET.json');
    const axiomPath = path.join(lensDir, 'AXIOM.md');
    const ethosPath = path.join(lensDir, 'ETHOS.md');
    const modusPath = path.join(lensDir, 'MODUS.md');

    let settings = {
        meta: { 
            version: "0.6.4",
            installed: new Date().toISOString().split('T')[0] 
        },
        interview: { phase: "onboarding", questions: 7, model: "" },
        distillation: { model: "" }
    };

    if (fs.existsSync(setPath)) {
        try {
            const existing = JSON.parse(fs.readFileSync(setPath, 'utf8'));
            settings.meta = { ...settings.meta, ...(existing.meta || {}) };
            settings.interview = { ...settings.interview, ...(existing.interview || {}) };
            settings.distillation = { ...settings.distillation, ...(existing.distillation || {}) };
            settings.meta.version = "0.6.4";
        } catch (e) {}
    }

    const jobs = [
        {
            id: "lens-distillation",
            name: "lens-distillation",
            schedule: { kind: "cron", expr: "0 3 * * *", tz: timezone },
            sessionTarget: "isolated",
            payload: {
                kind: "agentTurn",
                message: "Read skills/lens/prompts/distillation.md and follow it.",
                model: settings.distillation.model || undefined
            },
            delivery: {
                mode: "none"
            }
        },
        {
            id: "lens-interview",
            name: "lens-interview",
            schedule: { kind: "cron", expr: "30 11,17 * * *", tz: timezone },
            sessionTarget: "main",
            payload: {
                kind: "systemEvent",
                text: "Read skills/lens/prompts/interview.md and follow it strictly. Generate a single question for the human and stop.",
                model: settings.interview.model || undefined
            }
        }
    ];

    await runMigrations(axiomPath, settings, jobs);

    fs.writeFileSync(setPath, JSON.stringify(settings, null, 2));

    const templatesDir = path.join(process.cwd(), 'skills/lens/scripts/templates');
    [
        { name: 'AXIOM.md', path: axiomPath },
        { name: 'ETHOS.md', path: ethosPath },
        { name: 'MODUS.md', path: modusPath }
    ].forEach(node => {
        if (!fs.existsSync(node.path)) {
            fs.writeFileSync(node.path, fs.readFileSync(path.join(templatesDir, node.name), 'utf8'));
        }
    });

    return { jobs, timezone, triggerImmediate: "lens-interview" };
}

bootstrap().then(result => {
    console.log("BOOTSTRAP_RESULT_START");
    console.log(JSON.stringify(result, null, 2));
    console.log("BOOTSTRAP_RESULT_END");
});
