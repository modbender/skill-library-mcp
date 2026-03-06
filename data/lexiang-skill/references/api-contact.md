# 通讯录管理 API

## 一、成员管理

### 创建成员
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/create" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "staff_id": "zhangsan",
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "department": [1, 2],
    "position": "产品经理"
  }'
```
**参数：**
| 参数 | 必须 | 说明 |
|------|------|------|
| staff_id | 是 | 员工账号，企业内唯一 |
| name | 是 | 成员名称 |
| phone | 是 | 手机号码，企业内唯一 |
| email | 否 | 邮箱 |
| department | 否 | 部门ID列表 |
| is_leader_in_dept | 否 | 是否为部门领导（数组，对应 department） |
| direct_leader | 否 | 直属上级（staff_id 数组） |
| main_depart | 否 | 主部门ID |
| position | 否 | 职务 |
| extra_attr | 否 | 自定义字段 |

> **频率限制**：3000次/分钟

### 更新成员
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/update" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"staff_id": "zhangsan", "name": "张三丰"}'
```
> **注意**：成员激活后，phone 和 email 不可通过接口变更

### 删除成员（离职）
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/resign" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"staff_id": "zhangsan"}'
```
> 删除后无法再使用乐享或接收消息，如需恢复可调用"重新入职"接口

### 重新入职
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/entry" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"staff_id": "zhangsan", "department": [1]}'
```

### 禁用成员（批量）
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/forbidden" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"staffs": ["staff1", "staff2"]}'
```
> 禁用后无法使用乐享或接收消息，但其他成员仍可见其数据。最多100个

### 重新启用
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/active" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"staffs": ["staff1", "staff2"]}'
```

### 添加管理员
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/add-manager" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"staff_id": "zhangsan"}'
```

### 获取成员信息
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/get?staff_id=zhangsan" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 获取部门下成员
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/list?department_id=1&page=1&per_page=100&fetch_child=1" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```
| 参数 | 必须 | 说明 |
|------|------|------|
| department_id | 是 | 部门ID |
| page | 否 | 页码，默认1 |
| per_page | 否 | 每页数量，最大1000 |
| fetch_child | 否 | 1:包含子部门成员, 0:不包含 |

### 获取管理员列表
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/managers" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 获取自定义字段
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/contact/user/extra-attrs" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 导出所有成员信息（异步）
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/export/user" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"aeskey": "your_32_char_aes_key_here_12345"}'
```
> - `aeskey` 为32位加密密钥（a-z, A-Z, 0-9），用于解密下载文件
> - 频率限制：10次/分钟
> - 需轮询查询任务状态获取下载链接

## 二、部门管理

### 创建部门
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/department/create" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"name": "研发部", "parent_id": 1, "order": 100}'
```
| 参数 | 必须 | 说明 |
|------|------|------|
| name | 是 | 部门名称 |
| parent_id | 是 | 父部门ID（根部门为1） |
| id | 否 | 指定部门ID（32位整型，>1） |
| order | 否 | 排序值（范围 [0, 2^32)，越大越靠前） |

**常见错误码：**
- 1003: 参数错误
- 1005: 部门名称已存在
- 1007: 部门层级超过15层

### 更新部门
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/department/edit" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"id": 2, "name": "产品研发部"}'
```

### 删除部门
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/department/delete" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"id": 2}'
```
> 不能删除根部门、含有子部门或成员的部门

### 获取子部门
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/contact/department/index?id=1&with_descendant=1" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 获取单个部门信息
```bash
curl "https://lxapi.lexiangla.com/cgi-bin/v1/contact/department/get?id=2" \
  -H "Authorization: Bearer $LEXIANG_TOKEN"
```

### 导出所有部门信息（异步）
```bash
curl -X POST "https://lxapi.lexiangla.com/cgi-bin/v1/contact/export/department" \
  -H "Authorization: Bearer $LEXIANG_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"aeskey": "your_32_char_aes_key_here_12345"}'
```

## 通讯录错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户不存在 |
| 1002 | 部门不存在 |
| 1003 | 参数错误 |
| 1004 | 部门下存在子部门 |
| 1005 | 部门下存在用户 / 部门名称已存在 |
| 1006 | 该部门是根部门 |
| 1007 | 部门层级超过15层 |
| 1010 | 父部门不能为该部门的子部门 |
