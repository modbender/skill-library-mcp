/**
 * 配置管理器 - 配置驱动重构工具
 * 版本：v1.0
 * 基于易经思维设计：简易、变易、整体
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_CONFIG_ITEMS 1000
#define MAX_KEY_LENGTH 256
#define MAX_VALUE_LENGTH 1024

// 配置项类型
typedef enum {
    CONFIG_STRING,
    CONFIG_INT,
    CONFIG_BOOL,
    CONFIG_FLOAT
} ConfigType;

// 配置项结构
typedef struct {
    char key[MAX_KEY_LENGTH];
    ConfigType type;
    union {
        char str_value[MAX_VALUE_LENGTH];
        int int_value;
        bool bool_value;
        float float_value;
    } value;
    bool is_set;
} ConfigItem;

// 配置管理器
typedef struct {
    ConfigItem items[MAX_CONFIG_ITEMS];
    int count;
    char* file_path;
} ConfigManager;

// ==================== 核心函数 ====================

// 创建配置管理器
ConfigManager* config_create() {
    ConfigManager* cm = (ConfigManager*)malloc(sizeof(ConfigManager));
    if (cm) {
        cm->count = 0;
        cm->file_path = NULL;
        memset(cm->items, 0, sizeof(cm->items));
    }
    return cm;
}

// 销毁配置管理器
void config_destroy(ConfigManager* cm) {
    if (cm) {
        if (cm->file_path) free(cm->file_path);
        free(cm);
    }
}

// 查找配置项
static ConfigItem* find_item(ConfigManager* cm, const char* key) {
    for (int i = 0; i < cm->count; i++) {
        if (strcmp(cm->items[i].key, key) == 0) {
            return &cm->items[i];
        }
    }
    return NULL;
}

// 添加字符串配置
bool config_add_string(ConfigManager* cm, const char* key, const char* value) {
    if (!cm || !key || !value) return false;
    if (cm->count >= MAX_CONFIG_ITEMS) return false;
    
    ConfigItem* existing = find_item(cm, key);
    if (existing) {
        strncpy(existing->value.str_value, value, MAX_VALUE_LENGTH - 1);
        existing->type = CONFIG_STRING;
        existing->is_set = true;
        return true;
    }
    
    ConfigItem* item = &cm->items[cm->count++];
    strncpy(item->key, key, MAX_KEY_LENGTH - 1);
    strncpy(item->value.str_value, value, MAX_VALUE_LENGTH - 1);
    item->type = CONFIG_STRING;
    item->is_set = true;
    return true;
}

// 添加整数配置
bool config_add_int(ConfigManager* cm, const char* key, int value) {
    if (!cm || !key) return false;
    if (cm->count >= MAX_CONFIG_ITEMS) return false;
    
    ConfigItem* existing = find_item(cm, key);
    if (existing) {
        existing->value.int_value = value;
        existing->type = CONFIG_INT;
        existing->is_set = true;
        return true;
    }
    
    ConfigItem* item = &cm->items[cm->count++];
    strncpy(item->key, key, MAX_KEY_LENGTH - 1);
    item->value.int_value = value;
    item->type = CONFIG_INT;
    item->is_set = true;
    return true;
}

// 添加布尔配置
bool config_add_bool(ConfigManager* cm, const char* key, bool value) {
    if (!cm || !key) return false;
    if (cm->count >= MAX_CONFIG_ITEMS) return false;
    
    ConfigItem* existing = find_item(cm, key);
    if (existing) {
        existing->value.bool_value = value;
        existing->type = CONFIG_BOOL;
        existing->is_set = true;
        return true;
    }
    
    ConfigItem* item = &cm->items[cm->count++];
    strncpy(item->key, key, MAX_KEY_LENGTH - 1);
    item->value.bool_value = value;
    item->type = CONFIG_BOOL;
    item->is_set = true;
    return true;
}

// 获取字符串配置
const char* config_get_string(ConfigManager* cm, const char* key, const char* default_value) {
    if (!cm || !key) return default_value;
    
    ConfigItem* item = find_item(cm, key);
    if (item && item->type == CONFIG_STRING && item->is_set) {
        return item->value.str_value;
    }
    return default_value;
}

// 获取整数配置
int config_get_int(ConfigManager* cm, const char* key, int default_value) {
    if (!cm || !key) return default_value;
    
    ConfigItem* item = find_item(cm, key);
    if (item && item->type == CONFIG_INT && item->is_set) {
        return item->value.int_value;
    }
    return default_value;
}

// 获取布尔配置
bool config_get_bool(ConfigManager* cm, const char* key, bool default_value) {
    if (!cm || !key) return default_value;
    
    ConfigItem* item = find_item(cm, key);
    if (item && item->type == CONFIG_BOOL && item->is_set) {
        return item->value.bool_value;
    }
    return default_value;
}

// 简单配置加载（简化版 JSON 解析）
bool config_load_file(ConfigManager* cm, const char* file_path) {
    if (!cm || !file_path) return false;
    
    FILE* f = fopen(file_path, "r");
    if (!f) return false;
    
    // 简化实现：读取 key=value 格式
    char line[1024];
    while (fgets(line, sizeof(line), f)) {
        // 跳过注释和空行
        if (line[0] == '#' || line[0] == '\n') continue;
        
        char* eq = strchr(line, '=');
        if (eq) {
            *eq = '\0';
            char* key = line;
            char* value = eq + 1;
            
            // 去除空白
            while (*value == ' ' || *value == '\t') value++;
            char* end = value + strlen(value) - 1;
            while (end > value && (*end == '\n' || *end == '\r' || *end == ' ')) *end-- = '\0';
            
            // 自动推断类型并添加
            if (strcmp(value, "true") == 0 || strcmp(value, "false") == 0) {
                config_add_bool(cm, key, strcmp(value, "true") == 0);
            } else {
                // 尝试解析为整数
                char* endptr;
                long val = strtol(value, &endptr, 10);
                if (*endptr == '\0') {
                    config_add_int(cm, key, (int)val);
                } else {
                    config_add_string(cm, key, value);
                }
            }
        }
    }
    
    fclose(f);
    
    if (cm->file_path) free(cm->file_path);
    cm->file_path = strdup(file_path);
    
    return true;
}

// 保存配置到文件
bool config_save_file(ConfigManager* cm, const char* file_path) {
    if (!cm || !file_path) return false;
    
    FILE* f = fopen(file_path, "w");
    if (!f) return false;
    
    fprintf(f, "# Configuration File\n");
    fprintf(f, "# Generated by Config Manager v1.0\n\n");
    
    for (int i = 0; i < cm->count; i++) {
        ConfigItem* item = &cm->items[i];
        if (!item->is_set) continue;
        
        fprintf(f, "%s = ", item->key);
        switch (item->type) {
            case CONFIG_STRING:
                fprintf(f, "%s\n", item->value.str_value);
                break;
            case CONFIG_INT:
                fprintf(f, "%d\n", item->value.int_value);
                break;
            case CONFIG_BOOL:
                fprintf(f, "%s\n", item->value.bool_value ? "true" : "false");
                break;
            default:
                break;
        }
    }
    
    fclose(f);
    return true;
}

// 打印所有配置（调试用）
void config_print(ConfigManager* cm) {
    if (!cm) return;
    
    printf("=== Configuration (%d items) ===\n", cm->count);
    for (int i = 0; i < cm->count; i++) {
        ConfigItem* item = &cm->items[i];
        if (!item->is_set) continue;
        
        printf("%s = ", item->key);
        switch (item->type) {
            case CONFIG_STRING:
                printf("%s\n", item->value.str_value);
                break;
            case CONFIG_INT:
                printf("%d\n", item->value.int_value);
                break;
            case CONFIG_BOOL:
                printf("%s\n", item->value.bool_value ? "true" : "false");
                break;
            default:
                printf("(unknown)\n");
        }
    }
    printf("=== End ===\n\n");
}

// ==================== 使用示例 ====================

#ifdef CONFIG_DEMO
int main() {
    printf("配置管理器演示 v1.0\n\n");
    
    // 创建配置
    ConfigManager* cm = config_create();
    
    // 添加配置项
    config_add_string(cm, "server.host", "localhost");
    config_add_int(cm, "server.port", 8080);
    config_add_bool(cm, "server.ssl", false);
    config_add_int(cm, "database.pool_size", 10);
    config_add_string(cm, "logging.level", "info");
    
    // 打印配置
    config_print(cm);
    
    // 获取配置
    printf("Server: %s:%d\n", 
           config_get_string(cm, "server.host", "localhost"),
           config_get_int(cm, "server.port", 80));
    
    // 保存配置
    config_save_file(cm, "test_config.conf");
    printf("配置已保存到 test_config.conf\n");
    
    // 从文件加载
    ConfigManager* cm2 = config_create();
    if (config_load_file(cm2, "test_config.conf")) {
        printf("\n从文件加载配置:\n");
        config_print(cm2);
    }
    
    // 清理
    config_destroy(cm);
    config_destroy(cm2);
    
    printf("演示完成!\n");
    return 0;
}
#endif
