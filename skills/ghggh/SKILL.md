---
name: github-repo-stats
description: Query a GitHub repository's star count and lines of code. Use when the user asks for repo stars, stargazers, LOC, code lines, or repository statistics for a given GitHub repo.
---

# GitHub 仓库统计查询

在用户需要查询**某个 GitHub 仓库的 star 数量**和**代码行数**时，按下列方式执行。

## 1. Star 数量

使用 GitHub REST API（无需 token 即可查询公开仓库）：

- **接口**: `GET https://api.github.com/repos/{owner}/{repo}`
- **字段**: 响应 JSON 中的 `stargazers_count` 即为 star 数。

示例（将 `owner/repo` 换成实际仓库，如 `vllm-project/vllm`）：

```bash
curl -s "https://api.github.com/repos/owner/repo" | jq '.stargazers_count'
```

或在代码中请求同一 URL，解析 JSON 取 `stargazers_count`。若请求受限可设置 `User-Agent` 头（如 `User-Agent: curl`）。

## 2. 代码行数

GitHub API 不直接提供“总代码行数”，常用做法是**克隆仓库后本地统计**。

### 方式 A：使用 cloc（推荐）

```bash
git clone --depth 1 https://github.com/owner/repo.git /tmp/repo-stat && cloc /tmp/repo-stat --json
```

安装：`sudo apt install cloc` 或 `pip install cloc`（若有）。从输出 JSON 中取 `SUM` 的 `code` 作为代码行数，并清理临时目录。


## 3. 输出格式

回复用户时建议包含：

- **仓库**: `owner/repo`
- **Stars**: 数字
- **代码行数**: 数字（并注明统计方式，如 cloc/tokei/近似）

若克隆或统计失败，说明原因并给出可替代方式（例如仅提供 star 数，或提供仓库语言占比链接）。
