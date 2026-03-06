import { program } from "commander";
import {
  compressImage,
  removeBackground,
  replaceBackground,
  upscaleImage,
} from "./index.js";

program
  .name("image-process")
  .description("Image processing tool: compress, remove/replace background")
  .version("1.0.0");

program
  .command("compress <input> [output]")
  .description("Compress an image")
  .option("-q, --quality <quality>", "Quality (1-100)", "80")
  .option("-w, --max-width <width>", "Max width")
  .option("-h, --max-height <height>", "Max height")
  .action(async (input, output, options) => {
    try {
      const outputPath = output || input.replace(/(\.[^.]+)$/, '-compressed$1');
      console.log('Compressing: ' + input);
      await compressImage({
        input,
        quality: parseInt(options.quality),
        maxWidth: options.maxWidth ? parseInt(options.maxWidth) : undefined,
        maxHeight: options.maxHeight ? parseInt(options.maxHeight) : undefined,
        output: outputPath,
      });
      console.log('Saved to: ' + outputPath);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

program
  .command("remove-bg <input> [output]")
  .description("Remove background from an image")
  .action(async (input, output) => {
    try {
      const outputPath = output || input.replace(/(\.[^.]+)$/, '-nobg.png');
      console.log('Removing background from: ' + input);
      await removeBackground({
        input,
        output: outputPath,
        onProgress: (key, current, total) => {
          console.log('  Progress: ' + Math.round((current / total) * 100) + '%');
        },
      });
      console.log('Saved to: ' + outputPath);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

program
  .command("replace-bg <input> <background> [output]")
  .description("Replace background with color (#ffffff) or another image")
  .option("-q, --quality <quality>", "Output quality (1-100)", "95")
  .action(async (input, background, output, options) => {
    try {
      const outputPath = output || input.replace(/(\.[^.]+)$/, '-newbg$1');
      console.log('Replacing background...');
      console.log('  Input: ' + input);
      console.log('  Background: ' + background);
      await replaceBackground({
        input,
        background,
        quality: parseInt(options.quality),
        output: outputPath,
      });
      console.log('Saved to: ' + outputPath);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

program
  .command("upscale <input> [output]")
  .description("Upscale image to larger size")
  .option("-s, --scale <scale>", "Scale factor (e.g. 2 for 2x)", "2")
  .option("-w, --width <width>", "Target width (overrides scale)")
  .option("-h, --height <height>", "Target height (overrides scale)")
  .option("-q, --quality <quality>", "Output quality (1-100)", "95")
  .action(async (input, output, options) => {
    try {
      const outputPath = output || input.replace(/(\.[^.]+)$/, '-upscaled$1');
      console.log('Upscaling: ' + input);
      await upscaleImage({
        input,
        scale: parseFloat(options.scale),
        width: options.width ? parseInt(options.width) : undefined,
        height: options.height ? parseInt(options.height) : undefined,
        quality: parseInt(options.quality),
        output: outputPath,
      });
      console.log('Saved to: ' + outputPath);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

program.parse();
