#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <iostream>
#include "fps.h"

void red() {
    printf("\033[1;31m");
}
void yellow() {
    printf("\033[1;33m");
}
void reset() {
    printf("\033[0m");
}

typedef struct {
    int user;
    int nice;
    int system;
    int idle;
    int iowait;
    int irq;
    int softirq;
} CPUData;

typedef struct {
    CPUData initial[MAX_CPU_COUNT];
    CPUData current[MAX_CPU_COUNT];
} CPUControl;

void parse_cpu_data(const char* line, CPUData* data) {
    sscanf(line, "cpu %*d %d %d %d %d %d %d %d", &data->user, &data->nice, &data->system, &data->idle, &data->iowait, &data->irq, &data->softirq);
}

void initialize_cpu_control(CPUControl* control) {
    // system("adb shell cat /proc/stat > stat.txt");
    FILE* file = fopen("/proc/stat", "r");
    if (file == NULL) {
        printf("Failed to open stat.txt\n");
        return;
    }

    char line[MAX_LINE_LENGTH];
    fgets(line, MAX_LINE_LENGTH, file);  // Skip the first line

    for (int i = 0; i < MAX_CPU_COUNT; i++) {
        fgets(line, MAX_LINE_LENGTH, file);
        parse_cpu_data(line, &control->initial[i]);
    }

    fclose(file);
}

void update_cpu_utilization(CPUControl* control, double* utilization) {
    // system("adb shell cat /proc/stat > stat2.txt");
    FILE* file = fopen("/proc/stat", "r");
    if (file == NULL) {
        printf("Failed to open stat.txt\n");
        return;
    }

    char line[MAX_LINE_LENGTH];
    fgets(line, MAX_LINE_LENGTH, file);  // Skip the first line

    for (int i = 0; i < MAX_CPU_COUNT; i++) {
        fgets(line, MAX_LINE_LENGTH, file);
        parse_cpu_data(line, &control->current[i]);

        CPUData* initial = &control->initial[i];
        CPUData* current = &control->current[i];

        int curr_time = current->user + current->nice + current->system + current->idle + current->iowait + current->irq + current->softirq;
        int initial_time = initial->user + initial->nice + initial->system + initial->idle + initial->iowait + initial->irq + initial->softirq;
        int interval = curr_time - initial_time;

        double cpu_util = ((current->user + current->system + current->nice) - (initial->user + initial->system + initial->nice)) / (double)interval;
        utilization[i] = cpu_util;

        // Update initial data
        memcpy(initial, current, sizeof(CPUData));
    }

    fclose(file);
}

int get_gpu_freq() {
    const char* filename = "/sys/class/kgsl/kgsl-3d0/devfreq/cur_freq";
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Failed to open file: %s\n", filename);
        return -1;
    }

    int freq;
    if (fscanf(file, "%d", &freq) != 1) {
        printf("Failed to read frequency from file: %s\n", filename);
        fclose(file);
        return -1;
    }
    fclose(file);
    return freq;
}

float get_gpu_util() {
    const char* filename = "/sys/class/kgsl/kgsl-3d0/gpubusy";
    FILE* fp = fopen(filename, "r");
    int a, b;
    fscanf(fp, "%d%d", &a, &b);
    // printf("here in gpu_util %d, %d", a, b);
    if (a == 0 || b == 0) {
        return 0.0;
    }
    return (float)a / b;
}

int get_sbig_cpu_freq() {
    const char* filename = "/sys/devices/system/cpu/cpufreq/policy7/scaling_cur_freq";
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Failed to open file: %s\n", filename);
        return -1;
    }

    int freq;
    if (fscanf(file, "%d", &freq) != 1) {
        printf("Failed to read frequency from file: %s\n", filename);
        fclose(file);
        return -1;
    }

    fclose(file);
    return freq;
}

int get_big_cpu_freq() {
    const char* filename = "/sys/devices/system/cpu/cpufreq/policy4/scaling_cur_freq";
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Failed to open file: %s\n", filename);
        return -1;
    }

    int freq;
    if (fscanf(file, "%d", &freq) != 1) {
        printf("Failed to read frequency from file: %s\n", filename);
        fclose(file);
        return -1;
    }

    fclose(file);
    return freq;
}

