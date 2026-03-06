# storage.tf - 存储资源模板

# OBS 桶
resource "huaweicloud_obs_bucket" "static" {
  bucket        = "${local.project_name}-static-assets"
  storage_class = "STANDARD"
  acl           = "private"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD", "PUT", "POST"]
    allowed_origins = var.cors_origins
    expose_headers  = ["ETag", "x-obs-request-id"]
    max_age_seconds = 3600
  }

  lifecycle_rule {
    id      = "archive-old-files"
    enabled = var.enable_obs_lifecycle

    expiration {
      days = var.obs_expiration_days
    }

    noncurrent_version_expiration {
      days = 30
    }
  }

  tags = local.common_tags
}

# OBS 数据桶（备份/日志）
resource "huaweicloud_obs_bucket" "data" {
  count = var.enable_data_bucket ? 1 : 0

  bucket        = "${local.project_name}-data"
  storage_class = "STANDARD"
  acl           = "private"

  versioning = true

  lifecycle_rule {
    id      = "archive-old-backups"
    enabled = true

    transition {
      days          = 30
      storage_class = "WARM"
    }

    transition {
      days          = 90
      storage_class = "COLD"
    }

    expiration {
      days = 365
    }
  }

  tags = local.common_tags
}

# EVS 数据盘（单独创建）
resource "huaweicloud_evs_volume" "data" {
  count = var.standalone_data_disk ? 1 : 0

  name              = "${local.project_name}-data-disk"
  volume_type       = var.data_disk_type
  size              = var.data_disk_size
  availability_zone = var.availability_zones[0]

  tags = local.common_tags
}

# SFS 文件系统（可选）
resource "huaweicloud_sfs_file_system" "shared" {
  count = var.enable_sfs ? 1 : 0

  name        = "${local.project_name}-shared"
  size        = var.sfs_size
  share_proto = "NFS"
  description = "Shared file system for ${local.project_name}"

  tags = local.common_tags
}

# SFS 访问规则
resource "huaweicloud_sfs_share_access_rule" "main" {
  count = var.enable_sfs ? 1 : 0

  sfs_id          = huaweicloud_sfs_file_system.shared[0].id
  access_type     = "cert"
  access_to       = huaweicloud_vpc.main.id
  access_level    = "rw"
}

# CBR 备份库
resource "huaweicloud_cbr_vault" "ecs" {
  count = var.enable_backup ? 1 : 0

  name = "${local.project_name}-ecs-backup"
  type = "server"

  billing {
    charging_mode = "post_paid"
    console_url   = ""
  }

  dynamic "resources" {
    for_each = huaweicloud_compute_instance.web
    content {
      server_id = resources.value.id
    }
  }
}

resource "huaweicloud_cbr_policy" "daily" {
  count = var.enable_backup ? 1 : 0

  name        = "${local.project_name}-daily-backup"
  type        = "backup"
  time_period = "timezone:UTC+08:00"

  pattern = [
    "FREQ=DAILY;INTERVAL=1;BYHOUR=02;BYMINUTE=00"
  ]
}

resource "huaweicloud_cbr_vault_policy" "ecs" {
  count = var.enable_backup ? 1 : 0

  vault_id  = huaweicloud_cbr_vault.ecs[0].id
  policy_id = huaweicloud_cbr_policy.daily[0].id
}
