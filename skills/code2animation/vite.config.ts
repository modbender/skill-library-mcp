import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import { MsEdgeTTS, OUTPUT_FORMAT } from 'msedge-tts';
import { exec } from 'child_process';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    server: {
      port: 3000,
      host: '0.0.0.0',
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modifyâfile watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
    },
    plugins: [
      react(),
      tailwindcss(),
      {
        name: 'edge-tts-server',
        configureServer(server) {
          server.middlewares.use('/api/tts', async (req, res, next) => {
            if (req.method === 'POST') {
              let body = '';
              req.on('data', chunk => {
                body += chunk.toString();
              });
              req.on('end', async () => {
                try {
                  const { text, voice, rate, pitch } = JSON.parse(body);
                  const isChinese = /[\u4e00-\u9fa5]/.test(text);
                  const effectiveVoice = voice || (isChinese ? 'zh-CN-YunjianNeural' : 'en-US-GuyNeural');

                  const tts = new MsEdgeTTS();
                  await tts.setMetadata(effectiveVoice, OUTPUT_FORMAT.AUDIO_24KHZ_48KBITRATE_MONO_MP3);

                  // Generate SSML with rate and pitch
                  const ssml = `<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
                      <voice name='${effectiveVoice}'>
                          <prosody pitch='${pitch || "+0Hz"}' rate='${rate || "+0%"}' volume='+0%'>
                              ${text}
                          </prosody>
                      </voice>
                  </speak>`;

                  // Use rawToStream because we are providing full SSML
                  const result = await tts.rawToStream(ssml);

                  res.setHeader('Content-Type', 'audio/mpeg');
                  result.audioStream.pipe(res);
                } catch (err) {
                  console.error('TTS Error:', err);
                  res.statusCode = 500;
                  res.end(JSON.stringify({ error: err.message }));
                }
              });
            } else {
              next();
            }
          });

          server.middlewares.use('/api/generate-audio', async (req, res, next) => {
            if (req.method === 'POST') {
              let body = '';
              req.on('data', chunk => { body += chunk.toString(); });
              req.on('end', () => {
                const { projectId } = JSON.parse(body);
                // Run the script using tsx
                const cmd = `npx tsx scripts/generate-audio.ts ${projectId}`;
                console.log(`Executing: ${cmd}`);
                exec(cmd, (error: any, stdout: any, stderr: any) => {
                  if (error) {
                    console.error(`Exec error: ${error}`);
                    res.statusCode = 500;
                    res.end(JSON.stringify({ error: error.message, stderr }));
                    return;
                  }
                  res.end(JSON.stringify({ success: true, stdout }));
                });
              });
            } else {
              next();
            }
          });
        }
      }
    ],
    define: {
      'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
  };
});
