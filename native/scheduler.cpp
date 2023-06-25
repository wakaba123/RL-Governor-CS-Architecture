#include "scheduler.h"
#include <chrono>
#include "execute.h"
#include <iostream>
#include <vector>
#include <thread>
#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <cstring>
#include <asm/unistd.h>


int set_cpu_mask(pid_t pid, int from, int end) {
    return 1;
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
    return set_cpu_mask(pid, 0, 3);
}

int set_cpu_mask_little(pid_t pid) {
    return set_cpu_mask(pid, 4, 7);
}

int set_cpu_mask_all(pid_t pid) {
    return set_cpu_mask(pid, 0, 7);
}

std::vector<int> argsort(std::vector<double> input) {
    int h = input.size();
    std::vector<int> index(h);

    for (int i = 0; i < h; ++i)
        index[i] = i;

    for (int i = h - 1; i > 0; --i) {
        int min = 0;
        for (int j = 1; j <= i; ++j) {
            if (input[index[j]] < input[index[min]])
                min = j;
        }

        int temp = index[i];
        index[i] = index[min];
        index[min] = temp;
    }
    return index;
}

std::vector<std::string> split(const std::string& input, char delimiter) {  // 该split对单个分隔符进行分隔
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(input);

    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }

    return tokens;
}

std::vector<std::string> split(const std::string& str) {  // 该split对一个或多个空格进行分隔
    std::vector<std::string> tokens;
    std::istringstream tokenStream(str);
    std::string token;

    while (tokenStream >> token) {
        tokens.push_back(token);
    }

    return tokens;
}

std::string replace(const std::string& str, const std::string& oldStr, const std::string& newStr) {
    std::string result = str;
    size_t pos = 0;
    while ((pos = result.find(oldStr, pos)) != std::string::npos) {
        result.replace(pos, oldStr.length(), newStr);
        pos += newStr.length();
    }
    return result;
}

