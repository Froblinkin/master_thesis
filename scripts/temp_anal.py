"""Various plots showing temporal variation of features"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import datetime
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from sklearn import cluster, datasets, mixture
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler
from itertools import cycle, islice
from sklearn import manifold
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import linkage,fcluster
from scipy.spatial.distance import pdist
from collections import Counter

# Read in the data 
filename='data/model_tm.tsv'
df=pd.read_csv(filename,sep="\t",index_col=0)
df.index=pd.to_datetime(df.index)
song_count=(df.hip+df.rap+df.rock+df.metal+df.folk+df.country+df.blues+df['r&b']+df.soul+df.disco+df.funk+df['pop']+df['none']).values


fig, ax = plt.subplots()
datemin = np.datetime64(df.index[0], 'Y')
datemax = np.datetime64(df.index[-1], 'Y') + np.timedelta64(1, 'Y')
ax.set_xlim(datemin, datemax)

def price(x):
    return '$%1.2f' % x

ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.format_ydata = price
fig.autofmt_xdate()

# Compare hip hop and rap genres to a related topic model mixture 
fig, ax = plt.subplots()
ax.plot(df.rap/song_count,label='rap',marker="*",alpha=0.75,linestyle="None")
ax.plot(df.hip/song_count,label='hip hop',marker="+",alpha=0.75,linestyle="None")
ax.plot(df['4'],label='topic 4, 10 topic LDA',alpha=0.75)
plt.legend()
ax.set_xlabel('Time')
ax.set_ylabel('Abundance')
plt.show()

# Compare select The Echo Nest features with each other 
fig, ax = plt.subplots()
ax.plot(df.danceability,label='danceability',alpha=0.75)
ax.plot(df.valence,label='valence',alpha=0.75)
ax.plot(df.acousticness,label='acousticness',alpha=0.75)
plt.legend()
ax.set_xlabel('Time')
ax.set_ylabel('Abundance')
plt.show()

# Illustrate the notion of topic decomposition
filename='data/model_tm1.tsv'
df=pd.read_csv(filename,sep="\t",index_col=0)
df.index=pd.to_datetime(df.index)
df=df[df.index<'2011-01-01']
song_count=(df.hip+df.rap+df.rock+df.metal+df.folk+df.country+df.blues+df['r&b']+df.soul+df.disco+df.funk+df['pop']+df['none']).values

fig, ax = plt.subplots()

# Mixture from 10 topic model 
ax.plot(df['0'],label='topic 0, 10 topic LDA',alpha=0.75)
filename='data/model_tm1.tsv'
df_topic10=df.copy()
df=pd.read_csv(filename,sep="\t",index_col=0)
df.index=pd.to_datetime(df.index)
df=df[df.index<'2011-01-01']

# Mixtures from 20 topic model 
ax.plot(df['15'],label='topic 15, 20 topic LDA',alpha=0.75)
ax.plot(df['18'],label='topic 18, 20 topic LDA',alpha=0.75)
plt.legend()
ax.set_xlabel('Time')
ax.set_ylabel('Abundance')
plt.show()

df_topic20=df.copy()

from scipy.stats.stats import pearsonr

# Compute correlation between topic mixtures 
pearsonr(df_topic10['0'],df_topic20['15'])
pearsonr(df_topic10['0'],df_topic20['18'])
pearsonr(df_topic10['0'],df_topic20['15']+df_topic20['18'])


# Find the highest correlated combination of topic mixtures 
max_cor=0
for i in range(20):
	for j in range(20):
		for k in range(20):
			for l in range(20):
				a=pearsonr(df_topic10['0'],df_topic20[str(i)]+df_topic20[str(j)]+df_topic20[str(k)]+df_topic20[str(l)])
				if a[0]>max_cor:
					max_cor=a[0]
					print(str(i)+" "+str(j)+" "+str(k)+" "+str(l))

# Get topic mixtures for clusteirng 
filename='data/model_tm3.tsv'
df=pd.read_csv(filename,sep="\t",index_col=0)
df.index=pd.to_datetime(df.index)
df=df[df.index<'2011-01-01']
song_count=(df.hip+df.rap+df.rock+df.metal+df.folk+df.country+df.blues+df['r&b']+df.soul+df.disco+df.funk+df['pop']+df['none']).values
df[['hip','rap','rock','metal','folk','country','blues','r&b','soul','disco','funk','pop','none']]=(df[['hip','rap','rock','metal','folk','country','blues','r&b','soul','disco','funk','pop','none']].transpose()/song_count).transpose()
X=df.transpose().iloc[10:90].values

d=pdist(X,'correlation')
z=linkage(d,'complete')

class model:
    labels_=[]

# Compare hierarchical clusteirng with K-means 
for n_clusters in range(2,10):
	kmean = KMeans(n_clusters=n_clusters,init='random',random_state=0)
	model1=model()
	setattr(model1,'labels_',fcluster(z,n_clusters,"maxclust")-1)
	model2=kmean.fit(X)

	# t-SNE projection of topic mixture features  
	tsne = manifold.TSNE(n_components=2, init='random', perplexity=30,random_state=2)
	Y = tsne.fit_transform(X)

	# Plot clustering 
	fig, ax = plt.subplots(nrows=2)
	ax[0].set_title(n_clusters)
	ax[0].scatter(Y[:, 0], Y[:, 1],c=model1.labels_,alpha=0.25)
	ax[1].scatter(Y[:, 0], Y[:, 1],c=model2.labels_,alpha=0.25)

	# Show clustering counts 
	print(Counter(model1.labels_))
	print(Counter(model2.labels_))
	plt.show()

# Plot cluster time series  
n_clusters = 9
fig, ax = plt.subplots(nrows=3,ncols=3)
j=0
for i in range(n_clusters):
	ax[i%3][j].set_title( ' '.join([str(x) for x in np.where(model2.labels_==i)[0]]))
	ax[i%3][j].plot(np.transpose(X[model2.labels_==i]),alpha=0.5)

	for item in ([ax[i%3][j].title, ax[i%3][j].xaxis.label, ax[i%3][j].yaxis.label] +
			ax[i%3][j].get_xticklabels() + ax[i%3][j].get_yticklabels()):
		item.set_fontsize(5)

	if i%3==2:
		j+=1
plt.tight_layout()
plt.show()

for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(20)


# Box plots for topic mixtures split by season 
top_10_path="data/model/0/3/top10words"
with open(top_10_path,"rt") as f:
	a=f.readlines()
a=[x.split() for x in a]
a={int(x[0]):x[2:] for x in a}

fig, ax = plt.subplots()
X=df.transpose().iloc[10:90]
month=X.keys().month

# Seasons 
season={1:[9,10,11],2:[12,1,2],3:[3,4,5],4:[6,7,8]}
for i in range(80):
	fig, ax = plt.subplots()
	ax.set_title(a[i])

	# Mixture abundances 
	month_counts=[]
	for j in range(1,5):
		curr_months=season[j]
		curr_sum=[X.iloc[i][month==k].values for k in curr_months]
		curr_sum=[item for sublist in curr_sum for item in sublist]
		month_counts.append(np.array(curr_sum))

	ax.boxplot(month_counts,notch=True)
	print(i)
	plt.show()

# Test stationarity of topic mixtures 
from statsmodels.tsa.stattools import adfuller

a={}
for i in range(80):
	a[i]=adfuller(X.iloc[i].values,maxlag=52)[1]

# Plot sample time series 
fig, ax = plt.subplots()
ax.plot(df['5'],label='topic 5',alpha=0.75)
ax.plot(df['69'],label='topic 69',alpha=0.75)
ax.plot(df['0'],label='topic 0',alpha=0.75)
plt.legend()
ax.set_xlabel('Time')
ax.set_ylabel('Abundance')
plt.show()

# Box plots for specific topic mixtures split by season 

# Topic model 11 
X=df.transpose().iloc[10:90]
month=X.keys().month
season={1:[9,10,11],2:[12,1,2],3:[3,4,5],4:[6,7,8]}
i=11
fig, ax = plt.subplots()
ax.set_title('topic '+str(i))

month_counts=[]
for j in range(1,5):
	curr_months=season[j]
	curr_sum=[X.iloc[i][month==k].values for k in curr_months]
	curr_sum=[item for sublist in curr_sum for item in sublist]
	month_counts.append(np.array(curr_sum))
bplot=ax.boxplot(month_counts,notch=True,vert=True,patch_artist=True)

colors = ['pink', 'lightblue', 'lightgreen','orange']

for patch, color in zip(bplot['boxes'], colors):
    patch.set_facecolor(color)

labels = [item.get_text() for item in ax.get_xticklabels()]
labels=["fall","winter","spring","summer"]
ax.set_xticklabels(labels)
ax.set_xlabel('Time')
ax.set_ylabel('Abundance')
plt.show()

# Topic model 57
i=57
fig, ax = plt.subplots()
ax.set_title('topic '+str(i))

month_counts=[]
for j in range(1,5):
	curr_months=season[j]
	curr_sum=[X.iloc[i][month==k].values for k in curr_months]
	curr_sum=[item for sublist in curr_sum for item in sublist]
	month_counts.append(np.array(curr_sum))
bplot=ax.boxplot(month_counts,notch=True,vert=True,patch_artist=True)

colors = ['pink', 'lightblue', 'lightgreen','orange']

for patch, color in zip(bplot['boxes'], colors):
    patch.set_facecolor(color)

labels = [item.get_text() for item in ax.get_xticklabels()]
labels=["fall","winter","spring","summer"]
ax.set_xticklabels(labels)
ax.set_xlabel('Time')
ax.set_ylabel('Abundance')
plt.show()