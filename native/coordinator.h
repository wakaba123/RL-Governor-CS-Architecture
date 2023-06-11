#ifndef COORDINATOR_H
#define COORDINATOR_H

#include <vector>
#include <algorithm>

class Coordinator {
private:
    std::vector<int> big_freq_list;
    std::vector<int> little_freq_list;

public:
    Coordinator(const std::vector<int>& big_freq_list, const std::vector<int>& little_freq_list);

    int getArrayIndex(const std::vector<int>& arr, int value);

    std::vector<double> coordinate(const std::vector<double>& commu_info, double big_util, double little_util, int big_current_freq, int little_current_freq);
};

#endif  // COORDINATOR_H