int get_little_cpu_freq() {
    const char* filename = "/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq";
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Failed to open file: %s\n", filename);
        return -1;
    }

    int freq;
    if (fscanf(file, "%d", &freq) != 1) {
        printf("Failed to read frequency from file: %s\n", filename);
        fclose(file);
        return -1;
    }

    fclose(file);

    // printf("Frequency: %d\n", freq);
    return freq;
}

int get_swap() {
    const char* filename = "/proc/meminfo";
    const char* pattern = "MemAvailable:";
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("Failed to open file: %s\n", filename);
        return -1;
    }

    char line[256];
    int mem = -1;

    while (fgets(line, sizeof(line), file)) {
        if (strstr(line, pattern) == line) {
            char* value = strtok(line, " \t");
            value = strtok(NULL, " \t");
            mem = atoi(value);
            break;
        }
    }

    fclose(file);

    return mem;
}

int init_msm_performance() {
    FILE* fp;

    // 打開第一個檔案，將指令輸出到其中
    fp = fopen("/sys/module/msm_performance/parameters/cpu_max_freq", "w");
    if (fp == NULL) {
        printf("無法打開檔案。\n");
        return 1;
    }
    fprintf(fp, "0:1785600 1:1785600 2:1785600 3:1785600 4:2419200 5:2419200 6:2419200 7:2841600");
    fclose(fp);

    // 打開第二個檔案，將指令輸出到其中
    fp = fopen("/sys/module/msm_performance/parameters/cpu_min_freq", "w");
    if (fp == NULL) {
        printf("無法打開檔案。\n");
        return 1;
    }
    fprintf(fp, "0:300000 1:300000 2:300000 3:300000 4:710400 5:710400 6:710400 7:825600");
    fclose(fp);

    return 0;
}

int check_freq(int sbig_freq, int big_freq, int little_freq) {
    const char* super_big_cpu = "/sys/devices/system/cpu/cpufreq/policy7/scaling_max_freq";
    const char* big_cpu = "/sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq";
    const char* little_cpu = "/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq";
    int real_sbig_freq = 0, real_big_freq = 0, real_little_freq = 0;

    FILE* file_super_big = fopen(super_big_cpu, "r");
    FILE* file_big = fopen(big_cpu, "r");
    FILE* file_little = fopen(little_cpu, "r");

    if (file_big == NULL || file_little == NULL || file_super_big == NULL) {
        printf("Failed to open file: %s or %s or %s\n", super_big_cpu, big_cpu, little_cpu);
        return -1;
    }

    fscanf(file_super_big, "%d", &real_sbig_freq);
    fscanf(file_big, "%d", &real_big_freq);
    fscanf(file_little, "%d", &real_little_freq);

    if (real_little_freq != little_freq || real_big_freq != big_freq || real_sbig_freq != sbig_freq) {
        printf("Check Frequency Setting Failed");
        printf("Expected freq: %d, %d, %d, Real freq: %d, %d , %d", sbig_freq, big_freq, little_freq, real_sbig_freq, real_big_freq, real_little_freq);
        return -1;
    }

    fclose(file_super_big);
    fclose(file_big);
    fclose(file_little);

    return 0;
}

int set_freq(int sbig_freq, int big_freq, int little_freq) {
    const char* super_big_cpu = "/sys/devices/system/cpu/cpufreq/policy7/scaling_max_freq";
    const char* big_cpu = "/sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq";
    const char* little_cpu = "/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq";

    FILE* file_super_big = fopen(super_big_cpu, "w");
    FILE* file_big = fopen(big_cpu, "w");
    FILE* file_little = fopen(little_cpu, "w");

    if (file_big == NULL || file_little == NULL || file_super_big == NULL) {
        printf("Failed to open file: %s or %s \n", big_cpu, little_cpu);
        return -1;
    }

    fprintf(file_super_big, "%d", sbig_freq);
    fprintf(file_big, "%d", big_freq);
    fprintf(file_little, "%d", little_freq);

    fclose(file_super_big);
    fclose(file_big);
    fclose(file_little);

    printf("freq : %d, %d, %d\n", sbig_freq, big_freq, little_freq);
    return 0;
}

