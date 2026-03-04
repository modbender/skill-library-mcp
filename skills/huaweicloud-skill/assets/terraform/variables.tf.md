# variables.tf - 变量定义

# ==================== 基础配置 ====================

variable "region" {
  type        = string
  default     = "cn-north-4"
  description = "华为云区域"
}

variable "project_name" {
  type        = string
  description = "项目名称"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "环境标识"
}

variable "availability_zones" {
  type        = list(string)
  default     = ["cn-north-4a", "cn-north-4b"]
  description = "可用区列表"
}

# ==================== 网络配置 ====================

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC 网段"
}

variable "enable_nat_gateway" {
  type        = bool
  default     = true
  description = "是否创建 NAT 网关"
}

variable "nat_bandwidth" {
  type        = number
  default     = 10
  description = "NAT 网关带宽 (Mbps)"
}

# ==================== 计算配置 ====================

variable "web_instance_count" {
  type        = number
  default     = 2
  description = "Web 服务器数量"
}

variable "web_instance_type" {
  type        = string
  default     = "s6.xlarge.2"
  description = "Web 服务器规格"
}

variable "web_root_volume_size" {
  type        = number
  default     = 50
  description = "系统盘大小 (GB)"
}

variable "web_data_volume_size" {
  type        = number
  default     = 100
  description = "数据盘大小 (GB)，0 表示不创建"
}

variable "web_bandwidth" {
  type        = number
  default     = 10
  description = "公网带宽 (Mbps)"
}

variable "web_user_data" {
  type        = string
  default     = ""
  description = "用户数据脚本"
}

variable "image_name" {
  type        = string
  default     = "CentOS 7.6 64bit"
  description = "镜像名称"
}

variable "public_key_path" {
  type        = string
  default     = "~/.ssh/id_rsa.pub"
  description = "SSH 公钥路径"
}

variable "enable_https" {
  type        = bool
  default     = false
  description = "是否启用 HTTPS"
}

variable "ssl_certificate_id" {
  type        = string
  default     = ""
  description = "SSL 证书 ID"
}

variable "health_check_path" {
  type        = string
  default     = "/health"
  description = "健康检查路径"
}

# ==================== 数据库配置 ====================

variable "db_instance_type" {
  type        = string
  default     = "rds.mysql.c6.xlarge.2.ha"
  description = "RDS 实例规格"
}

variable "db_version" {
  type        = string
  default     = "8.0"
  description = "MySQL 版本"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "数据库密码"
}

variable "db_storage_size" {
  type        = number
  default     = 100
  description = "数据库存储大小 (GB)"
}

variable "db_backup_retention" {
  type        = number
  default     = 7
  description = "备份保留天数"
}

variable "db_max_connections" {
  type        = string
  default     = "2000"
  description = "最大连接数"
}

variable "db_ha_enabled" {
  type        = bool
  default     = true
  description = "是否启用高可用"
}

variable "db_read_replica_count" {
  type        = number
  default     = 0
  description = "只读实例数量"
}

variable "db_read_replica_type" {
  type        = string
  default     = "rds.mysql.c6.large.2"
  description = "只读实例规格"
}

# Redis 配置
variable "redis_version" {
  type        = string
  default     = "6.0"
  description = "Redis 版本"
}

variable "redis_capacity" {
  type        = number
  default     = 4
  description = "Redis 容量 (GB)"
}

variable "redis_password" {
  type        = string
  sensitive   = true
  description = "Redis 密码"
}

variable "redis_ha_enabled" {
  type        = bool
  default     = true
  description = "是否启用 Redis 高可用"
}

# MongoDB 配置
variable "enable_mongodb" {
  type        = bool
  default     = false
  description = "是否启用 MongoDB"
}

variable "mongodb_cluster_type" {
  type        = string
  default     = "ReplicaSet"
  description = "MongoDB 集群类型"
}

variable "mongodb_node_count" {
  type        = number
  default     = 3
  description = "MongoDB 节点数量"
}

variable "mongodb_storage_size" {
  type        = number
  default     = 100
  description = "MongoDB 存储大小 (GB)"
}

variable "mongodb_password" {
  type        = string
  sensitive   = true
  default     = ""
  description = "MongoDB 密码"
}

# ==================== 存储配置 ====================

variable "enable_data_bucket" {
  type        = bool
  default     = false
  description = "是否创建数据 OBS 桶"
}

variable "enable_obs_lifecycle" {
  type        = bool
  default     = true
  description = "是否启用 OBS 生命周期"
}

variable "obs_expiration_days" {
  type        = number
  default     = 365
  description = "OBS 对象过期天数"
}

variable "cors_origins" {
  type        = list(string)
  default     = ["*"]
  description = "CORS 允许的来源"
}

variable "standalone_data_disk" {
  type        = bool
  default     = false
  description = "是否创建独立数据盘"
}

variable "data_disk_type" {
  type        = string
  default     = "SSD"
  description = "数据盘类型"
}

variable "data_disk_size" {
  type        = number
  default     = 500
  description = "数据盘大小 (GB)"
}

variable "enable_sfs" {
  type        = bool
  default     = false
  description = "是否启用 SFS 文件系统"
}

variable "sfs_size" {
  type        = number
  default     = 500
  description = "SFS 容量 (GB)"
}

variable "enable_backup" {
  type        = bool
  default     = true
  description = "是否启用备份"
}
