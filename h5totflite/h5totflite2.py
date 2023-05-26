import tensorflow as tf

# 加载模型
model = tf.keras.models.load_model('/home/blues/Desktop/netTrans/network/newModelWithNetwork.h5')

# 创建 TFLiteConverter 对象
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# 转换模型

converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]

tflite_fp16_model = converter.convert()

# 保存转换后的模型
with open('modelfloat16.tflite', 'wb') as f:
    f.write(tflite_fp16_model)
