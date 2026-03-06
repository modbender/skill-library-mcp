
# Model Alias Append Skill

> Automatically appends model alias to responses with configuration change detection
 
![Model Alias Example](https://github.com/Ccapton/FileRepertory/blob/master/files/model_alias_snapshot.png?raw=true)

## Key Features
- 🔍 **Automatic Detection** - Identifies the model used for each response
- 🏷️ **Alias Appending** - Adds model alias from openclaw config **agents.defaults.models.{yourModelDict}.alias** format like the config below
```
"agents": {
  "defaults": {
    "model": {
      "primary": "gemma3:27b-local",
      "fallbacks": [ "qwen" ]
    },
    "models": {
      "ollama-local/gemma3:27b": {
        "alias": "gemma3:27b-local"
      },
      "qwen-portal/coder-model": {
        "alias": "qwen"
      }
    }
  }
}
```
- 🔄 **Real-time Monitoring** - Watches for configuration changes
- 📢 **Update Notifications** - Shows when config changes occur
- 🛡️ **Format Preservation** - Maintains reply tags and formatting

## Install
```
npx clawhub@latest install model-alias-append
```

## How It Works
1. Intercepts responses before sending
2. Determines which model generated the response  
3. Appends the appropriate model alias
4. Shows update notices when configuration changes

## Setup
> No additional configuration needed - reads from your existing openclaw.json

## Output Example
```
Your response content...

[Model alias configuration updated] // This line will not appear until openclaw.json modified

gemma3:27b-local
```
 