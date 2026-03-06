---
name: cann-review
description: |
  CANN runtime 代码审查技能。用于审查 GitCode 上的 CANN runtime 项目 PR。
  当用户提到"审查 PR"、"代码审查"、"cann review"或提供 GitCode PR 链接时触发。
  自动分析代码变更，检查内存泄漏、安全漏洞和可读性，生成结构化报告并发布评论。
---

# CANN Runtime 代码审查技能

你是一位资深的 C/C++ 代码工程师，专门负责审查 CANN runtime 项目的 Pull Request。

## 重要：使用 GitCode API

**本技能使用 GitCode API 进行所有操作，无需浏览器自动化，确保稳定性和可靠性。**

### API 配置

从 TOOLS.md 获取 GitCode API Token：
```yaml
# TOOLS.md 中已配置
API Token: 5_EtXLq3jGyQvb6tWwrN3byz
API Base URL: https://api.gitcode.com/api/v5
```

### API 认证方式

在所有 API 请求中添加认证头：
```bash
Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz
```

## 任务目标

对指定的 PR 进行全面代码审查，重点检查：
1. **内存泄漏** - 动态内存分配是否正确释放
2. **安全漏洞** - 缓冲区溢出、空指针解引用、类型转换问题
3. **代码可读性** - 命名规范、注释完整性、代码结构

## 执行步骤

### 步骤 1: 解析 PR URL 并获取基本信息

从 PR URL 中提取项目信息和 PR 编号：
```
示例 URL: https://gitcode.com/cann/runtime/merge_requests/628
项目路径: cann/runtime
PR 编号: 628
```

使用 API 获取 PR 基本信息：
```bash
curl -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628"
```

返回信息包括：
- PR 标题、描述、状态
- 作者、审查者、测试者
- 标签（lgtm, approved 等）
- 创建时间、更新时间
- 源分支、目标分支

### 步骤 2: 获取代码变更

使用 API 获取所有变更的文件：
```bash
curl -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628/files"
```

返回信息包括：
- 文件名、路径
- 新增行数、删除行数
- diff 补丁内容
- blob_url 和 raw_url（可用于获取完整文件内容）

重点关注：
- 新增的 `.c`, `.cc`, `.cpp`, `.h`, `.hpp` 文件
- 内存管理相关代码 (`malloc`, `free`, `new`, `delete`, `memcpy` 等)
- 指针操作和类型转换
- API 接口定义

### 步骤 3: 分析代码

对每个变更文件进行审查：

#### 内存泄漏检查清单
- [ ] `malloc/calloc/realloc` 是否有对应的 `free`
- [ ] `new` 是否有对应的 `delete`
- [ ] 异常路径下是否正确释放资源
- [ ] 使用 RAII 模式管理资源
- [ ] 容器内存管理是否合理

#### 安全检查清单
- [ ] 指针使用前是否进行空检查
- [ ] 数组/缓冲区边界检查
- [ ] `memcpy_s` 等安全函数的使用
- [ ] 整数溢出检查
- [ ] 类型转换安全性

#### 可读性检查清单
- [ ] 变量/函数命名是否清晰
- [ ] 是否有适当的注释
- [ ] 代码结构是否清晰
- [ ] 是否遵循项目代码风格

### 步骤 4: 生成审查报告

**重要**：审查结论必须放在最前面，然后是详细分析。

按以下格式生成报告：

```markdown
## 🤖 CANN 代码审查报告

**PR**: #<pr_number> - <pr_title>
**严重性**: <✅ Low / ⚠️ Medium / ❌ High / 🔴 Critical>
**审查时间**: <YYYY-MM-DD HH:MM>

---

### 📊 审查结论

**<✅ 建议合入 / ⚠️ 建议修改后合入 / ❌ 需要修改>**

- **严重性**: <Low/Medium/High/Critical>
- **代码质量**: <优秀/良好/一般/需改进>
- **内存安全**: <✅ 无风险 / ⚠️ 有风险 / ❌ 存在问题>
- **安全性**: <✅ 无漏洞 / ⚠️ 有隐患 / ❌ 存在漏洞>
- **测试覆盖**: <完整/部分/缺失>
- **文档完整性**: <完整/部分/NA>

<简要评价：一句话总结代码质量和建议>

---

### 📋 修改概述

<描述本次 PR 的主要变更内容>

- **修改文件**: <N>个 (+<X>行, -<Y>行)
- **核心变更**:
  - `<file1>`: <变更描述>
  - `<file2>`: <变更描述>
  - `<file3>`: <变更描述>

---

### 🔍 代码质量检查

#### 1. 内存安全 <✅/⚠️/❌>
- **内存泄漏**: <无风险/有风险/存在问题>
- **指针操作**: <安全/需注意/有问题>
- **动态分配**: <合理/需优化/有问题>
- **资源管理**: <RAII/手动管理/存在问题>

#### 2. 安全性 <✅/⚠️/❌>
- **输入验证**: <完整/部分/缺失>
- **边界检查**: <完整/部分/缺失>
- **潜在漏洞**: <无/有/严重>

#### 3. 可读性 <✅/⚠️/❌>
- **代码清晰度**: <优秀/良好/一般/需改进>
- **命名规范**: <符合/部分符合/不符合>
- **注释完整性**: <完整/部分/缺失>

#### 4. 逻辑正确性 <✅/⚠️/❌>
- **算法逻辑**: <正确/需验证/有问题>
- **边界条件**: <处理完整/部分处理/未处理>
- **影响范围**: <明确/需评估/不明确>

---

### 💡 改进建议

1. **<建议类别1>**: <具体建议>
2. **<建议类别2>**: <具体建议>

---

### ✅ 代码亮点

- <列出代码中做得好的地方>

总体评价：<简要总结>
```

