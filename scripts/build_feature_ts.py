"""Contruct song features as time series """

import numpy as np
import pandas as pd
import string 
import matplotlib.pyplot as plt

# Read The Echo Nest features into DataFrame
frame=[]
file_list=['number']+list(string.ascii_uppercase)
for fname in file_list:
	fpath='data/model/Echo/'+fname+'.tsv'
	df=pd.read_csv(fpath,sep='\t',encoding='utf8')
	frame.append(df)
df=pd.concat(frame,ignore_index=True)
df_echo=df.rename(columns={'typ':'echo_typ','genre_typ':'echo_genre_typ','artist_typ':'echo_artist_typ'})

frame=[]

# model_num can be 0 to 3
model_num=1

# Merge topic models into DataFrame
for fname in file_list:
	fpath='data/model/'+str(model_num)+'/'+fname+'.tsv'
	df=pd.read_csv(fpath,sep='\t',encoding='utf8')
	frame.append(df)
df=pd.concat(frame,ignore_index=True)
df=df.join(df_echo[['echo_typ','echo_genre_typ','echo_artist_typ']])

# Truncated The Echo Nest similarity histogram
fig, ax = plt.subplots(figsize=(8,6))
df[df.echo_typ>0.025].echo_typ.hist(bins=np.array(100),alpha=0.75)
df[df.echo_genre_typ>0.025].echo_genre_typ.hist(bins=np.array(100),alpha=0.75)
df[df.echo_artist_typ>0.025].echo_artist_typ.hist(bins=np.array(100),alpha=0.75)
plt.ylabel('Count')
plt.xlabel('Similarity')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(False)
plt.legend(['Chart','Genre','Artist'])

# Truncated topic model similarity histograms (depends on model_num)
fig, ax = plt.subplots(figsize=(8,6))
df[df.typ>0.025].typ.hist(bins=np.array(100),alpha=0.75)
df[df.genre_typ>0.025].genre_typ.hist(bins=np.array(100),alpha=0.75)
df[df.artist_typ>0.025].artist_typ.hist(bins=np.array(100),alpha=0.75)
plt.ylabel('Count')
plt.xlabel('Similarity')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(False)
plt.legend(['Chart','Genre','Artist'])

# Expanded genre variables to track change in frequency of each genre 
genres=['hip','rap','rock','metal','folk','country','blues','r&b','soul','disco','funk','pop','none']
for g in genres:
	df[g]=0
for x in df.iterrows():
	df.loc[df.index==x[0],genres[x[1].genre]]=1

# Expanded key variables 
keys=['key0','key1','key2','key3','key4','key5','key6','key7','key8','key9','key10','key11']
for k in keys:
	df[k]=0
for x in df.iterrows():
	df.loc[df.index==x[0],keys[x[1].key]]=1

# Merge chart data into existing DataFrame to get detailed chart data, a song record for each week
cpath="data/chart_record.tsv"
df_chart=pd.read_csv(cpath,sep="\t",encoding="utf-8")
df=df_chart.merge(df)

# Convert date to index for time series
df.date=pd.to_datetime(df.date)
dates=np.sort(np.unique(df.date.tolist()))
df.index=df.date

# Count of songs histogram 
fig, ax = plt.subplots(figsize=(8,6))	
df.date.hist(bins=len(dates))
plt.ylabel('Count')
plt.xlabel('Date')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.grid(False)
plt.show()

# Feature sets used in temporal analysis 

# 10 topic model 
# features=["energy","liveness","tempo","speechiness",
# 	"acousticness","instrumentalness","time_signature","danceability",
# 	"valence","mode","0","1","2","3","4","5","6","7","8","9","typ","echo_typ",
# 	'hip','rap','rock','metal','folk','country','blues','r&b','soul','disco','funk','pop','none',
# 	'key0','key1','key2','key3','key4','key5','key6','key7','key8','key9','key10','key11']

# 80 topic model 
# features=["energy","liveness","tempo","speechiness",
# 	"acousticness","instrumentalness","time_signature","danceability",
# 	"valence","mode",
# 	"0","1","2","3","4","5","6","7","8","9",
# 	"10","11","12","13","14","15","16","17","18","19",
# 	"20","21","22","23","24","25","26","27","28","29",
# 	"30","31","32","33","34","35","36","37","38","39",
# 	"40","41","42","43","44","45","46","47","48","49",
# 	"50","51","52","53","54","55","56","57","58","59",
# 	"60","61","62","63","64","65","66","67","68","69",
# 	"70","71","72","73","74","75","76","77","78","79",
# 	"typ","echo_typ",
# 	'hip','rap','rock','metal','folk','country','blues','r&b','soul','disco','funk','pop','none',
# 	'key0','key1','key2','key3','key4','key5','key6','key7','key8','key9','key10','key11']

# 20 topic model 
features=["energy","liveness","tempo","speechiness",
	"acousticness","instrumentalness","time_signature","danceability",
	"valence","mode",
	"0","1","2","3","4","5","6","7","8","9",
	"10","11","12","13","14","15","16","17","18","19",
	"typ","echo_typ",
	'hip','rap','rock','metal','folk','country','blues','r&b','soul','disco','funk','pop','none',
	'key0','key1','key2','key3','key4','key5','key6','key7','key8','key9','key10','key11']
df=df[features]
df_features=pd.DataFrame(columns=features)

# Normalize feature values at each week based on the number of songs on the charts that we have records for 
for d in dates:
	df_sub=df.loc[df.index==d].astype('float64')
	df_features.loc[d]=df_sub.sum()/np.array([len(df_sub) if f not in genres else 1 for f in features])

# Write to file
df_features.to_csv('data/final/model_tm1.tsv',sep='\t',index=True,encoding='utf8')