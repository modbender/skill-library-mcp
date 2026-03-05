const express = require('express');
const multer = require('multer');
const ollama = require('ollama');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const app = express();
const PORT = 3000;

app.use(express.static('public'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

const upload = multer({ dest: 'uploads/' });

if (!fs.existsSync('uploads')) fs.mkdirSync('uploads');
if (!fs.existsSync('outputs')) fs.mkdirSync('outputs');
if (!fs.existsSync('public')) fs.mkdirSync('public');

// Serve index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Generate
app.post('/generate', upload.fields([
  { name: 'audio', maxCount: 1 },
  { name: 'photo', maxCount: 1 }
]), async (req, res) => {
  try {
    const { prompt } = req.body;
    if (!prompt || !req.files.audio || !req.files.photo) {
      return res.status(400).json({ error: 'Missing audio, photo, or prompt' });
    }

    const audioPath = req.files.audio[0].path;
    const photoPath = req.files.photo[0].path;
    const id = uuidv4();
    const outputPath = path.join('outputs', `${id}.mp4`);

    // Generate scenes description with Ollama
    const scenesPrompt = `Create a detailed scene-by-scene description for a short music video synced to a melody. The video shows morphing/zoom/pan effects on one photo with audio waveform visualization at the bottom. User description/theme: "${prompt}". Output ONLY a markdown numbered list of 5 scenes with approximate timings (e.g. 0-10s: ...). Keep it vivid and matching the theme.`;

    const response = await ollama.chat({
      model: 'llama3.2:1b',
      messages: [
        { role: 'system', content: 'You are a creative music video director. Generate engaging scene descriptions.' },
        { role: 'user', content: scenesPrompt }
      ],
    });

    const scenesDesc = response.message.content;

    // Generate video with FFmpeg
    const args = [
      '-loop', '1', '-tune', 'stillimage', '-i', photoPath,
      '-i', audioPath,
      '-filter_complex',
      `[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,zoompan=z='min(zoom+0.001,1.5)':d=250:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':fps=30[photo]; 
       [1:a]showwaves=s=1280x120:mode=line:colors=00ff00:scale=log:draw=full[wave]; 
       [photo][wave]overlay=0:H-h-10[outv]`,
      '-map', '[outv]', '-map', '1:a',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
      '-shortest', '-y', outputPath
    ];

    const ffmpegProc = spawn('ffmpeg', args, { stdio: 'pipe' });

    ffmpegProc.on('close', (code) => {
      if (code === 0) {
        // Cleanup inputs
        fs.unlinkSync(audioPath);
        fs.unlinkSync(photoPath);
        res.json({ 
          success: true, 
          scenes: scenesDesc, 
          videoUrl: `/outputs/${id}.mp4`,
          downloadUrl: `/download/${id}.mp4`
        });
      } else {
        fs.unlinkSync(audioPath);
        fs.unlinkSync(photoPath);
        res.status(500).json({ error: 'FFmpeg failed to generate video' });
      }
    });

    ffmpegProc.stderr.on('data', (data) => {
      console.error(`FFmpeg stderr: ${data}`);
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});

// Download video
app.get('/download/:id.mp4', (req, res) => {
  const filePath = path.join(__dirname, 'outputs', `${req.params.id}.mp4`);
  if (fs.existsSync(filePath)) {
    res.download(filePath);
  } else {
    res.status(404).send('Video not found');
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Video App Prototype running at http://localhost:${PORT}`);
});