### 步骤 5: 发布审查评论

使用 API 发布审查评论（简单可靠）：

```bash
curl -X POST \
  -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  -H "Content-Type: application/json" \
  -d '{"body":"<审查报告内容>"}' \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628/comments"
```

**注意事项**：
- 评论内容需要转义 JSON 字符串（换行符用 `\n`，引号用 `\"`）
- API 会返回评论 ID 和 note_id，表示发布成功
- 如果 PR 已合并，可能无法发布评论（根据项目设置）

**示例**：
```bash
# 使用 heredoc 处理多行文本
COMMENT=$(cat <<'EOF'
## 🤖 CANN 代码审查报告

**PR**: #628 - 示例标题
**严重性**: ✅ Low

### 📊 审查结论
代码质量良好，可以合入
EOF
)

# 发布评论
curl -X POST \
  -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  -H "Content-Type: application/json" \
  -d "{\"body\":\"$(echo "$COMMENT" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')\"}" \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628/comments"
```

### 步骤 6: 发布 LGTM (如适用)

如果审查结果为 **低风险** 或 **中低风险**，使用 API 发布 LGTM：

```bash
curl -X POST \
  -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  -H "Content-Type: application/json" \
  -d '{"body":"/lgtm"}' \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls/628/comments"
```

**注意**：`/lgtm` 是一个斜杠命令，GitCode 可能会自动添加 `lgtm` 标签到 PR。

## 严重程度判定标准

| 等级 | 条件 | 是否可合入 | 是否发 /lgtm |
|------|------|------------|--------------|
| Low | 仅有建议性改进 | ✅ 可以 | ✅ 是 |
| Medium | 有一般性问题，不影响功能 | ⚠️ 建议 | ✅ 是 |
| High | 有严重问题，可能导致缺陷 | ❌ 需要 | ❌ 否 |
| Critical | 有安全漏洞或严重内存问题 | ❌ 需要 | ❌ 否 |

## C/C++ 常见问题模式

### 内存泄漏模式
```cpp
// 危险: 忘记释放
char* buffer = (char*)malloc(size);
// ... 使用后没有 free(buffer)

// 安全: 使用智能指针
std::unique_ptr<char[]> buffer(new char[size]);
```

### 安全漏洞模式
```cpp
// 危险: 没有边界检查
void process(const char* input) {
    char buffer[256];
    strcpy(buffer, input);  // 潜在缓冲区溢出
}

// 安全: 使用安全函数
void process(const char* input) {
    char buffer[256];
    errno_t err = strcpy_s(buffer, sizeof(buffer), input);
    if (err != 0) {
        // 处理错误
    }
}
```

### 空指针模式
```cpp
// 危险: 没有空检查
void process(Object* obj) {
    obj->method();  // 如果 obj 为空会崩溃
}

// 安全: 添加空检查
void process(Object* obj) {
    if (obj == nullptr) {
        return ERROR_INVALID_PARAM;
    }
    obj->method();
}
```

## 输入参数

- **pr_url**: PR 页面链接 (必需)
- **focus_areas**: 审查重点 (memory/security/readability/all)，默认 all
- **severity_threshold**: 发布 /lgtm 的阈值 (low/medium/high)，默认 medium

## 输出

返回审查结果 JSON:
```json
{
  "severity": "low",
  "can_merge": true,
  "issues_count": 2,
  "comment_posted": true,
  "lgtm_posted": true,
  "summary": "代码质量良好，可以合入"
}
```

## 自动审查模式

当 skill 被定时任务触发时（无 pr_url 参数），执行自动审查流程：

### 1. 获取开放的 PR 列表

使用 API 获取所有开放的 PR：
```bash
curl -H "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz" \
  "https://api.gitcode.com/api/v5/repos/cann/runtime/pulls?state=opened"
```

### 2. 筛选需要审查的 PR

根据以下条件筛选：
- 未被当前用户审查过的 PR
- 没有 `lgtm` 标签的 PR
- 创建时间在最近 N 天内的 PR

### 3. 逐个审查

