"""Get Discogs genre for computing typicality"""

import numpy as np
import pandas as pd
import string
import ast
import math
import operator
from collections import Counter  
import random 
import discogs_client
import time


c_key= ###Discogs client key###
c_secret= ###Discogs client secret###

# Load project
d=discogs_client.Client('thesis_project')
d.set_consumer_key(c_key,c_secret)
d.get_authorize_url()

# Need new access token each run
verifier= ###Access token###
d.get_access_token(verifier)


# Stich all of the data sources together into a merged data frame
missing=[]
file_list=['number']+list(string.ascii_uppercase)

# Can get label data from Spotify by making requests to album associated with each track
# https://developer.spotify.com/documentation/web-api/reference/albums/get-album/
# Alternatively, using Discogs, you can get labels
# with open('data/major.txt','rb') as f:
# 	labels=f.readlines()
# labels=[x.split(' \n')[0].rstrip() for x in labels]
# sum([any([True if x.encode('utf8') in m_labels else False for x in ast.literal_eval(y)]) for y in df.label])


# Iterate through files
for fname in file_list:
	fpath='data/features/'+fname+'.tsv'
	df=pd.read_csv(fpath,sep='\t',encoding='utf8')

	# Discogs genre
	df['discog_genre']=''

	# Label
	df['label']=''

	# Associated members of each song
	df['members']=''

	for x in df.iterrows():
		artist=x[1].artist
		title=x[1].title

		artist=artist.replace('/',' ')
		title=title.replace('/',' ')

		q=artist+","+title
		results=d.search(q,type="release")
		time.sleep(2+np.random.randint(2))

		try:
			results=results[0]
			genre=[g for g in results.genres]
			label=[l.name for l in results.labels]
			members=[[m.name for m in art.members] for art in results.artists]
		except:
			print('Could not find song '+title+' by artist '+artist)
			missing.append((artist,title))

			genre=''
			label=''
			members=''

		df.loc[x[0],['discog_genre','label','members']]=[str(genre),str(label),str(members)]
	print(fname)
	df.to_csv('data/discog/'+fname+'.tsv',sep='\t',index=False,encoding='utf8')

# Write missing records to file
with open('data/discog/missing.tsv','wb') as f:
	f.write('artist\ttitle\n')
	for x in missing:
		artist=x[0].encode('utf8')
		title=x[1].encode('utf8')
		f.write(artist+'\t'+title+'\n')
