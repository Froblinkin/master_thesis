"""Visualize time series from each target variable class"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

# Song records 
path_tm="data/model1_data.tsv"
df=pd.read_csv(path_tm,sep='\t',encoding='utf8')

# Time series 
path='data/ts_ngp.tsv'
ts=[]
with open(path,'rb') as f:    
	reader=csv.reader(f,delimiter='\t')
	for row in reader:
		ts.append(np.array(row[2:]).astype(np.float))
ts=np.array(ts)

def plot_hits(miss,hit,target,ax):
	"""Plot time series and address a typo in the time series data

	Parameters
	----------
	miss : list 
	List of class labels corresponding to misses
	
	hit : list 
	List of class labels corresponding to hits

	target : string 
	Target variable (either interval or alignment)

	ax : matplotlib subplot ax object
	Axis where time series will be plotted 
	"""

	hit_tracks=np.array([])
	miss_tracks=np.array([])

	# Find all tracks that are hits and flops from chart time series 
	for h in hit:
		hit_tracks=np.concatenate((hit_tracks,ts[np.where(df[target]==h)[0]]),axis=0)
	for m in miss:
		miss_tracks=np.concatenate((miss_tracks,ts[np.where(df[target]==m)[0]]),axis=0)

	# Duplicate record double its actual length corrected 
	if target=="interval":
		if 39 in hit:
			len_list=np.array([len(x) for x in hit_tracks])
			broken_idx=np.where(len_list==28)[0][0]
			x,y,z=hit_tracks[:broken_idx],hit_tracks[broken_idx],hit_tracks[broken_idx+1:]
			hit_tracks=np.concatenate([x,z])
			first_release=y[:14]
			sec_release=y[14:]
			hit_tracks=list(hit_tracks)
			hit_tracks.append(first_release)
			hit_tracks.append(sec_release)
			hit_tracks=np.array(hit_tracks)
		elif 39 in miss:
			len_list=np.array([len(x) for x in miss_tracks])
			broken_idx=np.where(len_list==28)[0][0]
			x,y,z=miss_tracks[:broken_idx],miss_tracks[broken_idx],miss_tracks[broken_idx+1:]
			miss_tracks=np.concatenate([x,z])
			first_release=y[:14]
			sec_release=y[14:]
			miss_tracks=list(miss_tracks)
			miss_tracks.append(first_release)
			miss_tracks.append(sec_release)
			miss_tracks=np.array(miss_tracks)

	# Plot tracks for hits and flops 
	plot_tracks(hit_tracks,'r',ax,'Late')
	plot_tracks(miss_tracks,'b',ax,'Early')


def plot_tracks(tracks,color,plot,label):
	"""Plot tracks with a specific colour 

	Parameters
	----------
	tracks : list of NumPy arrays
	Time series to be plotted 

	color : string
	Colour for points and line 

	plot : matplotlib subplot ax 
	Axis where time series will be plotted 

	label : string 
	Label for legend 
	"""
	# Plot tracks as detached points 
	max_len=0
	for t in tracks:
		plot.plot(t,'.',color=color,alpha=0.025)
		if max_len<len(t):
			max_len=len(t)
	
	# Average line through individual time series 
	agr_t=np.zeros(max_len)
	denom_t=np.zeros(max_len)

	# Draw a line through all of the points 
	for t in tracks:
		agr_t+=np.concatenate((t,np.zeros(len(agr_t)-len(t))),axis=0)
		denom_t+=np.concatenate((np.ones(len(t)),np.zeros(len(agr_t)-len(t))),axis=0)
	if color=='b':
		line_col='midnightblue'
	if color=='r':
		line_col='maroon'
	plot.plot(agr_t/denom_t,line_col,alpha=1,label=label)

# Plot binary classes 
fig, ax = plt.subplots(nrows=2,ncols=1,sharex=True,sharey=True)
plot_hits([0],[34,35,40,41],'interval',ax[0])
plot_hits([4,5],[10,30,11],'align',ax[1])
plt.ylabel('Position')
plt.xlabel('Time') 
plt.legend()

# Plot interval classes for comparing weeks on chart 
fig, ax = plt.subplots(nrows=3,ncols=1,sharex=True,sharey=True)
plot_hits([0],[2,3,4],'interval',ax[0])
plot_hits([12,13,14],[16,17],'interval',ax[1])
plot_hits([38,39],[41],'interval',ax[2])
plt.ylabel('Position')
plt.xlabel('Time') 
plt.legend()

# Plot interval classes for comparing peak position 
fig, ax = plt.subplots(nrows=3,ncols=1,sharex=True,sharey=True)
plot_hits([17,23],[41],'interval',ax[0])
plot_hits([3,9],[39],'interval',ax[1])
plot_hits([2],[26,32,38],'interval',ax[2])
plt.ylabel('Position')
plt.xlabel('Time') 
plt.legend()

# Plot alignment classes for multiclass task 
fig, ax = plt.subplots(nrows=5,ncols=1,sharex=True,sharey=True)
plot_hits([7],[],'align',ax[0])
plot_hits([28],[],'align',ax[1])
plot_hits([2],[],'align',ax[2])
plot_hits([10],[],'align',ax[3])
plot_hits([34],[],'align',ax[4])
plt.ylabel('Position')
plt.xlabel('Time') 
plt.legend()

# Plot songs from classes that were released in the first 30 years of the charts 
fig, ax = plt.subplots(nrows=2,ncols=1,sharex=True,sharey=True)
ts=ts[df['time'].isin([1,2,3,5,6,7])]
df=df[df['time'].isin([1,2,3,5,6,7])]
plot_hits([],[35,34,33,32],'align',ax[0])
plot_hits([40,39,38,37,10],[],'align',ax[1])
plt.ylabel('Position')
plt.xlabel('Time') 
plt.legend()
