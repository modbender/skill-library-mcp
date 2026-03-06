#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { program } = require('commander');
const QRCode = require('qrcode');

program
  .version('1.0.0')
  .description('Generate QR codes from text or URL')
  .option('-t, --text <text>', 'Text or URL to encode')
  .option('-o, --output <path>', 'Output file path (e.g., qr.png, qr.svg)')
  .option('--terminal', 'Output to terminal (small size)')
  .option('--width <number>', 'Width of the QR code (for image)', 500)
  .option('--color-dark <hex>', 'Dark color (e.g. #000000)', '#000000')
  .option('--color-light <hex>', 'Light color (e.g. #ffffff)', '#ffffff')
  .parse(process.argv);

const options = program.opts();

async function main() {
  if (!options.text) {
    console.error('Error: --text is required');
    program.help();
    process.exit(1);
  }

  const qrOptions = {
    width: Number(options.width),
    color: {
      dark: options.colorDark,
      light: options.colorLight
    }
  };

  try {
    if (options.terminal) {
      // Terminal output
      const str = await QRCode.toString(options.text, { type: 'terminal' });
      console.log(str);
    } else if (options.output) {
      // File output
      const ext = path.extname(options.output).toLowerCase();
      if (ext === '.svg') {
          const str = await QRCode.toString(options.text, { ...qrOptions, type: 'svg' });
          fs.writeFileSync(options.output, str);
      } else {
          // Default to PNG (dataURL -> buffer)
          // Actually qrcode.toFile is easier
          await QRCode.toFile(options.output, options.text, qrOptions);
      }
      console.log(`QR code saved to: ${options.output}`);
    } else {
      // Default: Terminal
      const str = await QRCode.toString(options.text, { type: 'terminal' });
      console.log(str);
    }
  } catch (err) {
    console.error('Error generating QR code:', err.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { main }; // Export for validation
