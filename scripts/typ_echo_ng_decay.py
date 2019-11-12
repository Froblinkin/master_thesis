"""Compute the weighted-similarity score for each song based on its The Echo Nest features"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
import string
import ast
import copy
import math
import string
import pdb


def format_echo(tempo,time_signature):
	"""Normalize tempo and time signature features from The Echo Nest"""
	return (tempo/max(tempo)).as_matrix(), ((time_signature==4)).as_matrix()

def avg_typ(track_1,track_r):
	"""Find time-decayed typicality between some track and other chart or genre chart tracks

		Parameters
		----------
		track_1 : Pandas DataFrame element
		Track of interest that everything is compared with
		track_r : Pandas DataFrame
		Related tracks that were active one year from the track's release

		Notes
		-----
		Returns time-weighted cosine similaritiy scores

	"""
	# Time weight decay 
	track_r['decay']=0

	# Aggregate chart similarity
	agr_typ=0

	# Aggregate genre similarity 
	agr_genre_typ=0

	# Iterate through tracks 
	for x in track_r.iterrows():

		# Check if keys match (some controls used for similarity calculations)
		track_1_copy=track_1.copy()
		track_2=x[1].copy()
		key_match=track_1.key==track_2.key
		if key_match==1:
			track_1_copy.key=key_match
			track_2.key=key_match
		else:
			track_1_copy.key=0
			track_2.key=key_match

		# Compute week decay
		weeks=(track_1.release-track_2.release).days/7.0
		decay=np.exp(-weeks/52)

		# Aggregate time-weighted song similarities together 
		typ=decay*(1-cosine(track_1_copy[:-2].astype(float),track_2[:-3].astype(float)))
		agr_typ+=typ
		if track_1.genre==track_2.genre:
			agr_genre_typ+=typ
		track_r.loc[x[0],'decay']=decay	
	
	# Return normalized similarities
	return agr_typ/sum(track_r['decay']), (agr_genre_typ+0.0001)/(sum(track_r[track_r.genre==track_1.genre]['decay'])+0.01)

def artist_typ(track_1,track_a):
	"""Find time-decayed artist for an artist's track and previous works

		Parameters
		----------
		track_1 : Pandas DataFrame element
		Track of interest that everything is compared with
		track_r : Pandas DataFrame
		Related tracks that were active one year from the track's release

		Notes
		-----
		Returns time-weighted cosine similaritiy score for artist
	"""
	# Time decay
	track_a['decay']=0

	# Aggregate similarity 
	agr_typ=0

	# Iterate through tracks
	for x in track_a.iterrows():

		# Check if keys match
		track_1_copy=track_1.copy()
		track_2=x[1].copy()
		key_match=track_1.key==track_2.key
		if key_match==1:
			track_1_copy.key=key_match
			track_2.key=key_match
		else:
			track_1_copy.key=0
			track_2.key=key_match

		# Calculate decay 
		weeks=(track_1.release-track_2.release).days/7.0
		decay=np.exp(-weeks/52)

		# Score the song and update
		typ=decay*(1-cosine(track_1_copy[:-2].astype(float),track_2[:-3].astype(float)))
		agr_typ+=typ
		track_a.loc[x[0],'decay']=decay	

	# Return normalized similarity 
	return (agr_typ+0.0001)/(sum(track_a['decay'])+0.01)



# Read in file
fpath='data/genre_set.tsv'
df=pd.read_csv(fpath,sep='\t',encoding='utf8')

# Convert dates, tempo, and time_signature
df.release=pd.to_datetime(df.release)
dates=df.release.unique()
df.tempo,df.time_signature=format_echo(df.tempo,df.time_signature)

# Typicality measures
df['typ']=0
df['genre_typ']=0
df['artist_typ']=0

# Iterate through tracks by artist name and calculate typicality measures
file_list=['number']+list(string.ascii_uppercase)
for fname in file_list:
	if fname=='number':
		numbers=[False if x in string.ascii_uppercase else True for x in df.artist.str[0]]
		df_sub=df.copy()[numbers]
	else:
		df_sub=df.copy()[df.artist.str[0]==fname]

	for x in df_sub.iterrows():
		artist=x[1].artist
		title=x[1].title
		release=x[1].release

		# Song of interest
		track_1=x[1][['acousticness','danceability','energy','key','instrumentalness','liveness','mode','speechiness',
			'tempo','time_signature','valence','genre','release']]

		# Songs released 52 weeks prior
		track_r=df.loc[(df.release<=release) & (df.release>=release-np.timedelta64(52,'W')),['acousticness','danceability','energy','key',
			'instrumentalness','liveness','mode','speechiness','tempo','time_signature','valence','genre','release']].drop(x[0])
			
		typ,genre_typ=avg_typ(track_1,track_r)

		# Songs released by the same artist at an earleir date 
		track_a=df.loc[(df.release<=release) & (df.artist==artist),['acousticness','danceability','energy','key',
			'instrumentalness','liveness','mode','speechiness','tempo','time_signature','valence','genre','release']].drop(x[0])

		art_typ=artist_typ(track_1,track_a)
		df_sub.loc[(df_sub.title == title) & (df_sub.artist == artist),['typ','genre_typ','artist_typ']]=typ,genre_typ,art_typ

	df_sub.to_csv('data/model/echo/'+fname+'.tsv',sep='\t',index=False,encoding='utf8')
	print(fname)