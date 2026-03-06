---
name: todo-manager
description: "管理待办事项。添加、查看、完成、删除待办。"
argument-hint: "[add|list|done|rm] <内容>"
---

# Todo Manager - 待办事项管理

## 功能

### 添加待办
```
/todo add <事项>
/todo + <事项>
```

### 查看待办
```
/todo list
/todo ls
```

### 完成待办
```
/todo done <编号>
/todo <编号> done
```

### 删除待办
```
/todo rm <编号>
```

## 存储

待办文件：`~/.openclaw/workspace/todos.md`

格式：
```markdown
# 待办事项

- [ ] 任务1
- [x] 任务2
- [ ] 任务3

## 已完成
- 任务2 (2026-02-24)
```

## 使用示例

用户："/todo add 健身训练"
→ 添加待办：健身训练

用户："/todo list"
→ 显示所有待办

用户："/todo done 1"
→ 标记第一个待办为完成

---
*Todo Manager Skill*
