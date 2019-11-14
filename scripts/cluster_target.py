"""Perform interval clustering and alignment clustering given DTW distance matrix"""

import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram, complete
from collections import Counter

# Read in distance matrix
path='data/dtw_dm.tsv'
dm=[]
with open(path,'rb') as f:    
	reader=csv.reader(f,delimiter='\t')
	for row in reader:
		dm.append(row)

# Transform to full matrix from upper triangle
dm=np.array(dm).astype(np.float)
full_dm=dm+dm.transpose()
flat_dm=[x for idy,y in enumerate(dm) for idx,x in enumerate(y) if idx>idy]

# Read in song features 
fpath='data/genre_set.tsv'
df=pd.read_csv(fpath,sep='\t',encoding='utf8')

# Get chart data and merge records
chart_path = 'data/chart_record.tsv'
chart=pd.read_csv(chart_path,sep='\t',index_col=0,encoding='utf8')
df_c=df.merge(chart)

# Apply complete linkage clustering
# Cutoff of 14.5 chosen to generate 40 clusters 
labels=fcluster(linkage(flat_dm,method='complete'),14.5,'distance')
df['cluster']=labels

# Write labels to file 
with open('data/complete_linkage_40.txt','wb') as f:
	for l in labels:
		f.write(str(l)+'\n')

# Weeks on chart target variable 
df['week']=0

# Peak position target variable
df['peak']=0

# Find weeks on chart and peak position for each song 
for x in df.iterrows():
	artist=x[1].artist
	title=x[1].title
	chart_weeks=max(df_c.loc[(df_c.artist==artist) & (df_c.title==title),'week'])
	peak=min(df_c.loc[(df_c.artist==artist) & (df_c.title==title),'peak'])
	df.loc[(df.artist==artist) & (df.title==title),['week','peak']]=[chart_weeks,peak,]

# Merged peak position target variable 
df['mg']=0
df.loc[df.peak>60,'mg']=1
df.loc[(df.peak>40)&(df.peak<=60),'mg']=2
df.loc[(df.peak>20)&(df.peak<=40),'mg']=3
df.loc[(df.peak>10)&(df.peak<=20),'mg']=4
df.loc[(df.peak>5)&(df.peak<=10),'mg']=5
df.loc[(df.peak>1)&(df.peak<=5),'mg']=6
df.loc[df.peak==1,'mg']=7

# Merged weeks on chart target variable 
df['mw']=0
df.loc[df.week>20,'mw']=6
df.loc[(df.week>16)&(df.week<=20),'mw']=5
df.loc[(df.week>12)&(df.week<=16),'mw']=4
df.loc[(df.week>8)&(df.week<=12),'mw']=3
df.loc[(df.week>4)&(df.week<=8),'mw']=2
df.loc[df.week<=4,'mw']=1

# Find cross product between merged target variables 
cmb_map={}
count=0
for i in range(1,max(df.mg)+1):
	for j in range(1,max(df.mw)+1):
		cmb_map[(i,j)]=count
		count+=1
cmb=df[['mg','mw']].as_matrix()
cmb=np.array([cmb_map[tuple(x)] for x in cmb])
df['cmb']=cmb

# Write cross product classes to file 
with open('data/combined_cluster.txt','wb') as f:
	for c in cmb:
		f.write(str(c)+'\n')

# Get the counts from each class (used to build mosaic plots)
cmb_count=Counter(df.cmb)
for i in range(42):
	if i not in cmb_count:
		cmb_count[i]=0
cmb_count=np.array(list(cmb_count.values())).reshape((7,6))
np.savetxt("data/combined_count.csv",cmb_count,delimiter=',')

# Write cluster labels to song record DataFrame 
df.to_csv('data/clustered_df.tsv',sep='\t',index=False,encoding='utf8')