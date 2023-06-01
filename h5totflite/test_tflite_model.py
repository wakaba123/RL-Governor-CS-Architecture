import numpy as np
import tensorflow as tf

# 加载 TFLite 模型
interpreter = tf.lite.Interpreter(model_path='Newmodel.tflite')
interpreter.allocate_tensors()

# 获取输入和输出张量的信息
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# 构造输入数据

arr =[0.641, 0.5507246, 0.547, 0.875, 0.39520285, 0.7]
arr = [0.6413044, 0.78, 1, 0.547, 0.41352323, 0.3]
input_data = np.array(arr).reshape(np.array([1, 6], dtype=np.int32)).astype(np.float32)
interpreter.set_tensor(input_details[0]['index'], input_data)

# 进行模型预测
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])
max_index = np.argmax(output_data)

# 打印预测结果
print(output_data,max_index)

# 输入和输出信息
input_info = {'name': 'serving_default_dense_input:0', 'index': 0, 'shape': np.array([1, 6], dtype=np.int32)}
output_info = {'name': 'StatefulPartitionedCall:0', 'index': 9, 'shape': np.array([1, 27], dtype=np.int32)}

# 构造模型
model = tf.keras.models.load_model('newModelWithNetwork.h5')


input_data = np.array(arr).reshape(input_info['shape']).astype(np.float32)
# 进行模型预测
output_data = model.predict(input_data)
max_index = np.argmax(output_data)

print(input_data)
print(output_data)

print(max_index)
