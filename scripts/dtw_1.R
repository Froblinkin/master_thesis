# Compute DTW distance matrix from chart position time series 

require(dtw)

path="data/ts_ngp.tsv"
dat<-readLines(path)
dat<-strsplit(dat,'\t')
dm<-matrix(0,length(dat),length(dat))

# Pairwise comparisons for upper-triangle 
# Align each song chart position time series 
for (i in seq(length(dat))){
  for (j in seq(i,length(dat))){
    dm[i,j]<-dtw(as.integer(dat[[i]][-c(1,2)]),as.integer(dat[[j]][-c(1,2)]))$normalizedDistance
  }
}

# Write to file
write.table(dm,file="data/dtw_dm.tsv",sep="\t",row.names=FALSE,col.names=FALSE)