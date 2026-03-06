# s1cli 完整命令参考

## login — 登录

```bash
python3 -m s1cli login
python3 -m s1cli login -u <username> -p <password>
```

- 会话保存到 `~/.config/s1cli/session.toml`，有效期 7 天
- 到期后重新运行 `login` 即可

## logout — 登出

```bash
python3 -m s1cli logout
```

清除本地会话文件。

## list — 版块 & 帖子列表

```bash
# 列出所有版块（含版块 ID）
python3 -m s1cli list

# 列出指定版块的帖子（forum_id 为数字）
python3 -m s1cli list <forum_id>
python3 -m s1cli list <forum_id> -p <page>    # 指定页码，默认 1
python3 -m s1cli list <forum_id> --json       # JSON 格式输出
```

## thread — 查看帖子

```bash
python3 -m s1cli thread <thread_id>
python3 -m s1cli thread <thread_id> -p <page>   # 指定页码
```

- `thread_id` 可从帖子 URL 读取：`thread-2265956-1-1.html` → `2265956`
- `view` 命令是 `thread` 的旧别名，推荐用 `thread`

## post — 发新帖

```bash
python3 -m s1cli post -f <forum_name> -t "标题" -c "内容"
```

- `-f` 版块名（中文或英文均可，需与论坛版块名匹配）
- `-t` 帖子标题
- `-c` 帖子内容（支持 BBCode）

## reply — 回复帖子

```bash
python3 -m s1cli reply <thread_id> -c "回复内容"
```

## search — 搜索

```bash
python3 -m s1cli search "关键词"
python3 -m s1cli search "关键词" -f <forum_name>   # 限定版块
```

## checkin — 每日签到

```bash
python3 -m s1cli checkin
```

输出示例：
```
✓ 签到成功！获得 5 金币
```

已签到时会提示「今日已签到」。

## profile — 个人信息

```bash
python3 -m s1cli profile
```

显示用户名、等级、金币、积分等信息。

## config — 配置管理

```bash
python3 -m s1cli config show           # 查看当前配置
python3 -m s1cli config set key=value  # 修改配置项
```

可配置项（举例）：
- `theme=dark` / `theme=light`

## debug — 调试信息

```bash
python3 -m s1cli debug --ua    # 查看当前 User Agent
python3 -m s1cli debug -e      # 查看会话过期时间
```

## tui — 图形界面（TUI）

```bash
python3 -m s1cli tui
```

交互式终端 UI，适合浏览查看，无需记忆命令。

---

## 配置文件位置

| 文件 | 用途 |
|------|------|
| `~/.config/s1cli/config.toml` | 用户偏好（主题等） |
| `~/.config/s1cli/session.toml` | 登录会话（cookies，7天有效） |
| `~/.config/s1cli/cache/` | 缓存目录 |
