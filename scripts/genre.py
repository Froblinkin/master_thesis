"""Get genre labels for each song based on Spotify tags"""

import numpy as np
import pandas as pd
import string
import ast
import math
import operator
from collections import Counter  
import random 
import pprint

# Stitch data from separate sources together 
frame=[]
file_list=['number']+list(string.ascii_uppercase)

for fname in file_list:
	fpath='data/discog/'+fname+'.tsv'
	dpath='data/dummy/'+fname+'.tsv'
	bwidpath='data/BOW_id/'+fname+'.tsv'
	bwpath='data/BOW/'+fname+'.tsv'

	df1=pd.read_csv(fpath,sep='\t',encoding='utf8')
	df2=pd.read_csv(dpath,sep='\t',encoding='utf8')
	df3=pd.read_csv(bwidpath,sep='\t',encoding='utf8')
	df4=pd.read_csv(bwpath,sep='\t',encoding='utf8')

	df_f=df1.merge(df2)
	df_bw=df3.merge(df4)
	df=df_f.merge(df_bw)
	frame.append(df)

df=pd.concat(frame)
df=df.dropna().reset_index()

# Custom genres based on Spotify tags selected because they are substrings of some popular tags
genres=['rap','rock','metal','folk','country','blues','r&b','disco','pop','none']
count_list=[]

# Finding most frequent Spotify tags 
a=df.genres.tolist()
a=[ast.literal_eval(x) for x in a]
a=[x for y in a for x in y]
a_len=len(a)
a=Counter(a)
a={k:v for k, v in a.items() if v>=30}
a=Counter(a)

# Finding top tf-idf tags for each genre 
for g in genres:
	b=df[df.genres.str.contains(g)].genres.tolist()
	b=[ast.literal_eval(x) for x in b]
	b=[x for y in b for x in y]
	b_len=len(b)
	b=Counter(b)
	b={k:v for k, v in b.items() if v>=30}
	b=Counter(b)
	for w in b:
		b[w]=tuple([b[w]/float(b_len)*math.log(a_len)/(1+a[w]),a[w]])
	count_list.append(b.most_common(30))

genre_dict={}
for idx,g in enumerate(genres):
	for i in range(len(count_list[idx])):
		pprint.pprint(str(i+1)+' '+str(count_list[idx][i]))
	try:
		genre_dict[g]=count_list[idx][:int(raw_input())]
	except:
		genre_dict[g]=count_list[idx]

# Genre label
df['genre']=0

# Crossover control
df['crossover']=0

# Find the most likely genre for each song based on matches between the tags associated with each genre 
# and the artist's tags 
for x in df.iterrows():
	artist=x[1].artist
	title=x[1].title
	track_genres=x[1].genres
	genre_count={k:0 for k in genres}
	cross=0

	for g in genre_count:
		for w in genre_dict[g]:
			if w[0] in track_genres:
				genre_count[g]+=1

	for g in genre_count:
		if genre_count[g]>0:
			genre_count[g]=float(genre_count[g])/len(genre_dict[g])

	# No genre
	if sum(genre_count.values())==0:
		genre_count['none']=1
	# Tie between two genres 
	elif sum([1 for x in genre_count.values() if x==max(genre_count.values())])>1:
		cross=1

	# Some genre 
	mv=max(genre_count.values())
	max_genre=random.choice([k for (k,v) in genre_count.items() if v==mv])
	df.loc[(df.artist==artist) & (df.title==title),['genre','crossover']]=[genres.index(max_genre),cross]
df.to_csv('data/genre_set.tsv',sep='\t',index=False,encoding='utf8')

###################################################################################################

"""Visualizing genre agreement and distributions"""

import matplotlib.pyplot as plt
import seaborn as sns

# Genre overlap based on tags 
mat=np.zeros([len(genre_dict),len(genre_dict)])

for idx,x in enumerate(genres):
	for idy,y in enumerate(genres):
		mat[idx,idy]=len([l1 for l1 in genre_dict[x] if l1[0] in [l2[0] for l2 in genre_dict[y]]])

genres[0]='hip hop'
genres[7]='R&B'

fig, ax = plt.subplots()
sns.heatmap(mat,cmap=sns.cm.rocket_r)

for axis in [ax.xaxis, ax.yaxis]:
    axis.set(ticks=np.arange(0.5, len(genres)), ticklabels=genres)
plt.xticks(rotation=45) 
plt.yticks(rotation=0) 
plt.ylabel('Genre') 
plt.xlabel('Genre') 

# Genre distributions
fig, ax = plt.subplots()	
df.genre.hist(bins=np.arange(2*len(genres))-0.5)
plt.xticks(np.arange(len(genres)),genres,rotation=45) 
plt.xlim([-1,len(genres)+1])
plt.ylabel('Count')
plt.xlabel('Genre') 
plt.show()