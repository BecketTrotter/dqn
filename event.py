class event:
	def __init__(self, state, next_state, action, done):
		self.state = state
		self.next_state = next_state
		self.action = action
		self.done = done
