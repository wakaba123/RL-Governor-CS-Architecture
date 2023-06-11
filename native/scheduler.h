#ifndef SCHEDULER_H
#define SCHEDULER_H

#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

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
    Scheduler(std::string tid_list_str, std::vector<int>& big_freq_list_in, std::vector<int>& little_freq_list_in);
    std::vector<double> schdule(int big_current_freq, int little_current_freq);
    // Other member functions and variables
};

#endif // SCHEDULER_H
