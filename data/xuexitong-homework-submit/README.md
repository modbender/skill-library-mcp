# xuexitong-homework-submit

学习通（超星）作业自动化 Skill。

**当前版本：v1.1.2**

## 能力
- 扫描作业入口、解析 doHomeWork URL
- 抓题并生成答案模板
- 暂存（save）与交卷（submit）
- 手写图答案流水线（渲染→上传→HTML 回填→暂存）

## 更新检查
脚本每次运行会到 GitHub 检查最新 `VERSION`，发现新版本时会提示使用：

```bash
clawhub update xuexitong-homework-submit
```

## 致谢
本项目感谢以下三个核心依赖/服务：
- **HandWrite**（手写渲染能力）
- **学习通 API**：`mooc1-api.chaoxing.com`
- **超星图床上传接口**：`notice.chaoxing.com/pc/files/uploadNoticeFile`

## 仓库
https://github.com/smallwhiteman/xuexitong-homework-submit-skill
