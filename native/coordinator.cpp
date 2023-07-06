#include "coordinator.h"

Coordinator::Coordinator(const std::vector<int>& big_freq_list, const std::vector<int>& little_freq_list) {
    this->big_freq_list = big_freq_list;
    this->little_freq_list = little_freq_list;
}

int Coordinator::getArrayIndex(const std::vector<int>& arr, int value) {
    for (int i = 0; i < arr.size(); i++) {
        if (arr[i] == value) {
            return i;
        }
    }
    return -1;
}

std::vector<double> Coordinator::coordinate(const std::vector<double>& commu_info, double big_util, double little_util, int big_current_freq, int little_current_freq) {
    int big_scale_EFC = 0;
    int little_scale_EFC = 0;
    double big_priority = commu_info[0];
    double little_priority = commu_info[1];

    if (big_util >= 3 && big_priority >= 0.5) {
        if (big_priority >= 0.7) {
            big_scale_EFC = 2;
        } else {
            big_scale_EFC = 1;
        }
    }
    if (big_util < 1.75 && big_priority < 0.25) {
        big_scale_EFC = -1;
    }
    if (little_util >= 2.75 || little_priority >= 0.3) {
        little_scale_EFC = 2;
    }
    if (little_util < 1.75 && little_priority < 0.15) {
        little_scale_EFC = -1;
    }


    printf("Coordinator original big : %d little %d\n", big_scale_EFC, little_scale_EFC);
    int big_scale_freq_EFC = getArrayIndex(big_freq_list, big_current_freq) + big_scale_EFC * 2;
    int little_scale_freq_EFC = getArrayIndex(little_freq_list, little_current_freq) + little_scale_EFC * 2;

    double big_scale, little_scale;
    int big_scale_freq_idx, little_scale_freq_idx;
    if (commu_info[2] != 0) {
        if (big_scale_EFC * commu_info[2] < 0) {
            big_scale = 0;
            big_scale_freq_idx = getArrayIndex(big_freq_list, big_current_freq);
        } else {
            big_scale = commu_info[2];
            big_scale_freq_idx = (int)(commu_info[3]);
            /* due to reduced freq_list, this part of code is deprecated
            if (big_scale_freq_idx % 2 == 1) {
                big_scale_freq_idx += (int)(commu_info[2]);
            }
            */
        }
    } else {
        big_scale = big_scale_EFC;
        big_scale_freq_idx = big_scale_freq_EFC;
    }
    if (commu_info[4] != 0) {
        if (little_scale_EFC * commu_info[4] < 0) {
            little_scale = 0;
            little_scale_freq_idx = getArrayIndex(little_freq_list, little_current_freq);
        } else {
            little_scale = commu_info[4];
            little_scale_freq_idx = static_cast<int>(commu_info[5]);
            /*
            if (little_scale_freq_idx % 2 == 1) {
                little_scale_freq_idx += static_cast<int>(commu_info[4]);
            }
            */
        }
    } else {
        little_scale = little_scale_EFC;
        little_scale_freq_idx = little_scale_freq_EFC;
    }
    big_scale_freq_idx = std::min(2, big_scale_freq_idx);
    little_scale_freq_idx = std::min(2, little_scale_freq_idx);
    big_scale_freq_idx = std::max(0, big_scale_freq_idx);
    little_scale_freq_idx = std::max(0, little_scale_freq_idx);
    return { big_scale, (double)big_scale_freq_idx, little_scale, (double)little_scale_freq_idx };
}
