id: music-generation-kb
description: 定义音乐生成的API规范、Composition Plan结构和质量验证标准

model_capabilities:
  strengths:
    - 快速生成
    - 精确控制BPM和调性
    - 强大的Composition Plan支持
    - 多语言歌词支持
  limitations:
    - 不能提及版权艺术家/乐队名称
    - 不能使用版权歌词

duration_limits:
  minimum: 3000ms (3秒)
  maximum: 600000ms (10分钟)
  default: 模型根据Composition Plan自动计算

composition_plan_structure:
  description: Composition Plan是控制音乐生成的JSON结构
  
  schema:
    positive_global_styles:
      type: list of strings
      description: 整首歌要包含的风格和音乐方向
      example: ["electronic", "fast-paced", "driving synth arpeggios", "punchy drums"]
      
    negative_global_styles:
      type: list of strings
      description: 整首歌要排除的风格和音乐方向
      example: ["acoustic", "slow", "minimalist", "ambient", "lo-fi"]
      
    sections:
      type: list of section objects
      description: 歌曲的分段结构
      
  section_object:
    section_name:
      type: string
      description: 段落名称
      examples: ["Intro", "Verse 1", "Build-up", "Peak Drop", "Breakdown", "Climax", "Outro"]
      
    positive_local_styles:
      type: list of strings
      description: 该段落要包含的局部风格
      example: ["rising synth arpeggio", "glitch fx", "filtered noise sweep"]
      
    negative_local_styles:
      type: list of strings
      description: 该段落要排除的局部风格
      example: ["soft pads", "melodic vocals", "ambient textures"]
      
    duration_ms:
      type: integer
      description: 该段落时长（毫秒）
      example: 5000
      
    lines:
      type: list of strings
      description: 该段落的歌词行（纯器乐时为空数组）
      example: ["Verse 1 lyrics", "Second line of verse"]

composition_plan_example:
  positive_global_styles:
    - "electronic"
    - "fast-paced"
    - "driving synth arpeggios"
    - "high adrenaline"
  negative_global_styles:
    - "acoustic"
    - "slow"
    - "ambient"
  sections:
    - section_name: "Intro"
      positive_local_styles: ["rising synth arpeggio", "glitch fx", "building tension"]
      negative_local_styles: ["soft pads", "melodic vocals"]
      duration_ms: 3000
      lines: []
    - section_name: "Peak Drop"
      positive_local_styles: ["full punchy drums", "distorted bass", "aggressive rhythmic hits"]
      negative_local_styles: ["smooth transitions", "clean bass"]
      duration_ms: 4000
      lines: []
    - section_name: "Outro"
      positive_local_styles: ["glitch stutter", "energy burst", "quick transitions"]
      negative_local_styles: ["long reverb tails", "fadeout"]
      duration_ms: 3000
      lines: []

generation_parameters:
  duration:
    rule: 必须与视频时长精确匹配
    tolerance: ±0.5秒
    
  respect_sections_durations:
    type: boolean
    default: true
    description: 控制是否严格遵守Composition Plan中每个section的duration_ms
    values:
      true: 严格遵守每个段落的时长设定，确保音乐结构与视频结构精确对齐
      false: 允许模型根据音乐性调整段落时长，可能提高音乐质量但牺牲精确度
    recommendation: 视频配乐场景建议设为true，确保音画同步  
    
  format:
    production: WAV（无损，用于后期处理）
    delivery: MP3 高码率（最终交付）
    
  sample_rate:
    standard: 44100Hz
    high_quality: 48000Hz

copyright_restrictions:
  forbidden:
    - 提及乐队或音乐家名称
    - 使用版权歌词
    - 模仿特定受版权保护的歌曲
  error_handling:
    description: 如提示词或Composition Plan包含版权内容，API会返回错误及建议替代方案
    action: 使用建议的替代方案重新生成

quality_validation:
  duration_check:
    method: 比对音乐时长与目标时长
    pass_criteria: |音乐时长 - 目标时长| < 0.5秒
    fail_action: 重新生成
    
  style_consistency:
    check_points:
      - 情绪是否匹配positive_global_styles
      - 是否避免了negative_global_styles
      - 各段落是否符合局部风格要求
    fail_action: 调整Composition Plan重新生成
      
  audio_quality:
    check_points:
      - 无明显失真或削波
      - 无异常噪音
      - 动态范围正常
      - 段落过渡自然
    fail_action: 重新生成

regeneration_protocol:
  max_attempts: 3
  between_attempts:
    - 分析失败原因
    - 调整positive/negative styles
    - 调整段落时长分配
  escalation: 超过3次失败，报告并请求人工介入