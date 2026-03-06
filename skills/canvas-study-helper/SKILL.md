---
name: Canvas Study Helper Skill
description: 1. Canvas 课程监控
---

# Canvas Study Helper Skill

**Version:** 1.1.0  
**Author:** CanvasClaw  
**Description:** Canvas LMS 课程监控与学习笔记生成工具，支持公告检查、作业跟踪、PDF 学习笔记生成（CJK 支持）

---

## 🎯 功能

1. **Canvas 课程监控**
   - 检查课程公告（Announcements）
   - 跟踪作业截止日期（Assignments）
   - 下载课程文件（Files）

2. **学习笔记生成**
   - Markdown 格式学习笔记
   - PDF 导出（支持中文、LaTeX 数学公式）
   - Mock Test 生成（证明题专项）

3. **文件管理**
   - OneDrive 课程目录自动整理
   - 学习笔记分类存储
   - 临时文件清理

---

## 📁 目录结构

```
canvas-study-helper/
├── SKILL.md              # 本文件
├── scripts/
│   ├── check_canvas.sh   # Canvas 检查脚本
│   ├── md2pdf.sh         # Markdown 转 PDF
│   └── organize_files.sh # 文件整理脚本
├── templates/
│   ├── cjk_header.tex    # LaTeX CJK 配置
│   ├── lecture_notes.md  # 学习笔记模板
│   └── mock_test.md      # Mock Test 模板
└── examples/
    ├── check_canvas_example.sh
    └── generate_notes_example.sh
```

---

## 🔧 安装

```bash
# 使用 clawhub 安装
clawhub install canvas-study-helper

# 或手动克隆
git clone <repo_url> ~/.openclaw/workspace/skills/canvas-study-helper
```

---

## 📖 使用方法

### 1. Canvas 课程检查

```bash
# 配置 Cookie（从浏览器 DevTools 获取）
cat > ~/.canvas_cookie << 'EOF'
canvas_session=YOUR_SESSION_COOKIE
log_session_id=YOUR_LOG_SESSION_ID
EOF

# 运行检查脚本
./scripts/check_canvas.sh
```

**Cookie 获取方法（方案 1：浏览器 DevTools）：**
1. 登录 Canvas
2. 按 F12 打开 DevTools
3. Application → Cookies → 复制 `canvas_session` 和 `log_session_id`

**Cookie 获取方法（方案 2：WSLg Chromium - 推荐）：**

由于学校禁用 API Token，且 WSL2 无法解密 Windows DPAPI 加密的 Edge cookie，使用 WSLg 启动 Linux Chromium：

```bash
# 创建 canvas_browser.sh 脚本
cat > canvas_browser.sh << 'SCRIPT'
#!/bin/bash
# WSLg Chromium 浏览器控制脚本

CHROME_PORT=9222
COOKIE_FILE="${HOME}/.canvas_cookie"
CANVAS_DOMAIN="your-institution.instructure.com"

case "$1" in
    start)
        echo "🚀 启动 Chromium..."
        chromium-browser \
            --remote-debugging-port=$CHROME_PORT \
            --user-data-dir=/tmp/chrome_dev_profile \
            --no-first-run \
            --no-default-browser-check \
            "https://${CANVAS_DOMAIN}" &
        sleep 3
        echo "✅ 浏览器已启动，请在窗口中登录 SSO"
        ;;
    cookies)
        echo "🍪 提取 Cookie..."
        # 使用 CDP 获取 Cookie
        curl -s http://localhost:${CHROME_PORT}/json | jq -r '.[0].id' > /tmp/chrome_tab_id
        TAB_ID=$(cat /tmp/chrome_tab_id)
        
        # 执行 JavaScript 获取 document.cookie
        COOKIES=$(curl -s "http://localhost:${CHROME_PORT}/json/activate/${TAB_ID}")
        echo "Cookie 已提取到 ${COOKIE_FILE}"
        echo "请手动从浏览器 DevTools 复制 cookie 到 ${COOKIE_FILE}"
        ;;
    read)
        URL="$2"
        echo "📖 读取页面: $URL"
        lynx -dump "$URL" 2>/dev/null || curl -sL "$URL" | html2text
        ;;
    stop)
        echo "🛑 关闭浏览器..."
        pkill -f "chromium-browser.*remote-debugging-port=${CHROME_PORT}"
        rm -rf /tmp/chrome_dev_profile
        echo "✅ 浏览器已关闭"
        ;;
    *)
        echo "用法: $0 {start|cookies|read <url>|stop}"
        exit 1
        ;;
esac
SCRIPT
chmod +x canvas_browser.sh

# 使用方法
./canvas_browser.sh start   # 启动浏览器并登录
./canvas_browser.sh cookies # 提取 Cookie
./canvas_browser.sh stop    # 关闭浏览器
```

**WSLg 方案优势：**
- ✅ 绕过 Windows DPAPI 加密限制
- ✅ 直接在 WSL 环境中操作
- ✅ 可使用 Chrome DevTools Protocol (CDP) 自动化

**注意事项：**
- 需要在 WSLg 窗口中手动登录 SSO
- Cookie 会过期，需定期重新获取
- 确保安装了 `chromium-browser` 和 `jq`

