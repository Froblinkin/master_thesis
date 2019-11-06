# Master's thesis: Modelling Chart Trajectories using Song Features
This will be my attempt at making the code from my [master's thesis](https://uwspace.uwaterloo.ca/handle/10012/14937) avaiable for those who are curious and/or want to dabble into music information retrieval. 

# Data acquisition
1. Chart data: [billboard.py](https://github.com/guoguo12/billboard-charts), [weekly Billboard Hot 100](https://www.billboard.com/charts/hot-100/1958-08-04)
2. Lyrics data: Musixmatch, [the Million Song Dataset](http://millionsongdataset.com/)
  * [Lyrics](http://millionsongdataset.com/sites/default/files/AdditionalFiles/mxm_dataset.db)
  * [Metadata](http://millionsongdataset.com/sites/default/files/AdditionalFiles/track_metadata.db)
3. Audio features: [spotipy](https://spotipy.readthedocs.io/en/latest/), [The Echo Nest](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)

# Pre-processing
1. similarity measure inspired by [Askin & Mauskapf](https://journals.sagepub.com/doi/abs/10.1177/0003122417728662)
2. [LDA topic modelling](http://mallet.cs.umass.edu/download.php) of BOW lyrics
3. normalizing features
4. matching records
5. genre labelling 

# Modeling (regression models as classifiers given some separator)
1. logistic regression
2. regularized logistic regression
3. one-against-all logistic regression

# Visualizations 
1. histogram distributions
2. chart trajectories
3. cluster analysis
