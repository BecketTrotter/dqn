from DQN import DQN
from Market import Player
from sql_to_minute import pull_range, pull_time_frame
from create_time_series import create_time_series
import datetime
from statistics import mean 

class option:
	opt1 = False

def train_remember(minutes, options, model, performance_path):
	time = 15
	
	time_limit = 140
	starting_cash = 1_000_000 
	curr_ind = 35
	

	bids = [minute.open for minute in minutes]
	asks = [minute.open for minute in minutes]

	player = Player(starting_cash, bids, asks, curr_ind)

	offset = curr_ind
	done = False

	
	while(not done):
		model_inp = create_time_series(time, curr_ind, minutes)

		a = model.play(model_inp)


		a = int(a)

		minutes[curr_ind].cash = player.cash / 1_000_000
		minutes[curr_ind].shares = player.shares
		minutes[curr_ind].action = a / 2
		minutes[curr_ind].curr_rat = player.curr_rat

		curr_net = player.calculate_net_worth()

		

		
		d = player.play(a)
		player.next_minute()
		

		if d == True:
			done = 1
		elif curr_ind > time_limit:
			done = 2
		
		prev_net = curr_net

		curr_net = (player.calculate_net_worth() - prev_net) / prev_net #make it track incremental change instead of overall
		curr_net *= 100

		

		minutes[curr_ind+1].curr_rat = player.curr_rat
		minutes[curr_ind+1].cash = player.cash / 1_000_000
		#minutes[curr_ind+1].shares = player.shares
		minutes[curr_ind+1].action = 1

		#minutes[curr_ind+1].net = (10 * player.calculate_net_worth() / prev_net) - 1

		curr_state = create_time_series(time, curr_ind, minutes)
		
		next_state = create_time_series(time, curr_ind + 1, minutes)

		model.remember(a, curr_state, next_state, done, curr_net)
		
		

		curr_ind += 1

		

	player.graph_performance(performance_path, model.epsilon)

	if len(model.memory) > model.batch_size:
		model.train()

	if len(player.positions) == 0:
		return [player.net, 0, 0, 0, 0]

	return [player.net, int(min(player.positions) * player.m.get_current_bid()), int(max(player.positions) * player.m.get_current_bid()), int(mean(player.positions) * player.m.get_current_bid()), curr_ind]
		


def run():
	time = 15
	observation_size = 8

	model = DQN(time, observation_size)
	opt = option()
	model.build_network(time, observation_size)

	#model.load_weights('models/2020-05-01 08:30:45.952242.h5')
	#model.epsilon = .8
	model.gamma = .98

	tickers = ['MSFT']#, 'AAPL', 'GS', 'CVX', 'NKE', 'V', 'BA', 'KO', 'JPM', 'MMM']
	years = [2014,2015,2016,2017,2018,2019,2020]

	model.epsilon_decay = .995
	model.lr = .03

	running_total = 0
	index = {x:0 for x in tickers}

	hours = [10, 13]

	for day in range(1, 31):
		for month in range(1,12):
			for year in years:
				try:
					x = datetime.datetime(int(year), int(month), int(day))

					if x.weekday() > 5:
						continue
				except:
					continue

				start = '{}-{}-{} {}:00:00'.format(int(year), int(month), int(day), 9)
				end = '{}-{}-{} {}:00:00'.format(int(year), int(month), int(day), 11)
				minutes = pull_time_frame('MSFT', start, end) #test pull for day

				if len(minutes) == 0:
					continue

				for ticker in tickers:
					for hour in hours:
						start = '{}-{}-{} {}:00:00'.format(int(year), int(month), int(day), int(hour))
						end = '{}-{}-{} {}:00:00'.format(int(year), int(month), int(day), int(hour)+3)

						minutes = pull_time_frame(ticker, start, end)

						if minutes == None or len(minutes) == 0:
							continue

						elif len(minutes) > 170:
							index[ticker] += 1

							if index[ticker] >= 100:
								index[ticker] = 0

							performance_path = 'Performance/{}-{}'.format(ticker, index[ticker])
							ret = train_remember(minutes, opt, model, performance_path)

							net = ret[0]
							mini = ret[1]
							maxi = ret[2]
							avg = ret[3]
							frames = ret[4] - 35
							
							if abs(running_total) > 2500000:
								running_total = 0

							running_total += (net - 1_000_000)

							print('NET: {:5}     total {:5} \non {}-{}-{}-{}-{}-{} \nmini: {} max: {} avg: {}\nFrames: {}\n\n'.format(int(net-1_000_000), int(running_total), ticker, 
																																	year, month, day, hour, int(model.epsilon*100),
																																	mini, maxi, avg, frames))
						else:
							print('not enough minutes {}'.format(len(minutes)))

			model.save_weights('models/' + str(datetime.datetime.now()) + '.h5')

'''ticker = 'MSFT'
year = 2019
hour = 12
month = 1 
minutes = pull_month_hour(ticker, year, month, hour)
print(minutes)'''
run()

