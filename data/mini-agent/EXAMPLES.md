# Mini-Agent 使用示例

本文件提供丰富的使用示例，帮助你快速掌握 Mini-Agent 的各种用法。

## 文件操作示例

### 读取文件

**简单读取**
```
读取当前目录下的 README.md 文件
```

**分块读取大文件**
```
读取 /path/to/large_file.txt，从第 100 行开始，读取 50 行
```

**读取多个文件**
```
读取 config.yaml 和 package.json 这两个配置文件
```

### 写入文件

**创建新文件**
```
在当前目录下创建一个新文件 test.py，内容如下：
#!/usr/bin/env python3
print("Hello World")
```

**覆盖文件**
```
将 /home/pi/notes.txt 的内容完全替换为新的内容
```

### 编辑文件

**精确替换**
```
修改 index.html 文件，将 <title> 标签的内容从 "Old Title" 改为 "New Title"
```

**修改代码**
```
在 utils.js 文件的 add 函数末尾添加错误处理逻辑
```

## 代码开发示例

### 编写新代码

**Python 示例**
```
写一个 Python 函数，接受一个字符串列表，返回最长的字符串
```

**JavaScript 示例**
```
用 Node.js 写一个 HTTP 服务器，监听 3000 端口，返回 JSON 数据
```

**Shell 脚本**
```
写一个 Shell 脚本，备份 /home 目录到 /backup
```

### 代码修改

**修复 Bug**
```
修复 /home/pi/project/main.py 中的空指针错误，错误信息是 "TypeError: 'NoneType' object is not subscriptable"
```

**重构代码**
```
将 /home/pi/utils.js 中的所有 var 声明改为 const 或 let
```

**添加功能**
```
在 /home/pi/app.py 的 User 类中添加一个 to_dict 方法
```

### 代码审查

**检查代码问题**
```
审查 /home/pi/project/src/app.ts 文件，指出潜在的性能问题
```

**代码优化**
```
优化 /home/pi/algorithm.py 中的排序算法，提高执行效率
```

## 系统操作示例

### 文件管理

**列出文件**
```
列出 /home/pi 目录下所有的 .md 文件
```

**搜索文件**
```
在 /home/pi/project 目录下查找所有包含 "TODO" 的文件
```

**创建目录**
```
在 /home/pi/projects 目录下创建 my-project/src/components 子目录
```

### 进程管理

**启动服务**
```
在后台启动一个 Flask 服务器，端口 5000
```

**查看进程**
```
查看当前运行的所有 Node.js 进程
```

**停止进程**
```
停止端口 8080 上运行的服务
```

### Git 操作

```
初始化一个新的 Git 仓库
```

```
查看 /home/pi/project 的 Git 提交历史
```

```
创建并切换到新分支 feature/add-login
```

## 数据处理示例

### 文本处理

**批量重命名**
```
将 /home/pi/images 目录下所有 .jpeg 文件改为 .jpg
```

**文本替换**
```
将 /home/pi/docs 目录下所有文件中的 "旧公司名" 替换为 "新公司名"
```

### 数据转换

**CSV 处理**
```
读取 /home/pi/data.csv，统计每列的总和
```

**JSON 处理**
```
将 /home/pi/data.xml 转换为 JSON 格式
```

## 复杂任务示例

### 项目搭建

**完整项目创建**
```
1. 创建项目目录 /home/pi/myapp
2. 初始化 package.json
3. 创建 src/index.js 入口文件
4. 创建 README.md 说明文档
```

### 批量修改

**批量修改文件**
```
将 /home/pi/configs 目录下所有 .conf 文件中的端口从 8080 改为 9090
```

### 调试问题

**分析错误日志**
```
分析 /var/log/app.log 文件，找出最近 100 条错误记录
```

**定位问题**
```
用户报告登录功能报错，请帮我检查 /home/pi/webapp 的登录相关代码
```

## 最佳实践

### 1. 清晰描述需求

✅ 推荐：
```
"在 /home/pi/project/app.py 中找到 process_data 函数，添加输入参数验证，如果 data 为空则抛出 ValueError 异常"
```

❌ 不推荐：
```
"帮我改一下那个有问题的代码"
```

### 2. 逐步完成任务

✅ 推荐：
```
第一步：创建项目目录结构
第二步：添加配置文件
第三步：编写主程序
```

❌ 不推荐：
```
"帮我创建一个完整的电商系统"
```

### 3. 包含约束条件

✅ 推荐：
```
"用 Python 3 编写，不使用第三方库，保持 PEP 8 编码规范"
```

❌ 不推荐：
```
"写个排序算法"
```

### 4. 检查执行结果

完成每个步骤后，Mini-Agent 会报告结果。仔细检查输出，确保符合预期。

## 常见场景

### 场景 1: 快速查看文件内容

```
"显示 /home/pi/config.yaml 的前 20 行"
```

### 场景 2: 修改配置文件

```
"将 config.yaml 中的 debug 模式从 true 改为 false"
```

### 场景 3: 运行测试

```
"在 /home/pi/project 目录运行 pytest 测试"
```

### 场景 4: 代码片段生成

```
"写一个 Python 装饰器，用于测量函数执行时间"
```

### 场景 5: 文件搜索

```
"在当前目录递归搜索包含 'class User' 的所有 Python 文件"
```
