# offline-llama

Autonomously manage and use local Ollama models for continuous operation without internet dependency. Includes model health monitoring, automatic fallback, and self-healing capabilities.

## Overview

This skill enables autonomous operation with local Ollama models. It monitors model health, automatically switches between models when issues occur, and maintains functionality even without internet connectivity. The skill includes self-healing capabilities to restart services and clear resources when needed.

## Core Features

### Model Management
- **Health Monitoring**: Continuously check model availability and performance
- **Automatic Fallback**: Switch to alternative models when primary fails
- **Model Switching**: Dynamically select best available model for task

### Self-Healing
- **Service Restart**: Automatically restart Ollama when models become unavailable
- **Resource Management**: Clear cache and temporary files to free resources
- **Model Reinstallation**: Reinstall problematic models automatically

### Connectivity Awareness
- **Internet Detection**: Monitor internet connectivity status
- **Smart Fallback**: Switch to remote models when local models unavailable and internet is present
- **Offline Mode**: Maintain full functionality without internet

## Configuration

### Models
- **Primary**: llama-3.1-8b-instruct (general tasks)
- **Secondary**: mistral-7b-instruct (faster responses)
- **Specialized**: code-llama-7b (coding tasks)

### Health Checks
- **Model Status**: Monitor availability every 30 seconds
- **Latency Tracking**: Monitor response times every minute
- **Resource Usage**: Monitor GPU/CPU and memory every 5 minutes

### Fallback Strategies
1. **Model Switching**: Automatically switch to alternative local models
2. **Response Retry**: Retry failed requests with exponential backoff
3. **Degraded Mode**: Continue with limited functionality if all models unavailable

## Usage

### When Internet is Available
- Use local models primarily
- Fallback to remote models if local models unavailable
- Maintain optimal performance

### When Internet is Unavailable
- Use local models exclusively
- Continue all operations without interruption
- Provide degraded functionality if needed

## Commands

### Model Management
- `model_status` - Check current model health
- `switch_model` - Manually switch between models
- `restart_ollama` - Restart Ollama service

### Health Monitoring
- `check_health` - Run comprehensive health check
- `monitor_resources` - Monitor system resources
- `clear_cache` - Clear model cache and temporary files

## Self-Healing

### Automatic Actions
- **Service Restart**: Triggered when model becomes unavailable
- **Resource Cleanup**: Triggered when high memory usage detected
- **Model Reinstallation**: Triggered when persistent failures occur

### Manual Intervention
- **Manual Restart**: User can manually restart services
- **Cache Clearing**: User can manually clear resources
- **Model Updates**: User can update models as needed

## Security Considerations

- All operations performed locally
- No external dependencies required
- Secure model management
- Privacy-preserving by default

## Performance Optimization

- **Resource Monitoring**: Track GPU/CPU usage and memory
- **Latency Tracking**: Monitor response times and performance
- **Model Selection**: Choose optimal model based on task requirements

## Maintenance

### Regular Tasks
- **Health Checks**: Run periodic health checks
- **Cache Management**: Clear unused cache regularly
- **Model Updates**: Keep models updated when possible

### Troubleshooting
- **Log Analysis**: Monitor logs for issues
- **Performance Metrics**: Track performance over time
- **Error Handling**: Graceful error handling and recovery

## Integration

This skill integrates with:
- **Ollama**: Local model management
- **System Resources**: Monitor and manage system resources
- **Network**: Detect internet connectivity
- **OpenClaw**: Seamless integration with existing tools

## Future Enhancements

- **Model Training**: Support for custom model training
- **Advanced Routing**: Intelligent model selection based on task
- **Multi-GPU Support**: Scale across multiple GPUs
- **Cloud Sync**: Optional cloud backup and synchronization

## License

This skill is part of the OpenClaw ecosystem and follows the same licensing terms as OpenClaw itself.