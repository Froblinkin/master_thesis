"""Prepare features for Spotify genre critique analog"""

import pandas as pd
import numpy as np
import string
import matplotlib.pyplot as plt
import ast

# Stich records together
frame=[]
file_list=['number']+list(string.ascii_uppercase)

for fname in file_list:
	fpath='data/typ_paper_1b/'+fname+'.tsv'
	df=pd.read_csv(fpath,sep='\t',encoding='utf8')
	frame.append(df)

df=pd.concat(frame,ignore_index=True)
df=df.dropna()

chart_path = 'data/chart_record.tsv'
chart=pd.read_csv(chart_path,sep='\t',index_col=0,encoding='utf8')
df_c=df.merge(chart)

df['peak']=0
df['week']=0
df['long']=False
df['decade']=0
df.release=pd.to_datetime(df.release)

# Expand genre 
genres=['hip','rap','rock','metal','folk','country','blues','r&b','soul','disco','funk','pop','none']
for g in genres:
	df[g]=0
for x in df.iterrows():
	gv=[1 if x[1].genre==g else 0 for g in range(len(genres))]
	df.loc[x[0],genres]=gv

# Find peak position and weeks on chart for each song along with control for long songs and time block
for x in df.iterrows():
	print(x[0])
	artist=x[1].artist
	title=x[1].title
	release=x[1].release
	duration_ms=x[1].duration_ms
	labels=x[1].label
	labels=ast.literal_eval(labels)

	decade=np.floor((release-np.datetime64('1957','Y'))/np.timedelta64(52,'W')/5)
	chart_weeks=max(df_c.loc[(df_c.artist==artist) & (df_c.title==title),'week'])
	peak=min(df_c.loc[(df_c.artist==artist) & (df_c.title==title),'peak'])
	len_record=df.loc[(df.release<=release) & (df.release>=release-np.timedelta64(52,'W')),'duration_ms'].tolist()
	long_threshold=np.mean(len_record)+np.std(len_record)*2

	df.loc[(df.artist==artist) & (df.title==title),['week','long','peak','decade']]=[chart_weeks,
		long_threshold<duration_ms,peak,decade]

# Write features to file
df.set_index('track_id',inplace=True)
df.drop(['index','artist','title','duration_ms','loudness','release','mxm_artist','mxm_title','similarity','genres','genre','lyrics','members','label','discog_genre'],axis=1,inplace=True)
df=df*1
df.to_csv('data/paper_1b.tsv',sep='\t',index=False,encoding='utf8')



