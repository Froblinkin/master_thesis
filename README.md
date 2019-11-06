# Master's thesis: Modelling Chart Trajectories using Song Features
This will be my attempt at making the code from my [master's thesis](https://uwspace.uwaterloo.ca/handle/10012/14937) avaiable for those who are curious and/or want to dabble into music information retrieval. 

# Data acquisition
1. billboard.py, [weekly Billboard Hot 100](https://www.billboard.com/charts/hot-100/1958-08-04)
2. Musixmatch, the Million Song Dataset 
  * [Lyrics](http://millionsongdataset.com/sites/default/files/AdditionalFiles/mxm_dataset.db)
  * [Metadata](http://millionsongdataset.com/sites/default/files/AdditionalFiles/track_metadata.db)

3. The Echo Nest

# Pre-processing
1. similarity measure 
2. LDA topic modelling of BOW lyrics
3. normalizing features
4. matching records

# Modeling (regression models as classifiers given some separator)
1. logistic regression
2. regularized logistic regression
3. one-against-all logistic regression

# Visualizations 
1. histogram distributions
2. chart trajectories
3. cluster analysis
