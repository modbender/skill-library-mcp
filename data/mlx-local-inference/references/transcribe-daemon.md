# 自动转录守护进程

## 基本信息

| 项目 | 值 |
|------|-----|
| 功能 | 监听目录，自动转录音频并 LLM 校对 |
| 监听目录 | `~/transcribe/` |
| 输出目录 | `~/transcribe/done/` |
| 服务进程 | `transcribe-daemon.py` |
| launchd 服务 | `com.mlx-transcribe-daemon` |
| 脚本路径 | `~/.mlx-server/transcribe-daemon.py` |

## 使用方式

将音频文件放入 `~/transcribe/` 目录，守护进程会自动处理：

1. **Phase 1 - ASR 转录**：调用 Qwen3-ASR（端口 8788）将音频转为文字，生成 `文件名_raw.md`
2. **Phase 2 - LLM 校对**：卸载 ASR 模型释放内存，调用 Qwen3-14B（端口 8787）校对文本，生成 `文件名_corrected.md`
3. **归档**：将原始音频和结果移入 `~/transcribe/done/`

## 支持的音频格式

wav, mp3, m4a, flac, ogg, webm

## 处理参数

| 参数 | 值 |
|------|-----|
| 轮询间隔 | 15 秒 |
| 长音频切片 | 10 分钟/段 |
| LLM 校对分块 | 每块约 2000 字符 |
| LLM temperature | 0.3 |

## 依赖服务

- `com.mlx-audio-server`（端口 8788）— Qwen3-ASR 转录
- `com.mlx-server`（端口 8787）— Qwen3-14B 校对

两个服务都需要运行，守护进程才能完成全流程。

## 校对规则

- 修正同音字错误（的/得/地，在/再，他/她）
- 粤语内容保留粤语用字（嘅、唔、咁、喺、冇、佢、啲、嘢）
- 添加标点和分段
- 去除语气词和重复
- 修正领域专有名词

## 管理命令

```bash
# 启动
launchctl kickstart gui/$(id -u)/com.mlx-transcribe-daemon

# 停止
launchctl kill SIGTERM gui/$(id -u)/com.mlx-transcribe-daemon

# 查看日志
tail -f ~/.mlx-server/logs/transcribe-daemon.err.log
```

## 注意事项

- 为避免内存争用，ASR 和 LLM 不会同时加载，转录完所有文件后才开始校对
- 文件写入过程中不会被处理（通过文件大小稳定性检测）
- 处理中的文件会生成 `.processing` 标记，异常退出后重启会自动清理
