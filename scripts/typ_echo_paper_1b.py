""""Preparing features for critique model Spotify genre analog"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
import string
import ast
import copy
import math
import string

# Read in data 
fpath='data/genre_set.tsv'
df=pd.read_csv(fpath,sep='\t',encoding='utf8')
df.release=pd.to_datetime(df.release)
dates=df.release.unique()

# DataFrame for calculating differences between genres at each time index
genres=['hip','rap','rock','metal','folk','country','blues','r&b','soul','disco','funk','pop','none']
df_tg=pd.DataFrame(columns=genres+['weight'])
missing=[]

def format_echo(tempo,time_signature):
	"""Normalize tempo and set time signature control"""
	return (tempo/max(tempo)).as_matrix(), ((time_signature==4)).as_matrix()

df.tempo,df.time_signature=format_echo(df.tempo,df.time_signature)

def key_match(a,b):
	"""Check if keys match between songs"""
	return sum([x==y for x in a for y in b])/float(len(a)*len(b))

# Build average genre typicality DataFrame
for d in dates:
	gv=[]
	for g in range(len(genres)):
		record=df.loc[(df.release<=d) & (df.release>=d-np.timedelta64(52,'W'))&(df.genre==g),['acousticness',
			'danceability','energy','instrumentalness','liveness','speechiness','tempo','valence','mode']].copy()
		if len(record)==0:
			missing.append((d,g))
			print('No records found for genre '+g+' at date '+str(d))
			continue
		record=record.mean()
		gv.append([record,g])

	# Calculate cosine similarity weight between genres 
	for i in range(len(gv)):
		for j in range(i+1,len(gv)):
			genre_1=copy.copy(gv[i])
			genre_2=copy.copy(gv[j])
			weight=1-cosine(genre_1[0],genre_2[0])

			row=np.zeros(len(genres))
			row[genre_1[1]]=1
			row[genre_2[1]]=1
			row=row.tolist()+[weight]
			row=pd.DataFrame([row],columns=df_tg.columns)
			row=row.xs(0)
			row.name=d
			df_tg=df_tg.append(row)
	print("progress: "+str(np.where(dates==d)[0][0]/float(len(dates))))

def avg_typ(track_1,track_r,weights,genres):
	"""Find genre-weighted average typicality 

		Paramaters
		----------
		track_1 : Pandas DataFrame element
		Track of interest
		
		track_r : Pandas DataFrame 
		Related tracks that were active one year from the track's release
		
		weights : Pandas DataFrame
		DataFrame containing the genre weights at the release date
		
		genres : list 
		List of genres
	"""
	og_track_1=track_1.copy()
	agr_typ=0

	# Compare track of interest to related tracks 
	for x in track_r.iterrows():
		track_1=og_track_1.copy()
		track_2=x[1].copy()
		if track_1.genre==track_2.genre:
			weight=1
		else:
			weight=weights[(weights[genres[int(track_1.genre)]]==1)&(weights[genres[int(track_2.genre)]]==1)]['weight'].values[0]

		agr_typ+=weight*(1-cosine(track_1[:-1].astype(float),track_2[:-1].astype(float)))
	
	return agr_typ/len(track_r)

# Iterate through files alphabetically 
file_list=['number']+list(string.ascii_uppercase)
df['typ']=0
missing_typ=[]
for fname in file_list:
	if fname=='number':
		numbers=[False if x in string.ascii_uppercase else True for x in df.artist.str[0]]
		df_sub=df.copy()[numbers]
	else:
		df_sub=df.copy()[df.artist.str[0]==fname]

	# Compare each track with other tracks from the past year 
	for x in df_sub.iterrows():
		artist=x[1].artist
		title=x[1].title
		release=x[1].release
		track_1=x[1][['acousticness','danceability','energy','instrumentalness','liveness','speechiness',
			'tempo','valence','mode','genre']]
		track_r=df.loc[(df.release<=release) & (df.release>=release-np.timedelta64(52,'W')),['acousticness','danceability','energy',
			'instrumentalness','liveness','speechiness','tempo','valence','mode','genre']].drop(x[0])
		weights=df_tg.loc[df_tg.index==release]
		try:
			typ_score=avg_typ(track_1,track_r,weights,genres)
		except:
			print("No artists released in the previous year for track "+title+" by artist "+artist)
			missing_typ.append((artist,title))
			df_sub.drop(x[0],inplace=True)
		df_sub.loc[(df_sub.title == title) & (df_sub.artist == artist),'typ']=typ_score
	df_sub.to_csv('data/typ_paper_1b_2019/'+fname+'.tsv',sep='\t',index=False,encoding='utf8')
	print(fname)

# Write missing records to file 
with open('data/typ_paper_1b_2019/missing.tsv','wb') as f:
	f.write('date\tgenre\n')
	for x in missing:
		date=str(x[0]).encode('utf8')
		genre=str(x[1])
		f.write(date+'\t'+genre+'\n')

