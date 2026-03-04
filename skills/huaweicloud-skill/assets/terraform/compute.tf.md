# compute.tf - 计算资源模板

# 密钥对
resource "huaweicloud_compute_keypair" "main" {
  name       = "${local.project_name}-keypair"
  public_key = file(var.public_key_path)
}

# ECS 实例
resource "huaweicloud_compute_instance" "web" {
  count = var.web_instance_count

  name              = "${local.project_name}-web-${count.index + 1}"
  flavor_id         = var.web_instance_type
  image_id          = data.huaweicloud_images_image.web.id
  key_pair          = huaweicloud_compute_keypair.main.name
  availability_zone = var.availability_zones[count.index % length(var.availability_zones)]

  network {
    uuid = huaweicloud_vpc_subnet.public[count.index % length(var.availability_zones)].id
  }

  system_disk_type = "SSD"
  system_disk_size = var.web_root_volume_size

  dynamic "data_disks" {
    for_each = var.web_data_volume_size > 0 ? [1] : []
    content {
      type = "SSD"
      size = var.web_data_volume_size
    }
  }

  security_group_ids = [
    huaweicloud_networking_secgroup.web.id
  ]

  tags = merge(local.common_tags, {
    Role = "web"
  })

  user_data = var.web_user_data
}

# 数据镜像查询
data "huaweicloud_images_image" "web" {
  name        = var.image_name
  most_recent = true
}

# ELB 负载均衡
resource "huaweicloud_elb_loadbalancer" "web" {
  name         = "${local.project_name}-web-lb"
  vpc_id       = huaweicloud_vpc.main.id
  network_type = "ip"

  dynamic "availability_zone" {
    for_each = var.availability_zones
    content {
      name = availability_zone.value
    }
  }

  tags = local.common_tags
}

resource "huaweicloud_elb_listener" "http" {
  name            = "${local.project_name}-http"
  protocol        = "HTTP"
  protocol_port   = 80
  loadbalancer_id = huaweicloud_elb_loadbalancer.web.id
}

resource "huaweicloud_elb_listener" "https" {
  count = var.enable_https ? 1 : 0

  name                        = "${local.project_name}-https"
  protocol                    = "HTTPS"
  protocol_port               = 443
  loadbalancer_id             = huaweicloud_elb_loadbalancer.web.id
  default_tls_container_ref   = var.ssl_certificate_id
}

resource "huaweicloud_elb_pool" "web" {
  name            = "${local.project_name}-web-pool"
  protocol        = "HTTP"
  lb_method       = "ROUND_ROBIN"
  listener_id     = huaweicloud_elb_listener.http.id

  healthcheck {
    protocol    = "HTTP"
    port        = 80
    path        = var.health_check_path
    interval    = 10
    timeout     = 5
    max_retries = 3
  }
}

resource "huaweicloud_elb_member" "web" {
  count = var.web_instance_count

  pool_id       = huaweicloud_elb_pool.web.id
  subnet_id     = huaweicloud_vpc_subnet.public[count.index % length(var.availability_zones)].id
  address       = huaweicloud_compute_instance.web[count.index].access_ip_v4
  protocol_port = 80
}

# EIP
resource "huaweicloud_vpc_eip" "web" {
  publicip {
    type = "5_bgp"
  }
  bandwidth {
    name        = "${local.project_name}-web-bandwidth"
    size        = var.web_bandwidth
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

resource "huaweicloud_vpc_eip_associate" "web" {
  public_ip  = huaweicloud_vpc_eip.web.address
  network_id = huaweicloud_elb_loadbalancer.web.vip_subnet_id
}
