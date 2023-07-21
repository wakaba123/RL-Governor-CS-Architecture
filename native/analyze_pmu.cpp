#include <asm/unistd.h>
#include <linux/perf_event.h>
#include <math.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <algorithm>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
#include <thread>
#include <vector>
#include "execute.h"
#include "fps.h"

std::vector<int> little_freq;
std::vector<int> big_freq;

std::string get_all_freq_list(std::string file_name) {
    std::ifstream file(file_name);
    if (!file.is_open()) {
        std::cerr << "Failed to open file" << std::endl;
        return "";
    }

    std::string line;
    std::getline(file, line);

    file.close();
    return line;
}

// 定义性能事件类型
enum PerfEventType {
    TASK_CLOCK = PERF_TYPE_SOFTWARE,
    INSTRUCTIONS = PERF_TYPE_HARDWARE,
};

// 获取指定PID的性能事件计数器值
void getEventCounter(pid_t pid, PerfEventType eventType, long long& counter) {
    // 创建 perf_event_attr 结构体并设置属性
    struct perf_event_attr pe = {};
    std::memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.type = eventType;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = eventType == INSTRUCTIONS ? PERF_COUNT_HW_INSTRUCTIONS : PERF_COUNT_SW_TASK_CLOCK;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    // 创建 perf_event_open 的文件描述符
    int fd = syscall(__NR_perf_event_open, &pe, pid, -1, -1, 0);
    if (fd == -1) {
        std::perror("perf_event_open");
        return;
    }

    // 启动事件计数
    ioctl(fd, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);

    // 停止事件计数
    sleep(1);

    // 读取事件计数器的值
    read(fd, &counter, sizeof(long long));

    // 关闭文件描述符
    close(fd);
}

int set_freq(int big_freq, int little_freq) {
    const char* big_cpu = "/sys/devices/system/cpu/cpufreq/policy4/scaling_setspeed";
    const char* little_cpu = "/sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed";

    FILE* file_big = fopen(big_cpu, "w");
    FILE* file_little = fopen(little_cpu, "w");

    if (file_big == NULL || file_little == NULL) {
        printf("Failed to open file: %s or %s \n", big_cpu, little_cpu);
        return -1;
    }

    fprintf(file_big, "%d", big_freq);
    fprintf(file_little, "%d", little_freq);

    fclose(file_big);
    fclose(file_little);

    // printf("setting freq to:  %d, %d\n", big_freq, little_freq);
    return 0;
}

int set_governor(std::string target_governor) {
    const char* big_cpu = "/sys/devices/system/cpu/cpufreq/policy4/scaling_governor";
    const char* little_cpu = "/sys/devices/system/cpu/cpufreq/policy0/scaling_governor";

    FILE* file_big = fopen(big_cpu, "w");
    FILE* file_little = fopen(little_cpu, "w");
    if (file_big == NULL || file_little == NULL) {
        printf("Failed to open file: %s or %s \n", big_cpu, little_cpu);
        return -1;
    }

    fprintf(file_big, "%s", target_governor.c_str());
    fprintf(file_little, "%s", target_governor.c_str());

    fclose(file_big);
    fclose(file_little);

    return 0;
}

void output_max_min_avg_var(std::vector<int>& numbers) {
    int max = *std::max_element(numbers.begin(), numbers.end());

    // 最小值
    int min = *std::min_element(numbers.begin(), numbers.end());

    // 平均值
    double sum = 0.0;
    for (int num : numbers) {
        sum += num;
    }
    int average = sum / numbers.size();

    // 方差
    int variance = 0;
    for (int num : numbers) {
        variance += pow(num - average, 2);
    }

    variance /= numbers.size();

    std::cout << max << ',' << min << ',' << average << ',' << variance << std::endl;
}

int set_cpu_mask(pid_t pid, int from, int end) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);  // 初始化 CPU 集合

    for (int i = from; i <= end; i++) {
        CPU_SET(i, &cpuset);  // 将大集群中的核心添加到集合中
    }

    if (sched_setaffinity(pid, sizeof(cpuset), &cpuset) == -1) {
        perror("sched_setaffinity");
        return 1;
    }
    return 0;
}

int set_cpu_mask_big(pid_t pid) {
    return set_cpu_mask(pid, 4, 7);
}

int set_cpu_mask_little(pid_t pid) {
    return set_cpu_mask(pid, 0, 3);
}

int set_cpu_mask_all(pid_t pid) {
    return set_cpu_mask(pid, 0, 7);
}

std::vector<int> get_pid_list(std::string package_name) {
    std::string str = execute("pidof " + package_name);
    std::string pid1 = str.substr(0, str.length() - 1);
    str = execute("ps -T -p " + pid1 + " | grep RenderThread");
    std::istringstream iss(str);
    std::vector<std::string> tokens{std::istream_iterator<std::string>{iss},
                                    std::istream_iterator<std::string>{}};

    std::string pid2 = tokens[2];
    str = execute("pidof surfaceflinger");
    std::string pid3 = str.substr(0, str.length() - 1);
    return {atoi(pid1.c_str()), atoi(pid2.c_str()), atoi(pid3.c_str())};
}

