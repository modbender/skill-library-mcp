# 华为云 Terraform Provider 指南

本文档整理华为云 Terraform Provider 的使用方法和常用资源配置。

## 目录

1. [快速开始](#快速开始)
2. [Provider 配置](#provider-配置)
3. [常用资源](#常用资源)
4. [最佳实践](#最佳实践)
5. [常见问题](#常见问题)

---

## 快速开始

### 安装 Terraform

```bash
# macOS
brew install terraform

# Windows
choco install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### 验证安装

```bash
terraform version
```

### 初始化项目

```bash
mkdir my-hwc-project
cd my-hwc-project
terraform init
```

---

## Provider 配置

### 基础配置

```hcl
terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "~> 1.60.0"
    }
  }
}

provider "huaweicloud" {
  region = "cn-north-4"  # 华北-北京四

  # 推荐使用环境变量
  # HW_ACCESS_KEY
  # HW_SECRET_KEY
  # 或配置文件 ~/.hcloud/config.json
}
```

### 多区域配置

```hcl
provider "huaweicloud" {
  alias  = "beijing"
  region = "cn-north-4"
}

provider "huaweicloud" {
  alias  = "shanghai"
  region = "cn-east-3"
}
```

### 区域代码

| 区域名称 | 代码 |
|----------|------|
| 华北-北京一 | cn-north-1 |
| 华北-北京四 | cn-north-4 |
| 华东-上海一 | cn-east-3 |
| 华南-广州 | cn-south-1 |
| 西南-贵阳一 | cn-southwest-2 |
| 亚太-香港 | ap-southeast-1 |
| 亚太-新加坡 | ap-southeast-3 |

---

## 常用资源

### 网络资源

#### VPC

```hcl
resource "huaweicloud_vpc" "main" {
  name = "my-vpc"
  cidr = "10.0.0.0/16"

  tags = {
    environment = "production"
  }
}

resource "huaweicloud_vpc_subnet" "public" {
  name       = "public-subnet"
  vpc_id     = huaweicloud_vpc.main.id
  cidr       = "10.0.1.0/24"
  gateway_ip = "10.0.1.1"

  availability_zone = "cn-north-4a"
}

resource "huaweicloud_vpc_subnet" "private" {
  name       = "private-subnet"
  vpc_id     = huaweicloud_vpc.main.id
  cidr       = "10.0.10.0/24"
  gateway_ip = "10.0.10.1"

  availability_zone = "cn-north-4a"
}
```

#### 安全组

```hcl
resource "huaweicloud_networking_secgroup" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
}

resource "huaweicloud_networking_secgroup_rule" "http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.web.id
}

resource "huaweicloud_networking_secgroup_rule" "https" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.web.id
}

