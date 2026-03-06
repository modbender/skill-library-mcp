/**
 * Batch Process Entry Point
 * AutoClip Pro - 视频批量处理技能包
 * 
 * 主入口脚本，负责批量处理视频
 */

const fs = require('fs');
const path = require('path');
const VideoEditor = require('./video-editor');

// 支持的视频格式
const SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.webm'];

class BatchProcessor {
  constructor(configPath = '../config.json') {
    this.config = this.loadConfig(configPath);
    this.editor = new VideoEditor(this.config);
    this.stats = {
      total: 0,
      processed: 0,
      failed: 0,
      skipped: 0
    };
  }

  /**
   * 加载配置文件
   */
  loadConfig(configPath) {
    const fullPath = path.resolve(__dirname, configPath);
    if (fs.existsSync(fullPath)) {
      const content = fs.readFileSync(fullPath, 'utf8');
      return JSON.parse(content);
    }
    return this.getDefaultConfig();
  }

  /**
   * 默认配置
   */
  getDefaultConfig() {
    return {
      inputDir: './input',
      outputDir: './output',
      tempDir: './temp',
      template: 'knowledge',
      video: {
        resolution: '1080p',
        fps: 30,
        bitrate: '8000k',
        codec: 'libx264',
        preset: 'medium'
      },
      audio: {
        codec: 'aac',
        bitrate: '192k',
        sampleRate: 44100
      },
      subtitles: {
        enabled: true,
        font: 'Microsoft YaHei',
        fontSize: 24,
        fontColor: 'white',
        position: 'bottom',
        margin: 50
      },
      watermark: {
        enabled: false,
        text: 'AutoClip Pro',
        position: 'bottom-right',
        opacity: 0.5
      },
      transitions: {
        enabled: true,
        defaultDuration: 0.5,
        type: 'fade'
      },
      batch: {
        maxConcurrent: 2,
        overwriteExisting: false,
        keepTempFiles: false
      }
    };
  }

  /**
   * 加载模板
   */
  loadTemplate(templateName) {
    const templatePath = path.resolve(__dirname, '../templates', `${templateName}.json`);
    if (fs.existsSync(templatePath)) {
      const content = fs.readFileSync(templatePath, 'utf8');
      return JSON.parse(content);
    }
    return null;
  }

  /**
   * 扫描输入目录中的视频文件
   */
  scanVideos() {
    const inputDir = path.resolve(__dirname, '..', this.config.inputDir);
    
    if (!fs.existsSync(inputDir)) {
      fs.mkdirSync(inputDir, { recursive: true });
      return [];
    }

    const files = fs.readdirSync(inputDir);
    return files
      .filter(file => SUPPORTED_FORMATS.includes(path.extname(file).toLowerCase()))
      .map(file => ({
        name: file,
        path: path.join(inputDir, file),
        ext: path.extname(file)
      }));
  }

