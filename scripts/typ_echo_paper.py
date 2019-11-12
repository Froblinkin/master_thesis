"""Compute genre-weighted typicality as described by Askin and Mauskapf"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
import string
import ast
import copy
import math
import string

fpath='data/genre_set.tsv'
df=pd.read_csv(fpath,sep='\t',encoding='utf8')


# Convert the release dates to datetime objects 
df.release=pd.to_datetime(df.release)
dates=df.release.unique()

# Discogs genre 
mat=df.discog_genre.as_matrix()
mat=[ast.literal_eval(x) for x in mat]
genres=['Blues', "Children's", 'Classical', 'Electronic','Folk, World, & Country', 'Funk / Soul', 'Hip Hop', 'Jazz',
'Latin', 'Non-Music', 'Pop', 'Reggae', 'Rock','Stage & Screen']

# Temporal genre data frame
df_tg=pd.DataFrame(columns=genres+['weight'])
missing=[]

def format_echo(tempo,time_signature):
	"""Simple method to normalize tempo and time signature"""
	return (tempo/max(tempo)).as_matrix(), ((time_signature==4)).as_matrix()

df.tempo,df.time_signature=format_echo(df.tempo,df.time_signature)

def key_match(a,b):
	"""Check for key match"""
	return sum([x==y for x in a for y in b])/float(len(a)*len(b))

# Iterate through dates and get the average distance between songs from genres over time 
for d in dates:
	gv=[]
	# Iterate through genres
	for g in genres:
		# Find the mean values for tracks with release up to 1 year before date and with a specific genre
		record=df.loc[(df.release<=d) & (df.release>=d-np.timedelta64(52,'W'))&(df.discog_genre.str.contains(g)),['acousticness',
			'danceability','energy','instrumentalness','liveness','speechiness','tempo','valence','mode']].copy()
		if len(record)==0:
			missing.append((d,g))
			#print('No records found for genre '+g+' at date '+str(d))
			continue
		#key=record['key'].tolist()
		record=record.mean()
		gv.append([record,g])

	# Calculate the weight between genres
	for i in range(len(gv)):
		for j in range(i+1,len(gv)):
			genre_1=copy.copy(gv[i])
			genre_2=copy.copy(gv[j])

			#genre_1[0].key=1
			#genre_2[0].key=key_match(genre_1[1],genre_2[1])

			# Cosine similarity 
			weight=1-cosine(genre_1[0],genre_2[0])

			# Store weights in DataFrame
			row=np.zeros(len(genres))
			row[genres.index(genre_1[1])]=1
			row[genres.index(genre_2[1])]=1
			row=row.tolist()+[weight]
			row=pd.DataFrame([row],columns=df_tg.columns)
			row=row.xs(0)
			row.name=d
			df_tg=df_tg.append(row)
	print("progress: "+str(np.where(dates==d)[0][0]/float(len(dates))))

def avg_typ(track_1,track_r,weights,genres):
	"""Find genre-weighted average typicality 

		Parameters
		----------
		track_1 : Pandas DataFrame element
		Track of interest
		track_r : Pandas DataFrame
		Related tracks that were active one year from the track's release
		weights : Pandas DataFrame 
		Genre weights at the release date
		genres : List
		Genres used
	"""
	# Song record that can be manipulated
	og_track_1=track_1.copy()

	# Aggregate typicality 
	agr_typ=0

	# Iterate through comparison tracks
	for x in track_r.iterrows():
		track_1=og_track_1.copy()
		track_2=x[1].copy()

		# Matching genres, no need to change weight
		if track_1.discog_genre==track_2.discog_genre:
			weight=1
		# Different genres, find average distance between genres 
		else:
			wm=[]
			genre_1=[x for x in genres if x in track_1.discog_genre]
			genre_2=[x for x in genres if x in track_2.discog_genre]

			for g1 in genre_1:
				for g2 in genre_2:
					if g1==g2:
						wm.append(1)
					else:
						wm.append(weights[(weights[g1]==1)&(weights[g2]==1)]['weight'].values[0])
			# Normalize weight
			weight=sum(wm)/len(genre_1)/len(genre_2)

		# track_1.key=1
		# track_2.key=key_match([track_1.key],[track_2.key])

		agr_typ+=weight*(1-cosine(track_1[:-1].astype(float),track_2[:-1].astype(float)))

	# Normalize aggregate similarity 
	return agr_typ/len(track_r)


# Iterate through files alphabetically
file_list=['number']+list(string.ascii_uppercase)

# Typicality 
df['typ']=0

# Missing records
missing_typ=[]


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

		# Song record
		track_1=x[1][['acousticness','danceability','energy','instrumentalness','liveness','speechiness',
			'tempo','valence','mode','discog_genre']]

		# Songs released in the previous 52 weeks
		track_r=df.loc[(df.release<=release) & (df.release>=release-np.timedelta64(52,'W')),['acousticness','danceability','energy',
			'instrumentalness','liveness','speechiness','tempo','valence','mode','discog_genre']].drop(x[0])

		# Genre weights from past 52 weeks
		weights=df_tg.loc[df_tg.index==release]

		try:
			typ_score=avg_typ(track_1,track_r,weights,genres)
		except:
			print("No artists released in the previous year for track "+title+" by artist "+artist)
			missing_typ.append((artist,title))
			df_sub.drop(x[0],inplace=True)
			
		df_sub.loc[(df_sub.title == title) & (df_sub.artist == artist),'typ']=typ_score
	df_sub.to_csv('data/typ/'+fname+'.tsv',sep='\t',index=False,encoding='utf8')
	print(fname)

# Write missing records to file
with open('data/typ/missing.tsv','wb') as f:
	f.write('date\tgenre\n')
	for x in missing:
		date=str(x[0]).encode('utf8')
		genre=x[1].encode('utf8')
		f.write(date+'\t'+genre+'\n')
