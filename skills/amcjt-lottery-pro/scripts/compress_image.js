const fs = require('fs');
const path = require('path');

/**
 * 图片压缩脚本
 * 将彩票图片压缩到 200KB 以内（适合 OCR 上传）
 *
 * 使用方法：
 *   node compress_image.js <inputPath> [outputPath]
 *
 * 示例：
 *   node compress_image.js ./lottery.jpg ./lottery-small.jpg
 */

// 目标文件大小（200KB）
const TARGET_SIZE = 200 * 1024;

// 支持的图片格式
const SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.tiff', '.avif'];

/**
 * 检查 sharp 库是否已安装
 * @returns {boolean}
 */
function checkSharpInstalled() {
  try {
    require.resolve('sharp');
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * 获取文件扩展名
 * @param {string} filePath
 * @returns {string}
 */
function getExtension(filePath) {
  return path.extname(filePath).toLowerCase();
}

/**
 * 检查是否为支持的图片格式
 * @param {string} filePath
 * @returns {boolean}
 */
function isSupportedImage(filePath) {
  const ext = getExtension(filePath);
  return SUPPORTED_FORMATS.includes(ext);
}

/**
 * 格式化文件大小
 * @param {number} bytes
 * @returns {string}
 */
function formatSize(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
}

/**
 * 智能压缩图片
 * @param {string} inputPath - 输入文件路径
 * @param {string} outputPath - 输出文件路径
 * @param {number} targetSize - 目标大小（字节）
 * @returns {Promise<Object>}
 */
async function compressImage(inputPath, outputPath, targetSize = TARGET_SIZE) {
  const sharp = require('sharp');

  const inputStats = fs.statSync(inputPath);
  const inputSize = inputStats.size;

  console.log(`Input: ${inputPath} (${formatSize(inputSize)})`);

  // 如果已经小于目标大小，直接复制
  if (inputSize <= targetSize) {
    console.log(`✓ File already under ${formatSize(targetSize)}, copying without compression...`);
    fs.copyFileSync(inputPath, outputPath);
    return {
      success: true,
      inputSize,
      outputSize: inputSize,
      compressed: false,
      message: 'File already under target size'
    };
  }

  // 获取图片元数据
  const metadata = await sharp(inputPath).metadata();
  console.log(`Original dimensions: ${metadata.width}x${metadata.height}`);

  // 计算需要的压缩比例
  const compressionRatio = Math.sqrt(targetSize / inputSize);

  // 确定输出格式
  const ext = getExtension(outputPath);
  const format = ext === '.png' ? 'png' :
                 ext === '.webp' ? 'webp' :
                 ext === '.gif' ? 'gif' :
                 ext === '.avif' ? 'avif' :
                 ext === '.tiff' ? 'tiff' : 'jpeg';

  // 智能调整参数
  let quality;
  let resizeWidth = metadata.width;
  let resizeHeight = metadata.height;

  // 如果图片尺寸很大，先进行尺寸缩减
  const MAX_DIMENSION = 2048;
  if (metadata.width > MAX_DIMENSION || metadata.height > MAX_DIMENSION) {
    const scale = Math.min(MAX_DIMENSION / metadata.width, MAX_DIMENSION / metadata.height);
    resizeWidth = Math.round(metadata.width * scale);
    resizeHeight = Math.round(metadata.height * scale);
    console.log(`Resizing to: ${resizeWidth}x${resizeHeight}`);
  }

  // 根据压缩比例调整质量
  quality = Math.max(30, Math.min(85, Math.round(compressionRatio * 100)));

  // 构建 sharp 处理管道
  let pipeline = sharp(inputPath);

  // 调整尺寸
  if (resizeWidth !== metadata.width || resizeHeight !== metadata.height) {
    pipeline = pipeline.resize(resizeWidth, resizeHeight, {
      fit: 'inside',
      withoutEnlargement: true
    });
  }

  // 根据格式设置输出选项
  switch (format) {
    case 'jpeg':
    case 'jpg':
      pipeline = pipeline.jpeg({
        quality,
        progressive: true,
        mozjpeg: true
      });
      break;
    case 'png':
      pipeline = pipeline.png({
        compressionLevel: 9,
        adaptiveFiltering: true,
        palette: inputSize > 500 * 1024 // 大文件使用调色板模式
      });
      break;
    case 'webp':
      pipeline = pipeline.webp({
        quality,
        effort: 6
      });
      break;
    case 'avif':
      pipeline = pipeline.avif({
        quality,
        effort: 4
      });
      break;
    case 'gif':
      // GIF 压缩限制颜色数
      pipeline = pipeline.gif({
        colours: 128,
        effort: 10
      });
      break;
    case 'tiff':
      pipeline = pipeline.tiff({
        quality,
        compression: 'jpeg'
      });
      break;
  }

  // 执行压缩
  await pipeline.toFile(outputPath);

  // 检查结果
  const outputStats = fs.statSync(outputPath);
  const outputSize = outputStats.size;

  console.log(`Output: ${outputPath} (${formatSize(outputSize)})`);

  // 如果仍然超过目标大小，进行二次压缩
  if (outputSize > targetSize && format === 'jpeg') {
    console.log('Still over target size, applying additional compression...');

    // 进一步降低质量和尺寸
    const additionalQuality = Math.max(20, Math.round(quality * 0.7));
    const additionalScale = Math.sqrt(targetSize / outputSize) * 0.9;

    await sharp(outputPath)
      .resize(Math.round(resizeWidth * additionalScale), null, {
        fit: 'inside',
        withoutEnlargement: true
      })
      .jpeg({
        quality: additionalQuality,
        progressive: true,
        mozjpeg: true
      })
      .toFile(outputPath + '.tmp');

    fs.renameSync(outputPath + '.tmp', outputPath);

    const finalStats = fs.statSync(outputPath);
    console.log(`Final output: ${outputPath} (${formatSize(finalStats.size)})`);

    return {
      success: true,
      inputSize,
      outputSize: finalStats.size,
      compressed: true,
      compressionRatio: ((1 - finalStats.size / inputSize) * 100).toFixed(1),
      dimensions: `${Math.round(resizeWidth * additionalScale)}x${Math.round(resizeHeight * additionalScale)}`
    };
  }

  return {
    success: true,
    inputSize,
    outputSize,
    compressed: true,
    compressionRatio: ((1 - outputSize / inputSize) * 100).toFixed(1),
    dimensions: `${resizeWidth}x${resizeHeight}`
  };
}

/**
 * 主函数
 */
async function main() {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3];

  // 显示帮助信息
  if (!inputPath || inputPath === '--help' || inputPath === '-h') {
    console.log(`
╔════════════════════════════════════════════════════════════╗
║           Image Compressor - 图片压缩工具                   ║
╚════════════════════════════════════════════════════════════╝

Usage:
  node compress_image.js <inputPath> [outputPath]

Arguments:
  inputPath    输入图片路径（必需）
  outputPath   输出图片路径（可选，默认为 input-compressed.ext）

Supported formats:
  JPEG, PNG, WebP, GIF, TIFF, AVIF

Examples:
  node compress_image.js ./lottery.jpg
  node compress_image.js ./lottery.jpg ./lottery-small.jpg
  node compress_image.js ./photo.png ./photo-compressed.webp

Target size: 200KB (suitable for OCR upload)
`);
    process.exit(0);
  }

  // 检查 sharp 是否安装
  if (!checkSharpInstalled()) {
    console.error(`
❌ Error: 'sharp' library is not installed.

Please install it first:
  npm install sharp

Or if you're in the project root:
  cd ${path.dirname(__dirname)} && npm install
`);
    process.exit(1);
  }

  // 检查输入文件是否存在
  if (!fs.existsSync(inputPath)) {
    console.error(`❌ Error: File not found: ${inputPath}`);
    process.exit(1);
  }

  // 检查是否为支持的图片格式
  if (!isSupportedImage(inputPath)) {
    console.error(`❌ Error: Unsupported image format.`);
    console.error(`Supported formats: ${SUPPORTED_FORMATS.join(', ')}`);
    process.exit(1);
  }

  // 确定输出路径
  const finalOutputPath = outputPath || inputPath.replace(/\.([^.]+)$/, '-compressed.$1');

  // 确保输出目录存在
  const outputDir = path.dirname(finalOutputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  try {
    console.log('\n🖼️  Starting image compression...\n');

    const result = await compressImage(inputPath, finalOutputPath);

    console.log('\n✅ Compression completed successfully!');
    console.log(`   Original size: ${formatSize(result.inputSize)}`);
    console.log(`   Final size:    ${formatSize(result.outputSize)}`);
    if (result.compressed) {
      console.log(`   Reduced by:    ${result.compressionRatio}%`);
    }
    console.log(`   Output:        ${finalOutputPath}`);

    // 检查结果是否仍超过目标大小
    if (result.outputSize > TARGET_SIZE) {
      console.log(`\n⚠️  Warning: Output file (${formatSize(result.outputSize)}) still exceeds target size (${formatSize(TARGET_SIZE)}).`);
      console.log('   Consider using a lower resolution source image.');
    } else {
      console.log(`\n✓ File is now suitable for OCR upload!`);
    }

    process.exit(0);
  } catch (error) {
    console.error(`\n❌ Compression failed: ${error.message}`);

    // 如果压缩失败，尝试直接复制
    try {
      console.log('Attempting to copy file without compression...');
      fs.copyFileSync(inputPath, finalOutputPath);
      console.log(`✓ File copied to: ${finalOutputPath}`);
    } catch (copyError) {
      console.error(`❌ Copy also failed: ${copyError.message}`);
    }

    process.exit(1);
  }
}

// 运行主函数
main().catch(error => {
  console.error('Unexpected error:', error);
  process.exit(1);
});