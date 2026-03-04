# database.tf - 数据库资源模板

# RDS MySQL
resource "huaweicloud_rds_instance" "mysql" {
  name              = "${local.project_name}-mysql"
  flavor            = var.db_instance_type
  availability_zone = var.db_ha_enabled ? join(",", var.availability_zones) : var.availability_zones[0]

  vpc_id            = huaweicloud_vpc.main.id
  subnet_id         = huaweicloud_vpc_subnet.private[0].id
  security_group_id = huaweicloud_networking_secgroup.db.id

  db {
    type     = "MySQL"
    version  = var.db_version
    password = var.db_password
  }

  volume {
    type = "SSD"
    size = var.db_storage_size
  }

  backup_strategy {
    start_time = "03:00-04:00"
    keep_days  = var.db_backup_retention
  }

  parameters {
    name  = "max_connections"
    value = var.db_max_connections
  }

  tags = local.common_tags
}

# 只读实例（可选）
resource "huaweicloud_rds_read_replica_instance" "mysql" {
  count = var.db_read_replica_count

  name              = "${local.project_name}-mysql-read-${count.index + 1}"
  flavor            = var.db_read_replica_type
  primary_instance_id = huaweicloud_rds_instance.mysql.id
  availability_zone = var.availability_zones[(count.index + 1) % length(var.availability_zones)]

  volume {
    type = "SSD"
    size = var.db_storage_size
  }
}

# DCS Redis
resource "huaweicloud_dcs_instance" "redis" {
  name              = "${local.project_name}-redis"
  engine            = "Redis"
  engine_version    = var.redis_version
  capacity          = var.redis_capacity
  flavor            = var.redis_ha_enabled ? "redis.ha.xu1.large.r2.${var.redis_capacity}" : "redis.single.xu1.large.2"
  vpc_id            = huaweicloud_vpc.main.id
  subnet_id         = huaweicloud_vpc_subnet.private[0].id
  availability_zone = var.availability_zones[0]

  password          = var.redis_password

  backup_policy {
    backup_type = "auto"
    begin_at    = "02:00-03:00"
    period_type = "weekly"
    backup_at   = [1, 2, 3, 4, 5, 6, 7]
    save_days   = 7
  }

  tags = local.common_tags
}

# DDS MongoDB（可选）
resource "huaweicloud_dds_instance" "mongodb" {
  count = var.enable_mongodb ? 1 : 0

  name              = "${local.project_name}-mongodb"
  region            = var.region
  availability_zone = join(",", var.availability_zones)

  vpc_id  = huaweicloud_vpc.main.id
  subnet_id = huaweicloud_vpc_subnet.private[0].id

  flavor {
    type     = var.mongodb_cluster_type
    num      = var.mongodb_node_count
    storage  = "ULTRAHIGH"
    size     = var.mongodb_storage_size
  }

  password = var.mongodb_password

  tags = local.common_tags
}