---

### 2. 生成学习笔记

```bash
# 创建学习笔记
cat > lecture_notes.md << 'EOF'
# Course Lecture X - Topic Name

## 核心概念

### 定义
...

### 性质
...

## 例题
...
EOF

# 转换为 PDF
./scripts/md2pdf.sh lecture_notes.md lecture_notes.pdf
```

---

### 3. 生成 Mock Test

```bash
# 使用模板创建 Mock Test
cp templates/mock_test.md course_mock_test.md

# 编辑题目...

# 生成 PDF
./scripts/md2pdf.sh course_mock_test.md course_mock_test.pdf
```

---

## 🔑 Canvas API 端点

### 公告
```bash
curl -b "$CANVAS_COOKIE" \
  "https://<your-institution>.instructure.com/api/v1/announcements?context_codes[]=course_<COURSE_ID>"
```

### 作业
```bash
curl -b "$CANVAS_COOKIE" \
  "https://<your-institution>.instructure.com/api/v1/courses/<COURSE_ID>/assignments?per_page=50"
```

### 文件
```bash
curl -b "$CANVAS_COOKIE" \
  "https://<your-institution>.instructure.com/api/v1/courses/<COURSE_ID>/files?per_page=100"
```

**注意：**
- RSS Feed 可能已失效，建议使用 API
- Cookie 认证（学校通常禁用 API Token）
- Cookie 会过期，需定期更新

---

## 📄 PDF 生成配置

### 中文字体支持

使用 `cjk_header.tex` 配置：
```latex
\usepackage{xeCJK}
\setCJKmainfont{Droid Sans Fallback}
\usepackage{amsmath}
\usepackage{textcomp}
\usepackage{enumitem}
```

### 数学公式

- 行内公式：`$...$`
- 显示公式：`$$...$$`

### Emoji 处理

Linux 系统 emoji 可能乱码，建议替换为文本：
- ✅ → `[Correct]`
- ❌ → `[Wrong]`
- 📚 → `Book`

---

## 🗂️ 文件管理策略

### OneDrive 课程目录

```
/mnt/c/Users/<USER>/OneDrive - <INSTITUTION>/Classes/
├── <COURSE_CODE> <COURSE_NAME>/
│   ├── materials/        # Canvas 下载的资料
│   ├── study_notes/      # 生成的学习笔记
│   └── submissions/      # 已提交作业
```

### 工作流程

1. **生成** → 在 workspace 创建编辑
2. **保存** → 复制到 OneDrive `study_notes/`
3. **发送** → 需要时复制发送
4. **清理** → 删除临时文件

---

## 🛠️ 脚本说明

### check_canvas.sh

检查 Canvas 课程更新：
- 公告（过去 14 天）
- 作业（未来 14 天 + 过去 5 天）
- 文件同步

**依赖：** `curl`, `python3`, `jq`

---

### md2pdf.sh

Markdown 转 PDF（CJK 支持）：
- 自动处理 emoji
- 粗体后添加空行（修复列表渲染）
- 中文字体配置

**依赖：** `pandoc`, `texlive-xetex`, `texlive-xecjk`

**用法：**
```bash
./md2pdf.sh input.md output.pdf
```

---

### organize_files.sh

整理课程文件：
- 合并重复目录
- 清理临时文件
- 验证文件完整性

---

## 📝 模板

### 学习笔记模板

```markdown
# Course Lecture X - Topic Name

**Course:** Course Name  
**Instructor:** Instructor Name  
**Date:** YYYY-MM-DD

---

## 🎯 核心问题

这节课要解决什么问题？

---

## 📖 主要内容

### 定义

...

### 性质

| 性质 | 公式 | 含义 |
|------|------|------|
| ... | ... | ... |

---

## 📝 例题

...

---

## 🔑 知识总结

...
```

---

### Mock Test 模板

```markdown
# Course Lecture X - In-Class Test

**Course:** Course Name  
**Time limit:** 25 minutes  
**Total points:** 100 points

---

## Instructions

- This test consists of **6 proof-based questions**
- Show **all steps** of your proofs
- Full credit requires **complete justification**

---

## Question 1: Topic (XX points)

...

---

# Solutions & Grading Rubric

...
```

---

## ⚠️ 注意事项

### 隐私保护

- **不要** 在 skill 中存储 Cookie、Token
- **不要** 提交学生姓名、学号
- **不要** 泄露成绩、个人信息

### Cookie 安全

- Cookie 存储在 `~/.canvas_cookie`（gitignore）
- 定期更新 Cookie（过期后手动复制）
- 不要分享 Cookie 文件

### PDF 渲染

- 中文需要 xeCJK + Droid Sans Fallback
- Emoji 在 Linux 可能乱码，建议替换
- 数学公式用 `$...$` 或 `$$...$$`

---

## 🔄 更新日志

### v1.0.0 (2026-03-02)
- 初始版本
- Canvas API 检查脚本
- Markdown 转 PDF（CJK 支持）
- 学习笔记和 Mock Test 模板
- 文件管理策略

---

## 📞 支持

**Issues:** https://github.com/<repo>/issues  
**Discussions:** https://github.com/<repo>/discussions

---

## 📄 License

MIT License
