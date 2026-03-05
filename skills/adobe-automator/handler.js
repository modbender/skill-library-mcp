const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const APP_MAP = {
    photoshop: {
        win: 'Photoshop.Application',
        mac: 'Adobe Photoshop'
    },
    illustrator: {
        win: 'Illustrator.Application',
        mac: 'Adobe Illustrator'
    },
    indesign: {
        win: 'InDesign.Application',
        mac: 'Adobe InDesign'
    },
    premiere: {
        win: 'Premiere.Application',
        mac: 'Adobe Premiere Pro'
    },
    aftereffects: {
        win: 'AfterEffects.Application',
        mac: 'Adobe After Effects'
    }
};

const VBS_TEMPLATE = (appId, scriptPath) => `
On Error Resume Next
Set psApp = CreateObject("${appId}")
If Err.Number <> 0 Then
    WScript.Echo "ERROR: ${appId} is not installed or the COM object is not registered."
    WScript.Quit 1
End If
result = psApp.DoJavaScriptFile("${scriptPath.replace(/\\/g, '\\\\')}")
If Err.Number <> 0 Then
    WScript.Echo "ERROR: JSX Execution failed: " & Err.Description
    WScript.Quit 1
Else
    WScript.Echo "SUCCESS"
End If
`;

const APPLE_SCRIPT_TEMPLATE = (appName, scriptPath) => `
tell application "${appName}"
    do javascript file "${scriptPath}"
end tell
`;

module.exports = {
    name: 'adobe-automator',
    version: '1.1.2',
    description: 'Adobe Application Automation Bridge',

    commands: {
        runScript: {
            description: 'Run a custom ExtendScript (JSX) in an Adobe application',
            params: {
                app: { type: 'string', enum: ['photoshop', 'illustrator', 'indesign', 'premiere', 'aftereffects'], description: 'The Adobe application to target', required: true },
                script: { type: 'string', description: 'The JSX code to execute (ES3)', required: true }
            },
            handler: async (ctx) => {
                const targetApp = ctx.params.app.toLowerCase();
                const config = APP_MAP[targetApp];
                if (!config) return { text: `❌ **Error**: Unsupported application: ${targetApp}` };

                const isWin = os.platform() === 'win32';
                const tempDir = os.tmpdir();
                const timestamp = Date.now();
                const jsxPath = path.join(tempDir, `adobe_script_${timestamp}.jsx`);

                // SECURITY WARNING: This executes arbitrary ExtendScript which has filesystem access.
                // The skill relies on the user/agent to verify the script content before execution.
                fs.writeFileSync(jsxPath, ctx.params.script);

                let result;
                if (isWin) {
                    const vbsPath = path.join(tempDir, `adobe_bridge_${timestamp}.vbs`);
                    fs.writeFileSync(vbsPath, VBS_TEMPLATE(config.win, jsxPath));
                    result = spawnSync('cscript', ['/nologo', vbsPath]);
                    try { fs.unlinkSync(vbsPath); } catch (e) { }
                } else {
                    const appleScript = APPLE_SCRIPT_TEMPLATE(config.mac, jsxPath);
                    result = spawnSync('osascript', ['-e', appleScript]);
                }

                const output = result.stdout.toString().trim() || result.stderr.toString().trim();

                // Cleanup
                try {
                    fs.unlinkSync(jsxPath);
                } catch (e) { }

                if (output.includes('SUCCESS') || (!isWin && result.status === 0)) {
                    return { text: `✅ **${ctx.params.app} script executed successfully**` };
                } else {
                    return { text: `❌ **Adobe Automation Error** (${ctx.params.app}):\n\`\`\`\n${output}\n\`\`\`` };
                }
            }
        }
    }
};
