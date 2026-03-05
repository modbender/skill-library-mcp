# vpc.tf - 网络配置模板

# VPC
resource "huaweicloud_vpc" "main" {
  name = "${local.project_name}-vpc"
  cidr = "{{VPC_CIDR}}"

  tags = local.common_tags
}

# 公有子网
resource "huaweicloud_vpc_subnet" "public" {
  count = length(var.availability_zones)

  name              = "${local.project_name}-public-${count.index + 1}"
  vpc_id            = huaweicloud_vpc.main.id
  cidr              = cidrsubnet(var.vpc_cidr, 8, count.index)
  gateway_ip        = cidrhost(cidrsubnet(var.vpc_cidr, 8, count.index), 1)
  availability_zone = var.availability_zones[count.index]

  tags = local.common_tags
}

# 私有子网
resource "huaweicloud_vpc_subnet" "private" {
  count = length(var.availability_zones)

  name              = "${local.project_name}-private-${count.index + 1}"
  vpc_id            = huaweicloud_vpc.main.id
  cidr              = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  gateway_ip        = cidrhost(cidrsubnet(var.vpc_cidr, 8, count.index + 10), 1)
  availability_zone = var.availability_zones[count.index]

  tags = local.common_tags
}

# Web 安全组
resource "huaweicloud_networking_secgroup" "web" {
  name        = "${local.project_name}-web-sg"
  description = "Security group for web servers"
}

resource "huaweicloud_networking_secgroup_rule" "web_http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.web.id
}

resource "huaweicloud_networking_secgroup_rule" "web_https" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.web.id
}

resource "huaweicloud_networking_secgroup_rule" "web_ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = var.vpc_cidr
  security_group_id = huaweicloud_networking_secgroup.web.id
}

# 数据库安全组
resource "huaweicloud_networking_secgroup" "db" {
  name        = "${local.project_name}-db-sg"
  description = "Security group for database servers"
}

resource "huaweicloud_networking_secgroup_rule" "db_mysql" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 3306
  port_range_max    = 3306
  remote_ip_prefix  = var.vpc_cidr
  security_group_id = huaweicloud_networking_secgroup.db.id
}

resource "huaweicloud_networking_secgroup_rule" "db_redis" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 6379
  port_range_max    = 6379
  remote_ip_prefix  = var.vpc_cidr
  security_group_id = huaweicloud_networking_secgroup.db.id
}

# NAT 网关（可选，用于私有子网访问公网）
resource "huaweicloud_nat_gateway" "main" {
  count = var.enable_nat_gateway ? 1 : 0

  name                = "${local.project_name}-nat"
  spec                = "1"
  vpc_id              = huaweicloud_vpc.main.id
  subnet_id           = huaweicloud_vpc_subnet.public[0].id

  tags = local.common_tags
}

resource "huaweicloud_vpc_eip" "nat" {
  count = var.enable_nat_gateway ? 1 : 0

  publicip {
    type = "5_bgp"
  }
  bandwidth {
    name        = "${local.project_name}-nat-bandwidth"
    size        = var.nat_bandwidth
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

resource "huaweicloud_nat_snat_rule" "main" {
  count = var.enable_nat_gateway ? 1 : 0

  nat_gateway_id = huaweicloud_nat_gateway.main[0].id
  floating_ip_id = huaweicloud_vpc_eip.nat[0].id
  subnet_id      = huaweicloud_vpc_subnet.private[0].id
}
