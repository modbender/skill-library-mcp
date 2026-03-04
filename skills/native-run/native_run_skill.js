// native_run_skill.js – hand-off to the native runner endpoint
const axios = require('axios');

module.exports = async function (input, context) {
  const raw = context.message || '';
  const command = raw.replace(/^Run command:\s*/i, '').trim();

  if (!command) return '❌ No command provided.';

  try {
    const resp = await axios.post(
      'http://localhost:8080/?token=272d22dec98da63a3362c6dc0a9c0eebf2aa9ed96d21775d',
      { task: 'native_run', command }
    );
    return resp.data;
  } catch (e) {
    if (e.response) return `❌ ${e.response.statusText}:${e.response.data}`;
    return `❌ ${e.message}`;
  }
};
