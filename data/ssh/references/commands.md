# SSH 常用命令参考

## 系统管理

### 系统信息
```bash
uname -a              # 查看系统完整信息
hostnamectl           # 查看主机信息
uptime                # 查看运行时间
date                  # 查看当前日期时间
```

### 用户和权限
```bash
whoami                # 当前用户
id                    # 用户ID和组信息
users                 # 登录用户
last                  # 最近登录记录
```

### 进程管理
```bash
ps aux                # 查看所有进程
ps aux | grep nginx   # 查找特定进程
top                   # 实时进程监控
htop                  # 交互式进程查看
kill <pid>            # 杀死进程
killall <name>        # 按名称杀死进程
```

## 文件操作

### 导航和查看
```bash
pwd                   # 当前目录
ls -la                # 列出文件详细信息
cd <path>             # 切换目录
find / -name <file>   # 查找文件
cat <file>            # 查看文件内容
less <file>           # 分页查看
tail -f <file>        # 实时查看日志
```

### 文件传输
```bash
cp <src> <dst>        # 复制文件
mv <src> <dst>        # 移动/重命名
rm <file>             # 删除文件
mkdir <dir>           # 创建目录
chmod 755 <file>      # 修改权限
chown user:group <file> # 修改所有者
```

### 压缩解压
```bash
tar -czvf file.tar.gz <dir>   # 压缩
tar -xzvf file.tar.gz         # 解压
zip -r file.zip <dir>         # ZIP压缩
unzip file.zip                # ZIP解压
```

## 软件管理

### APT (Debian/Ubuntu)
```bash
apt update            # 更新软件源
apt upgrade           # 升级软件
apt install <pkg>     # 安装软件
apt remove <pkg>      # 卸载软件
apt search <pkg>      # 搜索软件
```

### YUM/DNF (CentOS/RHEL)
```bash
yum update            # 更新
yum install <pkg>     # 安装
yum remove <pkg>      # 卸载
yum search <pkg>      # 搜索
```

## 网络管理

### 网络工具
```bash
ip addr              # 查看IP信息
ip route             # 查看路由表
ping <host>          # 测试连通性
curl <url>           # HTTP请求
wget <url>           # 下载文件
netstat -tulpn       # 查看端口
ss -tulpn            # 查看端口
```

### 防火墙
```bash
# UFW (Ubuntu)
ufw status           # 状态
ufw allow 22         # 开放端口
ufw deny 80          # 关闭端口

# firewalld (CentOS)
firewall-cmd --list-ports
firewall-cmd --add-port=80/tcp
```

## 服务管理

### systemd
```bash
systemctl status <service>   # 查看状态
systemctl start <service>    # 启动
systemctl stop <service>     # 停止
systemctl restart <service>  # 重启
systemctl enable <service>   # 开机自启
systemctl disable <service>  # 关闭自启
journalctl -u <service>      # 查看日志
```

### 查看日志
```bash
tail -f /var/log/syslog          # 系统日志
tail -f /var/log/nginx/access.log # Nginx访问日志
tail -f /var/log/auth.log         # 认证日志
```

## Docker (如果安装了)
```bash
docker ps                     # 查看运行中的容器
docker ps -a                  # 所有容器
docker images                 # 查看镜像
docker logs <container>       # 容器日志
docker exec -it <container> bash # 进入容器
```
