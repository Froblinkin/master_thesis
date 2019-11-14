"""Prepare features for critique model"""

import pandas as pd
import numpy as np
import string
import matplotlib.pyplot as plt
import ast

# Stitch all of the records together 
frame=[]
file_list=['number']+list(string.ascii_uppercase)

for fname in file_list:
	fpath='data/typ/'+fname+'.tsv'
	df=pd.read_csv(fpath,sep='\t',encoding='utf8')
	frame.append(df)

df=pd.concat(frame,ignore_index=True)
df=df.dropna()

# Merge chart data with song records 
chart_path = 'data/chart_record.tsv'
chart=pd.read_csv(chart_path,sep='\t',index_col=0,encoding='utf8')
df_c=df.merge(chart)

# Peak position 
df['peak']=0

# Weeks on chart 
df['week']=0

# Long song control
df['long']=False

# Time block control
df['decade']=0

# Major label control
#df['major']=0

df.release=pd.to_datetime(df.release)

# Label songs with genre
genres=['Blues', "Children's", 'Classical', 'Electronic','Folk, World, & Country', 'Funk / Soul', 'Hip Hop', 'Jazz',
'Latin', 'Non-Music', 'Pop', 'Reggae', 'Rock','Stage & Screen']
for g in genres:
	df[g]=0

# Use a vector representation of genres, so songs can have multiple genre labels (crossover)
for x in df.iterrows():
	gv=[1 if g in x[1].discog_genre else 0 for g in genres]
	df.loc[x[0],genres+['crossover']]=gv+[sum(gv)>1]

# Major label feature not used in final analysis 
# with open('data/major.txt','rb') as f:
# 		labels=f.readlines()
# 		labels=[x.split(' \n')[0].rstrip() for x in labels]
# maj_labels=labels+[x.split('Records')[0].split('Recordings')[0].rsplit()[0] for x in labels if 'Records' in x or 'Recordings' in x]


for x in df.iterrows():
	artist=x[1].artist
	title=x[1].title
	release=x[1].release
	duration_ms=x[1].duration_ms
	labels=x[1].label
	labels=ast.literal_eval(labels)

	# Time block
	decade=np.floor((release-np.datetime64('1957','Y'))/np.timedelta64(52,'W')/5)

	# Weeks on chart 
	chart_weeks=max(df_c.loc[(df_c.artist==artist) & (df_c.title==title),'week'])

	# Peak position 
	peak=min(df_c.loc[(df_c.artist==artist) & (df_c.title==title),'peak'])

	# Long song control 
	len_record=df.loc[(df.release<=release) & (df.release>=release-np.timedelta64(52,'W')),'duration_ms'].tolist()
	long_threshold=np.mean(len_record)+np.std(len_record)*2

#	major=any([True for l in labels if l.encode('utf8') in maj_labels])

	df.loc[(df.artist==artist) & (df.title==title),['week','long','peak','decade']]=[chart_weeks,
		long_threshold<duration_ms,peak,decade]

# Write song records to file 
df.set_index('track_id',inplace=True)
df.drop(['index','artist','title','duration_ms','loudness','release','mxm_artist','mxm_title','similarity','genres','genre','lyrics','members','label','discog_genre'],axis=1,inplace=True)
df=df*1
df.rename(index=str, columns={genres[1]:"Child"}).to_csv('data/logit_data_sp_echo.tsv',sep='\t',index=False,encoding='utf8')