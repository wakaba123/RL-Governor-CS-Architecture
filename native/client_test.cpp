#include <iostream>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

const int BUFFER_SIZE = 1024;

std::string sendAndReceiveSocket(const std::string& message, const std::string& serverIP, int port) {
    // 创建套接字
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        std::cerr << "Failed to create socket" << std::endl;
        return "";
    }

    // 准备服务器地址结构体
    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(port);

    // 将IP地址从字符串转换为二进制格式
    if (inet_pton(AF_INET, serverIP.c_str(), &(serverAddress.sin_addr)) <= 0) {
        std::cerr << "Invalid address/ Address not supported" << std::endl;
        close(sock);
        return "";
    }

    // 连接到服务器
    if (connect(sock, (struct sockaddr*)&serverAddress, sizeof(serverAddress)) < 0) {
        std::cerr << "Connection failed" << std::endl;
        close(sock);
        return "";
    }

    // 发送数据
    if (send(sock, message.c_str(), message.size(), 0) < 0) {
        std::cerr << "Failed to send data" << std::endl;
        close(sock);
        return "";
    }

    // 接收数据
    char buffer[BUFFER_SIZE];
    std::string receivedData;
    int bytesRead;
    while ((bytesRead = recv(sock, buffer, BUFFER_SIZE - 1, 0)) > 0) {
        buffer[bytesRead] = '\0';
        receivedData += buffer;
    }

    if (bytesRead < 0) {
        std::cerr << "Failed to receive data" << std::endl;
    }

    // 关闭套接字
    close(sock);

    return receivedData;
}

int main() {
    std::string serverIP = "127.0.0.1";
    int port = 8888;

    std::string message1 = "2";
    std::string receivedData = sendAndReceiveSocket(message1, serverIP, port);
    std::cout << "Received data: " << receivedData << std::endl;
    sleep(1);
 

    // 收集当前设备的信息
    message1 = "1";
    receivedData = sendAndReceiveSocket(message1, serverIP, port);
    std::cout << "Received data: " << receivedData << std::endl;
    sleep(1);
     
    // 设置频率
    std::string message2 = "0 2764800 2342400 1708800";
    receivedData = sendAndReceiveSocket(message2, serverIP, port);
    std::cout << "Received data: " << receivedData << std::endl;
    sleep(1);

    // 再收集设备的信息
    std::string message3 = "1";
    receivedData = sendAndReceiveSocket(message3, serverIP, port);
    std::cout << "Received data: " << receivedData << std::endl;
    sleep(1);

    message1 = "3";
    receivedData = sendAndReceiveSocket(message1, serverIP, port);
    std::cout << "Received data: " << receivedData << std::endl;
    sleep(1);
 

    return 0;
}
