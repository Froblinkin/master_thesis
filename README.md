# Master's thesis: Modelling Chart Trajectories using Song Features
This will be my attempt at making the code from my [master's thesis](https://uwspace.uwaterloo.ca/handle/10012/14937) avaiable for those who are curious and/or want to dabble into music information retrieval. I've simplified some of the pathing and updated some comments to make things more readable. 

In my thesis, I proposed two target variables for modelling hits and flops, which I then attemped to model with various forms of logistic regression.

![comparison](comparing_binary.png)

I presented it on August 16, 2019 ([announcement](https://uwaterloo.ca/artificial-intelligence-group/events/masters-thesis-presentation-modelling-chart-trajectories)). My slides can be found [here](http://www.jperrie.com/thesis_presentation_08_16_19.pdf) (I did have one typo, a duplicate figure, that I've since corrected). 

# Data acquisition
1. Chart data: [billboard.py](https://github.com/guoguo12/billboard-charts), [weekly Billboard Hot 100](https://www.billboard.com/charts/hot-100/1958-08-04)
2. Lyrics data: Musixmatch, [the Million Song Dataset](http://millionsongdataset.com/)
  * [Lyrics](http://millionsongdataset.com/sites/default/files/AdditionalFiles/mxm_dataset.db)
  * [Metadata](http://millionsongdataset.com/sites/default/files/AdditionalFiles/track_metadata.db)
3. Audio features: [spotipy](https://spotipy.readthedocs.io/en/latest/), [The Echo Nest](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)

# Pre-processing
1. Similarity measure inspired by [Askin & Mauskapf](https://journals.sagepub.com/doi/abs/10.1177/0003122417728662)
2. [LDA topic modelling](http://mallet.cs.umass.edu) of BOW lyrics
3. Normalizing features
4. Matching records
5. [Genre labelling](https://developer.spotify.com/documentation/web-api/reference/artists/get-artist/) 

# Modeling (regression models as classifiers given some separator)
1. Logistic regression
2. Regularized logistic regression
3. One-against-all logistic regression

# Visualizations 
1. Histogram distributions
2. Chart trajectories
3. Cluster analysis