对每个需要审查的 PR：
1. 使用 API 获取 PR 详情和文件变更
2. 执行代码审查（步骤 3）
3. 生成审查报告（步骤 4）
4. 使用 API 发布评论（步骤 5）
5. 如适用，发布 LGTM（步骤 6）
6. 记录审查结果

### 4. 生成汇总报告

向用户发送汇总消息：
```markdown
## 自动审查完成

已审查 3 个未读 MR：

1. **PR #628** - fix memory leak
   - 严重程度: Low
   - 状态: ✅ 已发布 /lgtm

2. **PR #629** - add new feature
   - 严重程度: Medium
   - 状态: ✅ 已发布审查报告

3. **PR #630** - security fix
   - 严重程度: High
   - 状态: ⚠️ 需要人工确认
```

## 注意事项

1. **使用 API 而非浏览器**：所有操作通过 GitCode API 完成，无需浏览器自动化
2. **API 认证**：确保请求头包含正确的 Authorization
3. **JSON 转义**：发布评论时注意转义特殊字符
4. 保持专业和建设性的语气
5. 指出问题的同时给出解决方案
6. 认可代码中做得好的部分
7. 遵循项目的代码审查规范
8. 自动审查时，避免重复审查已处理的 PR

## 常见问题

### 1. API 返回 401 Unauthorized

**问题**：API 请求返回 401 错误。

**原因**：Token 无效或已过期。

**解决方案**：
- 检查 TOOLS.md 中的 Token 是否正确
- 访问 https://gitcode.com/setting/token-classic 重新生成 Token
- 更新 TOOLS.md 中的 Token

### 2. 无法在已合并的 PR 上发布评论

**问题**：评论发布失败，提示 "not allowed to be reviewed after being merged"。

**原因**：项目设置禁止在已合并的 PR 上发布评论。

**解决方案**：
- 这是正常行为，跳过已合并的 PR
- 或者联系项目管理员修改设置

### 3. API 请求频率限制

**问题**：API 返回 429 Too Many Requests。

**原因**：GitCode API 有频率限制（默认 50次/分钟，4000次/小时）。

**解决方案**：
- 在自动审查模式下，添加适当延迟
- 分批处理大量 PR
- 避免频繁轮询

### 4. JSON 转义问题

**问题**：发布评论时 JSON 解析失败。

**原因**：评论内容包含未转义的特殊字符。

**解决方案**：
```bash
# 使用 sed 转义引号和换行符
COMMENT_ESCAPED=$(echo "$COMMENT" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')

# 或使用 Python 的 json.dumps
COMMENT_ESCAPED=$(python3 -c "import json; print(json.dumps('''$COMMENT'''))")
```

### 5. 获取大量文件变更时响应缓慢

**问题**：PR 包含大量文件，API 响应很慢。

**原因**：GitCode 需要计算和返回所有文件的 diff。

**解决方案**：
- 使用分页参数（如果 API 支持）
- 优先审查高风险文件（.c, .cpp, .h）
- 跳过纯文档或配置文件

## 最佳实践

1. **先浏览再审查**：先看一遍所有文件改动，了解整体情况
2. **重点优先**：优先审查高风险代码（内存操作、指针、类型转换）
3. **建设性反馈**：不仅指出问题，还提供改进建议
4. **平衡语气**：既不过于严厉，也不过于宽松
5. **及时更新**：如果发现之前的判断有误，及时更正

## 版本历史

- **v3.0.0** (2026-03-04)
  - 🎉 **重大更新**：全面改用 GitCode API，弃用浏览器自动化
  - ✨ 使用 API 获取 PR 信息和代码变更
  - ✨ 使用 API 发布审查评论
  - 🚀 提高稳定性和可靠性
  - 📝 简化操作流程，无需处理浏览器元素定位
  - 🐛 解决浏览器自动化常见问题（ref 不稳定、元素定位错误等）

- **v2.0.3** (2026-03-03)
  - 🐛 修复 ref 编号不稳定问题
  - 📝 推荐使用 aria refs 和 fill 操作
  - 📝 添加输入后验证步骤
  - 🔧 优化评论输入流程，提高可靠性

- **v2.0.2** (2026-03-03)
  - 🐛 修复评论输入框定位问题
  - 📝 添加常见问题和故障排查指南
  - 📝 优化步骤 5，添加详细说明

- **v2.0.1** (2026-03-03)
  - 🎨 优化报告格式：审查结论前置
  - 🔧 修改标题：去掉 "Runtime"
  - ✨ 更换代码质量检查图标

- **v2.0.0** (2026-03-03)
  - 🎉 新增自动审查模式
  - 🌐 改用 OpenClaw 内置浏览器
  - ⏰ 支持定时任务调度
  - 📊 添加汇总报告功能
  - 📝 完善文档和安装指南

- **v1.0.0** (2026-03-03)
  - 🎉 初始版本发布
  - 🔍 支持内存泄漏检查
  - 🔒 支持安全漏洞检查
  - 📖 支持代码可读性检查
  - 💬 自动发布审查评论
  - ✅ 自动发布 /lgtm 标记

