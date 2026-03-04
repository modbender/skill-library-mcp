# main.tf - 主配置模板

terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "~> 1.60.0"
    }
  }

  # 远程状态存储（可选）
  # backend "obs" {
  #   bucket = "your-terraform-state"
  #   key    = "{{PROJECT_NAME}}/terraform.tfstate"
  #   region = "{{REGION}}"
  # }
}

provider "huaweicloud" {
  region = "{{REGION}}"

  # 使用环境变量或配置文件
  # HW_ACCESS_KEY
  # HW_SECRET_KEY
}

# 项目信息
locals {
  project_name = "{{PROJECT_NAME}}"
  environment  = "{{ENVIRONMENT}}"
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "terraform"
  }
}
