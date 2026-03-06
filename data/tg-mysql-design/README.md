# 数据库设计助手 (tg-mysql-design)

## 功能说明

此 Skill 用于根据业务规则文档和存量 SQL DDL 脚本，设计符合阿里巴巴规范的 MySQL 5.7/8.0 建表语句。

## 使用方法

### 方式一：斜杠命令（推荐）

在对话中直接使用：

```
/database-design
```

然后提供您的业务需求，例如：
```
我需要设计一个商机跟进记录表，包含：跟进人、客户、跟进内容、跟进方式、跟进时间等字段
```

### 方式二：自然触发

当您提到以下关键词时，此 Skill 会自动触发：
- "数据库设计"
- "建表语句"
- "DDL"
- "表结构设计"
- "CREATE TABLE"
- "设计表"

## 输入要求

1. **业务规则文档**（可选）
   - 提供 `.md` 文件路径，包含详细的业务规则说明
   - 格式：字段定义、数据类型、约束条件、业务关系

2. **存量 SQL 脚本**（可选）
   - 提供现有 `.sql` 文件路径
   - 用于参考或重构现有表结构

3. **口头描述**
   - 直接用文字描述业务需求
   - 例如："设计一个订单表，包含订单号、客户、金额、状态"

## 输出内容

1. **标准 DDL 语句**
   - 符合阿里巴巴命名规范
   - 包含完整注释
   - 主键、索引、约束完整

2. **表结构说明**
   - 字段列表及含义
   - 索引设计说明
   - 业务规则说明

3. **最佳实践建议**
   - 性能优化建议
   - 扩展性考虑
   - 兼容性说明

## 支持的特性

- ✅ MySQL 5.7 / 8.0 双版本支持
- ✅ 阿里巴巴数据库设计规范
- ✅ 自动审计字段（创建时间、更新时间等）
- ✅ 智能索引设计
- ✅ 逻辑删除支持
- ✅ 标准字符集设置
- ✅ 业务规则文档解析

## 示例

**输入：**
```
设计一个项目管理表，项目名称、项目经理、开始时间、结束时间、项目状态
状态包括：未开始、进行中、已完成、已延期
```

**输出：**
```sql
DROP TABLE IF EXISTS `pm_project`;

CREATE TABLE `pm_project` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键ID',
  `project_name` VARCHAR(128) NOT NULL COMMENT '项目名称',
  `manager_id` VARCHAR(32) NOT NULL COMMENT '项目经理ID',
  `start_date` DATE DEFAULT NULL COMMENT '开始日期',
  `end_date` DATE DEFAULT NULL COMMENT '结束日期',
  `project_status` TINYINT NOT NULL DEFAULT 0 COMMENT '项目状态(0-未开始 1-进行中 2-已完成 3-已延期)',
  `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `create_by` VARCHAR(32) DEFAULT NULL COMMENT '创建人ID',
  `update_by` VARCHAR(32) DEFAULT NULL COMMENT '更新人ID',
  `deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除标识(0-未删除 1-已删除)',
  PRIMARY KEY (`id`),
  KEY `idx_manager_id` (`manager_id`),
  KEY `idx_project_status` (`project_status`),
  KEY `idx_start_date` (`start_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='项目管理主表';
```

## 技术规范参考

- [阿里巴巴 Java 开发手册 - 数据规约](https://github.com/alibaba/p3c)
- [MySQL 8.0 官方文档](https://dev.mysql.com/doc/refman/8.0/en/)
- [MySQL 5.7 官方文档](https://dev.mysql.com/doc/refman/5.7/en/)
