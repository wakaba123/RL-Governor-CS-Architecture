application 中为app的代码

h5totflite 中为将h5模型转换为tflite格式的模型的代码

native 中为编写的native层的收集信息的二进制程序

test_tools 为进行整机基准测试算法测试的代码



分支：
- master 为google pixel
- Oneplus7Pro 为一加7pro (server修改为了设置3核频率，修改了test_tools中的get_view函数)

如果要适配一台新设备/适配一个新应用

1. native/server.cpp的set_freq函数需要根据需要修改2核或3核的频率，compile.sh中的编译器选择
2. application中的Config.java中需要修改为对应机型支持的大小核频率，需要测试的view的名称
3. application的assets文件夹添加对应的模型
    1. move h5 model in the native/ directory
    2. generate tflite file
    3. rename and move tflite file to application/app/src/main/assets/ directory
4. test_tools中的get_view函数，get_charge_count等函数