resource "huaweicloud_networking_secgroup_rule" "ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "10.0.0.0/16"  # 仅内网
  security_group_id = huaweicloud_networking_secgroup.web.id
}
```

#### EIP

```hcl
resource "huaweicloud_vpc_eip" "web" {
  publicip {
    type = "5_bgp"
  }
  bandwidth {
    name        = "web-bandwidth"
    size        = 10
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

resource "huaweicloud_vpc_eip_associate" "web" {
  public_ip  = huaweicloud_vpc_eip.web.address
  network_id = huaweicloud_compute_instance.web.network.0.uuid
}
```

#### ELB

```hcl
resource "huaweicloud_elb_loadbalancer" "web" {
  name           = "web-lb"
  vpc_id         = huaweicloud_vpc.main.id
  network_type   = "ip"

  availability_zone {
    name = "cn-north-4a"
  }
}

resource "huaweicloud_elb_listener" "http" {
  name            = "http-listener"
  protocol        = "HTTP"
  protocol_port   = 80
  loadbalancer_id = huaweicloud_elb_loadbalancer.web.id
}

resource "huaweicloud_elb_pool" "web" {
  name            = "web-pool"
  protocol        = "HTTP"
  lb_method       = "ROUND_ROBIN"
  listener_id     = huaweicloud_elb_listener.http.id

  healthcheck {
    protocol    = "HTTP"
    port        = 80
    path        = "/health"
    interval    = 10
    timeout     = 5
    max_retries = 3
  }
}

resource "huaweicloud_elb_member" "web" {
  count         = 2
  pool_id       = huaweicloud_elb_pool.web.id
  subnet_id     = huaweicloud_vpc_subnet.public.id
  address       = huaweicloud_compute_instance.web[count.index].access_ip_v4
  protocol_port = 80
}
```

---

### 计算资源

#### ECS 实例

```hcl
resource "huaweicloud_compute_instance" "web" {
  count         = 2
  name          = "web-server-${count.index + 1}"
  flavor_id     = "s6.xlarge.2"
  image_id      = "your-image-id"
  key_pair      = "your-keypair"

  availability_zone = "cn-north-4a"

  network {
    uuid = huaweicloud_vpc_subnet.public.id
  }

  system_disk_type = "SSD"
  system_disk_size = 50

  data_disks {
    type = "SSD"
    size = 200
  }

  security_group_ids = [
    huaweicloud_networking_secgroup.web.id
  ]

  tags = {
    role = "web"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum install -y nginx
              systemctl start nginx
              EOF
}
```

#### 密钥对

```hcl
resource "huaweicloud_compute_keypair" "main" {
  name       = "my-keypair"
  public_key = file("~/.ssh/id_rsa.pub")
}
```

---

### 存储资源

#### OBS 桶

```hcl
resource "huaweicloud_obs_bucket" "static" {
  bucket        = "my-static-assets"
  storage_class = "STANDARD"
  acl           = "public-read"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }

  tags = {
    environment = "production"
  }
}

resource "huaweicloud_obs_bucket_object" "index" {
  bucket  = huaweicloud_obs_bucket.static.bucket
  key     = "index.html"
  source  = "static/index.html"
  content_type = "text/html"
}
```

#### EVS 磁盘

```hcl
resource "huaweicloud_evs_volume" "data" {
  name              = "data-disk"
  volume_type       = "SSD"
  size              = 500
  availability_zone = "cn-north-4a"

  tags = {
    type = "data"
  }
}

resource "huaweicloud_compute_volume_attach" "data" {
  instance_id = huaweicloud_compute_instance.web[0].id
  volume_id   = huaweicloud_evs_volume.data.id
}
```

---

### 数据库资源

#### RDS MySQL

```hcl
resource "huaweicloud_rds_instance" "mysql" {
  name              = "my-mysql"
  flavor            = "rds.mysql.c6.xlarge.2.ha"
  availability_zone = ["cn-north-4a", "cn-north-4b"]

  vpc_id    = huaweicloud_vpc.main.id
  subnet_id = huaweicloud_vpc_subnet.private.id

  security_group_id = huaweicloud_networking_secgroup.db.id

  db {
    type     = "MySQL"
    version  = "8.0"
    password = var.db_password
  }

  volume {
    type = "SSD"
    size = 200
  }

  backup_strategy {
    start_time = "03:00-04:00"
    keep_days  = 7
  }

  parameters {
    name  = "max_connections"
    value = "2000"
  }
}
```

#### DCS Redis

```hcl
resource "huaweicloud_dcs_instance" "cache" {
  name              = "my-redis"
  engine            = "Redis"
  engine_version    = "6.0"
  capacity          = 4
  flavor            = "redis.ha.xu1.large.r2.4"
  vpc_id            = huaweicloud_vpc.main.id
  subnet_id         = huaweicloud_vpc_subnet.private.id
  availability_zone = "cn-north-4a"

  backup_policy {
    backup_type   = "auto"
    begin_at      = "02:00-03:00"
    period_type   = "weekly"
    backup_at     = [1, 2, 3, 4, 5, 6, 7]
    save_days     = 7
  }
}
```

---

### 其他资源

#### IAM 用户

```hcl
resource "huaweicloud_identity_user" "dev" {
  name        = "dev-user"
  password    = var.user_password
  enabled     = true
  email       = "dev@example.com"
}

resource "huaweicloud_identity_group" "developers" {
  name = "developers"
}

resource "huaweicloud_identity_group_membership" "dev" {
  group = huaweicloud_identity_group.developers.id
  users = [huaweicloud_identity_user.dev.id]
}

resource "huaweicloud_identity_role_assignment" "dev" {
  user_id    = huaweicloud_identity_user.dev.id
  project_id = var.project_id
  role_id    = "your-role-id"
}
```

#### CBR 备份

```hcl
resource "huaweicloud_cbr_vault" "ecs" {
  name = "ecs-backup-vault"

  resources {
    server_id = huaweicloud_compute_instance.web[0].id
  }

  policy_id = huaweicloud_cbr_policy.daily.id
}

resource "huaweicloud_cbr_policy" "daily" {
  name        = "daily-backup"
  type        = "backup"
  time_period = "timezone:UTC+08:00"

  pattern = [
    "FREQ=DAILY;INTERVAL=1;BYHOUR=02;BYMINUTE=00"
  ]
}
```

---

## 最佳实践

### 1. 变量管理

```hcl
# variables.tf
variable "region" {
  type        = string
  default     = "cn-north-4"
  description = "华为云区域"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "VPC网段"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "数据库密码"
}

# 使用 tfvars 文件
# terraform.tfvars
region      = "cn-north-4"
vpc_cidr    = "10.0.0.0/16"
db_password = "your-secure-password"
```

### 2. 输出管理

```hcl
# outputs.tf
output "vpc_id" {
  value = huaweicloud_vpc.main.id
}

output "ecs_public_ips" {
  value = huaweicloud_vpc_eip.web.address
}

output "rds_connection" {
  value = huaweicloud_rds_instance.mysql.public_ips
}

output "obs_bucket" {
  value = huaweicloud_obs_bucket.static.bucket
}
```

### 3. 环境隔离

```hcl
# 目录结构
environments/
├── dev/
│   ├── main.tf
│   └── terraform.tfvars
├── staging/
│   ├── main.tf
│   └── terraform.tfvars
└── prod/
    ├── main.tf
    └── terraform.tfvars

# 使用工作区
terraform workspace new dev
terraform workspace new prod
terraform workspace select dev
```

### 4. 模块化

```hcl
# modules/vpc/main.tf
resource "huaweicloud_vpc" "main" {
  name = var.name
  cidr = var.cidr
}

resource "huaweicloud_vpc_subnet" "subnet" {
  for_each = var.subnets

  name              = each.key
  vpc_id            = huaweicloud_vpc.main.id
  cidr              = each.value.cidr
  availability_zone = each.value.az
}

# 使用模块
module "network" {
  source = "./modules/vpc"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  subnets = {
    public = {
      cidr = "10.0.1.0/24"
      az   = "cn-north-4a"
    }
    private = {
      cidr = "10.0.10.0/24"
      az   = "cn-north-4a"
    }
  }
}
```

### 5. 状态管理

```hcl
# 远程状态存储
terraform {
  backend "obs" {
    bucket = "my-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "cn-north-4"
  }
}

# 或使用本地加密
terraform {
  encryption {
    key_provider "pbkdf2" "pass" {
      passphrase = var.encryption_key
    }
  }
}
```

---

## 常见问题

### Q: 如何获取镜像 ID？

```bash
# 使用华为云 CLI
hcloud image list --region cn-north-4 --os-type Linux

# 或在 Terraform 中查询
data "huaweicloud_images_image" "centos" {
  name        = "CentOS 7.6 64bit"
  most_recent = true
}
```

### Q: 如何获取规格列表？

```bash
# 使用华为云 CLI
hcloud ecs flavors list --region cn-north-4
```

### Q: AK/SK 如何配置？

```bash
# 方式1: 环境变量
export HW_ACCESS_KEY="your-ak"
export HW_SECRET_KEY="your-sk"

# 方式2: 配置文件 (~/.hcloud/config.json)
{
  "access_key": "your-ak",
  "secret_key": "your-sk"
}

# 方式3: Provider 配置（不推荐）
provider "huaweicloud" {
  access_key  = "your-ak"  # 不要硬编码！
  secret_key  = "your-sk"  # 不要硬编码！
}
```

### Q: 如何调试？

```bash
# 详细日志
export TF_LOG=DEBUG

# 只显示华为云 API 调用
export HW_LOG_LEVEL=debug

# 执行计划
terraform plan -out=tfplan
terraform show tfplan
```

### Q: 如何导入现有资源？

```bash
# 导入 VPC
terraform import huaweicloud_vpc.main <vpc-id>

# 导入 ECS
terraform import huaweicloud_compute_instance.web <instance-id>

# 导入 RDS
terraform import huaweicloud_rds_instance.mysql <instance-id>
```

### Q: 如何处理依赖？

```hcl
# 隐式依赖（推荐）
resource "huaweicloud_compute_instance" "web" {
  network {
    uuid = huaweicloud_vpc_subnet.public.id  # 自动创建依赖
  }
}

# 显式依赖
resource "huaweicloud_elb_member" "web" {
  depends_on = [huaweicloud_compute_instance.web]
}
```

---

## 参考资料

- [Terraform 华为云 Provider 文档](https://registry.terraform.io/providers/huaweicloud/huaweicloud/latest/docs)
- [华为云 Terraform 最佳实践](https://support.huaweicloud.com/intl/en-us/productdesc-terraform/index.html)
- [Terraform 官方文档](https://developer.hashicorp.com/terraform/docs)

---

*注：本文档基于 Terraform 1.6+ 和华为云 Provider 1.60+，API 可能有变化，请以官方文档为准。*
