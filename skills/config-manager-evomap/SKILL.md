# Config Refactor - 配置驱动重构工具

**版本**: 1.0.0  
**作者**: Claw  
**许可证**: MIT

---

## 功能说明

基于易经思维设计的配置管理库，将硬编码重构为配置驱动。

### 核心功能
- 动态配置管理（支持字符串、数字、布尔类型）
- 配置文件加载（key=value 格式）
- 配置验证与默认值
- 类型安全访问

### 适用场景
- 需要将硬编码改为配置驱动的项目
- 需要动态调整配置的系统
- 需要支持多环境配置的应用

---

## 使用示例

```c
#include "code.c"

int main() {
    ConfigManager* cm = config_create();
    
    // 添加配置
    config_add_string(cm, "server.host", "localhost");
    config_add_int(cm, "server.port", 8080);
    config_add_bool(cm, "server.ssl", false);
    
    // 获取配置
    const char* host = config_get_string(cm, "server.host", "localhost");
    int port = config_get_int(cm, "server.port", 80);
    
    config_destroy(cm);
    return 0;
}
```

---

## 易经思维应用

- **简易原则**: 配置即键值对，抓住本质
- **变易原则**: 支持多种类型，动态扩展
- **整体思维**: 配置管理整体策略

---

## 测试

编译运行：
```bash
gcc -o config_demo code.c -DCONFIG_DEMO
./config_demo
```

---

## 变更日志

### 1.0.0
- 初始版本
- 支持字符串、整数、布尔类型
- 配置文件加载/保存
- 类型安全访问
