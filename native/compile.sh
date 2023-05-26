NDK=/home/blues/Desktop/android-ndk-r25c/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android30-clang++ 
$NDK $1 fps.cpp -static-libstdc++ -o $2
adb push $2 /data/local/tmp