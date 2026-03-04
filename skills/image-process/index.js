import { removeBackground } from "@imgly/background-removal-node";
import sharp from "sharp";
import fs from "fs/promises";
import path from "path";

const getMimeType = (filePath) => {
  const ext = path.extname(filePath).toLowerCase();
  const mimeTypes = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
  };
  return mimeTypes[ext] || 'image/jpeg';
};

/**
 * Compress image with adjustable quality
 * @param {Object} options
 * @param {string|Buffer} options.input - Input file path or buffer
 * @param {number} options.quality - Compression quality (1-100), default 80
 * @param {string} options.output - Output file path (optional)
 * @param {number} options.maxWidth - Max width (optional)
 * @param {number} options.maxHeight - Max height (optional)
 */
const compressImage = async (options) => {
  const {
    input,
    quality = 80,
    output,
    maxWidth,
    maxHeight,
  } = options;

  let imageBuffer;
  if (typeof input === "string") {
    imageBuffer = await fs.readFile(path.resolve(input));
  } else if (Buffer.isBuffer(input)) {
    imageBuffer = input;
  } else {
    throw new Error("Input must be a file path string or Buffer");
  }

  let pipeline = sharp(imageBuffer);

  if (maxWidth || maxHeight) {
    pipeline = pipeline.resize(maxWidth, maxHeight, {
      fit: 'inside',
      withoutEnlargement: true,
    });
  }

  const ext = output ? path.extname(output).toLowerCase() : '.jpg';

  if (ext === '.png') {
    pipeline = pipeline.png({ compressionLevel: 9 });
  } else if (ext === '.webp') {
    pipeline = pipeline.webp({ quality });
  } else {
    pipeline = pipeline.jpeg({ quality, mozjpeg: true });
  }

  const result = await pipeline.toBuffer();

  if (output) {
    await fs.writeFile(path.resolve(output), result);
    console.log('Compressed image saved to: ' + output);
  }

  return result;
};

/**
 * Remove background from image using AI
 * @param {Object} options
 * @param {string|Buffer} options.input - Input file path or buffer
 * @param {string} options.output - Output file path (optional)
 * @param {Function} options.onProgress - Progress callback (optional)
 */
const removeBackgroundFromImage = async (options) => {
  const { input, output, onProgress } = options;

  const config = {
    progress: (key, current, total) => {
      if (onProgress) {
        onProgress(key, current, total);
      }
    },
  };

  let imageBlob;
  if (typeof input === "string") {
    const absolutePath = path.resolve(input);
    const imageBuffer = await fs.readFile(absolutePath);
    const mimeType = getMimeType(input);
    imageBlob = new Blob([imageBuffer], { type: mimeType });
  } else if (Buffer.isBuffer(input)) {
    imageBlob = new Blob([input], { type: 'image/jpeg' });
  } else {
    throw new Error("Input must be a file path string or Buffer");
  }

  const result = await removeBackground(imageBlob, config);
  const resultBuffer = Buffer.from(await result.arrayBuffer());

  if (output) {
    await fs.writeFile(path.resolve(output), resultBuffer);
    console.log('Background removed image saved to: ' + output);
  }

  return resultBuffer;
};

/**
 * Replace background with solid color or another image
 * @param {Object} options
 * @param {string|Buffer} options.input - Foreground image path or buffer
 * @param {string} options.background - Hex color (e.g. '#ffffff') or path to background image
 * @param {string} options.output - Output file path (optional)
 * @param {number} options.quality - Output quality (1-100), default 95
 */
const replaceBackground = async (options) => {
  const {
    input,
    background,
    output,
    quality = 95,
  } = options;

  let foregroundBuffer;
  if (typeof input === "string") {
    foregroundBuffer = await fs.readFile(path.resolve(input));
  } else if (Buffer.isBuffer(input)) {
    foregroundBuffer = input;
  } else {
    throw new Error("Input must be a file path string or Buffer");
  }

  console.log("Removing background from foreground...");
  const foregroundNoBg = await removeBackgroundFromImage({ input: foregroundBuffer });

  const fgMeta = await sharp(foregroundNoBg).metadata();

  let bgBuffer;

  if (background.startsWith('#') || background.startsWith('rgb')) {
    bgBuffer = await sharp({
      create: {
        width: fgMeta.width,
        height: fgMeta.height,
        channels: 3,
        background: background,
      }
    }).png().toBuffer();
  } else {
    bgBuffer = await fs.readFile(path.resolve(background));
    bgBuffer = await sharp(bgBuffer)
      .resize(fgMeta.width, fgMeta.height, { fit: 'cover' })
      .toBuffer();
  }

  const result = await sharp(bgBuffer)
    .composite([
      {
        input: foregroundNoBg,
        top: 0,
        left: 0,
      },
    ])
    .jpeg({ quality })
    .toBuffer();

  if (output) {
    await fs.writeFile(path.resolve(output), result);
    console.log('Background replaced image saved to: ' + output);
  }

  return result;
};

/**
 * Upscale image to larger size
 * @param {Object} options
 * @param {string|Buffer} options.input - Input file path or buffer
 * @param {number} options.scale - Scale factor (e.g. 2 for 2x), default 2
 * @param {number} options.width - Target width (optional, overrides scale)
 * @param {number} options.height - Target height (optional, overrides scale)
 * @param {string} options.output - Output file path (optional)
 * @param {number} options.quality - Output quality (1-100), default 95
 */
const upscaleImage = async (options) => {
  const {
    input,
    scale = 2,
    width,
    height,
    output,
    quality = 95,
  } = options;

  let imageBuffer;
  if (typeof input === "string") {
    imageBuffer = await fs.readFile(path.resolve(input));
  } else if (Buffer.isBuffer(input)) {
    imageBuffer = input;
  } else {
    throw new Error("Input must be a file path string or Buffer");
  }

  const meta = await sharp(imageBuffer).metadata();

  let targetWidth = width;
  let targetHeight = height;

  if (!targetWidth && !targetHeight) {
    targetWidth = Math.round(meta.width * scale);
    targetHeight = Math.round(meta.height * scale);
  } else if (targetWidth && !targetHeight) {
    targetHeight = Math.round(targetWidth * (meta.height / meta.width));
  } else if (!targetWidth && targetHeight) {
    targetWidth = Math.round(targetHeight * (meta.width / meta.height));
  }

  console.log('Upscaling from ' + meta.width + 'x' + meta.height + ' to ' + targetWidth + 'x' + targetHeight);

  const result = await sharp(imageBuffer)
    .resize(targetWidth, targetHeight, {
      kernel: 'lanczos3',
      fit: 'fill',
    })
    .jpeg({ quality })
    .toBuffer();

  if (output) {
    await fs.writeFile(path.resolve(output), result);
    console.log('Upscaled image saved to: ' + output);
  }

  return result;
};

export {
  compressImage,
  removeBackgroundFromImage as removeBackground,
  replaceBackground,
  upscaleImage,
};

export default {
  compressImage,
  removeBackground: removeBackgroundFromImage,
  replaceBackground,
  upscaleImage,
};