int main() {
    std::string package_name = "com.smile.gifmaker";
    std::string view_name = "com.smile.gifmaker/com.yxcorp.gifshow.HomeActivity#0";

    // get available frequencies
    const std::string little_file = "/sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies";
    const std::string big_file = "/sys/devices/system/cpu/cpufreq/policy4/scaling_available_frequencies";

    std::string line1 = get_all_freq_list(little_file);
    std::string line2 = get_all_freq_list(big_file);

    std::istringstream iss(line1);
    int value;
    while (iss >> value) {
        little_freq.push_back(value);
    }

    std::istringstream iss2(line2);
    while (iss2 >> value) {
        big_freq.push_back(value);
    }

    // start fps thread
    FPSGet* fps = new FPSGet(view_name);
    fps->start();
    sleep(1);

    // init some environment
    std::vector<int> pid_list = get_pid_list(package_name);
    // for (auto& pid : pid_list) {
    //     std::cout << pid << ',';
    // }
    // std::cout << std::endl;

    set_governor("userspace");
    for (int i = 0; i < 3; i++) {
        set_cpu_mask_all(pid_list[i]);
    }

    int position_bit_arr[8][3] = {{0, 0, 0}, {0, 0, 1}, {0, 1, 0}, {0, 1, 1}, {1, 0, 0}, {1, 0, 1}, {1, 1, 0}, {1, 1, 1}};

    // start traverse
    for (int b = 0; b < 8; b++) {
        for (int k = 0; k < 3; k++) {
            if (position_bit_arr[b][k] == 1) {
                if (set_cpu_mask_big(pid_list[k]) == 0) {
                    std::cout << "big\t";
                } else {
                    std::cout << "switch " << pid_list[k] << " to big failed" << std::endl;
                }
            } else {
                if (set_cpu_mask_little(pid_list[k]) == 0) {
                    std::cout << "little\t";
                } else {
                    std::cout << "switch " << pid_list[k] << " to little failed" << std::endl;
                }
            }
        }
        std::cout << std::endl;

        std::vector<std::vector<int>> final_tc(3, std::vector<int>(0));    // gifmaker,  renderthread, surfaceflinger
        std::vector<std::vector<int>> final_inst(3, std::vector<int>(0));  // gifmaker,  renderthread, surfaceflinger

        for (int i = little_freq.size() - 12; i >= 1; i--) {
            for (int j = big_freq.size() - 15; j >= 1; j--) {
                set_freq(big_freq[j], little_freq[i]);

                //  conduct 7 tests
                for (int eposide = 0; eposide < 1; eposide++) {
                    std::vector<long long> taskClockList(pid_list.size());
                    std::vector<long long> instructionsList(pid_list.size());

                    std::vector<std::thread> threads;

                    // 创建线程获取每个PID的计数器值
                    for (size_t i = 0; i < pid_list.size(); ++i) {
                        threads.emplace_back([&taskClockList, &instructionsList, i, pid_list]() {
                            getEventCounter(pid_list[i], TASK_CLOCK, taskClockList[i]);
                        });
                        threads.emplace_back([&taskClockList, &instructionsList, i, pid_list]() {
                            getEventCounter(pid_list[i], INSTRUCTIONS, instructionsList[i]);
                        });
                    }

                    // 等待所有线程完成
                    for (auto& thread : threads) {
                        thread.join();
                    }
                    int cur_fps = fps->getFPS();
                    //             std::cout << "cur_fps is " << cur_fps << std::endl;

                    if (cur_fps >= 59) {
                        // collect all qualified pmu data
                        for (size_t i = 0; i < pid_list.size(); i++) {
                            final_tc[i].push_back(taskClockList[i]);
                            final_inst[i].push_back(instructionsList[i]);
                            //                        std::cout << "PID: " << pid_list[i] << std::endl;
                            //                       std::cout << "Task Clock: " << taskClockList[i] << std::endl;
                            //                      std::cout << "Instructions: " << instructionsList[i] << std::endl;
                        }
                    } else {
                        sleep(1);
                        continue;
                    }
                }
            }
        }

        std::cout << "max" << ',' << "min" << ',' << "average" << ',' << "variance" << std::endl;

        std::cout << "gifmaker_tc:";
        output_max_min_avg_var(final_tc[0]);

        std::cout << "gifmaker_inst:";
        output_max_min_avg_var(final_inst[0]);

        std::cout << "render_tc:";
        output_max_min_avg_var(final_tc[1]);

        std::cout << "render_inst:";
        output_max_min_avg_var(final_inst[1]);

        std::cout << "surfaceflinger_tc:";
        output_max_min_avg_var(final_tc[2]);

        std::cout << "surfaceflinger_inst:";
        output_max_min_avg_var(final_inst[2]);
    }

    /*
    // save to file
    std::string filename = "data.csv";
    std::ofstream file(filename);

    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        return 1;
    }

    std::cout << final_tc[0].size() << std::endl;

    file << "gifmaker_tc" << ',' << "gifmaker_inst" << ',' << "render_tc" << ',' << "render_inst" << ',' << "surfaceflinger_tc" << ',' << "surfaceflinger_inst" << '\n';

    for (int i = 0; i < final_tc[0].size(); i++) {
        file << final_tc[0][i] << ',' << final_inst[0][i] << ',' << final_tc[1][i] << ',' << final_inst[1][i] << ',' << final_tc[2][i] << ',' << final_inst[2][i] << '\n';
    }

    file.close();

    std::cout << "Data saved to " << filename << std::endl;
    */

    return 0;
}
