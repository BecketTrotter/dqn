import matplotlib.pyplot as plt
import random
from matplotlib.backends.backend_pdf import PdfPages

class Market:
	def __init__(self, bids, asks):
		self.bids = bids
		self.asks = asks
		self.minute = 0

	def get_current_ask(self):
		return self.bids[self.minute] * 1.00025

	def get_current_bid(self):
		return self.bids[self.minute] * .99975

	def next_minute(self):
		self.minute += 1


class Player:
	def __init__(self, cash, bids, asks, offset):
		self.cash = cash
		self.bids = bids
		self.asks = asks
		self.net = cash
		self.performance = []
		self.shares = 0
		self.m = Market(bids, asks)
		self.m.minute = offset
		self.positions = []
		self.curr_rat = 0
		self.offset = offset

	def calculate_net_worth(self):
		assets = 0
		liability = 0

		if self.shares > 0:
			assets = self.shares * self.m.get_current_bid()
		else:
			liability = -1 * (self.shares * self.m.get_current_ask())
		
		self.net = assets + self.cash - liability

		return self.net

	def play(self, amount):
		
		#amount = amount - .5
		#amount = amount * 2
		action_dict = {0: -.45, 1:0, 2:.45}
		amount = action_dict[amount]

		if amount == 0:
			return

		

		if self.shares < 0:
			self.curr_rat = (self.shares * self.m.get_current_ask()) / self.net
		elif 	self.shares > 0:
			self.curr_rat = (self.shares * self.m.get_current_ask()) / self.net
		else:
			self.curr_rat = 0

		self.calculate_net_worth()

		if amount > 0:
			self.buy(amount)
		elif amount < 0:
			self.sell(-amount)

		if self.shares < 0:
			self.curr_rat = (self.shares * self.m.get_current_ask()) / self.net
		elif 	self.shares > 0:
			self.curr_rat = (self.shares * self.m.get_current_ask()) / self.net
		else:
			self.curr_rat = 0

		if abs(self.curr_rat) > 1:
			return True	


	def buy(self, amount):
		amount = amount * self.net
		ex = self.m
		shares = amount / ex.get_current_ask()
		self.shares += shares
		self.cash -= amount
		

	def sell(self, amount):
		amount = amount * self.net
		ex = self.m
		shares = amount / ex.get_current_bid()

		self.shares -= shares
		self.cash += amount

	def next_minute(self):
		self.m.next_minute()
		self.positions.append(self.shares)
		self.performance.append(self.calculate_net_worth())
		if self.shares < 0:
			self.curr_rat = (self.shares * self.m.get_current_ask()) / self.net
		elif 	self.shares > 0:
			self.curr_rat = (self.shares * self.m.get_current_bid()) / self.net
		else:
			self.curr_rat = 0


	def graph_performance(self,location, epsilon):
		index = 211

		
		'''fig, ax = plt.subplots(figsize = (4,3))'''
		'''plt.subplot()'''


		if not (location.endswith('.pdf')):
			location += '.pdf'

		with PdfPages(location) as pdf:
			fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
			ax1.set_title('Eps : {}'.format(str(epsilon)[:4]))

			ax1.plot(range(self.offset,self.m.minute),self.performance)
			
			ax2.plot(range(self.offset, self.m.minute), self.asks[self.offset:self.m.minute])
			ax2.set_title('Eps : {}'.format('Price'))
			
			ax3.plot(range(self.offset, self.m.minute), self.positions)
			ax3.set_title('Shares'.format('Price'))
			
			
			pdf.savefig(fig)
			plt.close(fig)


		'''plt.close(fig2)'''
		



