import numpy as np
import tensorflow as tf

# 输入和输出信息
input_info = {'name': 'serving_default_dense_input:0', 'index': 0, 'shape': np.array([1, 5], dtype=np.int32)}
output_info = {'name': 'StatefulPartitionedCall:0', 'index': 9, 'shape': np.array([1, 9], dtype=np.int32)}

# 构造模型
model = tf.keras.models.load_model('newModelWithNetwork.h5')

# little  big  fps  cpu  mem
arr = [0.9292929, 0.568, 0.96944445, 0.74038243, 0.3]
arr = [0.9292929, 0.832, 0.9166667, 0.779694, 0.3]
arr = [0.5151515, 0.568, 0.92685187, 0.4318729, 0.3]

input_data = np.array(arr).reshape(input_info['shape']).astype(np.float32)
# 进行模型预测
output_data = model.predict(input_data)
max_index = np.argmax(output_data)

print(input_data)
print(output_data)

print(max_index)

