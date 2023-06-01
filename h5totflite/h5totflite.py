import tensorflow as tf

# 加载模型
model = tf.keras.models.load_model("./newModelWithNetwork.h5")

# 生成非量化的tflite模型
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
open("Newmodel.tflite", 'wb').write(tflite_model)
print('saved tflite model!')
