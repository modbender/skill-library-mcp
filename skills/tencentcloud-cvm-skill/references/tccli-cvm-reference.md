# 腾讯云 CVM tccli 命令参考

## API 文档链接

| API | 说明 | 文档链接 |
|-----|------|----------|
| RunInstances | 创建实例 | https://cloud.tencent.com/document/product/213/15730 |
| DescribeInstances | 查询实例 | https://cloud.tencent.com/document/product/213/15728 |
| StartInstances | 启动实例 | https://cloud.tencent.com/document/product/213/15735 |
| StopInstances | 停止实例 | https://cloud.tencent.com/document/product/213/15743 |
| RebootInstances | 重启实例 | https://cloud.tencent.com/document/product/213/15742 |
| TerminateInstances | 销毁实例 | https://cloud.tencent.com/document/product/213/15723 |
| DescribeImages | 查询镜像 | https://cloud.tencent.com/document/product/213/15715 |

## tccli 安装与配置

- 安装指南: https://cloud.tencent.com/document/product/440/34011
- 配置方法: https://cloud.tencent.com/document/product/440/34012

## 常用命令示例

### 创建实例

```bash
tccli cvm RunInstances \
  --InstanceChargeType POSTPAID_BY_HOUR \
  --Placement '{"Zone":"ap-guangzhou-3"}' \
  --InstanceType S5.MEDIUM2 \
  --ImageId img-xxx \
  --SystemDisk '{"DiskType":"CLOUD_PREMIUM","DiskSize":20}' \
  --VirtualPrivateCloud '{"VpcId":"vpc-xxx","SubnetId":"subnet-xxx"}' \
  --SecurityGroupIds '["sg-xxx"]' \
  --InstanceName my-instance \
  --LoginSettings '{"Password":"YourPassword123!"}'
```

### 带数据盘创建

```bash
tccli cvm RunInstances \
  --InstanceChargeType POSTPAID_BY_HOUR \
  --Placement '{"Zone":"ap-guangzhou-3"}' \
  --InstanceType S5.MEDIUM2 \
  --ImageId img-xxx \
  --SystemDisk '{"DiskType":"CLOUD_PREMIUM","DiskSize":20}' \
  --DataDisks '[{"DiskType":"CLOUD_PREMIUM","DiskSize":50}]' \
  --VirtualPrivateCloud '{"VpcId":"vpc-xxx","SubnetId":"subnet-xxx"}' \
  --SecurityGroupIds '["sg-xxx"]' \
  --InstanceName my-instance \
  --LoginSettings '{"Password":"YourPassword123!"}'
```

### 查询实例

```bash
# 查询所有实例
tccli cvm DescribeInstances --region ap-guangzhou

# 查询指定实例
tccli cvm DescribeInstances --region ap-guangzhou --InstanceIds '["ins-xxx"]'
```

### 启动/停止/重启实例

```bash
# 启动
tccli cvm StartInstances --region ap-guangzhou --InstanceIds '["ins-xxx"]'

# 停止
tccli cvm StopInstances --region ap-guangzhou --InstanceIds '["ins-xxx"]'

# 重启
tccli cvm RebootInstances --region ap-guangzhou --InstanceIds '["ins-xxx"]'
```

### 销毁实例

```bash
tccli cvm TerminateInstances --region ap-guangzhou --InstanceIds '["ins-xxx"]'
```

### 查询镜像

```bash
# 查询公共镜像
tccli cvm DescribeImages --region ap-guangzhou \
  --Filters '[{"Name":"image-type","Values":["PUBLIC_IMAGE"]}]'

# 查询 Ubuntu 镜像
tccli cvm DescribeImages --region ap-guangzhou \
  --Filters '[{"Name":"image-type","Values":["PUBLIC_IMAGE"]},{"Name":"platform","Values":["Ubuntu"]}]'
```

### 查询 VPC

```bash
tccli vpc DescribeVpcs --region ap-guangzhou
```

### 查询子网

```bash
# 查询所有子网
tccli vpc DescribeSubnets --region ap-guangzhou

# 查询指定 VPC 的子网
tccli vpc DescribeSubnets --region ap-guangzhou \
  --Filters '[{"Name":"vpc-id","Values":["vpc-xxx"]}]'
```

### 查询安全组

```bash
tccli vpc DescribeSecurityGroups --region ap-guangzhou
```

## 使用配置文件

### 生成参数骨架

```bash
tccli cvm RunInstances --generate-cli-skeleton > create-instance.json
```

### 从配置文件创建

```bash
tccli cvm RunInstances --cli-input-json file://./create-instance.json
```

### 预检查模式

```bash
tccli cvm RunInstances --cli-input-json file://./create-instance.json --DryRun True
```

## 参数说明

### InstanceChargeType (计费类型)

| 值 | 说明 |
|----|------|
| POSTPAID_BY_HOUR | 按量计费（按小时后付费）|
| PREPAID | 预付费（包年包月）|

### SystemDisk.DiskType (系统盘类型)

| 值 | 说明 |
|----|------|
| CLOUD_BASIC | 普通云硬盘 |
| CLOUD_SSD | SSD 云硬盘 |
| CLOUD_PREMIUM | 高性能云硬盘 |
| CLOUD_BSSD | 通用型 SSD 云硬盘 |

### StopType (停止类型)

| 值 | 说明 |
|----|------|
| SOFT | 软关机 |
| HARD | 硬关机 |

### StoppedMode (关机计费模式)

| 值 | 说明 |
|----|------|
| KEEP_CHARGING | 关机继续收费 |
| STOP_CHARGING | 关机停止收费 |
