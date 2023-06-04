#!/bin/bash

# 使用 top 命令获取进程名为 "server" 的 PID
pid=$(adb shell pgrep -x server) 

# 检查是否找到了进程
if [ -z "$pid" ]; then
  echo "未找到进程名为 'server' 的进程"
  exit 1
fi

# 使用 kill -9 命令杀死该进程
adb shell su -c "kill -9 $pid"

echo "进程已被杀死，PID: $pid"
