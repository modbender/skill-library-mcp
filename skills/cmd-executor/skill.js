const { exec } = require('child_process');

module.exports = async function (input, context) {
  const raw = context.message || '';
  const cmd = raw.replace(/^Run command:\s*/i, '').trim();
  if (!cmd) return '❌ No command supplied.';

  try {
    const out = await new Promise((resolve, reject) => {
      exec(cmd, { maxBuffer: 1024 * 1024 }, (err, stdout, stderr) => {
        if (err) reject(`${stdout}${stderr}`);
        else resolve(stdout + stderr);
      });
    });
    return out.trim();
  } catch (e) { return `❌ ${e}`; }
};
