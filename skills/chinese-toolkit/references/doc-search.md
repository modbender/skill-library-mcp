# 文档搜索和参考管理
## 技能开发中的文档管理和知识检索

## 🎯 文档管理策略

### 1. 文档分类体系
```
技能文档分类:
• 用户文档: 使用指南、API文档、示例
• 开发文档: 架构设计、代码注释、开发指南
• 参考文档: 技术参考、标准规范、最佳实践
• 管理文档: 发布流程、维护指南、变更日志
```

### 2. 文档存储结构
```
docs/
├── user/                    # 用户文档
│   ├── getting-started.md  # 快速开始
│   ├── api-reference.md    # API参考
│   ├── examples/           # 示例代码
│   └── faq.md             # 常见问题
├── developer/              # 开发文档
│   ├── architecture.md     # 架构设计
│   ├── contributing.md     # 贡献指南
│   └── testing.md         # 测试指南
├── reference/              # 参考文档
│   ├── standards.md       # 技术标准
│   ├── best-practices.md  # 最佳实践
│   └── glossary.md        # 术语表
└── admin/                  # 管理文档
    ├── release.md         # 发布流程
    ├── maintenance.md     # 维护指南
    └── changelog.md       # 变更日志
```

## 🔍 文档搜索技术

### 1. 本地文档搜索
#### 使用ripgrep进行代码搜索：
```bash
# 搜索特定函数
rg "def segment" --type py

# 搜索包含特定文本的文件
rg "中文分词" --type md

# 搜索并显示上下文
rg -C 3 "translation" --type py

# 搜索正则表达式
rg "def (segment|translate)" --type py
```

#### 使用fd进行文件搜索：
```bash
# 搜索特定扩展名文件
fd "\.md$" --type f

# 搜索包含特定名称的文件
fd "test" --type f

# 搜索并执行命令
fd "\.py$" --exec rg "import"
```

### 2. 结构化文档搜索
#### 创建文档索引：
```python
# document_index.py
import json
from pathlib import Path
from typing import Dict, List

class DocumentIndex:
    def __init__(self, docs_dir: str):
        self.docs_dir = Path(docs_dir)
        self.index = self._build_index()
    
    def _build_index(self) -> Dict:
        """构建文档索引"""
        index = {}
        for file_path in self.docs_dir.rglob("*.md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                index[str(file_path)] = {
                    'title': self._extract_title(content),
                    'summary': self._extract_summary(content),
                    'keywords': self._extract_keywords(content),
                    'size': len(content),
                    'modified': file_path.stat().st_mtime
                }
        return index
    
    def search(self, query: str) -> List[Dict]:
        """搜索文档"""
        results = []
        for path, metadata in self.index.items():
            if query.lower() in metadata['title'].lower():
                results.append({'path': path, 'score': 1.0, **metadata})
            elif query.lower() in ' '.join(metadata['keywords']).lower():
                results.append({'path': path, 'score': 0.8, **metadata})
        return sorted(results, key=lambda x: x['score'], reverse=True)
```

### 3. 语义搜索
#### 使用向量搜索：
```python
# semantic_search.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict

class SemanticSearch:
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
    
    def add_documents(self, documents: List[str]):
        """添加文档"""
        self.documents.extend(documents)
        self.embeddings = self.model.encode(self.documents)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """语义搜索"""
        query_embedding = self.model.encode([query])
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in indices:
            results.append({
                'document': self.documents[idx],
                'similarity': float(similarities[idx]),
                'index': idx
            })
        return results
```

## 📚 参考资源管理

### 1. 外部参考资源
#### 技术文档链接：
```markdown
## 中文处理相关
- [jieba中文分词](https://github.com/fxsjy/jieba)
- [pypinyin汉字转拼音](https://github.com/mozillazg/python-pinyin)
- [opencc简繁转换](https://github.com/BYVoid/OpenCC)

## OCR相关
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [pytesseract](https://github.com/madmaze/pytesseract)

## 翻译API
- [百度翻译API](https://api.fanyi.baidu.com/)
- [谷歌翻译API](https://cloud.google.com/translate)
- [腾讯云翻译](https://cloud.tencent.com/product/tmt)
```

#### 开发工具链接：
```markdown
## Python开发
- [Python官方文档](https://docs.python.org/3/)
- [PEP 8代码规范](https://www.python.org/dev/peps/pep-0008/)
- [Python类型提示](https://docs.python.org/3/library/typing.html)

## 测试工具
- [pytest文档](https://docs.pytest.org/)
- [unittest文档](https://docs.python.org/3/library/unittest.html)

## 性能优化
- [Python性能优化指南](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [内存分析工具](https://pypi.org/project/memory-profiler/)
```

### 2. 内部知识库
#### 创建知识库：
```python
# knowledge_base.py
import json
from datetime import datetime
from typing import Dict, List, Optional

class KnowledgeBase:
    def __init__(self, db_path: str = "knowledge_base.json"):
        self.db_path = db_path
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """加载知识库"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'articles': [], 'categories': [], 'tags': []}
    
    def add_article(self, title: str, content: str, 
                   categories: List[str] = None, 
                   tags: List[str] = None) -> str:
        """添加文章"""
        article_id = f"article_{len(self.knowledge['articles']) + 1}"
        article = {
            'id': article_id,
            'title': title,
            'content': content,
            'categories': categories or [],
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.knowledge['articles'].append(article)
        self._save_knowledge()
        return article_id
    
    def search(self, query: str, 
               category: Optional[str] = None,
               tag: Optional[str] = None) -> List[Dict]:
        """搜索文章"""
        results = []
        for article in self.knowledge['articles']:
            # 简单文本匹配
            if (query.lower() in article['title'].lower() or 
                query.lower() in article['content'].lower()):
                if (not category or category in article['categories']) and \
                   (not tag or tag in article['tags']):
                    results.append(article)
        return results
```

