# NSFW Detector Pro

## Metadata
- **ID**: nsfw-detector-pro
- **Version**: 1.0.0
- **Category**: content-filtering
- **Priority**: Critical
- **Installation**: ClawHub
- **Package**: `@raghulpasupathi/nsfw-detector-pro`

## Description
Advanced NSFW (Not Safe For Work) content detection system using computer vision, deep learning models, and multi-modal analysis. Detects explicit content in images, videos, and text with high accuracy and configurable sensitivity levels.

## Installation

### Via ClawHub
```
https://clawhub.ai/raghulpasupathi/nsfw-detector-pro
```

### Via npm
```bash
npm install @raghulpasupathi/nsfw-detector-pro
```

## Features
- **Image Analysis**: Detect nudity, sexual content, and explicit imagery
- **Video Analysis**: Frame-by-frame and scene-level detection
- **Text Analysis**: Identify sexual language and explicit descriptions
- **Multi-class Detection**: Pornography, erotica, suggestive, safe categories
- **Confidence Scoring**: 0-100% confidence for each classification
- **Custom Thresholds**: Adjustable sensitivity per use case
- **Skin Tone Detection**: Identify exposed skin regions accurately
- **Context Awareness**: Distinguish artistic from explicit content
- **Real-time Processing**: Fast inference for live content
- **Batch Processing**: Efficient analysis of multiple items
- **Age Estimation**: Detect potential underage content (refer to CSAM Shield)
- **Model Ensemble**: Combines multiple models for better accuracy

## Configuration
```json
{
  "enabled": true,
  "settings": {
    "defaultSensitivity": "moderate",
    "sensitivities": {
      "strict": {
        "pornography": 0.15,
        "erotica": 0.25,
        "suggestive": 0.40,
        "blockThreshold": 0.15
      },
      "moderate": {
        "pornography": 0.40,
        "erotica": 0.60,
        "suggestive": 0.75,
        "blockThreshold": 0.40
      },
      "relaxed": {
        "pornography": 0.70,
        "erotica": 0.85,
        "suggestive": 0.90,
        "blockThreshold": 0.70
      }
    },
    "models": {
      "image": {
        "enabled": true,
        "model": "nsfw-resnet-50",
        "useGPU": true
      },
      "video": {
        "enabled": true,
        "fps": 2,
        "maxFrames": 30
      },
      "text": {
        "enabled": true,
        "model": "bert-nsfw-classifier"
      }
    },
    "processing": {
      "imageMaxSize": "4096x4096",
      "videoMaxDuration": 300,
      "batchSize": 32,
      "cacheResults": true,
      "cacheTTL": 86400
    },
    "advanced": {
      "skinDetection": true,
      "faceDetection": true,
      "contextAnalysis": true,
      "artFilter": true,
      "medicalFilter": true
    }
  }
}
```

## API Examples

See [nsfw-detector-pro-examples.js](./examples/nsfw-detector-pro-examples.js) for complete usage examples.

## Dependencies
- **@tensorflow/tfjs-node-gpu**: ^4.0.0 - TensorFlow for GPU inference
- **sharp**: ^0.32.0 - Image processing
- **opencv4nodejs**: ^6.0.0 - Computer vision operations
- **ffmpeg-fluent**: ^2.1.0 - Video processing
- **nsfw.js**: ^3.0.0 - Pre-trained NSFW model

## Performance
- **Image Analysis**: 50-800ms depending on image size
- **Video Analysis**: 3-6s for 30s video at 2fps
- **Text Analysis**: 20-200ms depending on text length
- **Accuracy**: 96% for pornography detection
- **False Positive Rate**: 2-4%
- **False Negative Rate**: 1-3%

## Use Cases
- Social media content moderation
- Dating app photo verification
- User-generated content platforms
- Comment section filtering
- Profile picture screening
- Video streaming platforms
- E-commerce listings
- Community forums
- Educational platforms
- Corporate content filters

## Best Practices
1. Use appropriate sensitivity level for your use case
2. Enable caching to reduce repeated analysis costs
3. Use GPU acceleration for production workloads
4. Implement appeal process for false positives
5. Log all violations for audit trail
6. Provide clear feedback to users on violations
7. Enable art/medical filters if applicable
8. Use batch processing for efficiency
9. Monitor false positive/negative rates
10. Regular model updates for improved accuracy
11. Implement graceful degradation if service unavailable
12. Consider user reputation/history in moderation decisions
