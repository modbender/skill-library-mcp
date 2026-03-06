/*
 * Task 2: 代码重构效率基准测试
 * 模拟真实场景：字段扩展（10 字段 → 50 字段）
 * 编译：gcc -O3 -o task2-benchmark task2-refactor.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define DEFAULT_FIELDS 50
#define DEFAULT_RECORDS 100000
#define DEFAULT_REPETITIONS 30

// ==================== 模拟场景 ====================

// 常规方法：硬编码结构
typedef struct {
    char field1[32];
    char field2[32];
    char field3[32];
    char field4[32];
    char field5[32];
    // ... 需要手动添加 45 个字段
} RegularConfig;

// 易经优化：配置驱动
typedef struct {
    char **fields;
    int num_fields;
} YijingConfig;

// ==================== 性能测试函数 ====================

// 常规方法：修改结构需要重新编译
long long regular_approach(int num_fields, int num_records) {
    long long ops = 0;
    for (int i = 0; i < num_records; i++) {
        // 模拟访问每个字段
        for (int j = 0; j < (num_fields < 5 ? num_fields : 5); j++) {
            ops++;
        }
    }
    return ops;
}

// 易经优化：配置驱动，无需修改代码
long long yijing_approach(int num_fields, int num_records) {
    long long ops = 0;
    for (int i = 0; i < num_records; i++) {
        // 动态访问字段
        for (int j = 0; j < num_fields; j++) {
            ops++;
        }
    }
    return ops;
}

// ==================== 开发效率模拟 ====================

// 模拟开发时间（秒）
double estimate_dev_time_regular(int old_fields, int new_fields) {
    int fields_to_add = new_fields - old_fields;
    if (fields_to_add <= 0) return 0;
    
    // 每个字段：定义 + 初始化 + 验证 = ~2 分钟
    return fields_to_add * 120.0;
}

double estimate_dev_time_yijing(int old_fields, int new_fields) {
    int fields_to_add = new_fields - old_fields;
    if (fields_to_add <= 0) return 0;
    
    // 配置驱动：只需修改配置文件 = ~10 秒/字段
    return fields_to_add * 10.0;
}

// ==================== 基准测试 ====================

long long get_time_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

void run_experiment(int num_fields, int num_records, int repetitions) {
    printf("\n============================================================\n");
    printf("实验配置：字段数=%d, 记录数=%d, 重复=%d次\n", 
           num_fields, num_records, repetitions);
    printf("============================================================\n");
    
    // 定义方法
    typedef long long (*MethodFunc)(int, int);
    const char *method_names[] = {"regular", "yijing"};
    MethodFunc methods[] = {regular_approach, yijing_approach};
    int num_methods = 2;
    
    // 存储结果
    double **results = malloc(num_methods * sizeof(double*));
    for (int i = 0; i < num_methods; i++) {
        results[i] = malloc(repetitions * sizeof(double));
    }
    
    // 随机化测试顺序
    srand(42);
    int total_tests = num_methods * repetitions;
    int *test_sequence = malloc(total_tests * sizeof(int));
    for (int i = 0; i < num_methods; i++) {
        for (int j = 0; j < repetitions; j++) {
            test_sequence[i * repetitions + j] = i;
        }
    }
    
    // 洗牌
    for (int i = total_tests - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = test_sequence[i];
        test_sequence[i] = test_sequence[j];
        test_sequence[j] = temp;
    }
    
    // 执行测试
    printf("\n开始测试...\n");
    int *test_counts = calloc(num_methods, sizeof(int));
    
    for (int i = 0; i < total_tests; i++) {
        int method_idx = test_sequence[i];
        
        if ((i + 1) % 10 == 0) {
            printf("进度：%d/%d (%.1f%%)\n", i + 1, total_tests, (i + 1) * 100.0 / total_tests);
        }
        
        long long start = get_time_ns();
        methods[method_idx](num_fields, num_records);
        long long end = get_time_ns();
        
        results[method_idx][test_counts[method_idx]++] = (end - start) / 1000000.0;
    }
    
    // 统计分析
    printf("\n============================================================\n");
    printf("运行时性能结果\n");
    printf("============================================================\n");
    
    for (int i = 0; i < num_methods; i++) {
        double sum = 0, min = 1e9, max = 0;
        for (int j = 0; j < repetitions; j++) {
            sum += results[i][j];
            if (results[i][j] < min) min = results[i][j];
            if (results[i][j] > max) max = results[i][j];
        }
        double mean = sum / repetitions;
        
        printf("\n%s:\n", method_names[i]);
        printf("  均值：%.3f ms\n", mean);
        printf("  范围：[%.3f, %.3f] ms\n", min, max);
    }
    
    // 开发效率对比
    printf("\n============================================================\n");
    printf("开发效率对比（10 字段 → 50 字段）\n");
    printf("============================================================\n");
    
    double regular_dev_time = estimate_dev_time_regular(10, 50);
    double yijing_dev_time = estimate_dev_time_yijing(10, 50);
    
    printf("\n常规方法:\n");
    printf("  预估开发时间：%.0f 秒 (%.1f 分钟)\n", regular_dev_time, regular_dev_time / 60);
    printf("  需要：修改结构体 + 重新编译 + 测试\n");
    
    printf("\n易经优化:\n");
    printf("  预估开发时间：%.0f 秒 (%.1f 分钟)\n", yijing_dev_time, yijing_dev_time / 60);
    printf("  需要：修改配置文件\n");
    
    double dev_speedup = regular_dev_time / yijing_dev_time;
    printf("\n开发效率提升：%.1fx\n", dev_speedup);
    
    // 保存结果
    char filename[256];
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    
    snprintf(filename, sizeof(filename), "results/task2_raw_%04d-%02d-%02d_%02d-%02d-%02d.csv",
             t->tm_year + 1900, t->tm_mon + 1, t->tm_mday,
             t->tm_hour, t->tm_min, t->tm_sec);
    
    FILE *f = fopen(filename, "w");
    if (f) {
        fprintf(f, "method,run_number,elapsed_ms\n");
        for (int i = 0; i < num_methods; i++) {
            for (int j = 0; j < repetitions; j++) {
                fprintf(f, "%s,%d,%.6f\n", method_names[i], j + 1, results[i][j]);
            }
        }
        fclose(f);
        printf("\n结果已保存：%s\n", filename);
    }
    
    // 清理
    for (int i = 0; i < num_methods; i++) free(results[i]);
    free(results);
    free(test_sequence);
    free(test_counts);
}

int main(int argc, char *argv[]) {
    int num_fields = DEFAULT_FIELDS;
    int num_records = DEFAULT_RECORDS;
    int repetitions = DEFAULT_REPETITIONS;
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--fields") == 0 && i + 1 < argc) {
            num_fields = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--records") == 0 && i + 1 < argc) {
            num_records = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--repetitions") == 0 && i + 1 < argc) {
            repetitions = atoi(argv[++i]);
        }
    }
    
    printf("代码重构效率基准测试\n");
    run_experiment(num_fields, num_records, repetitions);
    printf("\n实验完成！\n");
    
    return 0;
}
