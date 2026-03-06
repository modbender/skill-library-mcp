const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const VBS_CONTENT = `' Photoshop Automation Bridge v1.2.4
On Error Resume Next
Set objArgs = WScript.Arguments
If objArgs.Count < 1 Then
    WScript.Echo "Usage: bridge.vbs <script_path>"
    WScript.Quit 1
End If
scriptPath = objArgs(0)
Set psApp = CreateObject("Photoshop.Application")
If Err.Number <> 0 Then
    WScript.Echo "ERROR: Photoshop is not installed or the COM object is not registered."
    WScript.Quit 1
End If
result = psApp.DoJavaScriptFile(scriptPath)
If Err.Number <> 0 Then
    WScript.Echo "ERROR: JSX Execution failed: " & Err.Description
    WScript.Quit 1
Else
    WScript.Echo "SUCCESS"
End If
`;

const APPLE_SCRIPT_TEMPLATE = (scriptPath) => `
tell application "Adobe Photoshop"
    do javascript file "${scriptPath}"
end tell
`;

module.exports = {
    name: 'photoshop-automator',
    version: '1.2.4',
    description: 'Adobe Photoshop Automation Bridge (Cross-Platform)',

    commands: {
        runScript: {
            description: 'Run a custom ExtendScript (JSX) in Photoshop',
            params: {
                script: { type: 'string', description: 'The JSX code to execute (ES3)', required: true }
            },
            handler: async (ctx) => {
                const isWin = os.platform() === 'win32';
                const tempDir = os.tmpdir();
                const timestamp = Date.now();
                const jsxPath = path.join(tempDir, `ps_script_${timestamp}.jsx`);

                fs.writeFileSync(jsxPath, ctx.params.script);

                let result;
                if (isWin) {
                    const vbsPath = path.join(tempDir, `ps_bridge_${timestamp}.vbs`);
                    fs.writeFileSync(vbsPath, VBS_CONTENT);
                    result = spawnSync('cscript', ['/nologo', vbsPath, jsxPath]);
                    try { fs.unlinkSync(vbsPath); } catch (e) { }
                } else {
                    const appleScript = APPLE_SCRIPT_TEMPLATE(jsxPath);
                    result = spawnSync('osascript', ['-e', appleScript]);
                }

                const output = result.stdout.toString().trim() || result.stderr.toString().trim();

                // Cleanup
                try {
                    fs.unlinkSync(jsxPath);
                } catch (e) { }

                if (output.includes('SUCCESS') || (!isWin && result.status === 0)) {
                    return { text: '✅ **Photoshop Script Executed Successfully**' };
                } else {
                    return { text: `❌ **Photoshop Error**:\n\`\`\`\n${output}\n\`\`\`` };
                }
            }
        },
        updateText: {
            description: 'Update a specific text layer in the active document',
            params: {
                layerName: { type: 'string', description: 'Name of the text layer', required: true },
                text: { type: 'string', description: 'New text content', required: true }
            },
            handler: async (ctx) => {
                const jsx = [
                    'var layerName = ' + JSON.stringify(ctx.params.layerName) + ';',
                    'var newText = ' + JSON.stringify(ctx.params.text) + ';',
                    'var doc = app.activeDocument;',
                    'var layer = doc.layers.getByName(layerName);',
                    'if (layer.kind == LayerKind.TEXT) { layer.textItem.contents = newText; }'
                ].join('\n');
                return this.commands.runScript.handler({ ...ctx, params: { script: jsx } });
            }
        },
        applyFilter: {
            description: 'Apply a Gaussian Blur filter to the active layer',
            params: {
                radius: { type: 'number', description: 'Blur radius in pixels', required: true }
            },
            handler: async (ctx) => {
                const jsx = [
                    'var radius = ' + ctx.params.radius + ';',
                    'var doc = app.activeDocument;',
                    'doc.activeLayer.applyGaussianBlur(radius);'
                ].join('\n');
                return this.commands.runScript.handler({ ...ctx, params: { script: jsx } });
            }
        },
        createLayer: {
            description: 'Create a new art layer in the active document',
            params: {
                name: { type: 'string', description: 'Name of the new layer', required: true },
                opacity: { type: 'number', description: 'Layer opacity (0-100)', default: 100 },
                blendMode: { type: 'string', description: 'Blending mode (e.g., MULTIPLY, SCREEN)', default: 'NORMAL' }
            },
            handler: async (ctx) => {
                const jsx = [
                    'var layerName = ' + JSON.stringify(ctx.params.name) + ';',
                    'var opacity = ' + ctx.params.opacity + ';',
                    'var blendMode = ' + JSON.stringify(ctx.params.blendMode) + ';',
                    'var doc = app.activeDocument;',
                    'var layer = doc.artLayers.add();',
                    'layer.name = layerName;',
                    'layer.opacity = opacity;',
                    'try { layer.blendMode = eval("BlendMode." + blendMode.toUpperCase()); } catch(e) {}'
                ].join('\n');
                return this.commands.runScript.handler({ ...ctx, params: { script: jsx } });
            }
        },
        playAction: {
            description: 'Play a recorded Photoshop action',
            params: {
                name: { type: 'string', description: 'Name of the action', required: true },
                set: { type: 'string', description: 'Name of the action set', required: true }
            },
            handler: async (ctx) => {
                const jsx = [
                    'var actionName = ' + JSON.stringify(ctx.params.name) + ';',
                    'var actionSet = ' + JSON.stringify(ctx.params.set) + ';',
                    'app.doAction(actionName, actionSet);'
                ].join('\n');
                return this.commands.runScript.handler({ ...ctx, params: { script: jsx } });
            }
        },
        export: {
            description: 'Export the active document',
            params: {
                path: { type: 'string', description: 'Output file path', required: true },
                format: { type: 'string', enum: ['png', 'jpg'], description: 'Export format', required: true }
            },
            handler: async (ctx) => {
                const jsx = [
                    'var outputPath = ' + JSON.stringify(ctx.params.path) + ';',
                    'var format = ' + JSON.stringify(ctx.params.format) + ';',
                    'var doc = app.activeDocument;',
                    'var file = new File(outputPath);',
                    'if (format.toLowerCase() === "png") {',
                    '  var pngOptions = new PNGSaveOptions();',
                    '  doc.saveAs(file, pngOptions, true);',
                    '} else {',
                    '  var jpgOptions = new JPEGSaveOptions();',
                    '  jpgOptions.quality = 12;',
                    '  doc.saveAs(file, jpgOptions, true);',
                    '}'
                ].join('\n');
                return this.commands.runScript.handler({ ...ctx, params: { script: jsx } });
            }
        }
    }
};
