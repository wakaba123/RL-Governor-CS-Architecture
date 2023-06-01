from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Dense
from collections import deque

state_size = 6
action_size = 27
learning_rate = 0.005


def build_model():
    model = Sequential()
    model.add(
        Dense(64,
              input_dim=state_size,
              activation='relu',
              kernel_initializer='normal'))
    model.add(Dense(64, activation='relu', kernel_initializer='normal'))
    model.add(
        Dense(action_size, activation='linear', kernel_initializer='normal'))
    model.compile(loss='mse', optimizer=Adam(lr=learning_rate))
    model.summary()
    return model


model = build_model()
#model.load_weights("model2023-03-06-15-42.h5")
model.load_weights("model2023-06-01-11-58.h5")
model.save("newModelWithNetwork.h5")
