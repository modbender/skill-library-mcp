# 📺 B站UP主更新查看器

查看B站UP主的最新视频和动态，支持按用户名搜索、检查今日更新，自动缓存查询过的UP主信息。

## 功能

- 按用户名搜索UP主（自动缓存到本地）
- 查看UP主最新视频列表
- 查看UP主最新动态
- 检查UP主今天是否更新了视频

## 前置条件

- Python 3.9+
- B站 Cookies（用于访问 API）

## 安装

```bash
pip install -r requirements.txt
```

## 配置

需要设置 `BILIBILI_COOKIES` 环境变量。获取方法：

1. 登录 [bilibili.com](https://www.bilibili.com)
2. 按 `F12` → `Network` 选项卡 → 刷新页面
3. 点击任意请求 → Request Headers → 复制 Cookie 字段

```bash
export BILIBILI_COOKIES="你的B站cookies"
```

## 使用示例

```bash
# 按用户名搜索UP主
python3 update_viewer.py --search "影视飓风"

# 查看UP主最新视频（通过 mid）
python3 update_viewer.py --mid 946974 --videos

# 查看UP主最新动态
python3 update_viewer.py --mid 946974 --dynamics

# 同时查看视频和动态，指定数量
python3 update_viewer.py --mid 946974 --videos --dynamics --count 5

# 从缓存中快速查找UP主的 mid
python3 get_mid.py "影视飓风"
```

## 命令行参数

### update_viewer.py

| 参数 | 说明 | 必需 |
|------|------|------|
| `--mid` | UP主的 mid（用户ID） | 与 `--search` 二选一 |
| `--search`, `-s` | 按用户名搜索UP主 | 与 `--mid` 二选一 |
| `--videos`, `-v` | 显示最新视频 | 否 |
| `--dynamics`, `-d` | 显示最新动态 | 否 |
| `--count`, `-n` | 显示数量（默认 3） | 否 |

### get_mid.py

从本地缓存 (`user_cache.json`) 中查找UP主的 mid，避免重复搜索。

```bash
python3 get_mid.py "用户名"
# 输出 mid 数字，未找到则输出 NOT_FOUND
```

## 文件结构

```
bilibili-update-viewer/
├── SKILL.md              # OpenClaw Skill 定义
├── README.md             # 本文件
├── requirements.txt      # Python 依赖
├── bilibili_api.py       # B站 API 封装（WBI 签名、视频/动态/搜索接口）
├── update_viewer.py      # 主工具（查看视频、动态、搜索用户）
├── get_mid.py            # 从本地缓存查找 mid
└── user_cache.json       # 搜索结果缓存（自动生成）
```

## 注意事项

- Cookie 有效期有限，失效后需重新获取
- B站 API 有频率限制，请求间隔建议 1 秒以上
- 动态 API 可能会因 B站更新而变化

## 安全说明

- 所有凭据仅存储在用户本地，不会上传
- 网络请求均使用 HTTPS
- Cookies 通过环境变量传递，不写入代码或配置文件

## License

MIT

## 致谢

本项目基于 [bilibili-hot-monitor](https://clawhub.ai/Jacobzwj/bilibili-hot-monitor) 的 B站 API 封装进行开发，感谢原作者的贡献。
