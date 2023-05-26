步骤：

1.修改tran.py的第27行为模型的路径

2.运行后会生成一个newModelWithNetwork.h5，是包含网络结构的模型

3.修改h5totflite2.py的第4行为有网络结构的模型的路径，运行h5totflite2.py

生成的modelfloat16.tflite即为最终的tflite文件。





测试方法：

test_tflite_model.py函数中，修改h5和tflite模型路径，并且修改第14行的arr即可测试两个模型对于同一个输入的输出。



部署方法：

将tflite模型命名为model.tflite. 然后复制到networkTrans的assets中(/[app](https://github.com/blue-vegetable/neural-networks-based-governor-for-android/tree/main/app)/[src](https://github.com/blue-vegetable/neural-networks-based-governor-for-android/tree/main/app/src)/[main](https://github.com/blue-vegetable/neural-networks-based-governor-for-android/tree/main/app/src/main)/**assets**/)即可。



解释：

tran.py函数：因为学长的h5文件只有权重，没有网络结构，所以需要用这个代码把网络结构加进去。