## 🔧 文档工具集成

### 1. 文档生成工具
#### 自动生成API文档：
```python
# api_doc_generator.py
import inspect
from typing import get_type_hints
import markdown

class APIDocGenerator:
    def __init__(self, module):
        self.module = module
        self.functions = self._extract_functions()
    
    def _extract_functions(self):
        """提取模块中的函数"""
        functions = []
        for name, obj in inspect.getmembers(self.module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                functions.append({
                    'name': name,
                    'doc': inspect.getdoc(obj),
                    'signature': str(inspect.signature(obj)),
                    'type_hints': get_type_hints(obj)
                })
        return functions
    
    def generate_markdown(self) -> str:
        """生成Markdown文档"""
        md = "# API 参考文档\n\n"
        
        for func in self.functions:
            md += f"## `{func['name']}`\n\n"
            md += f"```python\n{func['name']}{func['signature']}\n```\n\n"
            
            if func['doc']:
                md += f"{func['doc']}\n\n"
            
            if func['type_hints']:
                md += "**类型提示:**\n\n"
                for param, type_hint in func['type_hints'].items():
                    md += f"- `{param}`: `{type_hint}`\n"
                md += "\n"
        
        return md
```

### 2. 文档验证工具
#### 检查文档完整性：
```python
# doc_validator.py
import ast
from pathlib import Path
from typing import List, Dict

class DocValidator:
    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
    
    def validate_functions(self) -> List[Dict]:
        """验证函数文档"""
        issues = []
        
        for py_file in self.source_dir.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node):
                        issues.append({
                            'file': str(py_file),
                            'function': node.name,
                            'line': node.lineno,
                            'issue': '缺少文档字符串',
                            'severity': 'warning'
                        })
        
        return issues
    
    def validate_examples(self) -> List[Dict]:
        """验证示例代码"""
        issues = []
        examples_dir = self.source_dir / "examples"
        
        if examples_dir.exists():
            for example_file in examples_dir.glob("*.py"):
                try:
                    with open(example_file, 'r', encoding='utf-8') as f:
                        exec(f.read(), {})
                except Exception as e:
                    issues.append({
                        'file': str(example_file),
                        'issue': f'示例代码执行失败: {e}',
                        'severity': 'error'
                    })
        
        return issues
```

## 📊 文档质量指标

### 1. 文档质量评估
```
文档完整性指标:
• 函数文档覆盖率: > 90%
• 示例代码覆盖率: > 80%
• API文档完整性: > 95%
• 错误处理文档: > 85%

文档可读性指标:
• 平均句子长度: < 25字
• 专业术语解释: > 90%
• 代码示例数量: > 每功能1个
• 图表使用率: > 30%

文档实用性指标:
• 搜索命中率: > 80%
• 问题解决率: > 70%
• 用户满意度: > 4.0/5.0
• 文档更新频率: 每月至少1次
```

### 2. 文档维护计划
```
日常维护:
• 每日: 检查文档链接有效性
• 每周: 更新示例代码
• 每月: 全面审查和更新

定期更新:
• 每季度: 更新API文档
• 每半年: 重构文档结构
• 每年: 全面重审和优化

响应式更新:
• 新功能发布: 立即更新文档
• Bug修复: 同步更新文档
• 用户反馈: 及时响应和更新
```

## 🚀 最佳实践

### 1. 文档编写规范
```
标题规范:
• 使用清晰的层级结构
• 标题反映内容主题
• 避免使用模糊词汇

内容规范:
• 每段一个主要观点
• 使用列表和表格组织信息
• 提供具体的示例
• 解释专业术语

代码规范:
• 提供完整的可运行示例
• 注释解释关键代码
• 展示输入和输出
• 包含错误处理示例
```

### 2. 文档搜索优化
```
元数据优化:
• 添加描述性标题
• 使用相关关键词
• 创建清晰的摘要
• 添加分类和标签

内容优化:
• 使用标准术语
• 提供多种表达方式
• 创建交叉引用
• 建立术语表

结构优化:
• 清晰的目录结构
• 逻辑的内容组织
• 方便的导航链接
• 响应式设计
```

### 3. 文档协作流程
```
编写流程:
1. 确定文档需求
2. 创建文档大纲
3. 编写初稿内容
4. 添加示例代码
5. 进行自我审查

审查流程:
1. 技术准确性审查
2. 内容完整性审查
3. 语言表达审查
4. 格式规范审查
5. 用户体验测试

发布流程:
1. 最终版本确认
2. 格式转换和优化
3. 发布到目标平台
4. 通知相关人员
5. 收集用户反馈
```

---
**文档搜索和参考管理指南版本**: 1.0.0
**最后更新**: 2026-02-23
**适用对象**: 技能开发者、技术文档作者

**优秀文档，卓越体验！** 📚✨

**文档即产品，质量即生命！** 🏆📝