  /**
   * 处理单个视频
   */
  async processVideo(video, index, total) {
    console.log(`\n[${index + 1}/${total}] 处理: ${video.name}`);
    
    const outputDir = path.resolve(__dirname, '..', this.config.outputDir);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const outputName = path.basename(video.name, video.ext) + '_processed.mp4';
    const outputPath = path.join(outputDir, outputName);

    // 检查是否已存在
    if (!this.config.batch.overwriteExisting && fs.existsSync(outputPath)) {
      console.log(`  ⏭️ 跳过 (已存在): ${outputName}`);
      this.stats.skipped++;
      return { success: true, skipped: true };
    }

    try {
      // 1. 获取视频信息
      console.log('  📊 分析视频信息...');
      const info = await this.editor.getVideoInfo(video.path);
      console.log(`     时长: ${this.formatDuration(info.duration)}`);
      console.log(`     分辨率: ${info.width}x${info.height}`);
      console.log(`     帧率: ${info.fps} fps`);

      // 2. 应用模板处理
      const template = this.loadTemplate(this.config.template);
      let tempFile = video.path;
      const tempFiles = [];

      // 3. 调整分辨率
      if (this.config.video.resolution) {
        console.log(`  📐 调整分辨率: ${this.config.video.resolution}`);
        const resizedFile = path.join(outputDir, `_temp_resized_${index}.mp4`);
        await this.editor.resize(tempFile, resizedFile, this.config.video.resolution);
        if (tempFile !== video.path) tempFiles.push(tempFile);
        tempFile = resizedFile;
        tempFiles.push(resizedFile);
      }

      // 4. 添加水印
      if (this.config.watermark.enabled) {
        console.log('  💧 添加水印...');
        const watermarkedFile = path.join(outputDir, `_temp_watermark_${index}.mp4`);
        await this.editor.addWatermark(tempFile, watermarkedFile, this.config.watermark);
        tempFiles.push(tempFile);
        tempFile = watermarkedFile;
        tempFiles.push(watermarkedFile);
      }

      // 5. 添加转场效果
      if (this.config.transitions.enabled && template?.transitions) {
        console.log('  ✨ 添加转场效果...');
        const transitionFile = path.join(outputDir, `_temp_transition_${index}.mp4`);
        await this.editor.addTransition(tempFile, transitionFile, {
          type: this.config.transitions.type,
          duration: this.config.transitions.defaultDuration
        });
        tempFiles.push(tempFile);
        tempFile = transitionFile;
        tempFiles.push(transitionFile);
      }

      // 6. 移动到最终输出
      if (tempFile !== video.path) {
        fs.renameSync(tempFile, outputPath);
      } else {
        // 如果没有任何处理，直接复制
        fs.copyFileSync(video.path, outputPath);
      }

      // 7. 生成缩略图
      console.log('  🖼️ 生成缩略图...');
      const thumbName = path.basename(video.name, video.ext) + '_thumb.jpg';
      const thumbPath = path.join(outputDir, thumbName);
      await this.editor.generateThumbnail(video.path, thumbPath).catch(() => {
        console.log('  ⚠️ 缩略图生成失败，跳过');
      });

      // 8. 清理临时文件
      if (!this.config.batch.keepTempFiles) {
        tempFiles.forEach(f => {
          if (fs.existsSync(f)) {
            fs.unlinkSync(f);
          }
        });
      }

      console.log(`  ✅ 完成: ${outputName}`);
      this.stats.processed++;
      return { success: true, output: outputPath };

    } catch (error) {
      console.error(`  ❌ 失败: ${error.message}`);
      this.stats.failed++;
      return { success: false, error: error.message };
    }
  }

  /**
   * 格式化时长
   */
  formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}分${secs}秒`;
  }

  /**
   * 主处理流程
   */
  async run() {
    console.log('');
    console.log('========================================');
    console.log('  AutoClip Pro - 视频批量处理');
    console.log('========================================');
    console.log('');

    // 扫描视频
    const videos = this.scanVideos();
    this.stats.total = videos.length;

    if (videos.length === 0) {
      console.log('❌ 没有找到视频文件');
      console.log(`   请将视频放入 ${path.resolve(__dirname, '..', this.config.inputDir)} 文件夹`);
      return;
    }

    console.log(`📹 找到 ${videos.length} 个视频文件`);
    console.log(`📁 模板: ${this.config.template}`);
    console.log(`📐 输出分辨率: ${this.config.video.resolution}`);
    console.log('');

    // 批量处理
    for (let i = 0; i < videos.length; i++) {
      await this.processVideo(videos[i], i, videos.length);
    }

    // 输出统计
    console.log('');
    console.log('========================================');
    console.log('  📊 处理完成');
    console.log('========================================');
    console.log(`  总计: ${this.stats.total} 个视频`);
    console.log(`  ✅ 成功: ${this.stats.processed} 个`);
    console.log(`  ⏭️ 跳过: ${this.stats.skipped} 个`);
    console.log(`  ❌ 失败: ${this.stats.failed} 个`);
    console.log('');

    if (this.stats.failed > 0) {
      process.exit(1);
    }
  }
}

// 运行批处理
const processor = new BatchProcessor();
processor.run().catch(err => {
  console.error('处理出错:', err);
  process.exit(1);
});