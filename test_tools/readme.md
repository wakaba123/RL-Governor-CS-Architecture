## 测试工具使用流程

### 路径问题

首先需要对学长的一些路径做适配，因为有sys.path.append()函数

1.所有sys.path.append函数中的路径都需要修改

2.config.py中的第8行，需要修改输出的文件的路径。


### 一些配置
config.py中可以修改base参数，控制运行和测试的时间
也可以修改view参数，修改测试的view

### 运行测试

**1.应用安装**

首先需要安装APP。github链接如下所示，选择ServiceVersion分支，该分支中为了减少APP的内存开销，删除了所有的Activity等无关内容。

https://github.com/blue-vegetable/RL-Governor-CS-Architecture/tree/master/application

修改Config.java中需要修改的配置文件

需要首次打开Activity一次，否则不能使用am开启服务。



**2.手动打开快手，进入到对应的view中。**



**3.运行testline_test.py ， 运行baseline_test.py**

运行过程中，可以查看testline.csv, baseline.csv, record.csv, 其中记录了中间结果



**4.运行python tools.py vis获得可视化的结果**

图像会保存在当前目录

