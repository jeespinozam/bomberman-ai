import json
import sys
import random
import os
import numpy as np
from collections      import deque
from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *


class KerasAgent:

    def __init__(self, shape, action_size):
        self.weight_backup      = "bombergirl_weight.model"
        self.shape              = shape
        self.action_size        = action_size
        self.memory             = deque(maxlen=2000)
        self.learning_rate      = 0.001
        self.gamma              = 0.95
        self.exploration_rate   = 1.0
        self.exploration_min    = 0.01
        self.exploration_decay  = 0.995
        self.model              = self._build_model()

    def _build_model(self):
        model = Sequential()

        # Convolutions.
        model.add(Conv2D(
            16,
            kernel_size=(3, 3),
            strides=(1, 1),
            #data_format='channels_first',
            input_shape=self.shape
        ))
        model.add(Activation('relu'))
        model.add(Conv2D(
            32,
            kernel_size=(3, 3),
            strides=(1, 1),
            data_format='channels_first'
        ))
        model.add(Activation('relu'))

        # Dense layers.²
        model.add(Flatten())
        model.add(Dense(256))
        model.add(Activation('relu'))
        model.add(Dense(self.action_size))

        model.summary()
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        #model.compile(RMSprop(), 'MSE')

        if os.path.isfile(self.weight_backup):
            model.load_weights(self.weight_backup)
            self.exploration_rate = self.exploration_min

        return model

    def save_model(self, name):
        self.model.save(self.weight_backup)
        self.model.save(name)

    def act(self, state):
        if np.random.rand() <= self.exploration_rate:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, sample_batch_size=256):
        if len(self.memory) < sample_batch_size:
            sample_batch_size=len(self.memory)
        sample_batch = random.sample(self.memory, sample_batch_size)
        for state, action, reward, next_state, done in sample_batch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay
