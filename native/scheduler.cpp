#include "scheduler.h"

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

std::string execute(const std::string& command) {
    std::string result;
    char buffer[1024];
    FILE* pipe = fopen(command.c_str(), "r");
    if (!pipe) {
        printf("执行命令失败！\n");
        return "";
    }

    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        result += buffer;
    }

    pclose(pipe);
    return result;
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

class Scheduler {
   private:
    int interval = 5;
    int pmu_num = 2;
    int thread_num;
    std::vector<double> priority_arr;
    std::vector<std::vector<int>> main_pmu_data;
    std::vector<std::vector<int>> render_pmu_data;
    std::vector<std::vector<int>> sf_pmu_data;
    std::vector<std::vector<int>> all_pmu_data;
    std::vector<double> commu_info;

    int inst_min[3] = {30000000, 100000000, 60000000};

    int task_clock_max_little[3] = {220, 600, 260};
    int task_clock_max_big[3] = {160, 350, 180};

    int task_clock_min_little[3] = {150, 400, 160};
    int task_clock_min_big[3] = {60, 170, 90};

    std::vector<int> tid_list;
    std::string tid_list_str;

    int big_scale = 0;
    int little_scale = 0;
    int big_scale_freq_idx = 0;
    int little_scale_freq_idx = 0;
    int big_scale_freq;
    int little_scale_freq;

    std::vector<int> big_freq_list;
    std::vector<int> little_freq_list;

    double big_priority = 0;
    double little_priority = 1;
    int position_bit[3] = {1, 1, 0};

   public:
    Scheduler(std::string tid_list_str, std::vector<int>& big_freq_list_in, std::vector<int>& little_freq_list_in) {
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
    std::vector<double> schdule(int big_current_freq, int little_current_freq) {
        big_scale = 0;
        little_scale = 0;
        big_scale_freq_idx = 0;
        little_scale_freq_idx = 0;
        // std::string command = "su -c 'simpleperf stat -e task-clock,instructions -t " + tid_list_str + " --duration 1 --per-thread'";
        std::string result = execute("simpleperf.txt");
        std::cout << result << std::endl;
        std::vector<std::string> result_array = split(result, '\n');
        result_array = std::vector<std::string>(result_array.begin() + 3, result_array.end());
        printf("here success\n");

        if (result_array.size() != 8) {
            commu_info.push_back(big_priority);
            commu_info.push_back(little_priority);
            commu_info.push_back(static_cast<double>(big_scale));
            commu_info.push_back(static_cast<double>(big_scale_freq_idx));
            commu_info.push_back(static_cast<double>(little_scale));
            commu_info.push_back(static_cast<double>(little_scale_freq_idx));
            return commu_info;
        }

        int pmu;
        int i;
        for (i = 0; i < pmu_num; i++) {
            std::string thread_name = split(result_array[i * thread_num])[0];
            if (result_array[i * thread_num].find("(ms)") != std::string::npos) {
                pmu = std::stoi(replace(split(split(result_array[i * thread_num])[3], '.')[0], ",", ""));
            } else {
                pmu = std::stoi(replace(split(result_array[i * thread_num])[3], ",", ""));
            }
            if (thread_name == ".smile.gifmaker") {
                main_pmu_data[i].push_back(pmu);
                all_pmu_data[0].push_back(pmu);
            } else if (thread_name == "RenderThread") {
                render_pmu_data[i].push_back(pmu);
                all_pmu_data[1].push_back(pmu);
            } else {
                sf_pmu_data[i].push_back(pmu);
                all_pmu_data[2].push_back(pmu);
            }

            thread_name = split(result_array[i * thread_num + 1])[0];
            if (result_array[i * thread_num + 1].find("(ms)") != std::string::npos) {
                pmu = std::stoi(replace(split(split(result_array[i * thread_num + 1])[3], '.')[0], ",", ""));
            } else {
                pmu = std::stoi(replace(split(result_array[i * thread_num + 1])[3], ",", ""));
            }
            if (thread_name == ".smile.gifmaker") {
                main_pmu_data[i].push_back(pmu);
                all_pmu_data[0].push_back(pmu);
            } else if (thread_name == "RenderThread") {
                render_pmu_data[i].push_back(pmu);
                all_pmu_data[1].push_back(pmu);
            } else {
                sf_pmu_data[i].push_back(pmu);
                all_pmu_data[2].push_back(pmu);
            }

            thread_name = split(result_array[i * thread_num + 2])[0];
            if (result_array[i * thread_num + 2].find("(ms)") != std::string::npos) {
                pmu = std::stoi(replace(split(split(result_array[i * thread_num + 2])[3], '.')[0], ",", ""));
            } else {
                pmu = std::stoi(replace(split(result_array[i * thread_num + 2])[3], ",", ""));
            }
            if (thread_name == ".smile.gifmaker") {
                main_pmu_data[i].push_back(pmu);
                all_pmu_data[0].push_back(pmu);
            } else if (thread_name == "RenderThread") {
                render_pmu_data[i].push_back(pmu);
                all_pmu_data[1].push_back(pmu);
            } else {
                sf_pmu_data[i].push_back(pmu);
                all_pmu_data[2].push_back(pmu);
            }
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

        for (i = 0; i < sort_index.size(); i++) {
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
};
