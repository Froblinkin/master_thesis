"""Processing Billboard chart data to find when a song was released and controls for it 
being a reissue or from a popular artist"""

import numpy as np
import pandas as pd
import string

# Get artist-song pairs
chart_path = 'data/chart_record.tsv'
chart=pd.read_csv(chart_path,sep='\t',index_col=0,encoding='utf8')
df=chart[['artist','title']].as_matrix()
df=[list(x) for x in set(tuple(x) for x in df)]
df=pd.DataFrame(df)
df.columns=['artist','title']


def chart_success(var):
	"""Return control variable for past number of successes"""
	if var==1:
		return 0
	elif var>1 and var<=3:
		return 1
	elif var>3 and var<=10:
		return 2
	elif var>10:
		return 3
	else:
		print('Invalid number of successes!')
		return -1

# Iterate through tracks based on starting char in artist name
file_list=['number']+list(string.ascii_uppercase)
for file in file_list:
	if file=='number':
		numbers=[False if x in string.ascii_uppercase else True for x in df.artist.str[0]]
		df_sub=df.copy()[numbers]
	else:
		df_sub=df.copy()[df.artist.str[0]==file]

	# Release date
	df_sub['release']=''

	# Reissue control
	df_sub['reissue']=0

	# Past artist success control
	df_sub['success']=-1

	for x in df_sub.iterrows():
		artist=x[1].artist
		title=x[1].title

		chart_position=chart.loc[(chart.title == title) & (chart.artist == artist),'week']
		df_sub.loc[(df_sub.title == title) & (df_sub.artist == artist),'release']=chart_position.idxmin()
		dates=pd.to_datetime(chart_position.index).tolist()
		old=dates.pop(dates.index(min(dates)))

		# Songs are defined as reissues if they appeared on the charts twice over a span greater than half a year
		while len(dates)>0:
			new=dates[dates.index(min(dates))]
			if old+np.timedelta64(26,'W')<new:
				df_sub.loc[(df_sub.title == title) & (df_sub.artist == artist),'reissue']=1
			old=dates.pop(dates.index(min(dates)))

	for x in df_sub.iterrows():
		artist=x[1].artist
		title=x[1].title
		release=x[1].release
		artist_releases=df_sub.loc[(df_sub.artist == artist),'release']
		success_factor=chart_success(sum(artist_releases<=release))
		df_sub.loc[(df_sub.title == title) & (df_sub.artist == artist),'success']=success_factor

	df_sub.to_csv('data/dummy/'+file+'.tsv',sep='\t',index=False,encoding='utf8')
	print(file)
