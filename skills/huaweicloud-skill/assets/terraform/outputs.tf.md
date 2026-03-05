# outputs.tf - 输出变量

# ==================== 网络输出 ====================

output "vpc_id" {
  value       = huaweicloud_vpc.main.id
  description = "VPC ID"
}

output "vpc_cidr" {
  value       = huaweicloud_vpc.main.cidr
  description = "VPC 网段"
}

output "public_subnet_ids" {
  value       = huaweicloud_vpc_subnet.public[*].id
  description = "公有子网 ID 列表"
}

output "private_subnet_ids" {
  value       = huaweicloud_vpc_subnet.private[*].id
  description = "私有子网 ID 列表"
}

output "web_security_group_id" {
  value       = huaweicloud_networking_secgroup.web.id
  description = "Web 安全组 ID"
}

output "db_security_group_id" {
  value       = huaweicloud_networking_secgroup.db.id
  description = "数据库安全组 ID"
}

# ==================== 计算输出 ====================

output "web_instance_ids" {
  value       = huaweicloud_compute_instance.web[*].id
  description = "Web 服务器 ID 列表"
}

output "web_private_ips" {
  value       = huaweicloud_compute_instance.web[*].access_ip_v4
  description = "Web 服务器私有 IP"
}

output "load_balancer_id" {
  value       = huaweicloud_elb_loadbalancer.web.id
  description = "负载均衡器 ID"
}

output "load_balancer_public_ip" {
  value       = huaweicloud_vpc_eip.web.address
  description = "负载均衡器公网 IP"
}

output "load_balancer_http_listener_id" {
  value       = huaweicloud_elb_listener.http.id
  description = "HTTP 监听器 ID"
}

output "load_balancer_https_listener_id" {
  value       = var.enable_https ? huaweicloud_elb_listener.https[0].id : null
  description = "HTTPS 监听器 ID"
}

# ==================== 数据库输出 ====================

output "mysql_instance_id" {
  value       = huaweicloud_rds_instance.mysql.id
  description = "RDS MySQL 实例 ID"
}

output "mysql_private_ip" {
  value       = huaweicloud_rds_instance.mysql.private_ips
  description = "RDS MySQL 私有 IP"
}

output "mysql_port" {
  value       = 3306
  description = "MySQL 端口"
}

output "mysql_connection_string" {
  value       = "mysql://${huaweicloud_rds_instance.mysql.private_ips[0]}:3306"
  description = "MySQL 连接字符串"
}

output "redis_instance_id" {
  value       = huaweicloud_dcs_instance.redis.id
  description = "Redis 实例 ID"
}

output "redis_connection_string" {
  value       = "redis://${huaweicloud_dcs_instance.redis.ip}:${huaweicloud_dcs_instance.redis.port}"
  description = "Redis 连接字符串"
}

output "mongodb_connection_string" {
  value       = var.enable_mongodb ? "mongodb://${huaweicloud_dds_instance.mongodb[0].private_ips[0]}:8635" : null
  description = "MongoDB 连接字符串"
}

# ==================== 存储输出 ====================

output "static_bucket_name" {
  value       = huaweicloud_obs_bucket.static.bucket
  description = "静态资源 OBS 桶名"
}

output "static_bucket_url" {
  value       = "https://${huaweicloud_obs_bucket.static.bucket}.obs.${var.region}.myhuaweicloud.com"
  description = "静态资源 OBS URL"
}

output "data_bucket_name" {
  value       = var.enable_data_bucket ? huaweicloud_obs_bucket.data[0].bucket : null
  description = "数据 OBS 桶名"
}

output "sfs_share_id" {
  value       = var.enable_sfs ? huaweicloud_sfs_file_system.shared[0].id : null
  description = "SFS 文件系统 ID"
}

output "sfs_export_location" {
  value       = var.enable_sfs ? huaweicloud_sfs_file_system.shared[0].export_location : null
  description = "SFS 挂载路径"
}

# ==================== 备份输出 ====================

output "backup_vault_id" {
  value       = var.enable_backup ? huaweicloud_cbr_vault.ecs[0].id : null
  description = "CBR 备份库 ID"
}

# ==================== 连接信息摘要 ====================

output "connection_summary" {
  value = <<-EOT

    ========== 连接信息 ==========

    应用入口: http://${huaweicloud_vpc_eip.web.address}

    MySQL:
      Host: ${huaweicloud_rds_instance.mysql.private_ips[0]}
      Port: 3306
      User: root

    Redis:
      Host: ${huaweicloud_dcs_instance.redis.ip}
      Port: ${huaweicloud_dcs_instance.redis.port}

    OBS 静态资源:
      Bucket: ${huaweicloud_obs_bucket.static.bucket}
      URL: https://${huaweicloud_obs_bucket.static.bucket}.obs.${var.region}.myhuaweicloud.com

    ==============================
  EOT
  description = "连接信息摘要"
}
