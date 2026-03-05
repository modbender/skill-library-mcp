/*
 * Task 5 v2: 真正的易经优化版本
 * 核心：自适应策略 + 多层次剪枝 + 统计感知
 * 编译：gcc -O3 -o task5-benchmark-v2 task5-string-search-v2.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <stdbool.h>

#define DEFAULT_TEXT_SIZE (100 * 1024 * 1024)  // 100MB
#define DEFAULT_PATTERN_SIZE 100
#define DEFAULT_REPETITIONS 30
#define ALPHABET_SIZE 26
#define BLOOM_SIZE 1000000

// ==================== 辅助函数 ====================

// 计算文本重复度（0-1，1 表示完全重复）
double calculate_redundancy(const char *text, int n) {
    int freq[ALPHABET_SIZE] = {0};
    for (int i = 0; i < n && i < 10000; i++) {
        freq[text[i] - 'a']++;
    }
    
    // 计算熵
    double entropy = 0;
    for (int i = 0; i < ALPHABET_SIZE; i++) {
        if (freq[i] > 0) {
            double p = (double)freq[i] / 10000;
            entropy -= p * log2(p);
        }
    }
    
    // 归一化到 0-1（最大熵 = log2(26) ≈ 4.7）
    double max_entropy = log2(ALPHABET_SIZE);
    return 1.0 - (entropy / max_entropy);
}

// 计算字符频率，返回最罕见字符的位置
int find_rarest_char_pos(const char *pattern, int m, const int *text_freq) {
    int rarest_pos = 0;
    int min_freq = text_freq[pattern[0] - 'a'];
    
    for (int i = 1; i < m; i++) {
        int freq = text_freq[pattern[i] - 'a'];
        if (freq < min_freq) {
            min_freq = freq;
            rarest_pos = i;
        }
    }
    
    return rarest_pos;
}

// ==================== 算法实现 ====================

// 朴素匹配
int naive_search(const char *text, int n, const char *pattern, int m) {
    int count = 0;
    for (int i = 0; i <= n - m; i++) {
        bool match = true;
        for (int j = 0; j < m; j++) {
            if (text[i + j] != pattern[j]) {
                match = false;
                break;
            }
        }
        if (match) count++;
    }
    return count;
}

// KMP 算法
void compute_lps(int *lps, const char *pattern, int m) {
    int len = 0;
    lps[0] = 0;
    int i = 1;
    while (i < m) {
        if (pattern[i] == pattern[len]) {
            len++;
            lps[i] = len;
            i++;
        } else {
            if (len != 0) len = lps[len - 1];
            else { lps[i] = 0; i++; }
        }
    }
}

int kmp_search(const char *text, int n, const char *pattern, int m) {
    int *lps = malloc(m * sizeof(int));
    compute_lps(lps, pattern, m);
    
    int count = 0, i = 0, j = 0;
    while (i < n) {
        if (pattern[j] == text[i]) { i++; j++; }
        if (j == m) { count++; j = lps[j - 1]; }
        else if (i < n && pattern[j] != text[i]) {
            if (j != 0) j = lps[j - 1];
            else i++;
        }
    }
    free(lps);
    return count;
}

// 易经优化 v3: 真正的简易 + 变易（光光的洞察）
int yijing_v3_search(const char *text, int n, const char *pattern, int m) {
    // Step 1: 分析文本特征（采样 10KB）
    int sample_size = (n < 10000) ? n : 10000;
    int text_freq[ALPHABET_SIZE] = {0};
    for (int i = 0; i < sample_size; i++) {
        text_freq[text[i] - 'a']++;
    }
    
    // Step 2: 计算重复度
    double redundancy = calculate_redundancy(text, n);
    
    // Step 3: 易经决策 - 高重复=简单场景用朴素，低重复=复杂场景用优化
    if (redundancy > 0.3) {
        // 高重复 = 简单场景 → 简易原则 → 朴素匹配
        // "大道至简" - 简单场景用简单方法
        return naive_search(text, n, pattern, m);
    } else {
        // 低重复 = 复杂场景 → 变易原则 → 统计优化
        // "穷则变，变则通" - 复杂场景需要变通
        int rarest_pos = find_rarest_char_pos(pattern, m, text_freq);
        
        int count = 0;
        for (int i = 0; i <= n - m; i++) {
            // 从最罕见字符开始（最大化提前排除）
            if (text[i + rarest_pos] != pattern[rarest_pos])
                continue;
            
            // 完整匹配
            bool match = true;
            for (int j = 0; j < m; j++) {
                if (text[i + j] != pattern[j]) {
                    match = false;
                    break;
                }
            }
            if (match) count++;
        }
        return count;
    }
}

// ==================== 基准测试 ====================

long long get_time_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

char* generate_random_text(int size) {
    char *text = malloc(size);
    for (int i = 0; i < size; i++)
        text[i] = 'a' + (rand() % ALPHABET_SIZE);
    return text;
}

char* generate_high_redundancy_text(int size) {
    char *text = malloc(size);
    // 生成高重复文本（只有 5 个字符）
    for (int i = 0; i < size; i++)
        text[i] = 'a' + (rand() % 5);
    return text;
}

char* generate_pattern(const char *text, int text_size, int pattern_size) {
    char *pattern = malloc(pattern_size + 1);
    int start = rand() % (text_size - pattern_size);
    strncpy(pattern, text + start, pattern_size);
    pattern[pattern_size] = '\0';
    return pattern;
}

void run_experiment(int text_size, int pattern_size, int repetitions, bool high_redundancy) {
    printf("\n============================================================\n");
    printf("实验配置：文本=%d MB, 模式串=%d, 重复=%d, 文本类型=%s\n",
           text_size / (1024*1024), pattern_size, repetitions,
           high_redundancy ? "高重复" : "随机");
    printf("============================================================\n");
    
    srand(42);
    printf("生成文本... ");
    char *text = high_redundancy ? 
        generate_high_redundancy_text(text_size) : 
        generate_random_text(text_size);
    printf("完成（重复度=%.2f）\n", calculate_redundancy(text, text_size));
    
    char *pattern = generate_pattern(text, text_size, pattern_size);
    
    typedef int (*SearchFunc)(const char*, int, const char*, int);
    const char *names[] = {"naive", "kmp", "yijing_v2"};
    SearchFunc methods[] = {naive_search, kmp_search, yijing_v3_search};
    int num_methods = 3;
    
    double **results = malloc(num_methods * sizeof(double*));
    for (int i = 0; i < num_methods; i++)
        results[i] = malloc(repetitions * sizeof(double));
    
    srand(42);
    int total = num_methods * repetitions;
    int *seq = malloc(total * sizeof(int));
    for (int i = 0; i < num_methods; i++)
        for (int j = 0; j < repetitions; j++)
            seq[i * repetitions + j] = i;
    
    for (int i = total - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int tmp = seq[i]; seq[i] = seq[j]; seq[j] = tmp;
    }
    
    int *counts = calloc(num_methods, sizeof(int));
    printf("\n开始测试...\n");
    
    for (int i = 0; i < total; i++) {
        int idx = seq[i];
        if ((i + 1) % 10 == 0)
            printf("进度：%d/%d (%.1f%%)\n", i + 1, total, (i + 1) * 100.0 / total);
        
        long long start = get_time_ns();
        methods[idx](text, text_size, pattern, pattern_size);
        long long end = get_time_ns();
        
        results[idx][counts[idx]++] = (end - start) / 1000000.0;
    }
    
    // 验证
    int ref = naive_search(text, text_size, pattern, pattern_size);
    int kmp_c = kmp_search(text, text_size, pattern, pattern_size);
    int yij_c = yijing_v3_search(text, text_size, pattern, pattern_size);
    printf("\n验证：naive=%d, kmp=%d, yijing=%d %s\n", 
           ref, kmp_c, yij_c, (ref == kmp_c && ref == yij_c) ? "✅" : "⚠️");
    
    // 统计
    printf("\n============================================================\n");
    printf("结果\n");
    printf("============================================================\n");
    
    for (int i = 0; i < num_methods; i++) {
        double sum = 0, min = 1e9, max = 0;
        for (int j = 0; j < repetitions; j++) {
            sum += results[i][j];
            if (results[i][j] < min) min = results[i][j];
            if (results[i][j] > max) max = results[i][j];
        }
        double mean = sum / repetitions;
        printf("%s: %.3f ms [%.3f, %.3f]\n", names[i], mean, min, max);
    }
    
    // 保存
    char filename[256];
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    snprintf(filename, sizeof(filename), "results/task5_v2_%s_%04d-%02d-%02d_%02d-%02d-%02d.csv",
             high_redundancy ? "high_red" : "random",
             t->tm_year + 1900, t->tm_mon + 1, t->tm_mday,
             t->tm_hour, t->tm_min, t->tm_sec);
    
    FILE *f = fopen(filename, "w");
    if (f) {
        fprintf(f, "method,run_number,elapsed_ms\n");
        for (int i = 0; i < num_methods; i++)
            for (int j = 0; j < repetitions; j++)
                fprintf(f, "%s,%d,%.6f\n", names[i], j + 1, results[i][j]);
        fclose(f);
        printf("\n已保存：%s\n", filename);
    }
    
    for (int i = 0; i < num_methods; i++) free(results[i]);
    free(results); free(seq); free(counts);
    free(text); free(pattern);
}

int main(int argc, char *argv[]) {
    int text_size = DEFAULT_TEXT_SIZE;
    int pattern_size = DEFAULT_PATTERN_SIZE;
    int repetitions = DEFAULT_REPETITIONS;
    bool high_redundancy = false;
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--size") == 0 && i + 1 < argc)
            text_size = atoi(argv[++i]);
        else if (strcmp(argv[i], "--pattern") == 0 && i + 1 < argc)
            pattern_size = atoi(argv[++i]);
        else if (strcmp(argv[i], "--redundancy") == 0 && i + 1 < argc)
            high_redundancy = (atoi(argv[++i]) > 0);
        else if (strcmp(argv[i], "--repetitions") == 0 && i + 1 < argc)
            repetitions = atoi(argv[++i]);
    }
    
    printf("字符串搜索 - 易经优化 v3（真正的简易 + 变易）\n");
    run_experiment(text_size, pattern_size, repetitions, high_redundancy);
    printf("\n完成！\n");
    return 0;
}
