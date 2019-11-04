"""Get lyrics from MSD and match records with Billboard Hot 100"""

import pandas as pd
import sqlite3
import re
import string
from difflib import SequenceMatcher

# File paths for MSD data and Billboard records
metadata_db_path = 'data/MSD/MSongsDB/track_metadata.db'
lyrics_db_path = 'data/MSD/MSongsDB/mxm_dataset.db'
chart_path = 'data/chart_record.tsv'


# Get song-artist pairs from Billboard
chart=pd.read_csv(chart_path,sep='\t',index_col=0,encoding='utf8')
df=chart[['artist','title']].as_matrix()
df=[list(x) for x in set(tuple(x) for x in df)]
df=pd.DataFrame(df)
df.columns=['artist','title']

# Get song-artist pairs from MSD
conn_mdb = sqlite3.connect(metadata_db_path)
conn_ldb = sqlite3.connect(lyrics_db_path)
res=conn_mdb.execute("SELECT track_id, artist_name, title  FROM songs")
sa_pair=res.fetchall()
sa=pd.DataFrame(sa_pair)
sa.columns=['track_id','artist','title']
sa['title_mod']=''
conn_mdb.close()


def title_mod(title):
	"""Filter out specific keywords from title"""
	title_mod=re.split(' \[',title,1)[0]
	title_mod=re.split(' \(',title_mod,1)[0]
	title_mod=re.split(' (?i)feat(-?)',title_mod,1)[0]
	title_mod=re.split(' (?i)ft\.(-?)',title_mod,1)[0]
	return title_mod.lower()

def artist_mod(artist):
	"""Filter out specific keywords from artist name"""
	artist_mod=re.sub(' Featuring ',',',artist)
	artist_mod=re.sub(' & ',',',artist_mod)
	artist_mod=re.sub(', ',',',artist_mod)
	artist_mod=re.split(' Or ',artist_mod,1)[0]
	return artist_mod.lower()


def similar(a,b):
	"""Compares two sequences of strings and returns their similarity ratio"""
	return SequenceMatcher(None,a,b).ratio()

# Find modified titles 
for x in sa.iterrows():
	title=x[1].title
	sa.iloc[x[0]]['title_mod']=title_mod(title)

# Find the optimal match between records based on string similarities
file_list=['number']+list(string.ascii_uppercase)
for fname in file_list:
	if fname=='number':
		numbers=[False if x in string.ascii_uppercase else True for x in df.artist.str[0]]
		df_sub=df.copy()[numbers]
	else:
		df_sub=df.copy()[df.artist.str[0]==fname]

	df_sub['lyrics']=''
	df_sub['mxm_artist']=''
	df_sub['mxm_title']=''
	df_sub['similarity']=0
	df_sub['track_id']=''

	# Get all possible matches between the datasets and evaluate them
	for x in df_sub.iterrows():
		artist=x[1].artist
		title=x[1].title
		pos_matches=sa.loc[(sa.title_mod == title_mod(title))]
		old_sim = 0
		for y in pos_matches.iterrows():
			track_id=y[1].track_id
			mxm_artist=y[1].artist
			mxm_title=y[1].title

			res_lyrics = conn_ldb.execute("SELECT word, count FROM lyrics WHERE track_id=? ORDER BY count DESC", (track_id, ))
			lyrics = res_lyrics.fetchall()
			new_sim=similar(artist.lower(),mxm_artist.lower())

			# Baseline similarity of 0.6
			if new_sim>0.6 and new_sim>old_sim and artist.lower()[0]==mxm_artist.lower()[0] and len(lyrics) > 0:
				df_sub.loc[(df_sub.title == title) & (df_sub.artist == artist),['lyrics','mxm_artist','mxm_title','similarity','track_id']]=[(lyrics,),mxm_artist,mxm_title,new_sim,track_id]
				old_sim=new_sim

	df_lyrics=df_sub[df_sub.lyrics!=''].copy() 
	with open('data/BOW/'+fname+'.tsv','wb') as f:
		f.write('track_id\tlyrics\n')
		for x in df_lyrics.iterrows():
			track_id=x[1].track_id
			lyrics=x[1].lyrics
			f.write(track_id+'\t'+str(lyrics)+'\n')
	df_sub.drop('lyrics',axis=1).to_csv('data/BOW_id/'+fname+'.tsv',sep='\t',index=False,encoding='utf8')
	print(fname)
conn_ldb.close()