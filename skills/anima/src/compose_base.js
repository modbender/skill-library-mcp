const sharp = require('sharp');
const path = require('path');

const BG_PATH = 'skills/anima/assets/backgrounds/cherry_blossom_bg.png';
const AVATAR_PATH = 'avatars/shutiao_full.png'; // Use full body original
const OUTPUT_PATH = 'skills/anima/assets/sprites/shutiao_base.png';

async function compose() {
  try {
    // 1. Get dimensions
    const bgMetadata = await sharp(BG_PATH).metadata();
    
    // 2. Load avatar and resize
    // We want the avatar to be prominent, say 85% of the background height
    const targetHeight = Math.floor(bgMetadata.height * 0.85);
    
    // 3. Composite
    await sharp(BG_PATH)
      .composite([{
        input: await sharp(AVATAR_PATH).resize({ height: targetHeight }).toBuffer(),
        gravity: 'center' // Place in center
      }])
      .toFile(OUTPUT_PATH);
      
    console.log('Base sprite created at:', OUTPUT_PATH);
  } catch (err) {
    console.error('Error composing:', err);
    process.exit(1);
  }
}

compose();
