/**
 * Video Editor Core Module
 * AutoClip Pro - 视频批量处理技能包
 * 
 * 提供视频编辑的核心功能
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class VideoEditor {
  constructor(config = {}) {
    this.config = {
      ffprobePath: 'ffprobe',
      ffmpegPath: 'ffmpeg',
      ...config
    };
  }

  /**
   * 获取视频信息
   * @param {string} videoPath - 视频文件路径
   * @returns {Object} 视频信息
   */
  async getVideoInfo(videoPath) {
    const cmd = `"${this.config.ffprobePath}" -v quiet -print_format json -show_format -show_streams "${videoPath}"`;
    try {
      const output = execSync(cmd, { encoding: 'utf8' });
      const info = JSON.parse(output);
      
      const videoStream = info.streams.find(s => s.codec_type === 'video');
      const audioStream = info.streams.find(s => s.codec_type === 'audio');
      
      return {
        duration: parseFloat(info.format.duration),
        size: parseInt(info.format.size),
        bitrate: parseInt(info.format.bit_rate),
        width: videoStream?.width,
        height: videoStream?.height,
        fps: this.parseFps(videoStream?.r_frame_rate),
        videoCodec: videoStream?.codec_name,
        audioCodec: audioStream?.codec_name,
        hasAudio: !!audioStream
      };
    } catch (error) {
      throw new Error(`无法读取视频信息: ${error.message}`);
    }
  }

  /**
   * 解析帧率
   */
  parseFps(fpsString) {
    if (!fpsString) return 30;
    const [num, den] = fpsString.split('/');
    return den ? parseInt(num) / parseInt(den) : parseInt(num);
  }

  /**
   * 裁剪视频
   * @param {string} input - 输入文件
   * @param {string} output - 输出文件
   * @param {Object} options - 裁剪选项
   */
  async trim(input, output, options = {}) {
    const { start = 0, end, duration } = options;
    const durationArg = duration ? `-t ${duration}` : '';
    const endArg = end ? `-to ${end}` : '';
    
    const cmd = `"${this.config.ffmpegPath}" -y -ss ${start} -i "${input}" ${durationArg} ${endArg} -c copy "${output}"`;
    
    return this.executeFfmpeg(cmd);
  }

  /**
   * 调整分辨率
   * @param {string} input - 输入文件
   * @param {string} output - 输出文件
   * @param {string} resolution - 目标分辨率 (720p, 1080p, 4k)
   */
  async resize(input, output, resolution = '1080p') {
    const resolutions = {
      '720p': '1280:720',
      '1080p': '1920:1080',
      '4k': '3840:2160'
    };
    
    const scale = resolutions[resolution] || resolutions['1080p'];
    const cmd = `"${this.config.ffmpegPath}" -y -i "${input}" -vf "scale=${scale}:force_original_aspect_ratio=decrease" -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 192k "${output}"`;
    
    return this.executeFfmpeg(cmd);
  }

  /**
   * 添加水印
   * @param {string} input - 输入文件
   * @param {string} output - 输出文件
   * @param {Object} options - 水印选项
   */
  async addWatermark(input, output, options = {}) {
    const {
      text = 'AutoClip Pro',
      position = 'bottom-right',
      fontSize = 20,
      fontColor = 'white',
      opacity = 0.5
    } = options;

    const positions = {
      'top-left': 'x=10:y=10',
      'top-right': 'x=w-tw-10:y=10',
      'bottom-left': 'x=10:y=h-th-10',
      'bottom-right': 'x=w-tw-10:y=h-th-10',
      'center': 'x=(w-tw)/2:y=(h-th)/2'
    };

    const pos = positions[position] || positions['bottom-right'];
    const filter = `drawtext=text='${text}':fontsize=${fontSize}:fontcolor=${fontColor}@${opacity}:${pos}`;

    const cmd = `"${this.config.ffmpegPath}" -y -i "${input}" -vf "${filter}" -c:v libx264 -preset medium -crf 23 -c:a copy "${output}"`;
    
    return this.executeFfmpeg(cmd);
  }

  /**
   * 添加字幕
   * @param {string} input - 输入文件
   * @param {string} output - 输出文件
   * @param {string} subtitleFile - 字幕文件路径
   */
  async addSubtitles(input, output, subtitleFile) {
    const cmd = `"${this.config.ffmpegPath}" -y -i "${input}" -vf "subtitles='${subtitleFile}'" -c:v libx264 -preset medium -crf 23 -c:a copy "${output}"`;
    
    return this.executeFfmpeg(cmd);
  }

  /**
   * 添加转场效果
   * @param {string} input - 输入文件
   * @param {string} output - 输出文件
   * @param {Object} options - 转场选项
   */
  async addTransition(input, output, options = {}) {
    const { type = 'fade', duration = 0.5 } = options;
    
    let filter;
    switch (type) {
      case 'fade':
        filter = `fade=t=in:st=0:d=${duration},fade=t=out:st=${duration}:d=${duration}`;
        break;
      case 'slide':
        filter = `slide=t=in:st=0:d=${duration}`;
        break;
      default:
        filter = `fade=t=in:st=0:d=${duration}`;
    }

    const cmd = `"${this.config.ffmpegPath}" -y -i "${input}" -vf "${filter}" -c:v libx264 -preset medium -crf 23 -c:a copy "${output}"`;
    
    return this.executeFfmpeg(cmd);
  }

  /**
   * 合并多个视频
   * @param {string[]} inputs - 输入文件列表
   * @param {string} output - 输出文件
   */
  async concatenate(inputs, output) {
    // 创建文件列表
    const listFile = path.join(path.dirname(output), 'concat_list.txt');
    const listContent = inputs.map(f => `file '${path.resolve(f)}'`).join('\n');
    fs.writeFileSync(listFile, listContent);

    const cmd = `"${this.config.ffmpegPath}" -y -f concat -safe 0 -i "${listFile}" -c copy "${output}"`;
    
    try {
      await this.executeFfmpeg(cmd);
    } finally {
      // 清理临时文件
      if (fs.existsSync(listFile)) {
        fs.unlinkSync(listFile);
      }
    }
  }

  /**
   * 提取音频
   * @param {string} input - 输入文件
   * @param {string} output - 输出文件
   */
  async extractAudio(input, output) {
    const cmd = `"${this.config.ffmpegPath}" -y -i "${input}" -vn -c:a aac -b:a 192k "${output}"`;
    
    return this.executeFfmpeg(cmd);
  }

  /**
   * 添加背景音乐
   * @param {string} videoInput - 视频输入
   * @param {string} audioInput - 音频输入
   * @param {string} output - 输出文件
   * @param {Object} options - 选项
   */
  async addBackgroundMusic(videoInput, audioInput, output, options = {}) {
    const { volume = 0.3, loop = true } = options;
    
    const loopArg = loop ? '-stream_loop -1' : '';
    const cmd = `"${this.config.ffmpegPath}" -y ${loopArg} -i "${audioInput}" -i "${videoInput}" -filter_complex "[0:a]volume=${volume}[bg];[1:a][bg]amix=inputs=2:duration=first[aout]" -map 1:v -map "[aout]" -c:v copy -c:a aac "${output}"`;
    
    return this.executeFfmpeg(cmd);
  }

  /**
   * 生成视频缩略图
   * @param {string} input - 输入文件
   * @param {string} output - 输出文件
   * @param {Object} options - 选项
   */
  async generateThumbnail(input, output, options = {}) {
    const { time = '00:00:01', width = 320 } = options;
    
    const cmd = `"${this.config.ffmpegPath}" -y -ss ${time} -i "${input}" -vframes 1 -vf "scale=${width}:-1" "${output}"`;
    
    return this.executeFfmpeg(cmd);
  }

  /**
   * 执行 FFmpeg 命令
   * @param {string} cmd - FFmpeg 命令
   * @returns {Promise}
   */
  executeFfmpeg(cmd) {
    return new Promise((resolve, reject) => {
      console.log(`执行: ${cmd}`);
      
      const process = spawn(cmd, [], {
        shell: true,
        stdio: ['ignore', 'pipe', 'pipe']
      });

      let stderr = '';

      process.stderr.on('data', (data) => {
        stderr += data.toString();
        // 显示进度
        if (data.includes('time=')) {
          const match = data.toString().match(/time=(\d+:\d+:\d+\.\d+)/);
          if (match) {
            process.stdout.write(`\r处理中: ${match[1]}`);
          }
        }
      });

      process.on('close', (code) => {
        console.log(''); // 换行
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`FFmpeg 错误 (code ${code}): ${stderr}`));
        }
      });

      process.on('error', (err) => {
        reject(new Error(`执行失败: ${err.message}`));
      });
    });
  }
}

module.exports = VideoEditor;