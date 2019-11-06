"""Build corpus for LDA"""

import pandas as pd
import numpy as np
import ast
import string
from nltk.corpus import stopwords

# Stitch data sources together 
frame=[]
file_list=['number']+list(string.ascii_uppercase)

for fname in file_list:
	fpath='data/features/'+fname+'.tsv'
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

df=pd.concat(frame,ignore_index=True)
df=df.dropna()
df=df.reset_index()

def length_condition(word):
	"""Word must have at least 3 unique characters"""
	return len(np.unique(list(word)))>2

# Filter out stop words 
stop = stopwords.words('english') + list(string.punctuation)

# Filter special characters 
printable = set(string.printable)

# Relative year of release
cutoff=int(df.release.min()[:4])

# Build corpus: index, relative year of release, BOW expanded representation 
topic_model_path = 'data/lda_corpus.tsv'
with open(topic_model_path, 'wb') as f:
	for x in df.iterrows():
		year=int(x[1].release[:4])
		lyrics = x[1].lyrics
		lyrics=ast.literal_eval(lyrics)
		lyrics = [y[0] for y in lyrics for i in range(y[1])]
		lyrics = [y for y in lyrics if y not in stop and length_condition(y)]
		lyrics = ' '.join(lyrics)
		lyrics = filter(lambda y: y in printable, lyrics)
		f.write(str(x[0])+'\t'+str(year-cutoff)+'\t'+lyrics+'\n')