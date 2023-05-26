from keras.models import load_model
import numpy as np

model = load_model('newModelWithNetwork.h5')

a = [0.9292929, 0.832, 0.99, 0.93830127, 0.2]
x = np.array(a).reshape(1,5)

y =  model.predict(x).tolist()
print(y)
max_val = y[0][0]
choice = 0 
for i, num in enumerate(y[0]):
    if num > max_val:
        max_val = num
        choice = i
print(choice)


    
