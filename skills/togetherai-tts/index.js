const axios = require('axios');
const fs = require('fs');
const dotenv = require('dotenv');
dotenv.config();

const apiKey = process.env.TOGETHERAI_API_KEY;
const model = process.env.TOGETHERAI_MODEL;
const format = process.env.TTS_FORMAT;
const voice = process.env.TTS_VOICE;

async function generateTTS(text, outputFile) {
  try {
    const response = await axios.post(
      'https://api.together.ai/v1/audio/speech',
      {
        text,
        model,
        voice,
        format,
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
        },
      }
    );

    const audioData = response.data.audio;
    fs.writeFileSync(outputFile, Buffer.from(audioData, 'base64'));

    console.log(`TTS generated and saved to ${outputFile}`);
  } catch (error) {
    console.error('Error generating TTS:', error);
  }
}

if (process.argv.length < 4) {
  console.error('Usage: node index.js <text> <output_file>');
  process.exit(1);
}

const text = process.argv[2];
const outputFile = process.argv[3];

generateTTS(text, outputFile);
