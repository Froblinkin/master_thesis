"""Construct song record chart time series"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
import string
import ast
import copy
import math
import string


# Get chart records 
chart_path='data/no_folder/chart_record.tsv'
chart=pd.read_csv(chart_path,sep='\t',index_col=0,encoding='utf8')

# Get artist song pairs 
dpath='data/no_folder/genre_set.tsv'
df=pd.read_csv(dpath,sep='\t',encoding='utf8')
df=df[['artist','title']]

ts={}
empty_count=[]

# Gather chart data for each song 
for x in df.iterrows():
	count=[]
	artist=x[1].artist
	title=x[1].title

	# Chart data sorted by date 
	position=chart.loc[(chart.artist==artist)&(chart.title==title),'position'].sort_index()
	date=position.keys().tolist()
	position=position.tolist()

	if artist not in ts:
		ts[artist]={}
	ts[artist][title]={}
	ts[artist][title]['position']=position
	ts[artist][title]['date']=date

	ts_position=copy.copy(position)
	date=pd.to_datetime(date)

	# Fill empty dates where a song falls off the chart for some time only to return later 
	for i in range(1,len(date)):
		date_diff=int(np.ceil((date[i]-date[i-1])/np.timedelta64(7,'D')))
		if date_diff==1:
			continue
		else:
			for j in range(date_diff-1):
				ts_position.insert(i,None)
			count.append(date_diff)
	empty_count.append(count)

	ts[artist][title]['ts']=ts_position


# Write time series to file
fpath='data/ts_ngp.tsv'
with open(fpath,'wb') as f:
	for x in df.iterrows():
		artist=x[1].artist
		title=x[1].title
		position=ts[artist][title]['position']
		f.write(artist.encode('utf8')+'\t'+title.encode('utf8'))
		for y in position:
			f.write('\t'+str(y))
		f.write('\n')

