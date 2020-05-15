import pymysql
import numpy as np
from credentials import host, port, dbname, user, password

class minute:
	def __init__(self, date, open_p, high, low, close, volume):
		self.date = date
		self.open = open_p
		self.high =  high
		self.low = low
		self.close = close
		self.volume = volume
		self.shares = 0
		self.cash = 1_000_000
		self.action = 1
		self.net = 0
		self.curr_rat = 0

	def get_ask(self):
		return self.high

	def get_bid(self):
		return self.low

	def to_list_pct(self, previous):
		ret = []
		scale = [self.open, self.high, self.low, self.close, self.volume] # must correspond to to_list

		for x in range(len(scale)): # <- above note applies here
			if previous[x] == 0:
				ret.append(0)
			else:
				ret.append((scale[x] - previous[x])/previous[x])

		values = [self.curr_rat, self.cash]#, self.net]

		for x in values:
			ret.append(x)

		ret.append(self.action / 2)
		#ret.append(1/self.open)
		#ret.append(self.curr_rat)
		#ret.append(self.shares)
		#ret.append(self.net)


		return ret

	def to_list(self):
		return [self.open, self.high, self.low, self.close, self.volume] #, self.shares, self.cash,  self.net] #self.action,


def establish_connection():
	connection = pymysql.connect(host, user=user, port=port,
	                           passwd=password, db=dbname, connect_timeout = 5)
	cursor = connection.cursor()
	return connection

def pull_time_frame(ticker, start, end):
	connection = establish_connection()
	cursor = connection.cursor()
	sql = "SELECT * FROM {} WHERE timekey BETWEEN '{}' AND '{}';".format(ticker, start, end)
	cursor.execute(sql)
	results = cursor.fetchall()

	ret_li = []
	for entry in results:
			ret = minute(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5])
			ret_li.append(ret)

	return ret_li



def pull_range(ticker, start, end):
	connection = establish_connection()
	with connection.cursor() as cursor:
		sql = "SELECT * FROM {} WHERE timekey BETWEEN '{}' AND '{}';".format(ticker, start, end)
		try:
			cursor.execute(sql)
		except:
			raise Exception('usage start/end = YYYY-MM-DD 00:00:00')
		
		results = cursor.fetchall()
		connection.close()
		results = list(results)
		ret_li = []
		for entry in results:
			ret = minute(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5])
			ret_li.append(ret)

		return ret_li