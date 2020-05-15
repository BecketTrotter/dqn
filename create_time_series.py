from collections import deque


def create_time_series(time, curr_ind, minutes):
	past = deque(maxlen = time)
	time_series = []
	index = 0
	#time series includes current minute and time amount of prev ones
	i = 0
	if len(minutes) == 0:
		raise Exception('minutes empty')
		
	while(1):
		if len(past) == time:
			return list(past)
			
		ind = curr_ind-i-1
		prev = minutes[ind].to_list()
		past.append(minutes[curr_ind-i].to_list_pct(prev))
		i = i + 1