---
name: today-in-history
description: 获取历史上的今天的重要事件，数据从Wikipedia获取。当用户询问"历史上的今天"、"今天发生了什么"、某月某日的历史事件时触发。
---

# Today in History

获取当前日期的历史事件，数据从Wikipedia获取。

## 使用方式

用户询问历史上的今天或特定日期的历史事件时使用此skill。

## 数据获取

### Wikipedia API

使用Wikipedia API获取历史上的今天：

```bash
curl -s "https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/MM/DD"
```

例如获取2月19日：
```bash
curl -s "https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/02/19"
```

返回JSON格式，包含该日期的所有历史事件，按年份排序。

### 中文维基（备选）
```bash
curl -s "https://zh.wikipedia.org/api/rest_v1/feed/onthisday/events/02/19"
```

## 筛选重要事件

筛选标准：
1. 改变历史进程的重大事件（战争、发明、领袖逝世等）
2. 知名度高、影响深远
3. 有中国相关事件则一定加入

优先选择：
- 中国相关事件
- 重大国际事件
- 知名人物

## 输出格式

```
---

📜 历史上的今天
YYYY年2月19日 事件描述1
YYYY年2月19日 事件描述2
YYYY年2月19日 事件描述3

---
```

示例：

```
---

📜 历史上的今天
197年2月19日 卢格杜努姆战役：塞普提米乌斯·塞维鲁击败克劳狄乌斯·阿尔比努斯，奠定罗马帝国统治
1807年2月19日 美国前副总统阿龙·伯尔因叛国罪被捕
1945年2月19日 硫磺岛战役开始

---
```

注意：
- 每年的事件都带当前日期
- 事件描述简洁，一句话概括
- 中文描述
- 分割线“---”用“======”代替
- 只输出要求输出的内容，前后不要输出多余的文本、说明、报错