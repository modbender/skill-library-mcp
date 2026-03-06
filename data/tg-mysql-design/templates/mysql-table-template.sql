DROP TABLE IF EXISTS `[module]_[table_name]`;

CREATE TABLE `[module]_[table_name]` (
  `id` VARCHAR(32) NOT NULL COMMENT '主键ID',
  `business_no` VARCHAR(64) NOT NULL COMMENT '业务编号 规则：[模块名]+[日期]+[随机4位数字]',
  `name` VARCHAR(128) NOT NULL COMMENT '名称',
  `business_status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态(0-禁用 1-启用)',
  `business_type` CHAR(2) NOT NULL DEFAULT 0 COMMENT '业务类型(01-采购合同 02-销售合同 03-采购订单 04-销售订单)',
  `enabled` TINYINT NOT NULL DEFAULT 0 COMMENT '是否启用(0-否 1-是)',
  `remark` VARCHAR(1024) DEFAULT NULL COMMENT '备注',
  `create_date` DATE NOT NULL DEFAULT CURRENT_DATE COMMENT '创建日期',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `create_by` VARCHAR(32) DEFAULT NULL COMMENT '创建人ID',
  `update_by` VARCHAR(32) DEFAULT NULL COMMENT '更新人ID',
  `deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除标识(0-未删除 1-已删除)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_business_no` (`business_no`),
  KEY `idx_name` (`name`),
  KEY `idx_status` (`business_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='[表注释]';
