#include <string>
#include <deque>
#include <mutex>
#include <vector>

class FPSGet {
private:
    std::string view;
    int fps;
    long t;
    std::deque<unsigned long long> frame_queue;
    std::mutex lock;
    unsigned long long base_timestamp = 0;
    unsigned long long last_timestamp = 0;
    void getFrameDataThread();

public:
    bool while_flag = 1;
    FPSGet(const std::string& view);
    void start();
    int getFPS();
    std::pair<unsigned long long, std::vector<unsigned long long>> getFrameData();
};

std::string execute(const std::string& command);
