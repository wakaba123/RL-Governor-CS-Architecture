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


int main() {
    set_cpu_mask_little(7769);
    set_cpu_mask_little(7884);
    set_cpu_mask_little(1120);
}
