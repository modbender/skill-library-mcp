import {
  translateText,
  detectLanguage,
  ocrImage,
  speechToText,
} from '../dist/index.js';
import { createStats, logSuiteStart, logSuiteEnd, runCase } from './_utils.mjs';

const stats = createStats();
logSuiteStart('feishu/ai (翻译/OCR/STT)');

await runCase(stats, {
  name: 'translateText',
  fn: () => translateText('你好，世界', 'zh', 'en'),
});

await runCase(stats, {
  name: 'detectLanguage',
  fn: () => detectLanguage('Hello world'),
});

await runCase(stats, {
  name: 'ocrImage',
  requires: ['TEST_OCR_IMAGE_PATH'],
  fn: () => ocrImage(process.env.TEST_OCR_IMAGE_PATH),
});

await runCase(stats, {
  name: 'speechToText',
  requires: ['TEST_AUDIO_PATH'],
  fn: () => speechToText(process.env.TEST_AUDIO_PATH, process.env.TEST_AUDIO_FORMAT || 'opus'),
});

logSuiteEnd('feishu/ai', stats);