Scheduler::Scheduler(std::string tid_list_str, std::vector<int>& big_freq_list_in, std::vector<int>& little_freq_list_in) {
    this->tid_list_str = tid_list_str;
    std::string delimiter = ",";
    size_t pos = 0;
    while ((pos = tid_list_str.find(delimiter)) != std::string::npos) {
        std::string value = tid_list_str.substr(0, pos);
        tid_list.push_back(std::stoi(value));
        tid_list_str.erase(0, pos + delimiter.length());
    }
    tid_list.push_back(std::stoi(tid_list_str));
    thread_num = tid_list.size();

    this->big_freq_list.resize(pmu_num);
    this->little_freq_list.resize(pmu_num);

    this->big_freq_list = big_freq_list_in;
    this->little_freq_list = little_freq_list_in;

    all_pmu_data.resize(10);
    main_pmu_data.resize(10);
    sf_pmu_data.resize(10);
    render_pmu_data.resize(10);

    for (int i = 0; i < thread_num; i++) {
        set_cpu_mask_all(tid_list[i]);
    }

    for (int i = 0; i < thread_num; i++) {
        std::string command;
        if (position_bit[i] == 1) {
            set_cpu_mask_big(tid_list[i]);
        } else {
            set_cpu_mask_little(tid_list[i]);
        }
    }
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
 

std::vector<double> Scheduler::schdule(int big_current_freq, int little_current_freq) {
    big_scale = 0;
    little_scale = 0;
    big_scale_freq_idx = 0;
    little_scale_freq_idx = 0;

    std::vector<pid_t> pidList = tid_list;  // 要监测的PID列表

    std::vector<long long> taskClockList(pidList.size());
    std::vector<long long> instructionsList(pidList.size());

    std::vector<std::thread> threads;

    // 创建线程获取每个PID的计数器值
    for (size_t i = 0; i < pidList.size() * 2; ++i) {
        threads.emplace_back([&taskClockList, &instructionsList, i, pidList]() {
            getEventCounter(pidList[i], TASK_CLOCK, taskClockList[i]);
            // getEventCounter(pidList[i], INSTRUCTIONS, instructionsList[i]);
        });
        threads.emplace_back([&taskClockList, &instructionsList, i, pidList]() {
            // getEventCounter(pidList[i], TASK_CLOCK, taskClockList[i]);
            getEventCounter(pidList[i], INSTRUCTIONS, instructionsList[i]);
        });
    }

    // 等待所有线程完成
    for (auto& thread : threads) {
        thread.join();
    }

    // 打印结果
    for (size_t i = 0; i < pidList.size(); ++i) {
        all_pmu_data[i].push_back(taskClockList[i]/100000);
        all_pmu_data[i].push_back(instructionsList[i]);
    }


    for (int i1 = 0; i1 < thread_num; i1++) {
        priority_arr.push_back(all_pmu_data[i1][0] / 1000.0);
    }


    little_priority = 0;
    big_priority = 0;

    for (int i1 = 0; i1 < thread_num; i1++) {
        if (position_bit[i1] == 0) {
            little_priority += priority_arr[i1];
        } else {
            big_priority += priority_arr[i1];
        }
    }

    std::vector<double> a = priority_arr;
    std::vector<int> sort_index = argsort(a);
    // std::reverse(sort_index.begin(), sort_index.end());

    std::vector<int> big_scale_arr = {0, 0, 0};
    std::vector<int> little_scale_arr = {0, 0, 0};
    std::vector<int> big_scale_freq_arr = {0, 0, 0};
    std::vector<int> little_scale_freq_arr = {0, 0, 0};

    for (int i = 0; i < sort_index.size(); i++) {
        int index = sort_index[i];
        int task_clock = all_pmu_data[index][0];
        int inst = all_pmu_data[index][1];
        int big_scale_freq = 0;
        int little_scale_freq = 0;

        if (inst > inst_min[index]) {
            if (position_bit[index] == 1 && task_clock < task_clock_min_big[index]) {
                big_scale_freq = big_freq_list[big_freq_list.size() - 1];
                for (int j = big_freq_list.size() - 1; j >= 0; j--) {
                    int big_freq = big_freq_list[index];
                    if (big_freq / big_current_freq < task_clock / task_clock_min_big[index]) {
                        big_scale_freq = big_freq;
                        break;
                    }
                }
                if (big_scale_freq == big_freq_list[big_freq_list.size() - 1]) {
                    little_priority += priority_arr[index];
                    big_priority -= priority_arr[index];
                    position_bit[index] = 0;
                    set_cpu_mask_little(tid_list[index]);
                    break;
                } else {
                    big_scale_arr[i] = -1;
                    big_scale_freq_arr[i] = big_scale_freq;
                }
            } else if (position_bit[index] == 0 && task_clock < task_clock_min_little[index]) {
                little_scale_arr[i] = -1;
                little_scale_freq = little_freq_list[little_freq_list.size() - 1];
                for (int j = little_freq_list.size() - 1; j >= 0; j--) {
                    int little_freq = little_freq_list[j];
                    if (little_freq / little_current_freq < task_clock / task_clock_min_little[index]) {
                        little_scale_freq = little_freq;
                        break;
                    }
                }
                if (little_scale_freq == little_freq_list[little_freq_list.size() - 1]) {
                    little_scale_freq_arr[i] = little_freq_list[0];
                } else {
                    little_scale_freq_arr[i] = little_scale_freq;
                }
            } else if (position_bit[index] == 1 && task_clock > task_clock_max_big[index]) {
                big_scale_arr[i] = 1;
                big_scale_freq = big_freq_list[0];
                for (const int big_freq : big_freq_list) {
                    if (big_freq / big_current_freq > task_clock / task_clock_max_big[index]) {
                        big_scale_freq = big_freq;
                        break;
                    }
                }
                if (big_scale_freq == big_freq_list[0]) {
                    big_scale_freq_arr[i] = big_freq_list[big_freq_list.size() - 1];
                } else {
                    big_scale_freq_arr[i] = big_scale_freq;
                }
            } else if (position_bit[index] == 0 && task_clock < task_clock_min_little[index]) {
                little_scale_freq = little_freq_list[0];
                for (const int little_freq : little_freq_list) {
                    if (little_freq / little_current_freq > task_clock / task_clock_max_little[index]) {
                        little_scale_freq = little_freq;
                        break;
                    }
                }
                if (little_scale_freq == little_freq_list[0]) {
                    big_priority += priority_arr[index];
                    little_priority -= priority_arr[index];
                    position_bit[index] = 1;
                    set_cpu_mask_big(tid_list[index]);
                    break;
                } else {
                    little_scale_arr[i] = 1;
                    little_scale_freq_arr[i] = little_scale_freq;
                }
            }
        } else if (inst < inst_min[index]) {
            if (position_bit[index] == 0) {
                little_scale_freq = little_freq_list[0];
                for (const int little_freq : little_freq_list) {
                    if (little_freq / little_current_freq > inst_min[index] / inst) {
                        little_scale_freq = little_freq;
                        break;
                    }
                }
                if (little_scale_freq == little_freq_list[0]) {
                    big_priority += priority_arr[index];
                    little_priority -= priority_arr[index];
                    position_bit[index] = 1;
                    set_cpu_mask_big(tid_list[index]);
                    break;
                } else {
                    little_scale_arr[i] = 1;
                    little_scale_freq_arr[i] = little_scale_freq;
                }
            } else {
                big_scale_arr[i] = 1;
                big_scale_freq = big_freq_list[0];
                for (const int big_freq : big_freq_list) {
                    if (big_freq / big_current_freq > inst_min[index] / inst) {
                        big_scale_freq = big_freq;
                        break;
                    }
                }
                if (big_scale_freq == big_freq_list[0]) {
                    big_scale_freq_arr[i] = big_freq_list[big_freq_list.size() - 1];
                } else {
                    big_scale_freq_arr[i] = big_scale_freq;
                }
            }
        }
    }
    int down_max_freq = big_freq_list[0];
    int min_freq = big_freq_list[big_freq_list.size() - 1];
    int max_freq = big_freq_list[0];
    bool up_bool = false;
    bool down_bool = false;

    for (int i1 = 0; i1 < big_scale_arr.size(); i1++) {
        if (big_scale_arr[i1] == 1) {
            max_freq = std::max(max_freq, big_scale_freq_arr[i1]);
            up_bool = true;
        } else if (big_scale_arr[i1] == -1) {
            down_max_freq = std::max(down_max_freq, big_scale_freq_arr[i1]);
            down_bool = true;
        }
    }

    if (up_bool) {
        big_scale = 1;
        big_scale_freq = max_freq;
    } else if (down_bool) {
        big_scale = -1;
        big_scale_freq = down_max_freq;
    }

    down_max_freq = little_freq_list[0];
    min_freq = little_freq_list[little_freq_list.size() - 1];
    max_freq = little_freq_list[0];
    up_bool = false;
    down_bool = false;

    for (int i1 = 0; i1 < little_scale_arr.size(); i1++) {
        if (little_scale_arr[i1] == 1) {
            max_freq = std::max(max_freq, little_scale_freq_arr[i1]);
            up_bool = true;
        } else if (little_scale_arr[i1] == -1) {
            down_max_freq = std::max(down_max_freq, little_scale_freq_arr[i1]);
            down_bool = true;
        }
    }

    if (up_bool) {
        little_scale = 1;
        little_scale_freq = max_freq;
    }
    if (down_bool) {
        little_scale = -1;
        little_scale_freq = down_max_freq;
    }

    if (big_scale != 0) {
        for (int i1 = 0; i1 < big_freq_list.size(); i1++) {
            if (big_freq_list[i1] == big_scale_freq) {
                big_scale_freq_idx = i1;
            }
        }
    }
    if (little_scale != 0) {
        for (int i1 = 0; i1 < little_freq_list.size(); i1++) {
            if (little_freq_list[i1] == little_scale_freq) {
                little_scale_freq_idx = i1;
            }
        }
    }

    commu_info.push_back(big_priority);
    commu_info.push_back(little_priority);
    commu_info.push_back(big_scale);
    commu_info.push_back(big_scale_freq_idx);
    commu_info.push_back(little_scale);
    commu_info.push_back(little_scale_freq_idx);

    return commu_info;
}
