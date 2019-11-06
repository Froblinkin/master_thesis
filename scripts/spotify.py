"""Get Spotify song IDs for as many Billboard songs as possible"""

import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import string
import time
import re 

chart_path = 'data/chart_record.tsv'
chart=pd.read_csv(chart_path,sep='\t',index_col=0,encoding='utf8')
df=chart[['artist','title']].as_matrix()
df=[list(x) for x in set(tuple(x) for x in df)]
df=pd.DataFrame(df)
df.columns=['artist','title']

# Credentials
cid = ###Spotify client ID###
cs = ###Spotify client Secret###

# Connect to Spotify API through Spotipy
client_credentials_manager = SpotifyClientCredentials(client_id=cid,client_secret=cs)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def find_spotify_id(artist,title,df_sub,miss_count,missing):
	"""Find spotify ID using artist and song strings 

		Parameters
		----------
		artist : string
		Artist name.

		title : string
		Song title.

		df_sub : Pandas DataFrame
		Chart records from Billboard.

		miss_count : int
		Count of missed songs.

		missing : list 
		List of missing songs. 
		
		Notes
		-----
		Uses a black box search API from Spotify to match records and takes the first match. 
	"""

	# Filtering 
	artist_mod=re.sub(' Featuring ',' ',artist)
	artist_mod=re.sub(' & ',' ',artist_mod)
	artist_mod=re.split(' Or ',artist_mod,1)[0]

	try:
		result=spotify.search(q='artist:'+artist_mod+' track:'+title,type='track',limit=1)
		tid=result['tracks']['items'][0]['id']
		aids=[x['id'] for x in result['tracks']['items'][0]['artists']]
		df_sub.loc[(df_sub.title == title) & (df_sub.artist == artist),['artist_ids','id']]=[str(aids),tid]
	except:
		miss_count+=1
		print('API failure #' + str(miss_count) + ' for song: '+title+' by artist: '+artist)
		missing.append((artist,title))
	return miss_count,missing

# Query Spotify for artists with numbers starting their name 
numbers=[False if x in string.ascii_uppercase else True for x in df.artist.str[0]]
df_sub=df.copy()[numbers]

df_sub['id']=''
df_sub['artist_ids']=''
missing=[]
miss_count=0

for x in df_sub.iterrows():
	artist=x[1].artist
	title=x[1].title
	time.sleep(2+np.random.randint(3))
	miss_count,missing=find_spotify_id(artist,title,df_sub,miss_count,missing)
df_sub.to_csv('data/Echo/number.tsv',sep='\t',index=False,encoding='utf8')
print('number')

# Query Spotify for artists with letters starting their name 
for letter in string.ascii_uppercase:
	df_sub=df.copy()[df.artist.str[0]==letter]
	df_sub['id']=''
	df_sub['artist_ids']=''
	for x in df_sub.iterrows():
		artist=x[1].artist
		title=x[1].title
		time.sleep(2+np.random.randint(3))
		miss_count,missing=find_spotify_id(artist,title,df_sub,miss_count,missing)
	df_sub.to_csv('data/Echo/'+letter+'.tsv',sep='\t',index=False,encoding='utf8')
	print(letter)

# Write missing records to file
with open('data/Echo/missing.tsv','wb') as f:
	f.write('artist\ttitle\n')
	for x in missing:
		artist=x[0].encode('utf8')
		title=x[1].encode('utf8')
		f.write(artist+'\t'+title+'\n')
