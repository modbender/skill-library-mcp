# {{PROJECT_NAME}} — 启动说明

## 网页地址

{{SERVICE_URL}}

## 启动服务

```bash
{{START_COMMAND}}
```

## 关闭服务

```bash
{{STOP_COMMAND}}
```

## 快速重启

```bash
{{RESTART_COMMAND}}
```

## 查看服务状态

```bash
{{STATUS_COMMAND}}
```

## 项目文件说明

| 文件 | 说明 |
|------|------|
| `{{ENTRY_FILE}}` | {{ENTRY_DESC}} |
<!-- 按实际文件逐行添加 -->

---

<!-- 
使用说明：
1. 替换所有 {{占位符}} 为实际内容
2. 文件清单表应列出所有关键源文件（不含 node_modules / dist / .git 等）
3. 每个文件一行，说明控制在一句话以内
4. 如项目有多个启动方式（开发/生产），分别列出

按项目类型的启动命令参考：

### Node.js 项目
```bash
cd /path/to/project
nohup node server.js > log/server.log 2>&1 &
echo "服务已启动，PID: $!"
```

### Python 项目
```bash
cd /path/to/project
python app.py
# 或
uvicorn main:app --reload --port 8000
```

### 纯前端项目
```bash
# 直接双击 index.html 即可运行
open index.html
```

### Docker 项目
```bash
docker-compose up -d
```
-->