int main(int argc, char* argv[]) {
    int server_fd, client_fd, valread;
    struct sockaddr_in server_addr;
    char buffer[1024] = {0};
    if (argc != 2) {
        printf("usage: ./server <view_name>\n");
    }
    std::string view = argv[1];

    // 初始化
    CPUControl control;
    initialize_cpu_control(&control);
    double utilization[MAX_CPU_COUNT];

    FPSGet* fps = new FPSGet(view.c_str());
    fps->start();

    // 创建Socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // 配置服务器地址
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    // 绑定Socket到端口
    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    // 监听连接请求
    if (listen(server_fd, 3) < 0) {
        perror("listen failed");
        exit(EXIT_FAILURE);
    }

    printf("服务端已启动，等待客户端连接...\n");

    // 接受客户端连接请求
    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_addr_len = sizeof(client_addr);

        if ((client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_addr_len)) < 0) {
            perror("accept failed");
            exit(EXIT_FAILURE);
        }

        memset(buffer, 0, sizeof(buffer));

        if (read(client_fd, buffer, sizeof(buffer)) < 0) {
            std::cerr << "Failed to read from socket\n";
            return 1;
        }
        printf("客户端已连接：%s\n", inet_ntoa(server_addr.sin_addr));
        printf("客户端的信息为:%s\n", buffer);

        int flag = 0;
        int sbig_freq, big_freq, little_freq;
        sscanf(buffer, "%d %d %d %d", &flag, &sbig_freq, &big_freq, &little_freq);

        if (flag == 0) {  // 本次请求为调频请求
            red();
            printf("flag 为 0, 是调频请求\n");
            reset();
            printf("超大核调节至 %d 大核调节至 %d, 小核调节至 %d\n", sbig_freq, big_freq, little_freq);

            // init_msm_performance();
            int result = set_freq(sbig_freq, big_freq, little_freq);

            std::string data = std::to_string(result);
            if(check_freq(sbig_freq, big_freq, little_freq) == -1){
                // init_msm_performance();
                result = set_freq(sbig_freq, big_freq, little_freq);
                printf("check failed\n");
                send(client_fd, data.c_str(), data.length(), 0);
                continue;
            }
            printf("check success\n");

            send(client_fd, data.c_str(), data.length(), 0);

        } else if (flag == 1) {  // 本次请求是获取信息的请求
            red();
            printf("flag 为 1, 是获取信息请求\n");
            reset();
            int sbig_freq = get_sbig_cpu_freq();
            int big_freq = get_big_cpu_freq();
            int little_freq = get_little_cpu_freq();
            int cur_fps = fps->getFPS();
            int mem = get_swap();

            update_cpu_utilization(&control, utilization);

            double little_util = 0.0;
            double big_util = 0.0;

            for (int i = 0; i < MAX_CPU_COUNT; i++) {
                if (i < 4) {
                    little_util += utilization[i];
                } else {
                    big_util += utilization[i];
                }
            }

            std::string data = std::to_string(sbig_freq) + " " +
                               std::to_string(big_freq) + " " +
                               std::to_string(little_freq) + " " +
                               std::to_string(cur_fps) + " " +
                               std::to_string(mem) + " " +
                               std::to_string(little_util) + " " +
                               std::to_string(big_util);

            send(client_fd, data.c_str(), data.length(), 0);

        } else if (flag == 2) {
            red();
            printf("flag 为 2, 检查server是否正常运行的请求\n");
            reset();
            send(client_fd, view.c_str(), view.length(), 0);

        } else if (flag == 3) {
            red();
            printf("flag 为 3, 让server自然关闭的请求\n");
            reset();
            std::string data = "0";
            send(client_fd, data.c_str(), data.length(), 0);
            close(client_fd);
            break;
        }

        close(client_fd);
    }

    // 关闭Socket

    printf("server正在关闭.....");
    close(server_fd);
    return 0;
}
