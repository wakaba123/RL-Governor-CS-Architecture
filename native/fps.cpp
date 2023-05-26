#include "fps.h"
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

const size_t MAX_QUEUE_SIZE = 200; // 设置队列的最大长度
std::string execute(const std::string& command) {
    std::string result;
    char buffer[128];
    FILE* pipe = popen(command.c_str(), "r");
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

FPSGet::FPSGet(const std::string& view) {
    this->view = view;
    fps = 0;
    t = 0;
    std::pair<unsigned long long, std::vector<unsigned long long>> frameData = getFrameData();
    unsigned long long refresh_period = frameData.first;
    std::vector<unsigned long long> timestamps = frameData.second;
    unsigned long long base_timestamp = 0;
    for (unsigned long long timestamp : timestamps) {
        if (timestamp != 0) {
            base_timestamp = timestamp;
            break;
        }
    }
    if (base_timestamp == 0) {
        throw std::runtime_error("请保证前台应用与view对应，期望的view为" + this->view);
    }

    unsigned long long last_timestamp = timestamps[timestamps.size() - 2];
    frame_queue.insert(frame_queue.end(), timestamps.begin(), timestamps.end());
}

void FPSGet::start() {
    std::thread fps_thread(&FPSGet::getFrameDataThread, this);
    fps_thread.detach();
}

void FPSGet::getFrameDataThread() {
    while (while_flag) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        std::pair<unsigned long long, std::vector<unsigned long long>> frameData = getFrameData();
        unsigned long long refresh_period = frameData.first;
        std::vector<unsigned long long> new_timestamps = frameData.second;
        if (new_timestamps.size() <= 120) {
            continue;
        }
        // std::cout << "len : " << new_timestamps.size() << std::endl;
        frame_queue.insert(frame_queue.end(), new_timestamps.begin(), new_timestamps.end());
        while (frame_queue.size() > MAX_QUEUE_SIZE) {
            frame_queue.pop_front();
        }
    }
}

int FPSGet::getFPS() {
    if (view.empty()) {
        throw std::runtime_error("Fail to get current SurfaceFligner view");
    }
    std::vector<unsigned long long> adjusted_timestamps;
    for (unsigned long long seconds : frame_queue) {
        seconds -= base_timestamp;
        if (seconds > 1e15) {  // too large, just ignore
            continue;
        }
        adjusted_timestamps.push_back(seconds);
    }

    unsigned long long from_time = adjusted_timestamps.back() - 1e9;
    int fps_count = 0;
    for (unsigned long long seconds : adjusted_timestamps) {
        if (seconds > from_time) {
            fps_count++;
        }
    }
    fps = std::min(fps_count, 60);
    return fps;
}

std::pair<unsigned long long, std::vector<unsigned long long>> FPSGet::getFrameData() {
    std::string command = "dumpsys SurfaceFlinger --latency " + view;
    std::string result = execute(command);

    std::vector<std::string> results;
    size_t startPos = 0;
    size_t endPos = result.find('\n');
    while (endPos != std::string::npos) {
        results.push_back(result.substr(startPos, endPos - startPos));
        startPos = endPos + 1;
        endPos = result.find('\n', startPos);
    }

    if (results.empty()) {
        throw std::runtime_error("Frame Data is Empty.");
    }

    unsigned long long nanoseconds_per_second = 1e9;
    unsigned long long refresh_period = std::stoull(results[0]) / nanoseconds_per_second;
    long long pending_fence_timestamp = (1LL << 63) - 1;

    std::vector<unsigned long long> timestamps;
    for (size_t i = 1; i < results.size(); i++) {
        std::vector<std::string> fields;
        std::istringstream iss(results[i]);
        std::string field;
        while (iss >> field) {
            fields.push_back(field);
        }

        if (fields.size() != 3) {
            continue;
        }

        int start = std::stoull(fields[0]);
        int submitting = std::stoull(fields[1]);
        int submitted = std::stoull(fields[2]);

        if (submitting == 0) {
            continue;
        }

        unsigned long long timestamp = std::stoull(fields[1]);
        if (timestamp == pending_fence_timestamp) {
            continue;
        }

        timestamps.push_back(timestamp);
    }

    return std::make_pair(refresh_period, timestamps);
};