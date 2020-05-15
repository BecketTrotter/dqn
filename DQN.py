import tensorflow as tf
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.activations import relu
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam, Adadelta
import numpy as np
import random
from collections import deque
from sklearn.preprocessing import MinMaxScaler

class DQN:
	def __init__(self, time, observation_size):
		self.memory = deque(maxlen = 200)
		self.lr = .01
		self.epsilon = 1
		self.gamma = .98

		self.batch_size = 32
		self.action_size = 3
		self.epsilon_decay = .995
		self.scaler = MinMaxScaler()
		self.fitted = 0
		self.epsilon_min = .05

	def build_network(self, time, observation_size):
		model = Sequential()
		model.add(LSTM(32, input_shape = (time, observation_size), activation = 'tanh', return_sequences = True))
		model.add(LSTM(16, input_shape = (time, observation_size), activation = 'tanh', return_sequences = False))

		#model.add(Dense(self.action_size, activation = "linear"))
		model.add(Dense(3, activation = "linear"))

		self.time = time
		self.observation_size = observation_size
		

		self.model = model

		opt = Adam(learning_rate = self.lr)

		self.model.compile(optimizer = opt, loss = 'mse')

	def remember(self, action, pre_action_state, post_action_state, done, curr_net):
		dec = [action, pre_action_state, post_action_state, done, curr_net]
		self.memory.append(dec)

	def play(self, state):
		state = np.reshape(state, (1, self.time, self.observation_size))

		if np.random.rand(1,1) < 1:
			return np.argmax(np.random.rand(1, self.action_size))
		else:
			return np.argmax(self.model.predict(state))

	def predict(self, state):
		state = np.reshape(state, (1, self.time, self.observation_size))
		return self.model.predict(state)
		
	def train(self):
		self.memory = random.sample(self.memory, self.batch_size)

		for event in self.memory:
			action = event[0]
			curr_time_ser = event[1]
			next_time_ser = event[2]
			done = event[3]

			
			curr_time_ser = np.reshape(curr_time_ser, (1, self.time, self.observation_size))
			next_time_ser = np.reshape(next_time_ser, (1, self.time, self.observation_size))

			target_f = self.model.predict(curr_time_ser)
			target_f = np.reshape(target_f, (1, self.action_size))

			pred = self.model.predict(next_time_ser)
			pred = np.reshape(pred, (1, self.action_size))
			#pred = np.reshape(pred, self.action_size)
			
			pred_max = np.amax(pred[0])
			pred_max = pred_max
			target = event[4]

			if done == 2:
				target = 0
			elif done == 1:
				target = -10
			else:
				target = target + ( self.gamma * pred_max )

			action = int(action)
			target_f[0][action] = target

			
			#self.model.fit(curr_time_ser, target_f, epochs=1, verbose=0)
			self.model.fit(curr_time_ser, target_f, epochs=1, verbose=0)


		if self.epsilon > self.epsilon_min:
			self.epsilon *= self.epsilon_decay
		else:
			self.epsilon = self.epsilon_min

	def save_weights(self, location):
		self.model.save_weights(location)

	def load_weights(self, location):
		self.model.load_weights(location)
		print('load successful')














