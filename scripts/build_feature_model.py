"""Prepare song features for use in models"""

import numpy as np
import pandas as pd
import string 

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

# model_num refers to the topic model
# 0 : 10 topics; 1 : 20 topics; 2 : 40 topics; 3 : 80 topics
model_num=0

# Merge topic mixture features into existing data
for fname in file_list:
	fpath='data/model/'+str(model_num)+'/'+fname+'.tsv'
	df=pd.read_csv(fpath,sep='\t',encoding='utf8')
	frame.append(df)
df=pd.concat(frame,ignore_index=True)
df=df.join(df_echo[['echo_typ','echo_genre_typ','echo_artist_typ']])

# Get five year time blocks for date of release control
date_range=[]
for i in range((2012-1958)/5+int((2012-1958)%5>0)+1):
	date_range.append(np.datetime64('1958','Y')+np.timedelta64(5,'Y')*i)
df.release=pd.to_datetime(df.release)

# Time block control
df['time']=0

# Long song control
df['long']=0

# Set controls for time blocks and long song 
for x in df.iterrows():
	artist=x[1].artist
	title=x[1].title
	release=x[1].release
	duration=x[1].duration_ms

	# Long song threshold is set as two standard deviations above the average song length within the last year
	len_record=df.loc[(df.release<=release) & (df.release>=release-np.timedelta64(52,'W')),'duration_ms'].tolist()
	long_threshold=np.mean(len_record)+np.std(len_record)*2

	time_block=[idx for idx,x in enumerate(date_range) if release<x][0]

	df.loc[(df.artist==artist) & (df.title==title),['time','long']]=[time_block,long_threshold<duration]

# Get target variable class labels
fpath='data/clustered_df.tsv'
df_cluster=pd.read_csv(fpath,sep='\t',encoding='utf8')
df['interval']=df_cluster.cmb
df['align']=df_cluster.cluster

# Reorganize features from DataFrame
if model_num==0:	
	features=["energy","liveness","tempo","speechiness","acousticness","instrumentalness","time_signature","danceability","key",
				"valence","mode","reissue","success","genre","crossover",
				"0","1","2","3","4","5","6","7","8","9",
				"typ","genre_typ","artist_typ","echo_typ","echo_genre_typ","echo_artist_typ","time","long","interval","align"]
elif model_num==1:
	features=["energy","liveness","tempo","speechiness","acousticness","instrumentalness","time_signature","danceability","key",
				"valence","mode","reissue","success","genre","crossover",
				"0","1","2","3","4","5","6","7","8","9",
				"10","11","12","13","14","15","16","17","18","19",
				"typ","genre_typ","artist_typ","echo_typ","echo_genre_typ","echo_artist_typ","time","long","interval","align"]
elif model_num==2:
	features=["energy","liveness","tempo","speechiness","acousticness","instrumentalness","time_signature","danceability","key",
				"valence","mode","reissue","success","genre","crossover",
				"0","1","2","3","4","5","6","7","8","9",
				"10","11","12","13","14","15","16","17","18","19",
				"20","21","22","23","24","25","26","27","28","29",
				"30","31","32","33","34","35","36","37","38","39",
				"typ","genre_typ","artist_typ","echo_typ","echo_genre_typ","echo_artist_typ","time","long","interval","align"]
elif model_num==3:
	features=["energy","liveness","tempo","speechiness","acousticness","instrumentalness","time_signature","danceability","key",
				"valence","mode","reissue","success","genre","crossover",
				"0","1","2","3","4","5","6","7","8","9",
				"10","11","12","13","14","15","16","17","18","19",
				"20","21","22","23","24","25","26","27","28","29",
				"30","31","32","33","34","35","36","37","38","39",
				"40","41","42","43","44","45","46","47","48","49",
				"50","51","52","53","54","55","56","57","58","59",
				"60","61","62","63","64","65","66","67","68","69",
				"70","71","72","73","74","75","76","77","78","79",
				"typ","genre_typ","artist_typ","echo_typ","echo_genre_typ","echo_artist_typ","time","long","interval","align"]

# Rescale features and write to file
df=df[features]
df_features=pd.DataFrame(columns=features)
df=df*1
df.to_csv('data/model'+str(model_num)+'_data.tsv',sep='\t',index=False,encoding='utf8')
