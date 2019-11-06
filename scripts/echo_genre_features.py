"""Request The Echo Nest audio features from Spotify"""

import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import string
import time
import ast

# Credentials
cid= ###Spotify client ID###
cs= ###Spotify client secret###

# connect to spotify API through spotipy
client_credentials_manager = SpotifyClientCredentials(client_id=cid,client_secret=cs)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# list for ids with no features
missing=[]

# iterate through files containing spotify ids 
file_list=['number']+list(string.ascii_uppercase)
for fname in file_list:
	file_path='data/Echo/'+fname+'.tsv'
	df=pd.read_csv(file_path,sep='\t',encoding='utf8')
	df=df.dropna()
	df.artist_ids=[ast.literal_eval(x) for x in df.artist_ids]

	# The Echo Nest features
	df['energy']=-1
	df['liveness']=-1
	df['tempo']=-1
	df['speechiness']=-1
	df['acousticness']=-1
	df['instrumentalness']=-1
	df['time_signature']=-1
	df['danceability']=-1
	df['key']=-1
	df['duration_ms']=-1
	df['loudness']=-1
	df['valence']=-1
	df['mode']=-1

	# Genres is a list of tags 
	df['genres']=''

	artist_list=[x for y in df.artist_ids.tolist() for x in y]
	artist_list=list(set(artist_list))
	artist_dict={}

	# Request artist features in batches of 50
	artist_range=range(len(artist_list)/50+(len(artist_list)%50>0))
	for ind in artist_range:
		if ind==max(artist_range):
			artist_ids=artist_list[ind*50:len(artist_list)]
			end=len(artist_list)-ind*50
		else:
			artist_ids=artist_list[ind*50:(ind+1)*50]
			end=50
		artists=spotify.artists(artist_ids)
		time.sleep(5+np.random.randint(5))
		for i in range(end):
			artist_dict[artists['artists'][i]['id']]=artists['artists'][i]['genres']


	# Request song features in batches of 100 
	track_range=range(len(df)/100+(len(df)%100>0))
	for ind in track_range:
		if ind==max(track_range):
			ids=df.id[ind*100:len(df)]
			end=len(df)-ind*100
		else:
			ids=df.id[ind*100:(ind+1)*100]
			end=100
		features=spotify.audio_features(ids.tolist())
		time.sleep(5+np.random.randint(5))
		for i in range(end):
			df_index=i+ind*100
			record=df.iloc[df_index]
			artist=record.artist
			title=record.title
			track_id=record.id
			artist_ids=record.artist_ids
			genres=[artist_dict[x] for x in artist_ids]
			genres=list(set([x for y in genres for x in y]))

			# Check that records are correct
			if features[i] is not None and track_id==features[i]['id']:
				df.loc[(df.title == title) & (df.artist == artist)]=[artist,title,track_id,str(artist_ids),
					features[i]['energy'],features[i]['liveness'],features[i]['tempo'],features[i]['speechiness'],
					features[i]['acousticness'],features[i]['instrumentalness'],features[i]['time_signature'],
					features[i]['danceability'],features[i]['key'],features[i]['duration_ms'],features[i]['loudness'],
					features[i]['valence'],features[i]['mode'],str(genres)]
			else:
				print('Empty feature set!')
				missing.append((artist,title))
	df.drop(['id','artist_ids'],axis=1).to_csv('data/features/'+fname+'.tsv',sep='\t',index=False,encoding='utf8')
	print(fname)

# Write missing records to file
with open('data/features/missing.tsv','wb') as f:
	f.write('artist\ttitle\n')
	for x in missing:
		artist=x[0].encode('utf8')
		title=x[1].encode('utf8')
		f.write(artist+'\t'+title+'\n')
