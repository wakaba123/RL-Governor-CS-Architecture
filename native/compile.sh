if [ $# != 2 ]; then
  echo "USAGE: ./comple.sh server.cpp server"
  exit -1;
fi
NDK_PATH=$(which ndk-build | xargs dirname)
ANDROID_VERSION=$(adb shell getprop ro.build.version.sdk)
NDK=$NDK_PATH/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android$ANDROID_VERSION-clang++ 

echo "$NDK $1 fps.cpp -static-libstdc++ -o $2" 
$NDK $1 fps.cpp -static-libstdc++ -o $2

echo "adb push $2 /data/local/tmp"
adb push $2 /data/local/tmp
