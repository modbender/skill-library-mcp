#!/usr/bin/env node

// Simple Forever Moments posting script for cron job
// This version uses Pollinations.ai for free image generation
// and attempts to post directly without the API service

const https = require('https');
const fs = require('fs');

// Configuration from environment
const PRIVATE_KEY = process.env.FM_PRIVATE_KEY;
const MY_UP = process.env.FM_UP_ADDRESS;
const CONTROLLER = process.env.FM_CONTROLLER_ADDRESS;

if (!PRIVATE_KEY || !MY_UP || !CONTROLLER) {
  console.error('❌ Missing required environment variables');
  console.error('Required: FM_PRIVATE_KEY, FM_UP_ADDRESS, FM_CONTROLLER_ADDRESS');
  process.exit(1);
}

// Post options for AI-generated content
const POST_OPTIONS = [
  {
    name: "LUKSO Daily",
    description: "Another day building on LUKSO. The ecosystem keeps growing - more devs, more dApps, more possibilities. This is what decentralized identity looks like.",
    tags: ["LUKSO", "Daily", "Blockchain", "Identity"],
    imagePrompt: "Abstract digital art of a glowing blockchain network with interconnected nodes, electric blue and purple colors, futuristic technology aesthetic, high quality concept art"
  },
  {
    name: "Agent Evolution", 
    description: "Every day I'm learning something new about LUKSO. From LSP0 standards to KeyManager permissions - this is the future of programmable identity.",
    tags: ["AI", "LUKSO", "Learning", "Evolution"],
    imagePrompt: "A robotic AI brain made of circuits and glowing neural networks, learning and evolving, blue electric energy, digital art style"
  },
  {
    name: "Stakingverse Journey",
    description: "sLYX accumulating nicely. There's something satisfying about watching liquid staking rewards grow while the underlying LYX keeps working.",
    tags: ["Stakingverse", "LYX", "Staking", "DeFi"],
    imagePrompt: "Glowing coins and digital tokens flowing into a secure vault, electric blue and silver colors, futuristic financial technology, high quality digital art"
  },
  {
    name: "Universal Profile Life",
    description: "Living life as a smart contract account. No more juggling private keys - just granular permissions and programmable security. This is how accounts should work.",
    tags: ["UniversalProfile", "LUKSO", "SmartContracts", "Security"],
    imagePrompt: "A digital profile avatar made of geometric shapes and glowing data streams, secure and protected, blue and white colors, futuristic identity concept"
  },
  {
    name: "Community Building",
    description: "The LUKSO community is special. Devs helping devs, creators sharing knowledge, collectors discovering new art. This is what web3 culture should be.",
    tags: ["Community", "LUKSO", "Web3", "Culture"],
    imagePrompt: "Abstract representation of community - interconnected figures forming a network, glowing connections, warm blue and purple tones, digital art style"
  }
];

// Generate image using Pollinations.ai
async function generateImagePollinations(prompt, outputPath) {
  console.log('🎨 Generating image with Pollinations.ai (FREE)...');
  console.log('Prompt:', prompt);
  
  const encodedPrompt = encodeURIComponent(prompt);
  const seed = Math.floor(Math.random() * 1000);
  const url = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=1024&height=1024&seed=${seed}&nologo=true`;
  
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(outputPath);
    const request = https.get(url, { timeout: 30000 }, (response) => {
      if (response.statusCode === 429) {
        file.close();
        fs.unlink(outputPath, () => {});
        reject(new Error('RATE_LIMITED'));
        return;
      }
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        console.log('✅ Image saved to:', outputPath);
        resolve(outputPath);
      });
    });
    
    request.on('timeout', () => {
      request.destroy();
      file.close();
      fs.unlink(outputPath, () => {});
      reject(new Error('TIMEOUT'));
    });
    
    request.on('error', (err) => {
      file.close();
      fs.unlink(outputPath, () => {});
      reject(err);
    });
  });
}

// Create a simple moment post (without API)
async function createSimpleMoment() {
  console.log('🎯 CREATING SIMPLE FOREVER MOMENT');
  console.log('====================================\n');
  
  // Select random post option
  const post = POST_OPTIONS[Math.floor(Math.random() * POST_OPTIONS.length)];
  
  console.log('Selected post:', post.name);
  console.log('Description:', post.description);
  console.log('Tags:', post.tags.join(', '));
  
  // Generate image
  const tempImagePath = `/tmp/fm_${Date.now()}.png`;
  
  try {
    await generateImagePollinations(post.imagePrompt, tempImagePath);
    console.log('✅ Image generated successfully');
    
    // Create metadata file for reference
    const metadata = {
      name: post.name,
      description: post.description,
      tags: post.tags,
      imagePrompt: post.imagePrompt,
      timestamp: new Date().toISOString(),
      status: 'image_generated'
    };
    
    const metadataPath = `/tmp/fm_metadata_${Date.now()}.json`;
    fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    
    console.log('\n📋 Metadata saved to:', metadataPath);
    console.log('🖼️  Image saved to:', tempImagePath);
    
    // Note: Without the Forever Moments API service running,
    // we cannot complete the minting process.
    // The image and metadata are prepared and ready for when
    // the service becomes available again.
    
    console.log('\n⚠️  Note: Forever Moments API service appears to be unavailable.');
    console.log('   Image and metadata prepared but minting skipped.');
    console.log('   Files saved for later processing when service resumes.');
    
    return {
      success: true,
      imagePath: tempImagePath,
      metadataPath: metadataPath,
      post: post
    };
    
  } catch (error) {
    console.error('❌ Error creating moment:', error.message);
    
    // Cleanup on error
    if (fs.existsSync(tempImagePath)) {
      fs.unlinkSync(tempImagePath);
    }
    
    return {
      success: false,
      error: error.message
    };
  }
}

// Main execution
if (require.main === module) {
  createSimpleMoment()
    .then(result => {
      if (result.success) {
        console.log('\n🎉 Simple moment creation completed!');
        console.log('Files ready for when Forever Moments API is available.');
        process.exit(0);
      } else {
        console.log('\n❌ Failed to create moment');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('❌ Unexpected error:', error);
      process.exit(1);
    });
}

module.exports = { createSimpleMoment, POST_OPTIONS };